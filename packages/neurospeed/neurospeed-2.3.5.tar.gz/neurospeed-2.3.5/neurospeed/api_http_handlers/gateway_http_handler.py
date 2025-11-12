# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 20:12:14 2021

@author: NeuroBrave
"""

from neurospeed.utils.http_service import HttpService
import copy 
import json
from neurospeed.constants import PROD_API_CONFIG

class Gateway_HttpHandler:
    
    def __init__(self, customer_auth_handler, api_config =PROD_API_CONFIG):
        self._customer_auth  = customer_auth_handler
        self._http_service = HttpService(customer_auth_handler, api_config=api_config)
        
        if customer_auth_handler.get_access_token() is None: 
            raise ValueError("no token for customer, failed to initialize gateway")
        self._http_service.set_headers(customer_auth_handler.get_access_token())
        
    def is_unauthorized(response):
        return response != None and isinstance(response, dict) and response.get('status_code') == 401

    # returns list of connected users : 
    # [{id: number; username: string;}, ..., {id: number; username: string;}]
    def get_connected_users(self):
        endpoint = "/gateway/users/connected"
        params = {}
        response = self._http_service.GET_request(endpoint, params, self._http_service.get_and_update_headers())
        return response

    def get_connections(self, page_number = 1, page_size = 50, filters={}): 
        endpoint = "/gateway/connections"

        payload  = {
            "pager": {
                "page_number": page_number,
                "page_size":page_size
            },
            "filters": filters
        }
        headers_copy = copy.deepcopy(self._http_service.get_and_update_headers())
        headers_copy["Content-type"] = "application/json"
        response = self._http_service.POST_request(endpoint, payload, headers_copy)
        return response
     
        
