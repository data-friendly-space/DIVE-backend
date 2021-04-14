from __future__ import unicode_literals
'''
Functions for reading, sampling, and detecting types of datasets

No manipulation or calculation, only description
'''

import os
import re
import csv
import xlrd
import json
import codecs
'''
try:
    import cStringIO as StringIO
except:
    import StringIO
'''
from io import StringIO
import boto3
import chardet
import pandas as pd

from werkzeug.utils import secure_filename
from flask import current_app

from dive.base.core import s3_client, compress
from dive.base.db import db_access
from dive.base.exceptions import UploadTooLargeException
from dive.worker.core import celery, task_app
from dive.base.data.access import get_data
from dive.base.data.in_memory_data import InMemoryData as IMD

import logging
logger = logging.getLogger(__name__)

from pathlib import Path
import sys
# added to create folder before file is saved


def save_fileobj_to_s3(fileobj, project_id, file_name):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params = {
                'Bucket': current_app.config['AWS_DATA_BUCKET'],
                'Key': file_name
            },
            ExpiresIn = 86400
        )

        s3_client.upload_fileobj(
            fileobj,
            current_app.config['AWS_DATA_BUCKET'],
            "%s/%s" % (project_id, file_name)
        )
    except Exception as e:
        logger.error(e, exc_info=True)
    return url


def upload_file(project_id, file_obj):
    '''
    1. Save file in uploads/project_id directory
    2. If excel or json, also save CSV versions
    3. If all steps are successful, save file location in project data collection

    file_name = foo.csv
    file_title = foo
    '''
    print('Upload file called')
    file_name = secure_filename(file_obj.filename)
    file_title, file_type = file_name.rsplit('.', 1)

    # Pre-save properties
    if current_app.config['STORAGE_TYPE'] == 'file':
        path = os.path.join(current_app.config['STORAGE_PATH'], str(project_id), file_name)
    elif current_app.config['STORAGE_TYPE'] == 's3':
        path = 'https://s3.amazonaws.com/%s/%s/%s' % (current_app.config['AWS_DATA_BUCKET'], str(project_id), file_name)

    # Persisting file and saving to DB
    datasets = save_dataset_to_db(
        project_id,
        file_obj,
        file_title,
        file_name,
        file_type,
        path,
        current_app.config['STORAGE_TYPE']
    )
    file_obj.close()
    return datasets


def get_encoding(file_obj, sample_size=100*1024*1024):
    try:
        blob = file_obj.read(sample_size)
        file_obj.seek(0)
    except:
        blob = file_obj

    encoding = chardet.detect(blob)
    return encoding['encoding']


def get_dialect(file_obj, sample_size=1024*1024):
    try:
        sample = file_obj.read(sample_size)
    except StopIteration:
        sample = file_obj.readline()
    file_obj.seek(0)

    print(sample)

    print('about to sniff for dialect')

    sniffer = csv.Sniffer()
    #dialect = sniffer.sniff(sample)
    # Changed due to bytes error in python 3
    dialect = sniffer.sniff(sample.decode('utf-8'))

    #---
    #dialect = csv.Sniffer().sniff(csvfile.read(1024))
    #---
    
    result = {
        'delimiter': dialect.delimiter,
        'doublequote': dialect.doublequote,
        'escapechar': dialect.escapechar,
        'lineterminator': dialect.lineterminator,
        'quotechar': dialect.quotechar,
    }
    print(result)
    return result


def save_dataset_to_db(project_id, file_obj, file_title, file_name, file_type, path, storage_type, limit_flat_file_size=False):
    encoding = 'utf-8'

    # Default dialect (for Excel and JSON conversion)
    dialect = {
        "delimiter": ",",
        "quotechar": "\"",
        "escapechar": None,
        "doublequote": False,
        "lineterminator": "\r\n"
    }

    file_docs = []

    if file_type in ['csv', 'tsv', 'txt']:
        dialect = get_dialect(file_obj)
        encoding = get_encoding(file_obj)
        file_obj.seek(0)

        # Force encoding to UTF-8
        if (encoding not in ['ascii']) and ('utf' not in encoding) and ('UTF' not in encoding):
            try:
                coerced_content = file_obj.read().decode(encoding).encode('utf-8', 'replace')
            except UnicodeDecodeError as UDE:
                try:
                    coerced_content = unicode(file_obj.read(), errors='replace')
                except UnicodeDecodeError as UDE:
                    logger.error('Error coercing unicode for file with path %s', path, exc_info=True)
                    raise UDE
            file_obj.seek(0)
            file_obj.write(coerced_content)
            file_obj.seek(0)

        if limit_flat_file_size:  # False by default, because implemented on front-end
            rows = file_obj.readlines()
            cols = rows[0].split(dialect['delimiter'])
            num_rows = len(rows)
            num_cols = len(cols)
            file_obj.seek(0)

            if (num_rows > current_app.config['ROW_LIMIT']):
                raise UploadTooLargeException('Uploaded file has {} rows, exceeding row limit of {}'.format(num_rows, current_app.config['ROW_LIMIT']))
            elif (num_cols > current_app.config['COLUMN_LIMIT']):
                raise UploadTooLargeException('Uploaded file has {} columns, exceeding row limit of {}'.format(num_cols, current_app.config['COLUMN_LIMIT']))

        file_doc = save_flat_table(project_id, file_obj, file_title, file_name, file_type, path)
        file_docs.append(file_doc)

    elif file_type.startswith('xls'):
        file_docs = save_excel_to_csv(project_id, file_obj, file_title, file_name, file_type, path)

    elif file_type == 'json':
        file_doc = save_json_to_csv(project_id, file_obj, file_title, file_name, file_type, path)
        file_docs.append(file_doc)

    datasets = []
    for file_doc in file_docs:
        path = file_doc['path']

        dataset = db_access.insert_dataset(project_id,
            path = path,
            encoding = encoding,
            dialect = dialect,
            offset = None,
            title = file_doc['file_title'],
            file_name = file_doc['file_name'],
            type = file_doc['type'],
            storage_type = storage_type
        )
        datasets.append(dataset)

    return datasets


