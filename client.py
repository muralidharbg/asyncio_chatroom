import asyncio
import json
import signal

class ChatClient(asyncio.Protocol):
    def __init__(self, loop):
        self._loop = loop
        self._transport = None
        self.buffer = []
        self._username = None
        self.temp_username = None
        self.quit = False
        self.server_active = False
    
    def connection_made(self, transport):
        self._transport = transport
        self.server_active = True

    def data_received(self, data_received):
        try:
            str_data = data_received.decode()
            dict_data = json.loads(str_data)
            # print(dict_data)
        except Exception as e:
            print("Exception occured of type ", type(e))
            print(e)
        else:
            if not self.is_loggedin():
                if dict_data['topic'] == 'temp_username':
                    self.temp_username = dict_data['message']
                elif dict_data['topic'] == 'register' and dict_data['status'] == 'success':
                    self.set_username(dict_data['message'])
                    self.temp_username = None
                    print("Welcome to the chat room. Type 'q!' to quit.")
                elif dict_data['topic'] == 'register' and dict_data['status'] == 'user_exists':
                    self.temp_username = dict_data['temp_username']
                    print("Username you entered already exists")
            elif self.is_loggedin():
                    print('\n' + dict_data["username"] + ": " + dict_data["message"])
                    print('--->')

    def connection_lost(self, exc):
        print('The server closed the connection')
        self._username = None
        self.temp_username = None
        self.server_active = False
        self.logout()

    def send_data(self, data):
        if self.server_active == True:
            if data['topic'] == 'msg':
                data['username'] = self._username
            elif data['topic'] == 'register' and not self.is_loggedin():
                data['temp_username'] = self.temp_username
                self.temp_username = None

            self._transport.write(json.dumps(data).encode('utf-8'))

    def set_username(self, username):
        self._username = username

    def is_loggedin(self):
        return self._username

    def logout(self):
        self.quit = True

    def close_connection(self):
        self._transport.close()

async def chatConsole(loop, chatClient):
    prompt = False
    
    while True:
        if chatClient.quit == True:
            break
        elif chatClient.is_loggedin():
            input_param = "--->"
            dict_data = {'topic' : 'msg'}
            prompt = True
        elif chatClient.temp_username != None:
            input_param = "Enter username: \n--->"
            dict_data = {'topic' : 'register'}
            prompt = True
        else:
            # give control to chatclient to recieve data - in the case request is sent to server to register username 
            await asyncio.sleep(0.5)

        try:
            if prompt:
                user_input = await loop.run_in_executor(None, input, input_param)

                if user_input == 'q!':
                    print("Quitting...")
                    chatClient.logout()
                
                dict_data['message'] = user_input
                chatClient.send_data(dict_data)
                prompt = False
                
        except asyncio.CancelledError:
            print('cancelled')
            chatClient.close_connection()
            break
            
    loop.stop()
    return

def singal_handler():
    for task in asyncio.Task.all_tasks():
        task.cancel()

def main():    
    loop = asyncio.get_event_loop()
    # loop.set_debug(1)

    chatClient = ChatClient(loop)
    connection_coro_obj = loop.create_connection(lambda: chatClient, '127.0.0.1', 8888)

    try:
        loop.run_until_complete(connection_coro_obj)    
    except ConnectionRefusedError as e:
        print(e)
    else:
        # try:
        chatTask = asyncio.ensure_future(chatConsole(loop, chatClient))

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, singal_handler)

        loop.run_forever()
        # except KeyboardInterrupt as e:
            # print("KeyboardInterrupt")
        #     chatTask.cancel()
        #     chatTask.exception()
            # singal_handler()
            # print("cancelled")
        # except asyncio.CancelledError as e:
            # print("Exception occured of type: " + type(e))
        # finally:
        
        loop.close()

if __name__ == '__main__':
    main()