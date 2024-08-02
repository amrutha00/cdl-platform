import multiprocessing
from app import RabbitMQManager



def consume(queue):
    rabbit_manager = RabbitMQManager('rabbitmq', 'user', 'admin')
    rabbit_manager.declare_queue()
    rabbit_manager.consume(queue)

def start_consumers():
    queues = ["add_submission"]#['community_join', 'add_submission', 'submission_upvote', 'submission_mention']
    processes = []
    for queue in queues:
        process = multiprocessing.Process(target=consume, args=(queue,))
        process.daemon = True
        process.start()
        processes.append(process)
