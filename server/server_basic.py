import socket
import threading
import wave
import time

host = "localhost"
port = 5432

# Variables for holding information about connections
connections = []
total_connections = 0

# Client class, new instance created for each connected client
# Each instance has the socket and address that is associated with items
# Along with an assigned ID and a name chosen by the client

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

    # Attempt to get data from client
    # If unable to, assume client has disconnected and remove him from server data
    # If able to and we get data back, print it in the server and send it back to every
    # client aside from the client that has sent it
    # .decode is used to convert the byte data into a printable string
    def run(self):
        while self.signal:
            try:
                data = self.socket.recv(32)
            except:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                connections.remove(self)
                break


# This will be a static message containing station information in an ordered list being sent to client.
multi_msg = [[0, 'Guitar Music', 'This station will play guitar music', '224.1.1.1', 5007, 'info_port-dont know', 44100],
             [1, 'Excuses', 'This station will play excuses',
                 '225.1.1.1', 5008, 'info_port-dont know', 44100],
             [2, 'General Music', 'This station will play general music', '226.1.1.1', 5009, 'info_port-dont know', 44100]]
# this will convert the list to a string which then will be sent to the client as a encoded message
multi_str = str(multi_msg)

def newConnections(socket):
    while True:  # infinite loop to accept clients
        sock, address = socket.accept()
        global total_connections
        connections.append(
            Client(sock, address, total_connections, "Name", True))
        connections[-1].start()
        print("New connection at ID " + str(connections[-1]))
        total_connections += 1
        # sending the client information regarding the stations and the songs being played on them as soon as it connects
        sock.send(multi_str.encode())

def station_n(M_CAST_GRP, M_CAST_PORT, song_path):
    BUFF_SIZE = 65536
    MULTICAST_TTL = 2
    MCAST_GRP = M_CAST_GRP
    MCAST_PORT = M_CAST_PORT
    # Creating a server socket to send data through UDP protocol
    server_socket = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Setting socket options for the server
    server_socket.setsockopt(
        socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

    while(True):
        CHUNK = 10240
        wf = wave.open(song_path)
        data = None
        cnt = 0
        while True:
            # Reading CHUNK sizes of data and sending them to the multicast address
            data = wf.readframes(CHUNK)
            server_socket.sendto(data, (MCAST_GRP, MCAST_PORT))
            # Here you can adjust it according to how fast you want to send data keep it > 0
            time.sleep(0.001)
            # Breaking the loop if no more chunks to be sent are remaining
            if cnt > (wf.getnframes()/CHUNK):
                break
            cnt += 1
        wf.close()


def main():
    # Creating a new TCP server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    # Create new thread to wait for connections
    newConnectionsThread = threading.Thread(
        target=newConnections, args=(sock,))
    newConnectionsThread.start()

    # songs for each station
    song_paths = ["./../songs/1.wav", "./../songs/2.wav", "./../songs/3.wav"]
    # The server has 3 base stations having different functionality
    # However, they will have MCAST GRPS and different mcast ports

    # start three threads - 1 for each station
    station1Thread = threading.Thread(target=station_n, args=(
        multi_msg[0][3], multi_msg[0][4], song_paths[0]))
    station1Thread.start()
    time.sleep(1)
    station2Thread = threading.Thread(target=station_n, args=(
        multi_msg[1][3], multi_msg[1][4], song_paths[1]))
    station2Thread.start()
    time.sleep(1)
    station3Thread = threading.Thread(target=station_n, args=(
        multi_msg[2][3], multi_msg[2][4], song_paths[2]))
    station3Thread.start()
    time.sleep(1)

    # Wait for all threads to join
    station1Thread.join()
    station2Thread.join()
    station3Thread.join()
    newConnectionsThread.join()
    # Close the TCP socket
    sock.close()


main()
