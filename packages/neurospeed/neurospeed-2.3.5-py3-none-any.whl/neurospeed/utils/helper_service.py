# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:07:49 2021

@author: NeuroBrave
"""

import json
import random
import string


class UtilService:
    
    def __init__(self):
        pass
      
    def load_config_file(config_path): 
        with open(config_path) as f:
          config = json.load(f)
          return config
      
        
    def generateId(id_length):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(id_length))