
comments:
1 -
    when you receive user_device disconnect event, this event means that specific USER HIA device disconnected,
    but not necessary means that user is no longer connected, because 2 hia devices might be connected for the same user
    and when one device disconnect, the other one might be still online, so this is not enough to determine whether to 
    disconnect from UserRoom as Customer. Only when there are no connections for this user at all, it's safe to disconnect from UserRoom without losing data.
    One way to decide whether user no longer connected is to query Neurospeed Api for the list of currently connected users

2 -  
    CustomerRoom produces live connection events, but at the time of CustomerRoom connection
    you might want to query Neurospeed Api for the list of currently connected users in order to know about
    connections which happened before CustomerRoom's connection established, you can do this by querying the NeuroSpeed api.
    
3 -  
    after CustomerRoom socket connection, the moment user connects - the CustomerRoom instance will propogate HIA's connection event to the main program,
	where it will fetch user's releated information, and will do a socket connection to UserRoom releated to this user. (if UserRoom not yet exist)
	same when HIA's disconnect event fired, it will first check if user really not online, and if so, it will disconnect from user's UserRoom (after user connectivity validation via API)

4 - event payload structure:
   connect event payload -  {'type': 'connect', 'username': 'some_user', 'hia_id': 'some_hia_id','sensors': {"stream_idX": {sensor_object},..,"stream_idY": {sensor_object}}}
   disconnect event payload - {'type': 'disconnect', 'username': 'some_user', 'hia_id': 'some_hia_id', 'sensors': {"stream_idX": {sensor_object},..,"stream_idY": {sensor_object}}}
   
   
5 - 
    initialize sensors must be called before connection request and sensors must be sent with the request itself.
    updating sensor information after connection is not allowed and would cause errors. 
    if it's necessary to update sensors info, one should disconnect and reconnect with new sensor information.