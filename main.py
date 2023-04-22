# TCP Server V3:
3/2/2023

from socket import *
from threading import Thread
import Server, os, ssl

def Thread_(target, args=[]):
    thread = Thread(target=target, args=args)
    thread.start()

def cls():
    x = os.system('cls')

class TCP_Server:
    # Server Initiators / Server Runners:
    def closeConnection(self, conn, port, addr):
        print(f"[SERVER][PORT:{port}] Connection {addr} Closed...")
        self.portMap = self.portMap[:self.PORT.index(port)] + [self.portMap[self.PORT.index(port)] - 1] + self.portMap[self.PORT.index(port)+1:]
        self.connectionMap.pop(str(conn.getpeername()))
        conn.close()

    def manageIndividual(self, conn, addr, port):
        self.portMap = self.portMap[:self.PORT.index(port)] + [self.portMap[self.PORT.index(port)] + 1] + self.portMap[self.PORT.index(port)+1:]
        while True:
            try:
                # Requests destributing system v2:
                function = conn.recv(1024).decode('utf-8')
                entityHandler = self.operations.structure[conn.category]
                if function == '' or function == b'':
                    self.closeConnection(conn, port, addr)
                    break
                elif function in dir(entityHandler):
                    conn.send(b'1')
                    entityHandler.__getattribute__(function)(conn)
                else: conn.send(b'0')
            except ConnectionResetError as e:
                self.closeConnection(conn, port, addr)
                break

    def runSocket(self, server, port):
        server.listen()
        # Wrap the socket with TLS encryption
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('server_certificate.pem', 'server_private_key.pem')
        encrypted_server_socket = context.wrap_socket(server, server_side=True)
        # Waiting for connections
        while True:
            conn, addr = encrypted_server_socket.accept()
            category = conn.recv(1024).decode('utf-8')
            if category in self.operations.structure.keys():
                conn.__class__.category = category
                conn.send(b'1')
            else: conn.send(b'0'); continue
            self.connectionMap[str(conn.getpeername())] = conn
            print(f"[SERVER][PORT:{port}] New Connection   ip:{addr}   entity::{category}")
            Thread_(target=self.manageIndividual, args=([conn, addr, port]))

    def startActiveSockets(self):
        for port in self.PORT:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.bind((self.HOST, port))
            self.activeSockets.append(sock)
        for sock in range(len(self.activeSockets)):
            Thread_(target=self.runSocket, args=([self.activeSockets[sock], self.PORT[sock]]))
        print(f"[SERVER][PORT:({min(self.PORT)}-{max(self.PORT)})] real-time connection server sockets are up for connections...")

    def startRouter(self):
        def main():
            self.router = socket(AF_INET, SOCK_STREAM)
            self.router.bind((self.HOST, self.PORT_R))
            getNextPort = lambda: self.PORT[self.portMap.index(min(self.portMap))]
            while True:
                self.router.listen(1)
                self.router.accept()[0].send(getNextPort().__str__().encode('utf-8'))
        Thread_(target=main)

    def startUp(self):
        self.startRouter()
        self.startActiveSockets()
    
    def ActiveConsole(self):
        def main():
            print("[SERVER][Console] Active Console  <ON>")
            while True:
                try:exec(input(), globals())
                except Exception as e: print(e)
        Thread_(main)

    def SQL_Database(self, db_name):
        self.DB = Server.sql_db(db_name)
        Server.UpdateSchema = self.UpdateSchema
        Server.DB = self.DB
        self.archive = Server.Archive(self)
        print("[SERVER][ARCHIVE] Archive Environment has been set up...")
        print(f'''[SERVER][SQL-DATABASE] "{db_name}" has been Initiated {str([i[0] for i in self.DB.names]).replace("'", '')}''')

    def UpdateSchema(self, db_name):
        Server.drop_db(db_name)
        Server.create_db(db_name)
        Server.loading_tbls(db_name)
        print(f'[SERVER][SQL-DATABASE] "{db_name}" Schema has been updated...')

    # Server Configurations:
    def RunServer(self):
        global this; this = self
        ## Server Vars:
        self.portMap = ([0] * len(self.PORT))
        self.activeSockets = []
        self.Crypto = Server.Crytography
        self.operations = Server.Operations(self)
        self.connectionMap = {}
        ## Server Activation:
        print("[SERVER] Initializing...")
        self.startUp()
        print("[SERVER] Server has been successfully Initialized...")

if __name__ == '__main__':
    server = TCP_Server()
    server.HOST = gethostbyname(gethostname())
    server.PORT = range(8000, 8011)
    server.PORT_R = 80
    # server.UpdateSchema('Project_DB_1')
    server.SQL_Database('Project_DB_1')
    server.ActiveConsole()
    server.RunServer()
