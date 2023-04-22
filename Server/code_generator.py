import os, socket

data = {}

data['connection_vent.py'] = '''from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
from request import RequestsGenerator
from socket import *
import base64, sys

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
            self.PORT = int(routerConnection.recv(1024))
            self.conn = socket(AF_INET, SOCK_STREAM)
            self.conn.connect((self.IP, self.PORT))
            self.conn.send(self.entity.encode('utf-8'))
            if int(self.conn.recv(1)):return 1
            else:return 0
        except ConnectionRefusedError:
            self.connectionRefused()
            self.createConnection()

    def SendProto(self, conn, d):
        Slice = lambda bs, data: [d[bs*i:bs*(i+1)] for i in range(int(len(d)/bs))] + [d[int(len(d)/bs)*5:]]
        # RSA:
        if conn.recv(1) == b'1': secure = True
        else: secure = False
        if secure:conn.send(b'0'); public_key = conn.recv(10_000)
        # send dictionary lingth:
        if conn.recv(1) == chr(0).encode('utf-8'):
            conn.send(len(d.keys()).__str__().encode('utf-8'))
            conn.recv(1) # Synchronizer
        # looging through the whole thing:
        RSA = RSA_Algorithm()
        for dic in d.keys():
            # Define Requerments:
            dtype = type(d[dic]).__name__
            if secure: 
                key = RSA.encrypt(dic.encode('utf-8'), public_key)
                if not isinstance(d[dic], bytes):
                    d[dic] = str(d[dic]).encode('utf-8')
                d[dic] = RSA.encrypt(d[dic], public_key)
            else: key = dic
            data = d[dic]
            # send Key & Type:
            if not isinstance(key, bytes): key = key.encode('utf-8')
            if conn.recv(1) == chr(1).encode('utf-8'): conn.send(key)
            if conn.recv(1) == chr(2).encode('utf-8'): conn.send(dtype.encode('utf-8'))
            ## Slice & Send:
            v = d[dic]
            # Encoding process:
            if type(v).__name__ == 'bytes': value = v
            elif type(v).__name__ == 'str': value = v.encode('utf-8')
            elif type(v).__name__ == 'int': value = v.__str__().encode('utf-8')
            else: value = str(v).encode('utf-8')
            # Sending the data size:
            conn.recv(1)
            conn.send(len(value).__str__().encode('utf-8'))
            # sending:
            conn.recv(1)
            conn.sendall(value)
            conn.recv(1)
        print("[SERVER][DATA-MANAGEMENT-PROTOCOL] Package has been sent to ", conn.getpeername(), f"Size:{sys.getsizeof(d)}")

    #  Custom Receiving protocol
    def RecvProto(self, conn, buffersize=1024, dump=True, secure=True):
        if secure:
            conn.send(b'1')
            # create RSA peer keys:
            RSA = RSA_Algorithm()
            public_key, private_key = RSA.generateKeys()
            # send the public key:
            conn.recv(1); conn.send(public_key)
        else: conn.send(b'0')
        # recv dictionary lingth:
        conn.send(chr(0).encode('utf-8'))
        length = int(conn.recv(1024))
        conn.send(chr(0).encode('utf-8'))
        # Getting the dictionary data:
        d = {}
        for dic in range(length):
            # receive Key & Type:
            conn.send(chr(1).encode('utf-8'))
            key = conn.recv(1024)
            if secure: key = RSA.decrypt(key, private_key)
            try: key = key.decode('utf-8')
            except UnicodeDecodeError: pass
            conn.send(chr(2).encode('utf-8'))
            dtype = conn.recv(1024).decode('utf-8')
            ## Receive the value fragments and Reassemble them:
            # Receiving data:
            conn.send(b'0')
            SIZE = int(conn.recv(1024))
            conn.send(b'0')
            v = b''
            while (v.__len__() != SIZE):
                v += conn.recv(buffersize)
            conn.send(b'0')
            if secure: v = RSA.decrypt(v, private_key)
            # Decoding:
            if dtype == 'bytes': value = v
            elif dtype == 'str': value = v.decode('utf-8')
            elif dtype == 'int': value = int(v)
            else: value = v.decode('utf-8')
            d[key] = value
        print("[SERVER][DATA-MANAGEMENT-PROTOCOL] Package has been Received from ", conn.getpeername(), f"Size:{sys.getsizeof(d)}")
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
'''.encode('utf-8')

data['main.py'] = lambda entity: f'''from Client.connection_vent import *

# write your code in the following class
class {entity.capitalize()}:
    def run(self):
        pass

if __name__ == '__main__':
    conn = Connection('{socket.gethostbyname(socket.gethostname())}', '{entity.lower()}')
    {entity.lower()} = {entity.capitalize()}(); {entity.lower()}.Requests = conn
    user.run()'''.encode('utf-8')

data['Entity.py'] = lambda entity: f'''# Requests and Server handling functions:
class {entity.capitalize()}:
    def request(self, conn):
        pass
'''.encode('utf-8')

data['request.py'] = '''# write your requests in the following class
class RequestsGenerator:
    def request(self, conn):
        return 0
'''.encode('utf-8')

def editDict(data, dict, key, val):
    datum = data[data.find(dict)+len(dict):]
    fragment = datum[:datum.find('}')]
    segment = fragment[:fragment.find('{')+1] + f'\n            {key}: {val},' + fragment[fragment.find('{')+1:]
    data = data[:data.find(dict)+len(dict)] + segment + data[data.find(fragment)+len(fragment):]
    return data

def editProcedure(name, dir):
    f = open(os.path.join(dir, 'ServerSide', 'Server', 'procedure.py'), 'r')
    data = f.read(); f.close()
    data = f'from .Entities.{name.lower()} import {name.capitalize()}\n' + data
    index = 'loadConnectionProtocols(server)'
    num = data.find(index) + len(index)
    data = data[:num] + f'\n        self.{name.lower()} = {name.capitalize()}(); loadProtocols(self, self.{name.lower()})' + data[num:]
    data = editDict(data, 'self.structure', f"'{name.lower()}'", f"self.{name.lower()}")
    f = open(os.path.join(dir, 'ServerSide', 'Server', 'procedure.py'), 'w')
    f.write(data); f.close()
data['procedure.py'] = editProcedure

def GenerateEntity(name):
    try:
        name = name.lower()
        dir = os.path.dirname(os.getcwd())
        os.mkdir(os.path.join(dir, 'ClientSide', name))
        # Client > connection.py, __init__.py
        os.mkdir(os.path.join(dir, 'ClientSide', name, 'Client'))
        open(os.path.join(dir, 'ClientSide', name, 'Client', '__init__.py'), 'x')
        file = open(os.path.join(dir, 'ClientSide', name, 'Client', 'connection_vent.py'), 'wb')
        file.write(data["connection_vent.py"]); file.close()
        # Client > main.py
        file = open(os.path.join(dir, 'ClientSide', name, 'main.py'), 'wb')
        file.write(data["main.py"](name)); file.close()
        # Server > Entities > {Entity name}.py
        file = open(os.path.join(dir, 'ServerSide', 'Server', 'Entities', f"{name}.py"), 'wb')
        file.write(data["Entity.py"](name)); file.close()
        data['procedure.py'](name, dir)
        # Client > request.py
        file = open(os.path.join(dir, 'ClientSide', name, 'request.py'), 'wb')
        file.write(data["request.py"]); file.close()
        print(f'[SERVER][Code-Generator] "{name}" code has been generated')
    except:
        print(f'[SERVER][CodeGenerator] Cannot generate "{name}"')
    
