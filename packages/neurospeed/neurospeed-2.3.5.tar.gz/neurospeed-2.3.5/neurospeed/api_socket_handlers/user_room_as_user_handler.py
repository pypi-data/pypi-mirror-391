# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 14:34:45 2021

@author: NeuroBrave
"""


import socketio 
from neurospeed.utils.api_config_service import ApiConfig
from neurospeed.api_http_handlers.customer_account_manager import Customer_Account_Manager
from neurospeed.constants import PROD_API_CONFIG
from urllib.parse import urlencode

class UserRoom_AS_User_Handler:    
    
    def __init__(self, user_auth_handler, api_config = PROD_API_CONFIG):
        self._user_auth = user_auth_handler
        self._user_access_token = self._user_auth.get_access_token()
        self._username = self._user_auth.get_username()
        self._data_external_handler = None
        self._event_external_handler = None
        
        # Create UserRoom_Api api instance 
        self._userRoom_api = self.UserRoom_Api(self._user_auth, api_config=api_config)


    def userRoom_socket_connection_handler(self):
         print("User {} connected to UserRoom".format( self._username ))
    
    def userRoom_socket_disconnect_handler(self):
        print("User {} disconnected from UserRoom".format(self._username ))
    
       
    
    # internal data handler for HIA output data from Neurospeed pipeline    
    def userRoom_data_handler(self, payload):
        stream_id = payload["stream_id"]
        device_type = payload["device_type"]
        hia_id = payload["hia_id"]
        sensor_info = payload["sensor_info"]

        # propogate data to main program (or to any other source, depends on the external_handler callback)
        if (self._data_external_handler != None):
            self._data_external_handler(payload)
            
            
    # receive live events like hia connect\disconnect for this specific user    
    def userRoom_events_handler(self, payload): 
        
         # propogate event to main program (or to any other source, depends on the external_handler callback)
        if (self._event_external_handler != None):
            self._event_external_handler(payload)

        
    def set_data_external_handler(self, handler):
       self._data_external_handler = handler
   
    def set_device_events_external_handler(self, handler):
       self._event_external_handler = handler   



    def connect(self):
        # attach relevant handlers for socket.io events
        self._userRoom_api.set_connection_handler(self.userRoom_socket_connection_handler)
        self._userRoom_api.set_disconnect_handler(self.userRoom_socket_disconnect_handler)
        self._userRoom_api.set_data_handler(self.userRoom_data_handler)
        self._userRoom_api.set_events_handler(self.userRoom_events_handler)
        
        # connect 
        self._userRoom_api.connect()
        
    def disconnect(self):
        self._userRoom_api.disconnect()
            
    def get_username(self):
        return self._username


    class UserRoom_Api:    
        
        def __init__(self, user_auth, api_config =PROD_API_CONFIG):
            self._api_config = api_config
            self._socket_url = ApiConfig(api_config).get_socket_url()
            
            self._user_auth = user_auth
            self._user_access_token = self._user_auth.get_access_token()
            self._username = self._user_auth.get_username()
            
            logger_on = True
            if self._user_auth.is_verbose_log() == False:
                logger_on = False
                
            self._sio = socketio.Client(logger=logger_on, engineio_logger=False,  reconnection_delay  = 5, reconnection = True) 


    
        def set_connection_handler(self, handler):
            self._sio.on('connect',handler = handler)
            
        def set_disconnect_handler(self, handler):
            self._sio.on('disconnect', handler = handler)
            
        def set_data_handler(self, handler):
            self._sio.on('data', handler = handler)
         
        def set_events_handler(self, handler):
            self._sio.on('events', handler = handler)
            
    
        def connect(self):
            query_params = {
                "jwt_token": self._user_access_token
            }
            query_string = urlencode(query_params)
            full_url = f"{self._socket_url}?{query_string}"

            print("UserRoom_Api - Connecting to {} UserRoom as USER ".format(self._username))
            try:
                self._sio.connect(url = full_url, transports ='websocket', socketio_path= '/target_is_user_room_as_user') 
            except:
                # Check if that because the user has no access to raw data
                customer_account = Customer_Account_Manager(self._user_auth, api_config=self._api_config)
                customers_raw_data_access = customer_account.get_access_to_raw_data()
                if not customers_raw_data_access:
                    print("User isn't authorized to access raw data")
                    return
    
        def disconnect(self):
           self._sio.disconnect()