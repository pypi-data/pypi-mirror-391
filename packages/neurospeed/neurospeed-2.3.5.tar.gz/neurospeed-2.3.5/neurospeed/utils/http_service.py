# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 20:07:52 2021

@author: NeuroBrave
"""


import requests
import json
from neurospeed.utils.api_config_service import ApiConfig
import copy 
import logging
from neurospeed.constants import PROD_API_CONFIG

class HttpService:    
    
    def __init__(self, auth_handler, api_config = PROD_API_CONFIG):
        api_config = ApiConfig(api_config)

        self._api_url =  api_config.get_http_url()
        self._api_url = self._api_url + '/api'
        self._auth_handler = auth_handler
    
    def GET_request(self, endpoint, params, headers = {}, can_update_refresh_token = True):
        api_url = self._api_url + endpoint
        if headers != {}:
            headers = self._headers
        logging.debug(f"HTTP GET to {api_url} with params: {params}")
        
        response = None
        try:
            response = requests.get(api_url, headers=headers, params = params)
            response.raise_for_status()
      
            if (response.ok):
                response_parsed = json.loads(response.content)
                logging.debug(f"GET response from {endpoint}")
                return response_parsed
    
            else:
                raise requests.exceptions.HTTPError
        
        except requests.exceptions.HTTPError as e:
            if can_update_refresh_token and e.response.status_code == 401 and json.loads(e.response.text)['message'] == 'Unauthorized':
                self._auth_handler.update_refresh_token() # try to update the refresh token
                self.get_and_update_headers()
                if headers != {}:
                    headers = self._headers
                return self.GET_request(endpoint, params, headers, can_update_refresh_token=False)
            print('Failed to HTTP GET to url:', api_url)
            print (e.response.text)
            
            
    def POST_request(self, endpoint, payload, headers = {}, can_update_refresh_token = True):
        api_url = self._api_url + endpoint
        if headers != {}:
            headers = self._headers
        logging.debug(f"HTTP POST to {api_url} with params: {payload}")
        try:
            clean_payload = copy.deepcopy(payload)
            for key in payload:
                if key == "password":
                    clean_payload.pop(key)
                    
            logging.debug(f"doing HTTP POST to {api_url} payload {clean_payload}")     
        except Exception as err:
            pass
           
        response = None 
        try:
            response = requests.post(api_url, json=payload, headers =headers)
            response.raise_for_status()
    
     
            if (response.ok):
                # Handle empty response content
                if response.content.strip() == b'':
                    logging.debug(f"POST response from {endpoint} is empty.")
                    return None  # or return {} if you expect a dictionary
                
                response_parsed = json.loads(response.content)
                logging.debug("POST response from {endpoint}:{response_parsed}")
                return response_parsed
    
            else:
                raise requests.exceptions.HTTPError
        
        except requests.exceptions.HTTPError as e:
            if can_update_refresh_token and e.response.status_code == 401 and json.loads(e.response.text)['message'] == 'Unauthorized':
                self._auth_handler.update_refresh_token() # try to update the refresh token
                self.get_and_update_headers()
                if headers != {}:
                    headers = self._headers
                return self.POST_request(endpoint, payload, headers, can_update_refresh_token=False)
            print('Failed to HTTP POST to url:', api_url)
            print (e.response.text)      
            logging.debug(f"Failed to HTTP POST to {api_url}: {e.response.text}")
            
    def PUT_request(self, endpoint, payload, params, headers = {}, can_update_refresh_token = True):
        api_url = self._api_url + endpoint
        if headers != {}:
            headers = self._headers
        print('doing HTTP PUT to url:', api_url, 'with params:', params, 'and payload:', payload, '')
        
        response = None
        try:
            response = requests.put(api_url, data=payload, headers =headers, params=params)
            response.raise_for_status()
            if (response.ok):
                response_parsed = json.loads(response.content)
                print('PUT response from {} '.format(endpoint ))
                return response_parsed
    
            else:
                raise requests.exceptions.HTTPError
        
        except requests.exceptions.HTTPError as e:
            if can_update_refresh_token and e.response.status_code == 401 and json.loads(e.response.text)['message'] == 'Unauthorized':
                self._auth_handler.update_refresh_token() # try to update the refresh token
                self.get_and_update_headers()
                if headers != {}:
                    headers = self._headers
                return self.PUT_request(endpoint, payload, params, headers, can_update_refresh_token=False)
            print('Failed to HTTP PUT to url:', api_url)
            print (e.response.text)      
            logging.debug(f"Failed to HTTP PUT to {api_url}: {e.response.text}")

    def DELETE_request(self, endpoint, params, headers = {}, can_update_refresh_token = True):
        api_url = self._api_url + endpoint
        if headers != {}:
            headers = self._headers
        print('doing HTTP DELETE to url:', api_url, 'with params:', params)
        
        response = None
        try:
            response = requests.delete(api_url, headers =headers, params=params)
            response.raise_for_status()

            if (response.ok):
                response_parsed = json.loads(response.content)
                print('DELETE response from {} '.format(endpoint ))
                return response_parsed
    
            else:
                raise requests.exceptions.HTTPError
        
        except requests.exceptions.HTTPError as e:
            if can_update_refresh_token and e.response.status_code == 401 and json.loads(e.response.text)['message'] == 'Unauthorized':
                self._auth_handler.update_refresh_token() # try to update the refresh token
                self.get_and_update_headers()
                if headers != {}:
                    headers = self._headers
                return self.DELETE_request(endpoint, params, headers, can_update_refresh_token=False)
            print('Failed to HTTP DELETE to url:', api_url)
            print (e.response.text)       
            logging.debug(f"Failed to HTTP DELETE to {api_url}: {e.response.text}")
    
    def get_and_update_headers(self):
        self._headers =  {
                "Authorization": "Bearer " + self._auth_handler.get_access_token()
            }
        return self._headers
        
    def set_headers(self, access_token):
        self._headers =  {
                "Authorization": "Bearer " + access_token
            }
        return self._headers
   