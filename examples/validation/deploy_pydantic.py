#!/usr/bin/env python3

import nestedtext as nt
from pydantic import BaseModel, EmailStr
from typing import List
from pprint import pprint

class Database(BaseModel):
    engine: str
    host: str
    port: int
    user: str

class Config(BaseModel):
    debug: bool
    secret_key: str
    allowed_hosts: List[str]
    database: Database
    webmaster_email: EmailStr

def normalize_key(key, parent_keys):
    return '_'.join(key.lower().split())

obj = nt.load('deploy.nt', normalize_key=normalize_key)
config = Config.parse_obj(obj)

pprint(config.dict())
