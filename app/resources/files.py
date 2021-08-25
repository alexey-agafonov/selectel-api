#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

from flask import abort, request
from flask_restful import Resource
from werkzeug.utils import secure_filename

from app.util.selectel import Client
from app.util.auth import require_user_token
from app.util.loggers import create_logger


class File(Resource):
    @require_user_token
    def delete(self, filename: str):
        """Delete unused user's files"""
        client = Client(user_id=request.headers.get('X-Auth-Token'))
        status = client.remove_file(filename=filename)

        return status


class FilesList(Resource):
    @require_user_token
    def get(self):
        """Get all user's files from cloud storage"""
        client = Client(user_id=request.headers.get('X-Auth-Token'))
        files = client.files()

        return files


class UploadFile(Resource):
    def __init__(self):
        self.logger = create_logger()

    @require_user_token
    def put(self):
        """Save user's files to the cloud storage"""
        files = request.files

        if len(files) == 0:
            return abort(400, 'No files in request.')

        try:
            token: str = request.headers.get('X-Auth-Token')
            Path(f'uploads/{token}').mkdir(parents=True, exist_ok=True)

            chunk_size: int = 16192 * 1024
            part: int = 1
            while True:
                chunk = files['file'].stream.read(chunk_size)
                filename: str = secure_filename(files['file'].filename)

                if filename == '':
                    return abort(400, 'Files must have a name.')

                if len(chunk) == 0:
                    self.logger.info(f'{filename=} all chunks has written to the disk.')
                    break
                self.logger.info(os.getenv("UPLOAD_FOLDER"))
                with open(f'uploads/{token}/{filename[:240]}_part{part}', 'bw') as f:
                    self.logger.info(f'{filename=} part {part} has written to the disk.')
                    f.write(chunk)

                part += 1

            client = Client(user_id=request.headers.get('X-Auth-Token'))
            status = client.save_file()

            if status[1] in (200, 201, 202):
                return {'message': f'File "{filename}" has uploaded successfully.'}, 201
            else:
                return status
        except Exception as ex:
            self.logger.error(ex)
            return abort(500)
