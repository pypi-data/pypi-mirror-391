# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 10:13:39 2021

@author: NeuroBrave
"""

import json
from neurospeed.utils.http_service import HttpService
from neurospeed.constants import PROD_API_CONFIG


# SSR => send events to HIA devices (enable\disable stream state, downlink etc..)
class SSR_HttpHandler:
    
    def __init__(self, customer_auth_handler, api_config = PROD_API_CONFIG):
        # create ssr http api instance
        self._ssr_api = self.SSR_HttpApi(customer_auth_handler, api_config=api_config)
    

    def change_stream_state(self, username, hia_id, stream_id, stream_state):
        print("Sending stream_state message to User: {} HIA: {} Stream: {} state: {}".format(username, hia_id, stream_id, stream_state))
        stream_state_payload = {
            "username": username, # required
            "hia_id": hia_id, # required
            "stream_id": stream_id, # required. take first sensor just for the example
            "stream_state": stream_state # required. options: 'disabled' or 'enabled'
        }     
    
        stream_state_response = self._ssr_api.change_stream_state(stream_state_payload)
        print("Stream state http response: {}".format(stream_state_response)  )
    
    def send_downlink(self, username, hia_id, payload):
        print("Sending downlink message to User: {} HIA: {}".format(username, hia_id))
        downlink_payload = {
            "username": username, # required
            "hia_id": hia_id,  # required
            "payload": json.dumps(payload) # required. payload is JSON object and can be anything up to 64 killobytes ~ 
        }     
    
        stream_state_response = self._ssr_api.downlink(downlink_payload)
        print("Downlink http response: {} ".format(stream_state_response) )
        
        
    class SSR_HttpApi:
    
        def __init__(self, auth_handler, api_config = PROD_API_CONFIG):
            self._http_service = HttpService(auth_handler, api_config=api_config)
            self._http_service.set_headers(auth_handler.get_access_token())
    
    
        def change_stream_state(self, payload):
            endpoint = '/gateway/ssr/stream_state'
           
            response = self._http_service.POST_request(endpoint, payload, self._http_service.get_and_update_headers())
            return response
                
                
        def downlink(self, payload):
            endpoint = '/gateway/ssr/downlink'
           
            response = self._http_service.POST_request(endpoint, payload, self._http_service.get_and_update_headers())
            return response