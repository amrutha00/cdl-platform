import multiprocessing
from app import RabbitMQManager
from threading import Thread
import os


def consume(queue):
    rabbit_manager = RabbitMQManager(
        rabbitmq_server=os.environ['rabbitmq_server'],
        rabbitmq_username=os.environ['rabbitmq_username'],
        rabbitmq_password=os.environ['rabbitmq_password'] 
    )
    rabbit_manager.declare_queue()
    rabbit_manager.consume(queue)

def start_consumers():
    queues = ["add_submission"]#['community_join', 'add_submission', 'submission_upvote', 'submission_mention']
    #threads = []
    processes = []
    for queue in queues:
        # thread = Thread(target=consume, args=(queue,))
        # thread.daemon = True
        # thread.start()
        # threads.append(thread)
        # process = multiprocessing.Process(target=consume, args=(queue,))
        # process.daemon = True
        # process.start()
        # processes.append(process)
