from Client.connection_vent import *

# write your code in the following class
class User:
    def run(self):
        username = input('username: ')
        password = input('password: ')
        # Request:
        response = self.Requests.PostRequest('login', [username, password])
        print(response)

if __name__ == '__main__':
    conn = Connection('192.168.1.7', 'user')
    user = User(); user.Requests = conn
    user.run()