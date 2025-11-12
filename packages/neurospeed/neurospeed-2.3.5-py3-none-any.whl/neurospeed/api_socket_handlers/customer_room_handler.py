# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 14:03:23 2021

@author: NeuroBrave
"""
import socketio 
from neurospeed.utils.api_config_service import ApiConfig
from neurospeed.constants import PROD_API_CONFIG


# target_is_customer_room 
class CustomerRoom_Handler:    
    
    def __init__(self, customer_auth_handler, api_config = PROD_API_CONFIG):
        self._auth_handler = customer_auth_handler
        self._hia_connection_external_event_handler = None
        self._hia_disconnect_external_event_handler = None
        self._customerRoom_api = None
        self._api_config = api_config

    def connect(self):
         # Create Customer_TargetRoom_Api
        self._customerRoom_api = self.CustomerRoom_Api(self._auth_handler, api_config=self._api_config)
        
        # attach relevant internal handlers for socket.io events
        self._customerRoom_api.set_connection_handler(self.customerRoom_socket_connection_handler)
        self._customerRoom_api.set_disconnect_handler(self.customerRoom_socket_disconnect_handler)
        self._customerRoom_api.set_hia_events_handler(self.customerRoom_hia_events_handler)
    
        self._customerRoom_api.connect()
        
        
    def disconnect(self):
        self._customerRoom_api.disconnect()
        
        
    def customerRoom_socket_connection_handler(self):
        print('customer connected to customerRoom')
        pass;
    
    def customerRoom_socket_disconnect_handler(self):
        print('customer disconnected from customerRoom')
        pass;
       
    # see README(4) for payload structure  
    def customerRoom_hia_events_handler(self, payload):

        event_type = payload["type"]
        username = payload["username"]
        hia_id = payload["hia_id"]
        sensors = payload["sensors"]
        
        if (event_type == 'connect'): 
            self.hia_connection_event_handler(payload)
        
        if (event_type == 'disconnect'):
            self.hia_disconnect_event_handler(payload)    
            
    
    # inner hia_connection event handler
    def hia_connection_event_handler(self, event):
        # propogate event to main program (or to any other source, depends on the external_handler callback)
        if (self._hia_connection_external_event_handler != None):
            self._hia_connection_external_event_handler(event)
    
    # inner hia_disconnect event handler
    def hia_disconnect_event_handler(self, event):
        # propogate event to main program (or to any other source, depends on the external_handler callback)
        if (self._hia_disconnect_external_event_handler != None):
            self._hia_disconnect_external_event_handler(event)      
  
    
    # setter for external handler
    def set_hia_connection_external_handler(self, handler):
        self._hia_connection_external_event_handler = handler
    
    # setter for external handler
    def set_hia_disconnect_external_handler(self, handler):
        self._hia_disconnect_external_event_handler = handler
        
        
    # Customer_Room_Api api class for receiving events across all user devices
    class CustomerRoom_Api:    
        
        def __init__(self, config, api_config = PROD_API_CONFIG):
            api_config = ApiConfig(api_config)
            self._config = config
            self._socket_url =  api_config.get_socket_url()
            self._access_token = config.get_access_token()
      
            logger_on = True
            if self._config.is_verbose_log() == False:
                logger_on = False
                
            self._sio = socketio.Client(logger=logger_on, engineio_logger=False, reconnection_delay  = 5, reconnection = True) 
    
    
        def set_connection_handler(self, handler):
            self._sio.on('connect',handler = handler)
            
        def set_disconnect_handler(self, handler):
            self._sio.on('disconnect', handler = handler)
    
        def set_hia_events_handler(self, handler):
            self._sio.on('hia_events', handler = handler)
    
    
        def connect(self):
            headers = {
                "jwt_token": self._access_token,
            }
         
            print("CustomerRoom_Api - Connecting to CustomerRoom",)
            self._sio.connect(url = self._socket_url, transports ='websocket', headers=headers, socketio_path= '/target_is_customer_room' ) 
    
        def disconnect(self):
           self._sio.disconnect()
        
