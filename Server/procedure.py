from .Entities.user import User
from .crypto_vent import RSA_Algorithm
import sys

## Connection Tools:
#  Custom Sending protocol:
def SendProto(conn, d):
    # send dictionary lingth:
    if conn.recv(1) == chr(0).encode('utf-8'):
        conn.send(len(d.keys()).__str__().encode('utf-8'))
        conn.recv(1) # Synchronizer
    for dic in d.keys():
        key = dic; data = d[dic]
        dtype = type(d[dic]).__name__
        # send Key & Type:
        if conn.recv(1) == chr(1).encode('utf-8'): conn.send(key.encode('utf-8'))
        if conn.recv(1) == chr(2).encode('utf-8'): conn.send(dtype.encode('utf-8'))
        v = d[dic]
        # Encoding process:
        if type(v).__name__ == 'bytes': value = v
        elif type(v).__name__ == 'str': value = v.encode('utf-8')
        elif type(v).__name__ == 'int': value = v.__str__().encode('utf-8')
        else: value = str(v).encode('utf-8')
        # sending
        conn.recv(1); conn.sendall(value); conn.recv(1)
        print("[SERVER][DATA-MANAGEMENT-PROTOCOL] Package has been sent to ", conn.getpeername(), f"Size:{sys.getsizeof(d)}")

def RecvProto(conn, buffersize=1024, dump=False):
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
    print("[SERVER][DATA-MANAGEMENT-PROTOCOL] Package has been Received from ", conn.getpeername(), f"Size:{sys.getsizeof(d)}")
    if dump: return d
    else: conn.__class__.payload = d

def RecvSignal(conn):
    msg = conn.recv(1024)
    return int(msg.decode('utf-8'))

def SendSignal(conn, num):
    if isinstance(num, int):
        msg = conn.send(num.__str__().encode('utf-8'))
    else:
        raise TypeError(f'Signal should be an intger not {type(num)}')

class loadConnectionProtocols:
    def __init__(self, server):
        server.SendProto = SendProto
        server.RecvProto = RecvProto
        server.SendSignal = SendSignal
        server.RecvSignal = RecvSignal

def loadProtocols(mainclass, entity):
    entity.Server = mainclass.server
    # load connection protocols
    entity.RecvProto = RecvProto
    entity.SendProto = SendProto
    # load connection signals
    entity.RecvSignal = RecvSignal
    entity.SendSignal = SendSignal
    # database & archive & crypto
    entity.Archive = mainclass.server.archive
    entity.DB = mainclass.server.DB
    entity.Cryptography = mainclass.server.Crypto

# main <——> porocedure Link:
class Operations:
    def __init__(self, server):
        self.server = server
        loadConnectionProtocols(server)
        self.user = User(); loadProtocols(self, self.user)
        self.structure = {
            'user': self.user,
        }
