# pull official base image
FROM python:3

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
    && apt-get install -y netcat python-scipy

# install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# copy project
COPY . /usr/src/app/

# run gunicorn
CMD ["gunicorn"  , "-b", "0.0.0.0:8081", "dive.server.core:app"]
