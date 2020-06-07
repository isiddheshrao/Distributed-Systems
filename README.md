# Distributed-Systems
Consists of Projects done in Distributed Systems. Includes a Client Server Chat System Based on Python 3
Steps for Running and Compiling the program
Step 1: Compile and run the Server.py file from command prompt.  Server UI Will start The Server UI will dynamically show, and update number of clients connected, Log of total usernames in the session and currently active usernames.
Step 2: Compile and run the Client.py file from command prompt. Client UI Will start
Step 3: Enter Unique Client username on the client UI prompt
Step 4: The Username if Unique, the client will login and options will be shown options for 1-1, 1-n, 1-all and check message. Else, if the username exists and is currently active, the client will be asked to enter the username again. 
Step 5: Based on the input, the client will be asked to enter recipient name & Message which will be stored in the recipient’s persistent message queue on the server side. Check message will show the client if he has any messages in the queue along with sender name and message timestamp.
Step 6: The client will return to the options menu after one complete iteration. To Quit, enter ‘bye’ in the input box which will close the client UI.

Notes:
•	Client & Server run through their respective UI.
•	Not more than 3 clients can run simultaneously
•	Clients must provide Unique username to start chat server.
•	1-to-1, 1-to-n & 1-to-all and Check messages work.
•	Server handles disconnections from client.
•	Server handles client usernames and keeps requesting new username if the username is not unique.
•	Server has a list to store all client’s usernames and currently active usernames.
•	Server dumps a dictionary on exit which stores username and its message queue. Upon next start. It checks if dump file exists and loads it.
