import pika
from pymongo import MongoClient
import asyncio
import json 
from bson import ObjectId
import time
import os
from websocker_server import WebSocketServer

class RabbitMQManager:

    def __init__(self, rabbitmq_server, rabbitmq_username, rabbitmq_password):
        self.parameters = pika.ConnectionParameters(
            host=rabbitmq_server,
            credentials=pika.PlainCredentials(rabbitmq_username, rabbitmq_password),
            heartbeat=300,
            blocked_connection_timeout=300,
            retry_delay=5

        )
        self.mongo_client = MongoClient(os.environ['cdl_test_uri'])
        self.db = os.environ['db_name']#'cdl-local'
        self.db_conn = self.mongo_client[self.db]
        self.websocker_server = WebSocketServer()
        self.connection = None
        self.establish_connection()
        
       

    def establish_connection(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(self.parameters)
                self.channel = self.connection.channel()
                self.declare_queue()
                break 
            except Exception as e:
                print(f"Connection failed: {e}, retrying in 5 seconds...")
                time.sleep(5)

    def check_connection(self):
        if not self.connection or self.connection.is_closed:
            print("Connection is closed, re-establishing...")
            self.connection = self.establish_connection()
    
    def declare_queue(self):
        try:
            self.channel.exchange_declare(exchange='notifications', exchange_type='direct', durable=True)
            notification_types = ['add_submission']#['community_join','add_submission','submission_upvote','submission_mention']
            for notification in notification_types:
                self.channel.queue_declare(queue=notification,durable=True)
                self.channel.queue_bind(exchange='notifications', queue=notification, routing_key=notification)
        except Exception as e:
            print(f"Failed to declare exchange or queue: {e}")


    def publish(self,routing_key,message):
        self.check_connection()
        try:
            self.channel.basic_publish(
                exchange='notifications',
                routing_key=routing_key,
                body=json.dumps(message).encode(),
                properties=pika.BasicProperties(
                    delivery_mode=2,  #  pika.DeliveryMode.Persistent
                )
            )
            print(f"Message sent to {routing_key} queue: {message}")
            return True
        except Exception as e:
            print(f"Failed to deliver message due to: {e}")
            return False
        
        finally:

            pass

    def consume(self,queue_name):
        def callback(ch, method, properties, body):
            data = body.decode()
            print(f"Received: {data}")
            asyncio.run(self.process_msgs(data))
        
        while True:
            try:
                self.check_connection()
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
                print(f"Starting to consume from {queue_name}")
                self.channel.start_consuming()
            except Exception as e:
                print(f" Rabbitmq exception: {e}")
                self.establish_connection()
                time.sleep(5)
    
   

    async def process_msgs(self,data):
        try: 
            
            data = json.loads(data)
            notif_db =  self.db_conn.notifications
            comm_db =  self.db_conn.communities
            users_db =  self.db_conn.users
            community = comm_db.find_one({"_id":ObjectId(data['community'])})
            community_name = community['name']
            users_in_comm =users_db.find(
                    {"communities": ObjectId(data['community'])},
                )
            src_notif_email = data['notify_src_email']
            del data['notify_src_email']
            del data['community']

            for user in list(users_in_comm):
                user_id = str(user['_id'])
                if user["email"] == src_notif_email:
                    continue
                notif_data = data.copy()
                print("self.websocket_server.connected_users",self.websocker_server.connected_users)
                if user_id in self.websocker_server.connected_users:
                    
                    await self.websocker_server.send_message(user_id, {"type": "notification", "data": notif_data})
                    notif_data['notify_delivered'] = True
                    print("notifying user", user['username'],user_id)
                else:
                    print("User not connected", user['username'],user_id)

                
                notif_data['notify_to'] = user
                insert_result = notif_db.insert_one(notif_data)
                print("Inserted document ID:", insert_result.inserted_id)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {'status': 'error', 'message': f'Unexpected error: {e}'}
        


    def close_connection(self):
        """Closes the RabbitMQ connection."""
        if self.connection:
            self.connection.close()
            print("Connection closed.")
