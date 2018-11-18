import argparse
import socket
import time
import json
import uuid
from queue import Queue


# смысл вводить get_queue

class Task:
    def __init__(self, task_length, task_data, task_id=None, task_status=None, task_start_time=None):
        self.length = task_length
        self.data = task_data
        self.id = task_id or str(uuid.uuid4())
        self.status = task_status or 'UNDONE'
        self.started_at = task_start_time


class TaskQueue:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.task_map = dict()
        #self.task_queue = Queue()

    def append(self, task: Task) -> str:
        self.task_map[task.id] = task
        #self.task_queue.put(task)
        return task.id

    # Он нужен???
    def __iter__(self):
        for task in self.task_map.values():
            yield task


class TaskQueueServer:
    def __init__(self, ip, port, path, timeout):
        self.ip = ip
        self.port = port
        self.path = path
        self.timeout = timeout
        self.queue_map = dict()

    def queue_add(self, args: list) -> bytes:
        if len(args) != 3:
            return b'ERROR'
        queue_name, length, data = args
        if queue_name not in self.queue_map:
            self.queue_map[queue_name] = TaskQueue(queue_name)
        task_id = self.queue_map[queue_name].append(Task(length, data))
        return task_id.encode()

    def queue_get(self, args: list) -> bytes:
        if len(args) != 1:
            return b'ERROR'
        queue_name, = args
        if queue_name in self.queue_map:
            task_queue = self.queue_map[queue_name]
            for task in task_queue:
                if task.status == 'UNDONE':
                    task.status = 'EXECUTING'
                    task.started_at = time.time()
                    task_id = task.id
                    task_length = task.length
                    task_data = task.data
                    return ' '.join([task_id, task_length, task_data]).encode()
        return b'NONE'

    def queue_ack(self, args: list) -> bytes:
        if len(args) != 2:
            return b'ERROR'
        queue_name, task_id = args
        if queue_name in self.queue_map:
            task_queue = self.queue_map[queue_name]
            if task_id in task_queue.task_map:
                task = task_queue.task_map[task_id]
                if task.status == 'EXECUTING':
                    task.status = 'DONE'
                    del task_queue.task_map[task_id]
                    return b'YES'
        return b'NO'

    def queue_in(self, args: list) -> bytes:
        if len(args) != 2:
            return b'ERROR'
        queue_name, task_id = args
        if queue_name in self.queue_map:
            task_queue = self.queue_map[queue_name]
            if task_id in task_queue.task_map:
                return b'YES'
        return b'NO'

    def queue_save(self):
        ark = dict()
        for queue in self.queue_map.values():
            queue_tasks = list()
            for task in queue.task_map.values():
                task_info = {"TASK_ID": task.id,
                             "TASK_DATA": task.data,
                             "TASK_LENGTH": task.length,
                             "TASK_STARTED_AT": task.started_at,
                             "TASK_STATUS": task.status}
                queue_tasks.append(task_info)
            ark[queue.queue_name] = queue_tasks
        print(json.dumps(ark))

    def queue_load(self):
        with open(self.path, 'r') as f:
            ark = json.loads(f.read)
        for queue_name in ark:
            queue = TaskQueue(queue_name)
            for task_info in ark[queue_name]:
                task_id = task_info["TASK_ID"]
                task_data = task_info["TASK_DATA"]
                task_length = task_info["TASK_LENGTH"]
                task_started_at = task_info["TASK_STARTED_AT"]
                task_status = task_info["TASK_STATUS"]
                task = Task(task_length, task_data, task_id, task_status, task_started_at)

    def run(self):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(('0.0.0.0', 5555))
        connection.listen()
        print('Starting listening')
        while True:
            current_connection, address = connection.accept()
            data = b''
            while not data.endswith(b'\r\n'):
                data += current_connection.recv(1024)
            print(data)
            request = data.decode()
            request_args = request.split()

            if len(request_args):
                command = request_args[0]
            else:
                command = None
            response = None
            if command == 'ADD':
                response = self.queue_add(request_args[1:])
            elif command == 'GET':
                response = self.queue_get(request_args[1:])
            elif command == 'ACK':
                response = self.queue_ack(request_args[1:])
            elif command == 'IN':
                response = self.queue_in(request_args[1:])
            elif command == 'SAVE':
                self.queue_save()
            else:
                current_connection.send(b'ERROR')

            if response:
                current_connection.send(response)
            current_connection.close()


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='0.0.0.0',
        help='Server ip adress')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
