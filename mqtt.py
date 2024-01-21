class MQTT():
    def __init__(self):        
        #self.inc_data = dict(str, list<str>)
        pass
    
    def connect(self, ip: str) -> bool: 
        # do all the cool connection stuff and reuturn True or False if successful or not
        return True
    
    def pub_topic(self, topic: str, data: str ) -> bool:
        # do some cool stuff to write data to a specific 
        return True
    
    def sub_topic(self, topic: str) -> bool:
        # do some cool stuff where we have a new thread to receive data and push it to the inc_data
        return True

    def data_available(self, topic: str) -> bool:
        # return if the list has some data
        return False
    
    def get_data(self, topic: str) -> (bool, str):
        # do some cool stuff and check if the topic has some data, return it and remove from the list.
        return True, ""
    
    

