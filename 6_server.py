from __future__ import annotations
import multiprocessing
import socket
import logging
import sys
from multiprocessing import Queue
from threading import Thread
from json import loads, dumps
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


HOST = "127.0.0.1"
PORT_1 = 65430
PORT_2 = 65429


class Server:
    def __init__(self, queue: multiprocessing.Queue, host: str) -> None:
        self.q, self.host = queue, host

    def __str__(self) -> str:
        return f'(Server {self.host})'

    def listner(self, port: int) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = ' '
                while data != b'':
                    data = conn.recv(1024)
                    if data == b'':
                        break
                    self.q.put(data)

    def client_server(self, port1: int, port2: int) -> None:
        client1 = Thread(target=self.listner, args=(port1,))
        client2 = Thread(target=self.listner, args=(port2,))
        client1.start()
        client2.start()
        client1.join()
        client2.join()
        self.serialize_data()

    def logger(self, data: dict, client: str) -> None:
        logger = logging.getLogger()
        if logger.hasHandlers():
            logger.handlers.clear()
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.info(f"Recieved '{client} started.'")
        for k in data.keys():
            info = data[k]['info']
            for i in info:
                logger.info(f"Recieved '{i}'")
        logger.info(f"Recieved '{client} ended.'")

    def serialize_data(self) -> None:
        data = ''
        while not self.q.empty():
            data = f'{data}{self.q.get().decode("utf-8")}'

        [print(i) for i in data.split('###')[:-1]]
        sp = [loads(i) for i in data.split('###')[:-1]]

        self.logger(sp[0], "Client 1")
        self.logger(sp[1], "Client 2")
        self.plot_data(sp)

    def fracture(self, lst: list[list[list[float], list[float]]]) -> None:
        # print(lst)
        for i in range(len(lst)):
            for j in range(len(lst[0])):

                lst[i][j] = np.linspace(lst[i][j][0], lst[i][j][-1], 50)

    def plot_data(self, data_clients: list[dict, dict]):
        # []
        p1 = [data_clients[0]['Process-1'][f'Thread-{i}'] for i in range(1, 4)] + \
             [data_clients[0]['Process-1'][f'Process-1_t']]
        # p1 = [[array(of 50 el), array(of 50 el)], [[], []] .....]
        p2 = [data_clients[0]['Process-2'][f'Thread-{i}'] for i in range(1, 4)] + \
             [data_clients[0]['Process-2'][f'Process-2_t']]
        p3 = [data_clients[0]['Process-3'][f'Thread-{i}'] for i in range(1, 4)] + \
             [data_clients[0]['Process-3'][f'Process-3_t']]
        p4 = [data_clients[1]['Process-1'][f'Thread-{i}'] for i in range(1, 4)] + \
             [data_clients[1]['Process-1'][f'Process-1_t']]
        p5 = [data_clients[1]['Process-2'][f'Thread-{i}'] for i in range(1, 4)] + \
             [data_clients[1]['Process-2'][f'Process-2_t']]
        mn1 = min([min([min(j) for j in i]) for i in [p1, p2, p3]])[0]
        mn2 = min([min([min(j) for j in i]) for i in [p4, p5]])[0]

        self.fracture(p1)
        self.fracture(p2)
        self.fracture(p3)
        self.fracture(p4)
        self.fracture(p5)

        def animate(i, p1, p2, p3, left_border, title):
            axes.clear()
            plt.title(title, color="black")
            x1_11, x1_21, x1_31 = (p1[0][0][i] - p1[0][0][0]) * 10, (p1[1][0][i] - p1[1][0][0]) * 10, (
                p1[2][0][i] - p1[2][0][0]) * 10
            x1_12, x1_22, x1_32 = (p1[0][1][i] - p1[0][1][0]) * 10, (p1[1][1][i] - p1[1][1][0]) * 10, (
                p1[2][1][i] - p1[2][1][0]) * 10
            x11, x12 = (p1[3][0][i] - p1[3][0][0]) * \
                10, (p1[3][1][i] - p1[3][1][0]) * 10

            axes.barh(0, x1_11 / 1e-4,
                      color=palette[0], left=(p1[0][0][0] - left_border) / 1e-4)
            axes.barh(0, x1_12 / 1e-4,
                      color=palette[0], left=(p1[0][1][0] - left_border) / 1e-4)

            axes.barh(1, x1_21 / 1e-4,
                      color=palette[0], left=(p1[1][0][0] - left_border) / 1e-4)
            axes.barh(1, x1_22 / 1e-4,
                      color=palette[0], left=(p1[1][1][0] - left_border) / 1e-4)

            axes.barh(2, x1_31 / 1e-4,
                      color=palette[0], left=(p1[2][0][0] - left_border) / 1e-4)
            axes.barh(2, x1_32 / 1e-4,
                      color=palette[0], left=(p1[2][1][0] - left_border) / 1e-4)

            axes.barh(
                3, x11 / 1e-4, color=palette[0], left=(p1[3][0][0] - left_border) / 1e-4)
            axes.barh(
                3, x12 / 1e-4, color=palette[0], left=(p1[3][1][0] - left_border) / 1e-4)

            x2_11, x2_21, x2_31 = (p2[0][0][i] - p2[0][0][0]) * 10, (p2[1][0][i] - p2[1][0][0]) * 10, (
                p2[2][0][i] - p2[2][0][0]) * 10
            x2_12, x2_22, x2_32 = (p2[0][1][i] - p2[0][1][0]) * 10, (p2[1][1][i] - p2[1][1][0]) * 10, (
                p2[2][1][i] - p2[2][1][0]) * 10
            x21, x22 = (p2[3][0][i] - p2[3][0][0]) * \
                10, (p2[3][1][i] - p2[3][1][0]) * 10

            axes.barh(4, x2_11 / 1e-4,
                      color=palette[1], left=(p2[0][0][0] - left_border) / 1e-4)
            axes.barh(4, x2_12 / 1e-4,
                      color=palette[1], left=(p2[0][1][0] - left_border) / 1e-4)

            axes.barh(5, x2_21 / 1e-4,
                      color=palette[1], left=(p2[1][0][0] - left_border) / 1e-4)
            axes.barh(5, x2_22 / 1e-4,
                      color=palette[1], left=(p2[1][1][0] - left_border) / 1e-4)

            axes.barh(6, x2_31 / 1e-4,
                      color=palette[1], left=(p2[2][0][0] - left_border) / 1e-4)
            axes.barh(6, x2_32 / 1e-4,
                      color=palette[1], left=(p2[2][1][0] - left_border) / 1e-4)

            axes.barh(
                7, x21 / 1e-4, color=palette[1], left=(p2[3][0][0] - left_border) / 1e-4)
            axes.barh(
                7, x22 / 1e-4, color=palette[1], left=(p2[3][1][0] - left_border) / 1e-4)

            if p3:
                x3_11, x3_21, x3_31 = (p3[0][0][i] - p3[0][0][0]) * 10, (p3[1][0][i] - p3[1][0][0]) * 10, (
                    p3[2][0][i] - p3[2][0][0]) * 10
                x3_12, x3_22, x3_32 = (p3[0][1][i] - p3[0][1][0]) * 10, (p3[1][1][i] - p3[1][1][0]) * 10, (
                    p3[2][1][i] - p3[2][1][0]) * 10
                x31, x32 = (p3[3][0][i] - p3[3][0][0]) * \
                    10, (p3[3][1][i] - p3[3][1][0]) * 10

                axes.barh(
                    8, x3_11 / 1e-4, color=palette[2], left=(p3[0][0][0] - left_border) / 1e-4)
                axes.barh(
                    8, x3_12 / 1e-4, color=palette[2], left=(p3[0][1][0] - left_border) / 1e-4)

                axes.barh(
                    9, x3_21 / 1e-4, color=palette[2], left=(p3[1][0][0] - left_border) / 1e-4)
                axes.barh(
                    9, x3_22 / 1e-4, color=palette[2], left=(p3[1][1][0] - left_border) / 1e-4)

                axes.barh(
                    10, x3_31 / 1e-4, color=palette[2], left=(p3[2][0][0] - left_border) / 1e-4)
                axes.barh(
                    10, x3_32 / 1e-4, color=palette[2], left=(p3[2][1][0] - left_border) / 1e-4)

                axes.barh(
                    11, x31 / 1e-4, color=palette[2], left=(p3[3][0][0] - left_border) / 1e-4)
                axes.barh(
                    11, x32 / 1e-4, color=palette[2], left=(p3[3][1][0] - left_border) / 1e-4)

                thr = ["Threads", "Threads", "Threads", "Process"]
                tick_lst = [f'{j}-{l}' for l in range(1, 4) for j in thr]
                plt.yticks(np.arange(12), tick_lst)
            else:
                tick_lst = ['Thread-1', 'Thread-2', 'Thread-3', 'Process-1',
                            'Thread-1', 'Thread-2', 'Thread-3', 'Process-2']
                plt.yticks(np.arange(8), tick_lst)

        palette = ('yellow', 'blue', 'red')
        fig, axes = plt.subplots(figsize=(12, 8))

        anim = FuncAnimation(fig, animate, interval=100, frames=50, repeat=False,
                             fargs=(p1, p2, p3, mn1, "Client 1\nprocesses & threads animation"))
        plt.show()
        fig, axes = plt.subplots(figsize=(12, 8))
        anim2 = FuncAnimation(fig, animate, interval=100, frames=50, repeat=False,
                              fargs=(p4, p5, [], mn2, "Client 2\nprocesses & threads animation"))
        plt.show()


if __name__ == '__main__':
    queue = Queue()
    serv = Server(queue, host=HOST)
    print(serv)
    serv.client_server(PORT_1, PORT_2)
