import os
import json

from jsonschema import Draft4Validator, ValidationError

config_schema = os.path.dirname(__file__)
config_schema = os.path.join(config_schema, 'schemas', 'config.json')

with open(config_schema, 'rb') as fh:
    config_schema = json.load(fh)
    config_validator = Draft4Validator(config_schema)
