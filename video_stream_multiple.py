from websockets.sync.server import serve 
import cv2
from multiprocessing import Process, Pipe
import functools
from os import pipe
 
IP = "127.0.0.1"
PORT = 5000

PROCESSES = []


def video_stream(output_pipe):
    cap = cv2.VideoCapture("rtsp://admin:friki123@192.168.0.172:554/ISAPI/Streaming/Channels/101")
    clients_list = []

    def broadcast():
         while True:
            succsess, frame = cap.read()

            client = output_pipe.poll()
            if client: clients_list.append(client)

            if not succsess:
                break
            else:
                frame = cv2.resize(frame, (640, 480))
                _, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                if frame:
                    for client in clients_list:
                        try:
                            client.send(frame)
                        except:
                            pass

    broadcast()


def on_connect(websocket, input_pipe):
    print("New client connected!")
    input_pipe.send(websocket)


def server_process(input_pipe):
    print(f"Running on ws://{IP}:{PORT}")

    handler = functools.partial(on_connect, input_pipe=input_pipe)
    
    with serve(handler, IP, PORT, close_timeout=2) as server:
        server.serve_forever()


def main():
    input_pipe, output_pipe = Pipe()

    PROCESSES.append(Process(target=server_process, args=(input_pipe,)))
    PROCESSES.append(Process(target=video_stream, args=(output_pipe,)))

    for p in PROCESSES:
        p.start()

    while True:
        pass


if __name__ == '__main__':
    try:
        main()
    except:
        for p in PROCESSES:
            p.terminate()
