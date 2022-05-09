import socket
import threading, wave, pyaudio, time, queue
import sys
import struct
import numpy as np
#Wait for incoming data from server
#.decode is used to turn the message in bytes to a string
host = "localhost"
port = 5432

terminateReturnThread = False
def receive(signal, multi_list, stat_int, client_socket):
    while signal:
        # try:
            # data = socket.recv(32)
            # print(str(data.decode("utf-8")))
        multi_station = multi_list[stat_int]
        print(multi_station)
        BUFF_SIZE = 65536 #this will later have to be calculated, t (taken as input) * bitrate provided by server
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        p = pyaudio.PyAudio()
        CHUNK = 1024*10
        MCAST_GRP = multi_station[3]
        MCAST_PORT = multi_station[4]
        client_socket.bind(('', MCAST_PORT))
        group = socket.inet_aton(MCAST_GRP)
        mreq = struct.pack('4sl', group, socket.INADDR_ANY)
        client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,1)
        # input_client(client_socket=client_socket)
        stream = p.open(format=p.get_format_from_width(2),
                        channels=2,
                        rate=44100,
                        output=True,
                        frames_per_buffer=CHUNK)
        # create socket
       
        # message = b'Hello'
        # client_socket.sendto(message,("localhost",5445))
        DATA_SIZE,_= client_socket.recvfrom(BUFF_SIZE)
        # print("Hello")
        # DATA_SIZE = int(DATA_SIZE.decode())
        # while True:
       
        q = queue.Queue(maxsize=10000000)
        cnt=0
        def getAudioData():
            while True:
                if(terminateReturnThread):
                    return
                frame,_= client_socket.recvfrom(BUFF_SIZE)
                q.put(frame)
                # print('[Queue size while loading]...',q.qsize())
                    
        t1 = threading.Thread(target=getAudioData, args=())
        t1.start()
        time.sleep(3)
        # DURATION = DATA_SIZE*CHUNK/44100
        # print('[Now Playing]... Data','[Audio Time]:','seconds')
        while True:
            if(terminateReturnThread):
                return
            frame = q.get()
            stream.write(frame)
            # time.sleep(0.0001)
            # print('[Queue size while playing]...',q.qsize(),'[Time remaining...]',round(DURATION),'seconds')
            # DURATION-=CHUNK/44100
            if(q.qsize()==0):
                break
        client_socket.close()
        print('Audio closed')
        # break


        # except:
        #     print("You have been disconnected from the server")
        #     signal = False
        #     break
def input_client(client_socket):
    client_msg = "Type P, R, T or S at any point you want to Pause, Restart, Terminate, or Switch respectively: "
    message = input(client_msg)
    print(message)
    # this will take mcast port as input as well as mcast grp
    client_socket.sendto(message.encode(),(host, port))

#Attempt connection to server through tcp protocol
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    multi_msg = sock.recv(1024).decode()
    print(multi_msg)
    # this will convert string into an ordered list
    multi_list = eval(multi_msg)
    print(multi_list)
    station = input("Enter the station you want to listen to: ")
    # the stat_int is the index of the station in the list, which will be sent to recieve
    # so as to know which station to listen to
    # and further would be used for switch station feature
    stat_int = int(station)
except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)
# this will get the station info from the selected choice    

sock.send(station.encode())

""" We need to get the signal to either pause, restart, terminate
or switch the respective station
It will be necessary to have a different thread which can do this for us   """
        # do something with the message
#Create new thread to wait for data
# other args will be given based on the selection
# receiveThread = threading.Thread(target = receive, args = (sock, True, multi_list, stat_int, client_socket))
# receiveThread.start()
# time.sleep(1)
# inputThread = threading.Thread(target=input_client, args = (client_socket,))
# inputThread.start()
isPlaying = True
while True:
    terminateReturnThread = False
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    receiveThread = threading.Thread(target = receive, args = (isPlaying, multi_list, stat_int, client_socket))
    receiveThread.start()
    time.sleep(1)
    client_msg = "Type P, R, T or S at any point you want to Pause, Restart, Terminate, or Switch respectively: "
    message = input(client_msg)
    print("message recieved", message)
    #switch case
    if(message=='P'):
        isPlaying = False
        terminateReturnThread = True
        receiveThread.join()
        client_socket.close()
        print("Paused")
    elif(message == 'R'):
        if(isPlaying):
            print("The song is already playing")
        else:
            terminateReturnThread = True
            receiveThread.join()
            client_socket.close()
            print("Restarted")
            isPlaying = True
    elif(message == 'T'):
        terminateReturnThread = True
        receiveThread.join()
        client_socket.close()
        exit()
    elif (message == 'S'):
        station = input("Enter the station you want to listen to: ")
        stat_int = int(station)
        client_socket.close()
        terminateReturnThread = True
        receiveThread.join()
        print("Switching")
    # this will take mcast port as input as well as mcast grp

#Send data to server
#str.encode is used to turn the string message into bytes so it can be sent across the network
# while True:
#     message = input()
#     sock.sendall(str.encode(message))
