'''
Set-up logging entry point given config file
'''
import os
import yaml
import logging
import logging.config


def setup_logging(default_path='logging.yaml', default_level=logging.DEBUG):
    path = default_path
    logging.basicConfig(level=default_level)
    return

    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
