# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 12:42:25 2021

@author: NeuroBrave
"""

import socketio 
from neurospeed.utils.api_config_service import ApiConfig
from neurospeed.constants import PROD_API_CONFIG

#target_is_downlink_room_as_customer
class DownlinkRoom_AS_Customer_Handler:
    
    def __init__(self, customer_auth_handler, username, api_config = PROD_API_CONFIG):

        self._auth_handler = customer_auth_handler
        self._customer_email = self._auth_handler.get_customer_email()
        self._username = username
        self._connection_status = False
        # Create UserTargetRoom and pass customer configuration and username 
        self._downlink_api = self.DownlinkRoom_Api(self._auth_handler, self._username, api_config=api_config)
        
    def downlinkRoom_socket_connection_handler(self):
        print("Customer {} connected to user's {} DownlinkRoom".format(self._customer_email, self._username ))
        self._connection_status = True
    
    
    def downlinkRoom_socket_disconnect_handler(self):
        print("Customer {} disconnected from user's {} DownlinkRoom".format(self._customer_email, self._username ))
        self._connection_status = False
        
    def route_message(self, payload):
        self._downlink_api.route_message(payload)
        
    
    # do socket connection 
    def connect(self):
        # attach relevant handlers for socket.io events
        self._downlink_api.set_connection_handler(self.downlinkRoom_socket_connection_handler)
        self._downlink_api.set_disconnect_handler(self.downlinkRoom_socket_disconnect_handler)

        self._downlink_api.connect()
        
        
    def disconnect(self):
        self._downlink_api.disconnect()
        
    def is_connected(self):
        return self._connection_status
            
    
    class DownlinkRoom_Api:
    
        def __init__(self, auth_handler, username, api_config = PROD_API_CONFIG):
            api_config = ApiConfig(api_config)
            self._socket_url = api_config.get_socket_url()
            
            self._access_token = auth_handler.get_access_token()
            self._username = username
            
            logger_on = True
            if auth_handler.is_verbose_log() == False:
                logger_on = False
            self._sio = socketio.Client(logger=logger_on, engineio_logger=False, reconnection_delay  = 5, reconnection = True) 
            
            
            
        def set_connection_handler(self, handler):
            self._sio.on('connect',handler = handler)
            
        def set_disconnect_handler(self, handler):
            self._sio.on('disconnect', handler = handler)
            
        def route_message(self, payload):
            self._sio.emit('router', payload)
         
            
        def connect(self):
           headers = {
               "jwt_token": self._access_token,
               "username": self._username, 
           }
        
           print("Downlink_Api - Connecting to user's {} Downlink room as customer ".format(self._username))
           self._sio.connect(url = self._socket_url, transports ='websocket', headers=headers, socketio_path= '/target_is_downlink_room_as_customer' ) 
    
        def disconnect(self):
           self._sio.disconnect()