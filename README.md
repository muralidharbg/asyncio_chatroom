# asyncio_chatroom
terminal based chatroom application built using python's asyncio library 

To run:
On server machine: `python3 server.py`
On client machine/s: `python3 client.py`

The ip address of the server can be changed in the client.py file at line `connection_coro_obj = loop.create_connection(lambda: chatClient, '127.0.0.1', 8888)`

After the client connects with the server, the user will have to choose a username that is unique (server checks for the uniqueness). To quit, the user can type `q!` in the terminal.  
