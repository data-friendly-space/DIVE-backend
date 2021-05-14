import logging

from dive.base.core import create_app

def create_api(app):
    from flask_restful import Api
    from dive.server.api import add_resources

    api = Api(catch_all_404s=True)
    api = add_resources(api)
    api.init_app(app)

    return api

app = create_app()
app.app_context().push()
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.INFO)

api = create_api(app)
