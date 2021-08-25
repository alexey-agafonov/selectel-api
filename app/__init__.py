#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from flasgger import Swagger
from flask import Flask
from flask_restful import Api

from app.resources.files import File, FilesList, UploadFile
from app.config import env_config
from app.util.selectel import CloudStorage

api = Api(prefix='/v1/', catch_all_404s=True)


def create_app(config_name: str) -> Flask:
    """Create Flask app from an environment config"""
    app: Flask = Flask(__name__)
    app.config.from_object(env_config[config_name])

    app.config['SWAGGER'] = {
        'title': 'Selectel Upload API',
        'uiversion': 2,
        'specs_route': '/docs/'
    }
    Swagger(app, template_file='../docs/swagger.yml', parse=True)
    from app.util.loggers import create_logger

    api.add_resource(FilesList, '/files/')
    api.add_resource(File, '/files/<string:filename>')
    api.add_resource(UploadFile, '/upload/')
    api.init_app(app=app)

    selectel_user_id = os.getenv('SELECTEL_USER_ID')
    selectel_password = os.getenv('SELECTEL_PASSWORD')
    cloud_storage = CloudStorage(user_id=selectel_user_id, password=selectel_password)
    cloud_storage.get_access_token()

    return app
