from pprint import pprint

import yaml

import logging
log = logging.getLogger(__name__)

def _overlay(defaults, config):
    # FIXME: Could do way more error checking of config
    for key, value in config.items():
        if key in defaults:
            if isinstance(defaults[key], dict):
                if not isinstance(value, dict):
                    raise ValueError(f'Expected {key} to be a dictionary')
                else:
                    _overlay(defaults[key], value)
            elif isinstance(defaults[key], list):
                if not isinstance(value, list):
                    raise ValueError(f'Expected {key} to be a list')
                else:
                    defaults[key] = value
            elif isinstance(defaults[key], str):
                if not isinstance(value, (str, float, int)):
                    raise ValueError(f'Expected {key} to be a string')
                else:
                    defaults[key] = str(value)
            elif isinstance(defaults[key], float):
                if not isinstance(value, (float, int)):
                    raise ValueError(f'Expected {key} to be a float')
                else:
                    defaults[key] = float(value)
            elif isinstance(defaults[key], int):
                if not isinstance(value, int):
                    raise ValueError(f'Expected {key} to be an integer')
                else:
                    defaults[key] = str(value)
            elif isinstance(defaults[key], bool):
                if not isinstance(value, bool):
                    raise ValueError(f'Expected {key} to be an boolean')
                else:
                    defaults[key] = value
            else:
                raise ValueError(f'Unexpected type {type(defaults[key])} for default {key}, value: "{defaults[key]}"')
        else:
            defaults[key] = value

def parse_yaml(defaults_fp, config_fp):
    log.info(f"Reading defaults from '{defaults_fp.name}'")
    defaults = yaml.load(defaults_fp, yaml.Loader)
    log.info(f"Reading input from '{config_fp.name}'")
    config = yaml.load(config_fp, yaml.Loader)
#     
#     print('defaults')
#     print('========')
#     pprint(defaults)
#     print()
# 
#     print('config')
#     print('======')
#     pprint(config)
#     print()
    
    _overlay(defaults, config)
    
    return defaults
        
        
