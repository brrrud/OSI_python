import socket
import random
from random import randint
import string
from time import sleep, perf_counter
from threading import current_thread, Thread
from multiprocessing import current_process, Process, Queue, Pipe
from json import dumps

HOST = "127.0.0.1"
PORT = 65430


def filter(letters):
    res = []
    letters = letters.split()
    for i in range(len(letters)):
        res.append(letters[i][len(letters[i])::-1])

    return ' '.join(res)


def generate_random_string(length):
    letters = string.ascii_letters
    result = []
    for j in range(length):
        for k in range(length):
            rand_digit = randint(2, length)
            rand_string = ''.join(random.choice(letters)
                                  for i in range(rand_digit))
        result.append(rand_string)

    return ' '.join(result)


def thread_task_1(strok, queue, input, output):
    timeit_1 = [perf_counter()]
    thread_name = current_thread().name
    timeit_1.append(perf_counter())
    process_name = current_process().name
    timeit_1.append(perf_counter())
    delay = 1e-4
    timeit_1.append(perf_counter())
    sleep(delay)
    timeit_2 = [perf_counter()]
    timeit_2.append(perf_counter())
    additive = ''
    timeit_2.append(perf_counter())
    if input != 0:
        additive = input.recv()
    timeit_2.append(perf_counter())
    before_filter = strok
    after_filter = filter(strok)
    timeit_2.append(perf_counter())
    strbuff = after_filter.replace(' ', '\n')
    timeit_2.append(perf_counter())
    strok = '\n' + strbuff

    timeit_2.append(perf_counter())
    data = f'{additive} {strok}'
    timeit_2.append(perf_counter())
    timeit = [process_name, thread_name] + [[timeit_1, timeit_2]]
    timeit.append(
        f'Thread {thread_name} in process {process_name} done with result {data} \n(started with string {before_filter})')
    queue.put(timeit)
    output.send(data)



def thread_task_2(queue, input, output):
    timeit_1 = [perf_counter()]
    thread_name = current_thread().name
    timeit_1.append(perf_counter())
    process_name = current_process().name
    timeit_1.append(perf_counter())
    delay = 1e-4
    timeit_1.append(perf_counter())
    sleep(delay)
    timeit_2 = [perf_counter()]
    timeit_2.append(perf_counter())
    strok = input.recv()
    timeit_2.append(perf_counter())
    strok = strok.split()
    timeit_2.append(perf_counter())
    for i, val in enumerate(strok):
        timeit_2.append(perf_counter())
        strok[i] = f'{i + 1}: {val}'
    timeit_2.append(perf_counter())
    data = ' '.join(strok)
    timeit_2.append(perf_counter())
    timeit = [process_name, thread_name]
    timeit.append([timeit_1])
    timeit_2.append(perf_counter())
    timeit[2].append(timeit_2)
    timeit += [
        f'Thread {thread_name} in process {process_name} done with result {data}']
    queue.put(timeit)
    output.send(data)

def process_task(queue):
    timeit_1 = [perf_counter()]
    conn1, conn2 = Pipe(duplex=True)
    timeit_1.append(perf_counter())
    conn3, conn4 = Pipe()
    timeit_1.append(perf_counter())
    conn5, conn6 = Pipe()
    timeit_1.append(perf_counter())
    stringa = generate_random_string(randint(2, 7))
    timeit_1.append(perf_counter())
    stringb = generate_random_string(randint(2, 7))
    timeit_1.append(perf_counter())
    thread1 = Thread(target=thread_task_1, args=([stringa, queue, 0, conn1]))
    timeit_1.append(perf_counter())
    thread2 = Thread(target=thread_task_1, args=(
        [stringb, queue, conn2, conn3]))
    timeit_1.append(perf_counter())
    thread3 = Thread(target=thread_task_2, args=([queue, conn4, conn5]))
    timeit_1.append(perf_counter())
    thread1.start()
    timeit_1.append(perf_counter())
    thread2.start()
    timeit_1.append(perf_counter())
    thread3.start()
    timeit_2 = [perf_counter()]
    thread1.join()
    timeit_2.append(perf_counter())
    thread2.join()
    timeit_2.append(perf_counter())
    thread3.join()
    timeit_2.append(perf_counter())
    item = conn6.recv()
    timeit_2.append(perf_counter())
    # queue.put(f'Finally {item}')
    process_name = current_process().name
    timeit = [process_name, f'{process_name}_t'] + [[timeit_1, timeit_2]] + \
             [f"Process {process_name} done with result {item}."]
    queue.put(timeit)


if __name__ == '__main__':
    queue = Queue()
    glob_keys = ['Process-1', 'Process-2', 'Process-3']
    inner_keys = ['Thread-1', 'Thread-2', 'Thread-3', 'info', '_t']
    info_dict = {val: {j if j != '_t' else f'{val}{j}': []
                       for j in inner_keys} for i, val in enumerate(glob_keys)}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        processes = [Process(target=process_task, args=(queue,))
                     for i in range(3)]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        while not queue.empty():
            data = queue.get()
            proc_name, thread_name, *times, info = data
            info_dict[proc_name][thread_name] = times[0]
            info_dict[proc_name]['info'].append(info)
            print(info)

        b = bytes(dumps(info_dict, indent=6) + '###', encoding='utf-8')
        s.sendall(b)

