# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 12:37:54 2021

@author: NeuroBrave
"""

from neurospeed.utils.http_service import HttpService
from neurospeed.constants import PROD_API_CONFIG

class Auth_AS_Customer_handler:

    def __init__(self, customer_config, api_config = PROD_API_CONFIG):

        self._contex = "Auth_As_Customer_Handler - "
        self._customer_config = customer_config
        
        if "Verbose_socket_log" in api_config:
            self._customer_config["Verbose_socket_log"] = api_config["Verbose_socket_log"]
        else:
            # If not, set it to False
            self._customer_config["Verbose_socket_log"] = False
            
        self._access_token = None
        self._refresh_token = None
        self._customer_email = self._customer_config["email"]
        self._auth_api_instance = self.Customer_Auth_Api(self, api_config)

        

    # login as customer
    def login(self):
        try:
            self._login_status = self._auth_api_instance.customer_login()
            if self._login_status == True:
                self._access_token = self._auth_api_instance.get_access_token()
                self._refresh_token = self._auth_api_instance.get_refresh_token()
                print('{} Successful login as customer {}'.format(self._contex, self._customer_email) )
            else:
               raise ValueError()
        except:
               print('{} Unable to login as [{}]'.format(self._contex, self._customer_email) )
               self._login_status = False
            
        finally:
            return self._login_status

        
    def get_access_token(self):
        return self._access_token
    
    def get_refresh_token(self):
        return self._refresh_token
    
    def get_config(self):
        return self._customer_config

    def get_customer_email(self):
        return self._customer_email
    
    def is_logged_in(self):
        return self._login_status
    
    def get_hia_id(self):
        return self._customer_config["HIA_ID"]

    def is_verbose_log(self):
        return self._customer_config["Verbose_socket_log"] == "True" or self._customer_config["Verbose_socket_log"]
    
    def update_refresh_token(self):
        if self._refresh_token is None:
                return False
        refresh_status = self._auth_api_instance.update_refresh_token()
        if refresh_status == True:
            self._access_token = self._auth_api_instance.get_access_token()
            self._refresh_token = self._auth_api_instance.get_refresh_token()
    
    class Customer_Auth_Api:
        
        def __init__(self, auth_handler_instance, api_config = PROD_API_CONFIG):
            self._contex = "Customer_Auth_Api - "
            
            self._customer_config = auth_handler_instance.get_config()
            self._customer_email = self._customer_config["email"]
            self._customer_password  = self._customer_config["password"]
 
            self._http_service = HttpService(auth_handler_instance, api_config=api_config)
            
        # login api flow
        def customer_login(self):
            endpoint = "/auth/login"
            
            print("{} Executing login flow as customer [{}]".format(self._contex, self._customer_email))
            
            login_payload = {
                "email": self._customer_email, 
                "password": self._customer_password,
            }
            login_status = False
            try:
                response_payload =  self._http_service.POST_request(endpoint, login_payload)
                
                token = response_payload["token"]
                self._access_token = token["accessToken"]
                self._http_service.set_headers(self._access_token)
                if "refreshToken" in token:
                    self._refresh_token = token["refreshToken"]
                else:
                    self._refresh_token = None
                login_status = True
            
            except:
                   raise ValueError() 

      
            return login_status

        def update_refresh_token(self):
            endpoint = "/auth/refresh_token"
            
            refresh_token_payload = {
                "refreshToken": self._refresh_token,
            }
            
            try:
                response_payload =  self._http_service.POST_request(endpoint, refresh_token_payload)
                
                token = response_payload["token"]
                self._access_token = token["accessToken"]
                self._refresh_token = token["refreshToken"]
                return True
                
            except:
                return False

            
        def get_access_token(self):
            return self._access_token
        
        def get_refresh_token(self):
            return self._refresh_token
