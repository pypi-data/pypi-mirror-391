

from neurospeed.utils.helper_service import UtilService as utils
from pathlib import Path
import os
import logging
from neurospeed.constants import PROD_API_CONFIG

class ApiConfig:

    def __init__(self, api_config = PROD_API_CONFIG):
        self._contex = "ApiConfig - "
        
        '''
        precedence of config path options: 
        
        if C:/neurobrave/hia_config.json exists, it's used
        otherwise, if /config/api_config.json exists under the runtime folder, its' used
        it none of these exist, defauilt that comes with the neurospeed library is used.
            
        '''
        
        self._api_config = api_config
        self._api_http_url = api_config["api_address"]
        self._pipeline_url = api_config["pipeline_address"]
        
        # print("api config path: " + self._config_path)
        # print("{} NeuroSpeed API HTTP URL: {} ".format(self._contex, self._api_http_url))
        # print("{} NeuroSpeed API SOCKET URL: {} ".format(self._contex, self._pipeline_url))
        
        logging.debug("{} NeuroSpeed API HTTP URL: {} ".format(self._contex, self._api_http_url))
        logging.debug("{} NeuroSpeed API SOCKET URL: {} ".format(self._contex, self._pipeline_url))
        
    def get_http_url(self):
        return self._api_http_url
    
    def get_socket_url(self):
        return self._pipeline_url
        