#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# standard python imports

import logging
import os


def create_logger() -> logging.Logger:
    """Create a logger for use in all cases"""
    level = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=level, format='%(message)s',
                        datefmt="[%d.%m.%Y %H:%M:%S]")
    return logging.getLogger('universal')
