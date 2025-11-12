# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 12:37:54 2021

@author: NeuroBrave
"""


from neurospeed.utils.http_service import HttpService
from neurospeed.utils.helper_service import UtilService
import logging
from neurospeed.constants import PROD_API_CONFIG

class Auth_AS_User_Handler:

    def __init__(self, user_config, api_config = PROD_API_CONFIG):
        self._contex = "User_Auth_Handler - "
        
        
            
        self._user_config = user_config
        if not "HIA_ID" in user_config.keys():
            self._user_config["HIA_ID"] = UtilService.generateId(6)
            
        if not "Verbose_socket_log" in user_config.keys():
            self._user_config["Verbose_socket_log"] = False
            
        self._user_username = self._user_config["username"]
        self._access_token = None
        self._refresh_token = None
        self._login_status = None
        self._account_id = None
        self._auth_api_instance = self.User_Auth_Api(self, api_config)
    
    def update_refresh_token(self):
        if self._refresh_token is None:
                return False
        refresh_status = self._auth_api_instance.update_refresh_token()
        if refresh_status == True:
            self._access_token = self._auth_api_instance.get_access_token()
            self._refresh_token = self._auth_api_instance.get_refresh_token()
    
    # login as HIA user
    def login(self):
        try:
            self._login_status = self._auth_api_instance.user_login()
            if (self._login_status):
                self._access_token = self._auth_api_instance.get_access_token()
                self._refresh_token = self._auth_api_instance.get_refresh_token()
                print('{} successful user login as {}'.format(self._contex, self._user_username) )
                logging.debug('{} successful user login as {}'.format(self._contex, self._user_username) )
            else:
               self._login_status = False
        except Exception as e:
            print('{} Unable to login as {}'.format(self._contex, self._user_username)) 
            logging.debug(f"{self._contex} Unable to login as {self._user_username}, reason {e}")
            self._login_status = False
            
        finally:
            return self._login_status
        
    def get_access_token(self):
        return self._access_token
    
    def get_refresh_token(self):
        return self._refresh_token
    
    def get_config(self):
        return self._user_config
    
    def get_hia_id(self):
        return self._user_config["HIA_ID"]
    
    def get_username(self):
        return self._user_config["username"]
    
    def is_logged_in(self):
        return self._login_status
    
    def is_verbose_log(self):
        return self._user_config["Verbose_socket_log"] == "True" or self._user_config["Verbose_socket_log"]

    class User_Auth_Api:
    
        def __init__(self, auth_handler_instance, api_config = PROD_API_CONFIG):
            self._contex = "User_Auth_Api -"
            
            self._user_config = auth_handler_instance.get_config()
            if "account_id" in self._user_config:                
                self._account_id  = self._user_config["account_id"] 
            else:
                self._account_id  = self._user_config["customer_username"] 
                
            self._user_username  = self._user_config["username"]
            self._user_password  = self._user_config["user_password"]

            self._http_service = HttpService(auth_handler_instance, api_config=api_config)
             
             
        def user_login(self):
            endpoint = "/users/login"
        
            #print("{} Executing Login as User {}".format(self._contex, self._user_username))
            
            login_payload = {
                "account_id": self._account_id, 
                "username": self._user_username, 
                "password": self._user_password,
            }
            login_status = False
            logging.debug(f"{self._contex} Executing login as {login_payload}")
            
            #try:
            response_payload =  self._http_service.POST_request(endpoint, login_payload)
            
            try:
                token = response_payload["token"]
                login_status = token is not None
                self._access_token = token["accessToken"]
                if "refreshToken" in token:
                    self._refresh_token = token["refreshToken"]
                else:
                    self._refresh_token = None
                # print("User access_token: ", self._access_token)
            except:
                self._access_token = None
                login_status = False
            
            logging.debug(f"login status {login_status}, response {response_payload}")
        #except Exception as e:
            #       logging.debug("exception while attempting login: {e}")
            #       raise ValueError() 
            
            return login_status
        
        def update_refresh_token(self):
            if self._refresh_token is None:
                return False
            
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
        