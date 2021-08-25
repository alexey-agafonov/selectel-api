#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import uuid
from typing import Optional, List, Union, Tuple

import requests

from app.util.loggers import create_logger


class CloudStorage:
    API_URL: str = 'https://api.selcdn.ru'
    AUTH_TOKENS_URL: str = f'{API_URL}/v3/auth/tokens'
    TEMP_TOKENS_URL: str = f'{API_URL}/v1/temptokens'

    def __init__(self, user_id: str, password: str):
        self.__user_id = user_id
        self.__password = password
        self.logger = create_logger()

    def get_access_token(self) -> Union[Optional[str], Tuple]:
        data = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "id": self.__user_id,
                            "password": self.__password
                        }
                    }
                }
            }
        }

        try:
            response = requests.post(self.AUTH_TOKENS_URL, data=json.dumps(data))
        except requests.exceptions.RequestException:
            return 'Can\'t request your data. Try again later.', 500

        if response.status_code == 201:
            return response.headers.get('X-Subject-Token')
        else:
            return response.text, response.status_code

    def create_container(self, user_id):
        access_token = self.get_access_token()

        headers = {
            'X-Auth-Token': access_token,
            'X-Container-Meta-Type': 'private'
        }

        try:
            response = requests.put(f'{self.API_URL}/v1/SEL_{self.__user_id}/{user_id}/',
                                       headers=headers)
        except requests.exceptions.RequestException:
            return 'Can\'t request your data. Try again later.', 500

        return response.text, response.status_code

    def get_files_from_container(self, user_id: uuid) -> Union[List, Tuple]:
        access_token = self.get_access_token()

        try:
            response = requests.get(f'{self.API_URL}/v1/SEL_{self.__user_id}/{user_id}',
                                    headers={'X-Auth-Token': access_token})
        except requests.exceptions.RequestException:
            return 'Can\'t request your data. Try again later.', 500

        raw_files = response.content.decode('utf-8').split('\n')
        files = [file for file in raw_files if file != '']

        if len(files) == 0:
            return '', 204

        return files

    def remove_file_from_container(self, user_id: uuid, filename: str) -> Optional[Tuple]:
        access_token = self.get_access_token()

        try:
            response = requests.delete(f'{self.API_URL}/v1/SEL_{self.__user_id}/{user_id}/{filename}',
                                       headers={'X-Auth-Token': access_token})
        except requests.exceptions.RequestException:
            return 'Can\'t request your data. Try again later.', 500

        return response.text, response.status_code


class Client:
    _cloud_storage = CloudStorage(user_id=os.getenv('SELECTEL_USER_ID'),
                                  password=os.getenv('SELECTEL_PASSWORD'))

    def __init__(self, user_id: uuid):
        self.user_id = user_id
        self.logger = create_logger()

    @property
    def cloud_storage(self):
        return self._cloud_storage

    def files(self) -> Union[List, Tuple]:
        files = self.cloud_storage.get_files_from_container(user_id=self.user_id)

        return files

    def save_file(self) -> Optional[Tuple]:
        status = self.cloud_storage.create_container(user_id=self.user_id)

        return status

    def remove_file(self, filename: str) -> Optional[Tuple]:
        status = self.cloud_storage.remove_file_from_container(user_id=self.user_id,
                                                               filename=filename)

        return status