def save_flat_table(project_id, file_obj, file_title, file_name, file_type, path):
    file_doc = {
        'file_title': file_title,
        'file_name': file_name,
        'type': file_type,
        'path': path
    }

    if current_app.config['STORAGE_TYPE'] == 'file':
        try:
            print('Saving file to this path', path)
            print(file_obj)

            last_path_char = path.rfind('/')
            if last_path_char != -1:
                dir_path = path[0:(last_path_char+1)]
                print("dir_path",dir_path)
                p = Path(dir_path)
                p.mkdir(exist_ok=True)

            file_obj.save(path)
            import os
            print('folder contentes', os.listdir("/usr/src/app/uploads/1/"))
        except IOError:
            print('File save error in save_flat_table', path)
            logger.error('Error saving file with path %s', path, exc_info=True)
        except: # catch *all* exceptions
            e = sys.exc_info()[0]
            print(str(e))
    elif current_app.config['STORAGE_TYPE'] == 's3':
        url = save_fileobj_to_s3(file_obj, project_id, file_name)
    return file_doc


def save_excel_to_csv(project_id, file_obj, file_title, file_name, file_type, path):
    book = xlrd.open_workbook(file_contents=file_obj.read())
    sheet_names = book.sheet_names()

    file_docs = []
    for sheet_name in sheet_names:
        sheet = book.sheet_by_name(sheet_name)

        if (sheet.nrows > current_app.config['ROW_LIMIT']):
            raise UploadTooLargeException('Uploaded file has {} rows, exceeding row limit of {}'.format(sheet.nrows, current_app.config['ROW_LIMIT']))
        elif (sheet.ncols > current_app.config['COLUMN_LIMIT']):
            raise UploadTooLargeException('Uploaded file has {} columns, exceeding row limit of {}'.format(sheet.ncols, current_app.config['COLUMN_LIMIT']))

        if sheet.nrows == 0: continue
        csv_file_title = file_name + "_" + sheet_name
        csv_file_name = csv_file_title + ".csv"

        if current_app.config['STORAGE_TYPE'] == 's3':
            csv_path = 'https://s3.amazonaws.com/%s/%s/%s' % (current_app.config['AWS_DATA_BUCKET'], str(project_id), csv_file_name)
            strIO = StringIO.StringIO()
            wr = csv.writer(strIO, quoting=csv.QUOTE_ALL)
            for rn in xrange(sheet.nrows) :
                wr.writerow([ unicode(v).encode('utf-8', 'replace') for v in sheet.row_values(rn) ])
            strIO.seek(0)

            response = s3_client.upload_fileobj(
                strIO,
                current_app.config['AWS_DATA_BUCKET'],
                '%s/%s' % ( str(project_id), csv_file_name )
            )

        if current_app.config['STORAGE_TYPE'] == 'file':
            csv_path = os.path.join(current_app.config['STORAGE_PATH'], str(project_id), csv_file_name)
            csv_file = open(csv_path, 'wb')
            wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            for rn in xrange(sheet.nrows) :
                wr.writerow([ unicode(v).encode('utf-8') for v in sheet.row_values(rn) ])
            csv_file.close()

        file_doc = {
            'file_title': csv_file_title,
            'file_name': csv_file_name,
            'path': csv_path,
            'type': 'csv',
            'orig_type': 'xls'
        }
        file_docs.append(file_doc)
    return file_docs


def save_json_to_csv(project_id, file_obj, file_title, file_name, file_type, path):
    f = open(path, 'rU')
    json_data = json.load(f)

    orig_type = file_name.rsplit('.', 1)[1]
    csv_file_title = file_title
    csv_file_name = csv_file_title + ".csv"
    csv_path = os.path.join(current_app.config['STORAGE_PATH'], project_id, csv_file_name)

    csv_file = open(csv_path, 'wb')
    wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

    header = json_data[0].keys()
    num_rows = len(json_data)
    num_cols = len(header)

    if (num_rows > current_app.config['ROW_LIMIT']):
        raise UploadTooLargeException('Uploaded file has {} rows, exceeding row limit of {}'.format(num_rows, current_app.config['ROW_LIMIT']))
    elif (num_cols > current_app.config['COLUMN_LIMIT']):
        raise UploadTooLargeException('Uploaded file has {} columns, exceeding row limit of {}'.format(num_cols, current_app.config['COLUMN_LIMIT']))

    wr.writerow([v.encode('utf-8') for v in header])
    for i in range(len(json_data)) :
        row = []
        for field in header :
            row.append(json_data[i][field])
        wr.writerow([unicode(v).encode('utf-8') for v in row])
    csv_file.close()
    file_doc = {
        'title': csv_file_title,
        'file_name': csv_file_name,
        'path': csv_path,
        'type': 'csv',
        'orig_type': 'json'
    }
    return file_doc
