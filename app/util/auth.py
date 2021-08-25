#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import wraps

import uuid as uuid
from flask import abort, request


def require_user_token(api_method):
    @wraps(api_method)
    def check_user_token(*args, **kwargs):
        token = request.headers.get('X-Auth-Token')
        try:
            uuid.UUID(token)
            return api_method(*args, **kwargs)
        except (TypeError, ValueError):
            abort(401, 'The server could not verify your token.')

    return check_user_token
