from base64 import b64decode, b64encode
from sqlite3 import connect
from socket import *
import time

class KMS_Server:
    def HandlingConnection(self):
        while True:
            code = int(self.conn.recv(1))
            if code == 1: # Insert
                AES_key = b64encode(self.conn.recv(1024))
                self.conn.send(b'0'); id_ = int(self.conn.recv(1024))
                self.cur.execute(f"INSERT INTO key VALUES({id_}, {AES_key}, {time.time()})")
                self.conn.send(b'0')
                print("[KMS] Iserting new cryptographic key has been implemented")
            elif code == 2: # Query
                id_ = int(self.conn.recv(1024))
                self.cur.execute(f"SELECT key FROM key WHERE id={id_};")
                key = b64decode(self.cur.fetchone()[0])
                self.conn.send(key)
                print("[KMS] The server has requested a cryptographic key")
            elif code == 3: # Delete
                id_ = int(self.conn.recv(1024))
                self.cur.execute(f"DELETE FROM key WHERE id={id_};")
                self.conn.send(b'1')
                print("[KMS] The server has deleted a key")

    def __init__(self):
        # sqlite3
        self.DB = connect('database.sqlite3')
        self.cur = self.DB.cursor()
        # socket
        self.KMS_PORT = 1688
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('', self.KMS_PORT))
        while True:
            self.sock.listen(1)
            conn, addr = self.sock.accept()
            if addr[0] == gethostbyname(gethostname()): break
            else: conn.close()
        self.conn = conn
        print('[KMS] connected to server...')

if __name__ == '__main__':
    KMS = KMS_Server()
    KMS.HandlingConnection()
