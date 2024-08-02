import asyncio
import websockets
import json
import os
from bson import ObjectId
from pymongo import MongoClient

class WebSocketServer:
    def __init__(self):
        self.connected_users = {}
        self.mongo_client = MongoClient(os.environ['cdl_test_uri']) 
        self.db = os.environ['db_name']
        self.db_conn = self.mongo_client[self.db]

    async def send_message(self, user_id, message):
        # if username in self.connected_users:
        websocket = self.connected_users[user_id]
        await websocket.send(json.dumps(message))
        print(f"Message {message['notify_msg']} sent to {user_id}")
    
    async def send_undelivered_messages(self, user_id):
        undelivered_messages = self.db_conn.notifications.find({'notify_to._id': ObjectId(user_id), 'notify_delivered': False})
        for message in undelivered_messages:
            
            print("message data in undelivered messages",message['notify_msg'],user_id)
            await self.send_message(user_id, {"type": "notification", "data": message['notify_msg']})
            self.db_conn.notifications.update_one({'_id': message['_id']}, {'$set': {'notify_delivered': True}})

    async def register(self, websocket, path):
        try:
            user_id = None
            async for message in websocket:
                data = json.loads(message)
                msg_type = data['type'] 
                user_id = data['user_id']
                if msg_type == 'register' and user_id not in self.connected_users :                   
                    self.connected_users[user_id] = websocket

                    print("Connection created for user with user id, ",user_id)
                    await self.send_undelivered_messages(user_id)
                    
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
