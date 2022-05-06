import socket
import threading, wave, pyaudio, time, queue
import sys

#Wait for incoming data from server
#.decode is used to turn the message in bytes to a string
def receive(sock, signal):
    while signal:
        # try:
            # data = socket.recv(32)
            # print(str(data.decode("utf-8")))

        BUFF_SIZE = 65536
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
        p = pyaudio.PyAudio()
        CHUNK = 10*1024
        stream = p.open(format=p.get_format_from_width(2),
                        channels=2,
                        rate=44100,
                        output=True,
                        frames_per_buffer=CHUNK)
                        
        # create socket
        message = b'Hello'
        client_socket.sendto(message,("localhost",5445))
        DATA_SIZE,_= client_socket.recvfrom(BUFF_SIZE)
        print("Hello")
        DATA_SIZE = int(DATA_SIZE.decode())
        q = queue.Queue(maxsize=DATA_SIZE)
        cnt=0
        def getAudioData():
            while True:
                frame,_= client_socket.recvfrom(BUFF_SIZE)
                q.put(frame)
                print('[Queue size while loading]...',q.qsize())
                    
        t1 = threading.Thread(target=getAudioData, args=())
        t1.start()
        time.sleep(5)
        DURATION = DATA_SIZE*CHUNK/44100
        print('[Now Playing]... Data',DATA_SIZE,'[Audio Time]:',DURATION ,'seconds')
        while True:
            frame = q.get()
            stream.write(frame)
            print('[Queue size while playing]...',q.qsize(),'[Time remaining...]',round(DURATION),'seconds')
            DURATION-=CHUNK/44100
            if(q.qsize()==0):
                break
        client_socket.close()
        print('Audio closed')
        break


        # except:
        #     print("You have been disconnected from the server")
        #     signal = False
        #     break

#Get host and port
host = "localhost"
port = 5432

#Attempt connection to server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)

#Create new thread to wait for data
receiveThread = threading.Thread(target = receive, args = (sock, True))
receiveThread.start()

#Send data to server
#str.encode is used to turn the string message into bytes so it can be sent across the network
# while True:
#     message = input()
#     sock.sendall(str.encode(message))

