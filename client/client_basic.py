import socket, threading, pyaudio, time, queue, sys, struct

host = "localhost"
port = 5432

# Global variable used as a flag to check whether we have to terminate the recieve thread
terminateRecieveThread = False 

def receive(signal, multi_list, stat_int, client_socket):
    while signal:
        multi_station = multi_list[stat_int] # station related information 
        print("Information about the current station: ",multi_station)
        BUFF_SIZE = 65536  #this will later have to be calculated, t (taken as input) * bitrate provided by server
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        p = pyaudio.PyAudio()
        CHUNK = 1024*10
        MCAST_GRP = multi_station[3] # multicast address of the station to be played 
        MCAST_PORT = multi_station[4] # multicast port of the station to be playeed
        client_socket.bind(('', MCAST_PORT))
        group = socket.inet_aton(MCAST_GRP)
        mreq = struct.pack('4sl', group, socket.INADDR_ANY)
        
        # Setting socket options
        client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,1)
        
        stream = p.open(format=p.get_format_from_width(2),
                        channels=2,
                        rate=44100,
                        output=True,
                        frames_per_buffer=CHUNK)

        q = queue.Queue(maxsize=10000000)
        def getAudioData():
            while True:
                if(terminateRecieveThread):
                    return
                try:
                    frame,_= client_socket.recvfrom(BUFF_SIZE)
                    q.put(frame)
                except:
                    pass
                
        t1 = threading.Thread(target=getAudioData, args=())
        t1.start()
        time.sleep(3)
        while True:
            if(terminateRecieveThread):
                return
            frame = q.get()
            stream.write(frame)
            if(q.qsize()==0):
                break
        # Closing the client_socket
        client_socket.close()

try:
    #Connect to server through tcp protocol
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
    while(stat_int >= len(multi_list) or stat_int < 0):
        station = input("Invalid station number. Please enter a valid station number (Between 0 and %d): "%(len(multi_list) - 1))
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
isPlaying = True
while True:
    terminateRecieveThread = False
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    receiveThread = threading.Thread(target = receive, args = (isPlaying, multi_list, stat_int, client_socket))
    receiveThread.start()
    time.sleep(1)
    client_msg = "Type P, R, T or S at any point you want to Pause, Restart, Terminate, or Switch respectively: "
    message = input(client_msg)
    print("message recieved", message)
    if(message=='P'):
        isPlaying = False
        terminateRecieveThread = True
        receiveThread.join()
        client_socket.close()
        print("Paused")
    elif(message == 'R'):
        if(isPlaying):
            print("The song is already playing")
        else:
            terminateRecieveThread = True
            receiveThread.join()
            client_socket.close()
            print("Restarted")
            isPlaying = True
    elif(message == 'T'):
        terminateRecieveThread = True
        receiveThread.join()
        client_socket.close()
        exit()
    elif (message == 'S'):
        station = input("Enter the station you want to listen to: ")
        stat_int = int(station)
        while(stat_int >= len(multi_list) or stat_int < 0):
            station = input("Invalid station number. Please enter a valid station number (Between 0 and %d): "%(len(multi_list) - 1))
            stat_int = int(station)
        client_socket.close()
        terminateRecieveThread = True
        receiveThread.join()
        print("Switching")
