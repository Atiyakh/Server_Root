from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
from request import RequestsGenerator
from socket import *
import base64, ssl

class RSA_Algorithm:
    def slice(self, data, num):
        d = [data[num*i:num*(i+1)] for i in range(int(len(data)/num))]
        completance = [data[num*int(len(data)/num):]]
        if completance not in [[''], [b''], []]: d += completance
        return d

    def generateKeys(self):
        key = RSA.generate(2048)
        private_key = key.exportKey()
        public_key = key.publickey().exportKey()
        return public_key, private_key
    
    def encrypt(self, plain_text, public_key):
        loaded_key1 = RSA.importKey(public_key)
        cipher = PKCS1_v1_5.new(loaded_key1)
        plain_list = self.slice(plain_text, 245)
        cipher_list = [base64.b64encode(cipher.encrypt(i)) for i in plain_list]
        return b''.join(cipher_list)
    
    def decrypt(self, cipher_text, private_key):
        loaded_key = RSA.importKey(private_key)
        cipher = PKCS1_v1_5.new(loaded_key)
        n = Random.new().read(int(15/SHA.digest_size))
        cipher_list = self.slice(cipher_text, 344)
        plain_list = [cipher.decrypt(base64.b64decode(i), n) for i in cipher_list]
        return b''.join(plain_list)

class Connection:
    def __init__(self, ip, entity):
        self.IP = ip; self.entity = entity
        self.Requests = RequestsGenerator()
        self.Requests.RecvProto = self.RecvProto
        self.Requests.SendProto = self.SendProto
        self.Requests.RecvSignal = self.RecvSignal
        self.Requests.SendSignal = self.SendSignal
    # Requests section:
    def PostRequest(self, req, args):
        self.createConnection()
        self.conn.send(req.encode('utf-8'))
        if int(self.conn.recv(1)):
            response = self.Requests.__getattribute__(req)(self.conn, *args)
            self.conn.close(); return response
        else: raise ConnectionError("The request you posted is not defined")
    # Actions section:
    def connectionRefused(self):
        print('Server cannot be reached!') # FIXME
    ## Don't edit the code below unless you know what you're doing
    def createConnection(self):
        try:
            routerConnection = socket(AF_INET, SOCK_STREAM)
            routerConnection.connect((self.IP, 80))
            self.HOST = (self.IP, int(routerConnection.recv(1024)))
            self.conn = socket(AF_INET, SOCK_STREAM)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self.encrypted_client_socket = context.wrap_socket(self.conn, server_hostname=self.IP)
            self.encrypted_client_socket.connect(self.HOST)
            self.encrypted_client_socket.send(self.entity.encode('utf-8'))
            if int(self.encrypted_client_socket.recv(1)):return 1
            else:return 0
        except ConnectionRefusedError:
            self.connectionRefused()
            self.createConnection()

    def SendProto(self, conn, d):
        # send dictionary lingth:
        if conn.recv(1) == chr(0).encode('utf-8'):
            conn.send(len(d.keys()).__str__().encode('utf-8'))
            conn.recv(1) # Synchronizer
        # looging through the whole thing:
        for dic in d.keys():
            # Define Requerments:
            key = dic; data = d[dic]
            dtype = type(d[dic]).__name__
            # send Key & Type:
            if conn.recv(1) == chr(1).encode('utf-8'): conn.send(key.encode('utf-8'))
            if conn.recv(1) == chr(2).encode('utf-8'): conn.send(dtype.encode('utf-8'))
            ## Slice & Send:
            v = d[dic]
            # Encoding process:
            if type(v).__name__ == 'bytes': value = v
            elif type(v).__name__ == 'str': value = v.encode('utf-8')
            elif type(v).__name__ == 'int': value = v.__str__().encode('utf-8')
            else: value = str(v).encode('utf-8')
            # sending
            conn.recv(1)
            conn.sendall(value)
            conn.recv(1)

    def RecvProto(self, conn, buffersize=1024, dump=True):
        # recv dictionary lingth:
        conn.send(chr(0).encode('utf-8'))
        length = int(conn.recv(1024))
        conn.send(chr(0).encode('utf-8'))
        # Getting the dictionary data:
        d = {}
        for dic in range(length):
            # receive Key & Type:
            conn.send(chr(1).encode('utf-8'))
            key = conn.recv(1024).decode('utf-8')
            conn.send(chr(2).encode('utf-8'))
            dtype = conn.recv(1024).decode('utf-8')
            ## Receive the value fragments and Reassemble them:
            # Receiving data:
            conn.send(b'0')
            data = []
            while True:
                datum = conn.recv(buffersize)
                if not len(datum) < buffersize:
                    data.append(datum)
                else: 
                    data.append(datum)
                    break
            conn.send(b'0')
            v = b''.join(data)
            # Decoding:
            if dtype == 'bytes': value = v
            elif dtype == 'str': value = v.decode('utf-8')
            elif dtype == 'int': value = int(v)
            else: value = v.decode('utf-8')
            d[key] = value
        if dump: return d
        else: conn.__class__.payload = d

    def RecvSignal(sekf, conn):
        msg = conn.recv(1024)
        return int(msg.decode('utf-8'))

    def SendSignal(self, conn, num):
        if isinstance(num, int):
            msg = conn.send(num.__str__().encode('utf-8'))
        else:
            raise TypeError(f'Signal should be an intger not {type(num)}')
