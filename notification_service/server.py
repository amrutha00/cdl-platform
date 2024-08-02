from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from app import RabbitMQManager  # Assuming RabbitMQManager is in app.py
from consumers import start_consumers
from websocker_server import WebSocketServer
import threading


app = Flask(__name__)
CORS(app)


env_file = 'env_local.ini'
with open(env_file, "r") as f:
    for line in f:
        split_line = line.split("=")
        name = split_line[0]
        value = "=".join(split_line[1:]).strip("\n").strip()
        os.environ[name] = value


websocket_server = WebSocketServer()

rabbitmq_manager = RabbitMQManager(
    rabbitmq_server=os.environ['rabbitmq_server'],
    rabbitmq_username=os.environ['rabbitmq_username'],
    rabbitmq_password=os.environ['rabbitmq_password'] 
)

@app.route('/health', methods=['GET'])
def health_check():
    try:
        rabbitmq_manager.connection.process_data_events()
        return jsonify({'status': 'up'}), 200
    except Exception as e:
        return jsonify({'status': 'down', 'error': str(e)}), 500


@app.route('/notify/publish', methods=['POST'])
def publish_message():
    try:
        data = request.json
        routing_key = data['routing_key']
        message = data['message']
        result = rabbitmq_manager.publish(routing_key, message)
        if result:
            return jsonify({'status': 'success', 'message': 'Message published successfully'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to publish message'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    start_consumers()
    websocket_thread = threading.Thread(target=websocket_server.run,daemon=True)
    websocket_thread.start()
    app.run(debug=True, host='0.0.0.0', port=80)
