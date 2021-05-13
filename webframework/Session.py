#!/usr/bin/env python3

import datetime
import uuid
from typing import Dict, Any


class Session:
    sid: str
    valid_until: datetime.datetime
    data: Dict[str, Any]

    def __init__(self, valid_for=datetime.timedelta(minutes=15)):
        self.sid = str(uuid.uuid1())
        self.valid_until = datetime.datetime.now() + valid_for
        self.data = {}
        self.authorized = False
        self.username = ''
        self.admin = False

    def refresh(self, valid_for=datetime.timedelta(minutes=15)):
        self.valid_until = datetime.datetime.now() + valid_for
