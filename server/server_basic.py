import socket
import threading, wave, pyaudio, time
import math
import struct
import numpy as np

#Variables for holding information about connections
connections = []
total_connections = 0

#Client class, new instance created for each connected client
#Each instance has the socket and address that is associated with items
#Along with an assigned ID and a name chosen by the client
class Client(threading.Thread):
    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal
    
    def __str__(self):
        return str(self.id) + " " + str(self.address)
    
    #Attempt to get data from client
    #If unable to, assume client has disconnected and remove him from server data
    #If able to and we get data back, print it in the server and send it back to every
    #client aside from the client that has sent it
    #.decode is used to convert the byte data into a printable string
    def run(self):

        while self.signal:
            try:
                data = self.socket.recv(32)
            except:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                connections.remove(self)
                break
            if data != "":
                print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))

                # for client in connections:
                #     if client.id != self.id:
                #         client.socket.sendall(data)
# This will be a static message containing station information in an ordered list being sent to client.       
multi_msg = [[0, 'Blinding Lights', 'This station will play blinding lights', '224.1.1.1', 5007, 'info_port-dont know', 44100],
[1, 'Blinding Lights', 'This station will play blinding lights', '225.1.1.1', 5008, 'info_port-dont know', 44100],
[2, 'Blinding Lights', 'This station will play blinding lights', '226.1.1.1', 5009, 'info_port-dont know', 44100]]
# this will convert the list to a string which then will be sent to the client as a encoded message
multi_str = str(multi_msg)
#Wait for new connections
def newConnections(socket):
    while True:
        sock, address = socket.accept()
        global total_connections
        connections.append(Client(sock, address, total_connections, "Name", True))
        connections[-1].start()
        print("New connection at ID " + str(connections[-1]))
        total_connections += 1
        sock.send(multi_str.encode())
        station = sock.recv(1024).decode()
        print(station)


# class Station1(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)

def station_n(M_CAST_GRP, M_CAST_PORT, song_path):
    BUFF_SIZE = 65536
    MULTICAST_TTL = 2
    MCAST_GRP = M_CAST_GRP
    MCAST_PORT = M_CAST_PORT
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, BUFF_SIZE)

    while(True):
        print("Hello")
        CHUNK = 1024*10
        wf = wave.open(song_path)
        p = pyaudio.PyAudio()
        # print('server listening at',("localhost", 5445),wf.getframerate())
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        input=True,
                        frames_per_buffer=CHUNK)

        data = None
        sample_rate = wf.getframerate()
        
        # msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
        # print('[GOT connection from]... ',client_addr,msg)
        # DATA_SIZE = math.ceil(wf.getnframes()/CHUNK)
        # DATA_SIZE = str(DATA_SIZE).encode()
        # print('[Sending data size]...',wf.getnframes()/sample_rate)
        # server_socket.sendto(DATA_SIZE,client_addr)
        # while True:
        
        cnt=0
        while True:
            
            data = wf.readframes(CHUNK)
            server_socket.sendto(data,(MCAST_GRP, MCAST_PORT))
            time.sleep(0.001) # Here you can adjust it according to how fast you want to send data keep it > 0
            # print(cnt)
            if cnt >(wf.getnframes()/CHUNK):
                break
            cnt+=1

            # break
        print('SENT...')            

def main():
    #Get host and port
    host = "localhost"
    port = 5432

    #Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    #Create new thread to wait for connections
    newConnectionsThread = threading.Thread(target = newConnections, args = (sock,))
    newConnectionsThread.start()
    song_paths = ["./../songs/lights.wav", "./../songs/excuses.wav", "./../songs/lights.wav"]
    # essentially the server will have some different stations with same functionality 
    # but different MCAST GRPS and different mcast ports
    station1Thread = threading.Thread(target=station_n, args = (multi_msg[0][3], multi_msg[0][4], song_paths[0]))
    station1Thread.start()
    #station2Thread = threading.Thread(target=station_n, args = (multi_msg[1][3], multi_msg[1][4], song_paths[1]))
    #station2Thread.start()
    #station3Thread = threading.Thread(target=station_n, args = (multi_msg[2][3], multi_msg[2][4], song_paths[2]))
    #station3Thread.start()

    
    
main()
