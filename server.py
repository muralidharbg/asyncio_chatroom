import asyncio
# from chat_protocol import ChatProtocol
import json

class ChatServer(asyncio.Protocol):

    user_transports = {}
    users = []
    temp_id = 0
    
    def connection_made(self, transport):
        temp_username = 'temp_user' + str(ChatServer.temp_id)
        
        ChatServer.user_transports[temp_username] = transport
        
        temp_data = {'topic' : 'temp_username', 'message': temp_username}
        transport.write(json.dumps(temp_data).encode('utf-8'))

        ChatServer.temp_id += 1

    def data_received(self, data):
        str_data = data.decode()
        dict_data = json.loads(str_data)
        # print(data)
        if dict_data['topic'] == 'register':
            if not self.user_exists(dict_data['message']):
                username = dict_data['message']
                self.register(username)
                ChatServer.user_transports[username] = ChatServer.user_transports.pop(dict_data['temp_username'])
                # ChatServer.user_transports[username].write(json.dumps({'topic': 'register', 'status': 'success', 'message': username}).encode('utf-8'))
                response_data = {'topic': 'register', 'status': 'success', 'message': username}
                self.send_data(ChatServer.user_transports[username], response_data)
            else:
                response_data = {'topic': 'register', 'status': 'user_exists', 'temp_username': dict_data['temp_username']}
				# ChatServer.user_transports[dict_data['temp_username']].write(json.dumps({'topic': 'register', 'status': 'user_exists', 'temp_username': dict_data['temp_username']}).encode('utf-8'))
                self.send_data(ChatServer.user_transports[dict_data['temp_username']], response_data)
        elif dict_data['topic'] == 'msg' and self.user_exists(dict_data['username']):
            if dict_data['message'] == 'q!':
                transport = ChatServer.user_transports[dict_data['username']]
                del ChatServer.user_transports[dict_data['username']]
                ChatServer.users.remove(dict_data['username'])
                transport.close()
            else:
                for transport in ChatServer.user_transports.values():
                    # transport.write(data)
                    self.send_data(transport, dict_data)
        else:
            print("something went wrong!")

    def register(self, username):
        ChatServer.users.append(username)

    def user_exists(self, username):
        return username in ChatServer.users

    def send_data(self, transport, data):
    	transport.write(json.dumps(data).encode('utf-8'))

    def connection_lost(self, exc):
    	print("connection lost")

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(ChatServer, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()