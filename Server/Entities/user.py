# Requests and Server handling functions:
class User:
    def login(self, conn):
        payload = self.RecvProto(conn, secure=False)
        query = self.DB.Check('accounts', {
            'username': payload['username'],
            'password': self.Cryptography().Hash.Sha512(payload['password'])
        })
        if query: self.SendSignal(conn, 1)
        else: self.SendSignal(conn, 0)
    def signup(self, conn):
        payload = self.RecvProto(conn, secure=False)
        query = self.DB.Check('accounts', {'username': payload['username']})
        if not query:
            self.DB.Insert('accounts', {
                'username': payload['username'],
                'password': self.Cryptography().Hash.Sha512(payload['password'])
            })
            self.SendSignal(conn, 1)
        else: self.SendSignal(conn, 0)
