# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 20:12:14 2021

@author: NeuroBrave
"""

from neurospeed.utils.http_service import HttpService
import logging
import json
from neurospeed.constants import PROD_API_CONFIG

class Customer_Account_Manager:
    
    def __init__(self, customer_auth_handler, api_config = PROD_API_CONFIG):
        self._customer_auth  = customer_auth_handler
        self._http_service = HttpService(customer_auth_handler,api_config=api_config)
        
        if customer_auth_handler.get_access_token() is None: 
            raise ValueError("no token for customer, failed to initialize gateway")
        
        self._http_service.set_headers(customer_auth_handler.get_access_token())

    
    def check_username_for_validity(self, username):
        if type(username) is not str:
            username = str(username)
        return True
    
    def get_headers(self):
        return self._http_service.get_and_update_headers()
    
    def get_user_id(self,username):
        if not self.check_username_for_validity(username):
            return -1
        endpoint = "/users/"+username
       
        result = self._http_service.GET_request(endpoint,{},self.get_headers())
        return result["id"]

    def check_password_for_validity(self, password):
        if type(password) is not str:
            password = str(password)
        if len(password) < 8:
            logging.debug("new password must be at least 8 characters")
            return False
        return True
            
    def get_all_existing_users(self, page_number = 1, page_size = 50):
        endpoint = "/users/list"
        # endpoint = "/pages/users"
        payload = {
            "pager": {
                "page_number": page_number,
                "page_size":page_size
            },
            "filters": {}
        }
        
        header = self._headers.copy()
        header["Content-Type"] =  "application/json"

        return self._http_service.POST_request(endpoint, payload, header)
  
    def get_insight_access(self):
        endpoint = "/customers/customers_access/get_insight_access"
        response = self._http_service.GET_request(endpoint,{},self.get_headers())
        if response is not None:
            response = response["access"]
        return response
    
    def get_recording_exporting_access(self):
        endpoint = "/customers/customers_access/get_recordings_access"
        response = self._http_service.GET_request(endpoint,{},self.get_headers())
        if response is not None:
            response = response["access"]
        return response
    
    def get_access_to_raw_data(self):
        endpoint = "/customers/customers_access/get_raw_data_access"
        response = self._http_service.GET_request(endpoint,{},self.get_headers())
        if response is not None:
            response = response["access"]
        return response

    def get_customer_details(self):
        endpoint = "/customers/current"
        return  self._http_service.GET_request(endpoint, {}, self.get_headers())
        '''
        response should look like that: 
            
            {'id': 45,
             'email': 'lab@neurospeed.com',
             'role': 'user',
             'firstName': 'lab',
             'is_active': True,
             'lastName': 'rador',
             'account_id': 'rador_54uL9rH4XY',
             'in_active_reason': None,
             'company_name': 'rador'}
        '''

    def create_new_user(self, new_username, new_password):
        #create user:
        endpoint = "/users"
        # new_username ='api_test_user'
        if not self.check_username_for_validity(new_username):
            return new_password
        if not self.check_password_for_validity(new_username):
            return None
        params = {"username": new_username, "password": new_password}
        return self._http_service.POST_request(endpoint, params, self.get_headers())

        '''
        response supposed to look like that: 
            {'id': 1298,
             'username': 'api_test_user',
             'settings': {'isDspEnabled': True,
              'userId': 1298,
              'dsp_config': None,
              'ppg_config': None,
              'garmin_config': None,
              'gsr_config': None,
              'dsp_config_source': None,
              'gsr_config_source': None,
              'active_markers': None,
              'push_user_key': None,
              'push_active': True,
              'id': 1298,
              'isAttachDataOrigin': True,
              'version': 1,
              'cognitive_type': 'moderate',
              'createdAt': '2024-03-11T16:03:29.361Z',
              'updatedAt': '2024-03-11T16:03:29.361Z'}}
        
        '''
        
    def delete_user(self, id_of_user_to_delete):
        if type(id_of_user_to_delete) is not int:
            logging.debug("failed to processed user delete request: user ID must be integer value")
            return None
        endpoint = "/users"
        params = {"id": id_of_user_to_delete}
        return  self._http_service.DELETE_request(endpoint, params, self.get_headers())
        #delete method returns true if successfull

    def modify_user(self, user_id_to_modify, new_username, new_password):
        endpoint = "/users" 
        
        if not self.check_username_for_validity(new_username):
            return new_password
        if not self.check_password_for_validity(new_username):
            return None
        
        params = {"username": new_username, "password": new_password}
        
        return  self._http_service.PUT_request(endpoint=endpoint, payload=params, params={'id':user_id_to_modify}, headers = self.get_headers())