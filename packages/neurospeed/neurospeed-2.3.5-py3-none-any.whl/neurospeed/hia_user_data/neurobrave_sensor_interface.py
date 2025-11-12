# https://python-socketio.readthedocs.io/en/latest/client.html
# https://flask-socketio.readthedocs.io/en/latest/
# https://python-socketio.readthedocs.io/en/latest/intro.html


import queue
import socketio
import json 
import time
import threading
from neurospeed.utils.api_config_service import ApiConfig
import logging
from neurospeed.constants import PROD_API_CONFIG

class HIA_Client:
    
    _HIA_version = "HIA version 2.2.1" 
    _packet_endpoint = 'pipeline'
    #_streams_dict = {}  # BAD IDEA - this variable would be shared across all class instances, causing data override


    def __init__(self, user_auth_handler, sensor_info, api_config = PROD_API_CONFIG):
        # Check if the dictionary is not empty
        if sensor_info:
            # Get the first key
            key_name = next(iter(sensor_info))
            # Safely get the device_type, defaulting to 'user_data' if not present
            self._device_type = sensor_info.get(key_name, {}).get('device_type', 'user_data')
        else:
            # Default value if the dictionary is empty
            self._device_type = 'user_data'
        self._hia_id = user_auth_handler.get_hia_id()
        self._username = user_auth_handler.get_username()
        self._contex = "User: {} HIA: {} - ".format(self._username, self._hia_id)
        self._api_config = ApiConfig(api_config)
        self._auth_handler = user_auth_handler
        
        # init streams qeueus for each sensor
        self._streams_dict = {} # GOOD IDEA - instance level variable, not shared at class level
        for key, value in sensor_info.items():
            stream_id = key
            sensor_payload =  value
            self._streams_dict[stream_id] = queue.Queue(-1)
            
        self._sensor_info = sensor_info
        self._access_token = self._auth_handler.get_access_token()
        self._refresh_token = self._auth_handler.get_refresh_token()
        self._user_config = self._auth_handler.get_config()
        self._exit_flag_2 = threading.Event() 
        #self._external_socket_connection_handler = None
        self._socket_connection_external_handler = None
        #self._external_socket_disconnect_handler = None
        self._external_disconnection_handler = None
        self._connection_status = False
        
        logger_on = True
        if self._auth_handler.is_verbose_log() == False:
                logger_on = False
                
        self._sio = socketio.Client(logger=logger_on, engineio_logger=False, reconnection_delay  = 5, reconnection = True) 

        self._current_experiment_labels = ["none"]
        self._current_experiment_onetime_labels = ["none"]
        
    # Socket data sender - Start 
    
    
    def set_label(self, label):
        self._current_experiment_labels = [label]
        self._current_experiment_onetime_labels = [label]
        logging.debug(f"label set to {label}")
        
        
    def send_data(self, data, stream_id):  
        data.append(time.time()) # append timestamp to the end of sample array
 
        # insert data into the stream queue for that stream_id   
        self._streams_dict[stream_id].put(data, timeout = 1)      

    def send_data_direct(self,data_packet,stream_id,timestamp=None, send_without_timestamp = False, device_type = None):
        '''
        data packet is type list of multichannel samples, each miltichannel sample is also type list 
        optionally accepts timestamp - must be list with same length as data_packet
        '''
        if self._connection_status:
            data_to_send = []
            # print(data_packet)
            # print(f"received data to transmit type {type(data_packet)}, length {len(data_packet)}")
            if send_without_timestamp:
                data_to_send = data_packet
            elif timestamp is None:       
                t = time.time()
                for sample in data_packet:
                    x = sample.copy()
                    x.append(t)
                    data_to_send.append(x)       
            else:
                for index, sample in enumerate(data_packet):
                    x = sample.copy()
                    x.append(timestamp[index])
                    data_to_send.append(x)
            # print(f"transmitting data type {type(data_to_send)}, length {len(data_to_send)}")
                    
            TX_buffer = {"sample": data_to_send}
            logging.debug(f"payload length: {len(json.dumps(TX_buffer))}")
            # if device_type is None:
            #     dev_type = self._device_type
            # else:
            #     dev_type= device_type
            dev_type = self._sensor_info[stream_id]["device_type"]
            
            packet_payload = {"stream_id": stream_id, "device_type": dev_type, "hia_id": self._hia_id, "data": json.dumps(TX_buffer)}                
            packet_payload["experiment"] = {
                            "packet_labels": self._current_experiment_labels,
                            "onetime_labels": self._current_experiment_onetime_labels
                            } 
                
            #print(len(str(json.dumps(TX_buffer))))
            self._sio.emit(self._packet_endpoint, packet_payload)      
        
        else:
            message = "{} Socket disconnected, stopping user_data upstream for stream_id: {}".format(self._contex, stream_id)
            logging.debug(message)
            return
        
    def send_user_data_to_websocket(self, stream_id):  
        packet_ready = False
        sender_active = True
        while sender_active:
            time.sleep(0.2) #minimum allowed interval 200 MS
            if self._connection_status is False:
                message = "{} Socket disconnected, stopping user_data upstream for stream_id: {}".format(self._contex, stream_id)
                logging.debug(message)
                sender_active = False
                return
            TX_buffer = {"sample": []}
            stream_q_user_data = self._streams_dict[stream_id] # get relevant stream queue
            while (stream_q_user_data.empty() == False):  
                # pull sample from queue, and add to TX buffer:
                sample = stream_q_user_data.get(timeout = 1)
                y = TX_buffer['sample']
                y.append(sample)
                packet_ready = True                    
            if (packet_ready):       
              #  print("{} user_data packet ready for stream_id: {} ".format(self._contex, stream_id))
                # print("data packet size " , len(TX_buffer['sample']))
                # print(self._device_type)
                
               
                
                packet_payload = {"stream_id": stream_id, "device_type": self._device_type, "hia_id": self._hia_id, "data": json.dumps(TX_buffer)}              
                
                packet_payload["experiment"] = {
                                "packet_labels": self._current_experiment_labels,
                                "onetime_labels": self._current_experiment_onetime_labels
                            } 
                # print(packet_payload["experiment"])
                # print(len(str(json.dumps(TX_buffer))))
                
                self._sio.emit(self._packet_endpoint, packet_payload)      
                packet_ready = False
     # Socket data sender - End      
    
    
    # Socket handlers - Start
    def attach_stream_state_handler(self, handler_function):
        self._sio.on('ssr_stream_state',handler = handler_function)
        
    def attach_downlink_handler(self, handler_function):
        self._sio.on('ssr_downlink',handler = handler_function)  
        
    def attach_socket_connection_handler(self, handler_function):
         self._sio.on('connect',handler = handler_function)
    
    def attach_socket_disconnect_handler(self, handler_function):
        self._sio.on('disconnect',handler = handler_function)
    
    def ping_handler(self):  # required DO NOT REMOVE
       self._sio.emit('pong')
       
       
    # internal stream state handler
    def stream_state_handler(self, data):
        logging.debug('{} SSR stream_state event: {}'.format(self._contex, data))
        # The incoming packet is a dictionary of shape {"stream_id_x": "stream_state", .., "stream_id_y": "stream_state"}
        # where stream_state is either "disabled" or "enabled" and stream_id is identifier of specific sensor
        str_id = list(data)[0] 
        if str_id in list(self._sensor_info):
            self._sensor_info[str_id]["stream_state"] = data[str_id]
        else:
            logging.debug("{} Stream state change error, invalid stream_id: {}".format(self._contex, str_id))
    
    # internal downlink handler
    def downlink_handler(self, payload):
        logging.debug('{} SSR downlink event: {}'.format(self._contex, payload))

        
    # internal connection error handler        
    def connection_error_handler(self, data):
        logging.debug('{} Connection error, message: {}'.format(self._contex, data) )
        self._connection_status = False
        
    # internal socket disconnect handler
    def socket_disconnect_handler(self):
        self._connection_status = False
        
        # propogate disconnect event to external handler if exist.. 
        if self._external_disconnection_handler != None:
            self._external_disconnection_handler(self) # send current instance contex
        
        
     # internal socket connection handler    
    def socket_connection_handler(self):
        logging.debug("{} Connected to NeuroSpeed Pipeline.".format(self._contex))
        self._connection_status = True

        # for each stream inside stream_dict, activate thread for sending data
        for key, value in self._streams_dict.items():
            stream_id = key
            logging.debug("{} starting user_data upstream thread for stream_id: {} ".format(self._contex, stream_id))
            user_data_outbound_websocket_TX = threading.Thread(target = self.send_user_data_to_websocket, args=[key])
            time.sleep(0.1)
            user_data_outbound_websocket_TX.start()
        
        # propogate connection event to external handler if exist.. 
        if self._socket_connection_external_handler != None:
            self._socket_connection_external_handler(self) # send current instance contex

   # Socket handlers - End
   
   
   #  Getters, Setters - Start
    def set_socket_connection_external_handler(self, handler):
        self._socket_connection_external_handler = handler
    
    def set_socket_disconnect_external_handler(self, handler):
        self._external_disconnection_handler = handler
        
    def is_connected(self):
        return self._connection_status == True
        
    def update_sensor_info(self, stream_id, payload):
        if (self.is_connected()):
            raise ValueError('Updating sensor info after connection is no allowed. ')
        self._sensor_info[stream_id].update(payload)    
        
    def is_stream_enabled(self, stream_id): 
        return self._sensor_info[stream_id]["stream_state"] == "enabled"
    
    def get_sensor_info(self):
        return self._sensor_info
    
    def get_username(self):
        return self._auth_handler.get_config()["username"]
    
    def get_hia_id(self):
        return self._hia_id
    
    # Self Getters Setters - End
    
    
    def connect(self, hia_version = None, device = None, system_version = None):
        logging.debug(self._HIA_version)
    
        # internal HIA handlers
        self._sio.on('connect_error', handler=self.connection_error_handler)
        self._sio.on('ping', handler=self.ping_handler) #required to identify HIA health by the server ! do not remove.
        self.attach_stream_state_handler(self.stream_state_handler)
        self.attach_downlink_handler(self.downlink_handler)
        self.attach_socket_connection_handler(self.socket_connection_handler)
        self.attach_socket_disconnect_handler(self.socket_disconnect_handler)
        
        headers = {
            "jwt_token": self._access_token,  # required
            "jwt_refresh_token": self._refresh_token,  # required
            "hia_version": hia_version,
            "hia_id": self._hia_id,  # required, make sure there are no 2 HIAs with the same id for specific user !
            "device": device,
            "system_version": system_version,
            "sensors_info": json.dumps(self._sensor_info),  # required, at least 1 sensor, otherwise connection will fail
            "current_local_time": str(round(time.time())),  #returns current system time that local OS reports.
            "local_timezone": time.strftime("%z"),       # returns the form "+/- 4DIGIT" that is standard in email headers (see section 3.3 of RFC 2822)
        }
        pipeline_url =  self._api_config.get_socket_url()
     
        logging.debug("Connecting to NeuroSpeed pipeline as HIA: {} User: {} Sensors Stream ids: {}"
              .format( self._hia_id, self._username, list(self._sensor_info.keys()) ))
  
        logging.debug(headers)
        
        

        logging.debug(f"connecting socket to {pipeline_url}")
        max_hia_reconnect_retries = 10
        for reconnect_idx in range(max_hia_reconnect_retries):
            try: 
                logging.debug(f"connection attempt {reconnect_idx+1}")
                self._sio.connect(url = pipeline_url, transports ='websocket', headers=headers, socketio_path= '/hia' ) 
                if self._sio.sid != None:
                    logging.debug(f'socket session ID is {self._sio.sid}')
                    break
                
            except Exception as e:
                logging.debug(f"exception caught while connecting socket, error message: {e}")
        
        if self._sio != None:
            logging.debug("session ID: " + str(self._sio.sid))
        
        
    

    

    def disconnect(self):
        self._sio.disconnect()