import random
import time
import paho.mqtt.client as mqtt
from threading import Thread, Lock, Semaphore, Event
import logging


class MQTT_Conn():
    MQTT_ID_PREFIX = 'pysoftplc-mqtt-'
    MQTT_CONN_SYM = ':'
    messages = {}
    _rcv_threads = []

    class MQTT_Conn_Obj():
        def __init__(self, conn_string: str):
            self.conn_string = conn_string
            self.messages = []
            self.access_lock = Lock()
            self.event = Event()   
        
        def add_message(self, message :str) -> None:
            """
            Inserts Message in the array in a thread safe way
            """
            logging.debug("MQTT_Conn_Obj.add_mesasge triggered: {0}".format(message))
            with self.access_lock:
                self.messages.append(message)
            self.event.set()
        
        def get_message(self) -> str:
            """
            Blocking wait for the mesasge in the storage
            - waits until a message is in the array
            - thread safe access to the array
            """
            logging.debug("MQTT_Conn_Obj.get_message triggered.")            
            ret = ""            
            self.event.wait()
            with self.access_lock:                
                if len(self.messages) > 0:
                    ret = self.messages.pop(0)
            self.event.clear()
            return ret
    
    @staticmethod
    def get_conn_topic_string(client: mqtt.Client, topic: str) -> str:
        ret = "{0}:{1}#{2}".format(client._host, client._port, topic)
        return ret
    
    @staticmethod
    def get_conn_obj(client, topic: str) -> MQTT_Conn_Obj:
        conn_string = MQTT_Conn.get_conn_topic_string(client, topic)
        if conn_string in MQTT_Conn.messages.keys():
            return MQTT_Conn.messages[conn_string]
        else:
            logging.warning("MQTT_Conn get_conn_obj: Empty object")
            return None
        
    @staticmethod
    def mqtt_thread(client: mqtt.Client):
        client.loop_forever()

    """
    Simple Wrapper to provide the wanted functionality for MQTT
    """
    def __init__(self, suffix:str = ""): 
        """
        Initialize a new MQTT Server to connect to.
        """   
        #Hint: this is the most simple configuration for the moment, maybe add stuff https://www.emqx.com/en/blog/how-to-use-mqtt-in-python        
        id = MQTT_Conn.MQTT_ID_PREFIX + str({random.randint(0, 1000)}) + suffix
        self.client = mqtt.Client(id)  
        self.client.on_connect = MQTT_Conn.on_connect
        self.client.on_message = MQTT_Conn.on_message

    def on_connect(client, userdata, flags, rc):
        """
        Callback for on_connect.
        """
        if rc == 0:
            logging.info("MQTT_Conn connected to MQTT Broker.")            
        else:
            logging.error("MQTT_Conn Failed to connect, return code: {0}".format(rc))            

    def on_message(client, userdata, msg):
        """
        Callback for on_message
        """
        logging.debug("MQTT_Conn.on_message triggered: Received {0} from {1}".format(msg.payload.decode(), msg.topic))
        dictkey = MQTT_Conn.get_conn_topic_string(client, msg.topic)
        MQTT_Conn.messages[dictkey].add_message(msg.payload.decode())

    def connect(self, ip: str, port: int, username: str, password: str) -> bool: 
        """
        Connect to the wanted server, with a ip, port, username and password.
        Returns true, if successful, or false if not
        """
        try:
            self.client.username_pw_set(username, password)        
            self.client.connect(ip, port)
        except Exception:
            logging.error("MQTT_Conn failed to connect, return code: {0}".format(Exception))

        return True #self.client.is_connected()
    
    def pub_topic(self, topic: str, data: str ) -> bool:
        """
        Publish a new message to the mqtt server
        """
        self.client.publish(topic, data)
        return True
    
    def sub_topic(self, topic: str) -> bool:
        """
        Subscribe to a specific topic and "install" a callback function
        """
        logging.debug("MQTT_Conn.sub_topic subscrive to topic: {0}".format(topic))

        conn_string = MQTT_Conn.get_conn_topic_string(self.client, topic)
        MQTT_Conn.messages[conn_string] = MQTT_Conn.MQTT_Conn_Obj(conn_string)
                
        self.client.subscribe(topic)        

        if not hasattr(self, 'thread'):
            self.thread = Thread(target=MQTT_Conn.mqtt_thread, args=(self.client,))            
            self.thread.start()
        return True

    def data_available(self, topic: str) -> bool:
        """
        Is data currently availalbe?
        """
        return False
    
    def get_data(self, topic: str) -> str:
        """
        Get fetched data from the MQTT broker
        """
        logging.debug("MQTT_Conn.get_data started: {0}".format(topic))
        obj = MQTT_Conn.get_conn_obj(self.client, topic)
        ret = ""
        if obj is not None:
            ret = obj.get_message() 
            logging.debug("MQTT_Conn.get_data received: {0}".format(ret))
        else:
            logging.error("MQTT_Conn.get_data no valid obj con data received.")
        return ret
    