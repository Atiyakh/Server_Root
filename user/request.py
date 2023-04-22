# write your requests in the following class
class RequestsGenerator:
    def signup(self, conn, username, password):
        self.SendProto(conn, {
            'username': username,
            'password': password
        })
        response = self.RecvSignal(conn)
        if response: return 'Your account has been created...'
        else: return 'Access denied!'
    def login(self, conn, username, password):
        self.SendProto(conn, {
            'username': username,
            'password': password
        })
        response = self.RecvSignal(conn)
        if response: return 'Accessed successfully!'
        else: return 'Access denied!'
