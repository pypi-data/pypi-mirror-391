# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 13:45:53 2021

@author: NeuroBrave
"""

from neurospeed.utils.http_service import HttpService
import copy 
import json
from neurospeed.constants import PROD_API_CONFIG

class UserRoom_Recorder_Handler:
    
    def __init__(self, customer_auth_handler, api_config = PROD_API_CONFIG):
        # create recorder http api instance
        self._recorder_api = self.Recorder_HttpApi(customer_auth_handler, api_config=api_config)
        
    # there can only be one recorder at a time per USER.
    # previous active recorder must be stopped in order to create another one
    # data still can be exported from stopped recorder, but recorder itself cannot be activated again
    def create_recorder(self, username, recorder_name = None):
        create_recorder = {
            "username": username,
            "recorder_name": recorder_name, 
            "unlimited": "true"
        }
        response = self._recorder_api.create_recorder(create_recorder)
        
        return response
    
    def update_recorder(self, recorder_id, status):
        update_recorder_payload = {
            "status": status,
        }
        params  = {"id": recorder_id} 
        response = self._recorder_api.update_recorder(params, update_recorder_payload)
        
        return response
    
    def list_recorders(self, page_number, page_size, filters = {} ):
        payload  = {
            "pager": {
                "page_number": page_number,
                "page_size":page_size
            },
            "filters": filters
        }
        response = self._recorder_api.list_recorders(payload)
        return response
    
    def get_recorder(self, recorder_id):
        response = self._recorder_api.get_recorder(recorder_id)
        
        return response
        
    def delete_recorder(self, recorder_id):
        params  = {
            "recorder_id": recorder_id
        }
        response = self._recorder_api.delete_recorder(params)
        return response
        
        
    class Recorder_HttpApi:
        
        def __init__(self, auth_handler, api_config = PROD_API_CONFIG):
            self._recorder_endpoint = '/gateway/recorder'
            self._http_service = HttpService(auth_handler, api_config=api_config)
            
            self._http_service.set_headers(auth_handler.get_access_token())
       
        def get_headers(self):
            return copy.deepcopy(self._http_service.get_and_update_headers())
            
        def create_recorder(self, payload):
            endpoint = self._recorder_endpoint
            response = self._http_service.POST_request(endpoint, payload, self.get_headers())
            
            return response
        
        def update_recorder(self, params, payload):
            endpoint = self._recorder_endpoint
            response = self._http_service.PUT_request(endpoint, payload, params, self.get_headers())
            
            return response
        
        def list_recorders(self, payload ):
            endpoint = self._recorder_endpoint + "/list"
            request_headers = self.get_headers()
            request_headers["content-type"] = "application/json"
            response = self._http_service.POST_request(endpoint, payload, request_headers)
            
            return response
        
        def get_recorder(self, recorder_id):

            endpoint = self._recorder_endpoint + "/" + str(recorder_id)
            response = self._http_service.GET_request(endpoint, {}, self.get_headers())
            
            return response
            
        def delete_recorder(self, params):
            endpoint = self._recorder_endpoint
            response = self._http_service.DELETE_request(endpoint, params, self.get_headers())
            
            return response