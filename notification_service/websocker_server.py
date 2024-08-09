import asyncio
import websockets
import json
import os
from bson import ObjectId
from pymongo import MongoClient

class WebSocketServer:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebSocketServer, cls).__new__(cls)
            print('web socket server is initialized')
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # This checks if it's the first time __init__ is called
            self.connected_users = {}
            self.mongo_client = MongoClient(os.environ['cdl_test_uri'])
            self.db = os.environ['db_name']
            self.db_conn = self.mongo_client[self.db]
            self.initialized = True

    async def send_message(self, user_id, message):

        # if username in self.connected_users:
        try:
            websocket = self.connected_users[user_id]
            await websocket.send(json.dumps(message))
            print(f"Message {message['data']['notify_msg']} sent to {user_id}")
        except Exception as e:
            print(f"Exception in send_messages for user_id: {user_id}: {e}")
    
    async def send_undelivered_messages(self, user_id):

        try:
            undelivered_messages = self.db_conn.notifications.find({'notify_to._id': ObjectId(user_id), 'notify_delivered': False})
            for message in undelivered_messages:
                #print("message in send_undelivered_msg",type(message),message['_id'])
                message_copy = {}
                message_copy['notify_msg'] = message['notify_msg']
                message_copy['notify_timestamp'] = message['notify_timestamp']
                message_copy['notify_type'] = message['notify_type']
                message_copy['notify_read'] = message['notify_read']
                message_copy['notify_delivered'] = message['notify_delivered']
                await self.send_message(user_id, {"type": "notification", "data": message_copy})
                self.db_conn.notifications.update_one({'_id': message['_id']}, {'$set': {'notify_delivered': True}})      
        except Exception as e:
            print(f"Exception in send_undelivered_messages for user_id: {user_id}: {e}")
            
        

    async def register(self, websocket, path):
        try:
            user_id = None
            async for message in websocket:
                data = json.loads(message)
                msg_type = data['type'] 
                user_id = data['user_id']
                print("self.connected_users in register",self.connected_users)
                if msg_type == 'register' and user_id not in self.connected_users :                   
                    self.connected_users[user_id] = websocket

                    print("Connection created for user with user id, ",user_id)
                    await self.send_undelivered_messages(user_id)
                else:
                    print(f"User with user_id: {user_id} is already registered")
        except Exception as e:
            print(f"Exception in websocket server: {e}")
        finally:
            if user_id and user_id in self.connected_users:
                del self.connected_users[user_id]
    
    async def start_server(self):
        async with websockets.serve(self.register, "0.0.0.0", 8090):
            await asyncio.Future()  

    def run(self):
        try:
            print("Starting WebSocket server...")
            asyncio.run(self.start_server())
        except Exception as e:
            print(f"RuntimeError: {e}")
