# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 14:02:51 2021

@author: NeuroBrave
"""

import json
import copy
from neurospeed.utils.http_service import HttpService
from neurospeed.constants import PROD_API_CONFIG

class UserRoom_Recorder_Exporter_Handler:
    
    def __init__(self, customer_auth_handler, api_config = PROD_API_CONFIG):
        # create exporter http api instance
        self._exporter_api = self.Exporter_HttpApi(customer_auth_handler, api_config=api_config)
        
    def create_exporter(self, recorder_id, config):
        create_exporter_payload = {
            "recorder_id": recorder_id,
            "exporter_config": config,
            "unlimited": True
        }
        # payload_json = json.dumps(create_exporter_payload)
        # response = self._exporter_api.create_exporter(payload_json)
        response = self._exporter_api.create_exporter(create_exporter_payload)
        
        return response
    
    def get_exported_url(self, exporter_id):
        params  = {
            "exporter_id": exporter_id
        }
        response = self._exporter_api.get_exported_url(params)
        
        return response
    
    def list_exporters(self, username, page_number, page_size):
        payload  = {
            "pager": {
                "page_number": page_number,
                "page_size":page_size
            },
            "filters": {
                "username": username
            }
        }
        response = self._exporter_api.list_exporters(payload)
        return response
    
    def get_exporter(self, exporter_id):
        response = self._exporter_api.get_exporter(exporter_id)
        
        return response
        
    def delete_exporter(self, exporter_id):
        params  = {
            "exporter_id": exporter_id
        }
        response = self._exporter_api.delete_exporter(params)
        return response
        
    class Exporter_HttpApi:
        
        def __init__(self, auth_handler, api_config = PROD_API_CONFIG):
            # create http service instance
            self._exporter_endpoint = '/gateway/exporter'
            self._http_service = HttpService(auth_handler, api_config=api_config)
            self._http_service.set_headers(auth_handler.get_access_token())
            
        def get_headers(self):
            return copy.deepcopy(self._http_service.get_and_update_headers())
        
        def create_exporter(self, payload):
            endpoint = self._exporter_endpoint
            request_headers = self.get_headers()
            request_headers["content-type"] = "application/json"
            response = self._http_service.POST_request(endpoint, payload, request_headers)
            
            return response
        
        def list_exporters(self, payload ):
          endpoint = self._exporter_endpoint + "/list"
          
          request_headers = self.get_headers()
          request_headers["content-type"] = "application/json"
          response = self._http_service.POST_request(endpoint, payload, request_headers)
          return response
    
        def get_exported_url(self, params):
            endpoint = self._exporter_endpoint + "/url"

            response = self._http_service.GET_request(endpoint, params , self.get_headers())
            
            return response
        
        def get_exporter(self, exporter_id):
            endpoint = self._exporter_endpoint + "/" + str(exporter_id)
            response = self._http_service.GET_request(endpoint, {}, self.get_headers())
            
            return response
            
        def delete_exporter(self, params):
            endpoint = self._exporter_endpoint
            response = self._http_service.DELETE_request(endpoint, params, self.get_headers())
            
            return response