from Crypto.Cipher import AES, PKCS1_v1_5
from hashlib import sha512, sha256, sha1
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto import Random
import base64

# Hashing Algorithms in use:
class Hashing_Algorithms:
    def Sha512(self, text:str):
        bytes_ = sha512(text.encode('utf-8'))
        hash = bytes_.hexdigest()
        return hash

    def Sha256(self, text):
        bytes_ = sha256(text.encode('utf-8'))
        hash = bytes_.hexdigest()
        return hash

    def Sha1(self, text):
        bytes_ = sha1(text.encode('utf-8'))
        hash = bytes_.hexdigest()
        return hash

# Symmetric encryption algorithms in use:
class AES_Algorithm:
    def Encrypt(self, data):
        block_size = 16
        padding = b"*"
        p = lambda s:s + (block_size-len(s)%block_size)*padding
        KEY = Random.new().read(16)
        IV = Random.new().read(16)
        E = AES.new(KEY, AES.MODE_CBC, IV)
        Encrypted_message = base64.b64encode(IV+ E.encrypt(p(data)))
        return Encrypted_message, KEY

    def Decrypt(self, KEY, Encrypted_message):
        Encrypted_Data = base64.b64decode(Encrypted_message)
        IV_ = Encrypted_Data[:16]
        Encrypted_message_ = Encrypted_Data[16:]
        print(len(IV_), len(Encrypted_message_))
        D = AES.new(KEY, AES.MODE_CBC, IV_)
        plain_text = D.decrypt(Encrypted_message_).rstrip(b"*")
        return plain_text

# Asymmetric encryption algorithms in use:
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

class Crytography:
    def __init__(self):
        self.AES = AES_Algorithm()
        self.RSA = RSA_Algorithm()
        self.Hash = Hashing_Algorithms()
