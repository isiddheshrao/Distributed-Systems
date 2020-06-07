
import datetime
from queue import Queue
import socket
import tkinter as tk
import sys
import threading
from _thread import *
import os
from os import path
import dill



#CREATING CODE FOR UI

#FUNCTION TO HANDLE QUIT
def QUIT(top):
    top.destroy()
    #https://www.datacamp.com/community/tutorials/pickle-python-tutorial
    dill.dump(USER_QUEUES,open('USERNAME_QUEUES.pkl','wb'))  #DUMP A FILE ON CURRENT PATH IF SERVER IS QUIT (For Persistency) AND LOAD IT WHEN SERVER STARTS
    sys.exit(1)

#STATUS OF CLIENTS ON UI
#https://www.python-course.eu/tkinter_labels.php
def MAIN_DISPLAY(NULL):
    top = tk.Tk()
    top.title("Server")
    main = tk.Canvas(top, height= 500,width= 600)
    main.pack()
    frame = tk.Frame(main)
    frame.place(relwidth = 1, relheight= 0.9)
    Label1 = tk.Label(frame)
    Label1.pack()
    title_label1 = tk.Label(frame, justify=tk.LEFT, padx = 10)
    title_label1.pack(side = "left")
    title_label1.config(text = "Total Usernames in this Session ->")
    title_label2 = tk.Label(frame, justify=tk.RIGHT, padx = 10)
    title_label2.pack(side = "right")
    title_label2.config(text = "<- Active Usernames in this Session")
    Label2 = tk.Label(frame, justify=tk.LEFT, padx = 10)
    Label2.pack(side ="left")
    Label3 = tk.Label(frame, justify=tk.RIGHT, padx = 10)
    Label3.pack(side ="right")
    UPDATE(Label1,top)
    SHOW_LIST(top, Label2, Label3)
    Button1 = tk.Button(frame, text = 'Quit', command = lambda: QUIT(top))
    Button1.pack()
    top.mainloop()

#CODE TO UPDATE CLIENT STATUS UI IN EVERY 1000MS
def UPDATE(Label1,top):
    global USER_STATUS
    global count
    if USER_STATUS == True:
        PRINT_UI = str(str(count) + " Client(s) Connected")
        Label1.config(text = PRINT_UI)
    else:
        Label1.config(text = "No Client Connected")
    top.after(1000, lambda: UPDATE(Label1, top))

#CODE TO UPDATE USERNAMES AND ACTIVE USERNAMES AND UPDATE EVERY 1000MS
def SHOW_LIST(top, label2, Label3):
    label2.config(text = USERNAMES)
    Label3.config(text = ACTIVE_USERNAMES)
    top.after(1000, lambda: SHOW_LIST(top, label2, Label3))


#CODE FOR THREAD DELETION
def THREAD_DEL():
    global STOP_CLIENT_THREAD
    global count
    STOP_CLIENT_THREAD = True
    count -=1 #UI UPDATE
    newclientthread.join()  #TO CHECK AND DELETE THREAD CONTEXT



#CODE TO MAKE QUEUE FOR NEW USERNAMES AND NOT FOR EXISTING ONES 
def MAKE_QUEUE(userdata): 
    if userdata in USERNAMES:
        if USER_QUEUES.get(userdata):
            Client_Queue = USER_QUEUES.get(userdata)
        else:
            Client_Queue = Queue()
            USER_QUEUES[userdata] = Client_Queue
    return Client_Queue

    

#---------------MAIN CODE---------------------------------#



class ClientThread(threading.Thread):
    def __init__(self, ClientAddr, ClientSock):
        threading.Thread.__init__(self)
        self.csocket = ClientSock
        print("New Client Connection Added from address: ", ClientAddr)
    
    
    #CREATING FUNCTION FOR POLLING/TIMESTAMPING MESSAGES
    def message_polling(self,input):
        reqdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        MAIN_MESSAGE = "Date: " + reqdate + "\t" + " Message: " + input + "\n"
        return MAIN_MESSAGE
    
    #CREATING COMPOSE AND CHECK MESSAGE FUNCTIONS
    def compose_message(self, userdata):
               
        recipient = self.csocket.recv(2048) # RECV 3 CLIENT MESSAGING 1-1 RECIPIENT NAME
        recipient = recipient.decode()
        print("Recipient is: ", recipient)
        message_in = self.csocket.recv(2048) #RECV 4 CLIENT MESSAGING 1-1
        message_in = message_in.decode()
        message_in = message_in + "\tSent From: "+ userdata
        message_in = self.message_polling(message_in) #ADDING TIMESTAMP
        print("Message is: ", message_in)
        # STORE MESSAGE IN QUEUE
        if recipient in USERNAMES:
            if recipient in USER_QUEUES.keys():
                MESSAGE_QUEUE = USER_QUEUES[recipient]
                MESSAGE_QUEUE.put(message_in)
                USER_QUEUES[recipient] = MESSAGE_QUEUE
                print("Message stored for: ", recipient," Message: ", message_in, " Size of Queue: ", MESSAGE_QUEUE.qsize())
            else:
                print("Recipient Doesn't Exist")
    
    #CREATING 1-N COMPOSE MESSAGE FUNCTION (ERROR IN LOOP)
    def compose1n(self, userdata):
        
        RECIPIENTS = []
        num_recipients = int(str(self.csocket.recv(2048),'utf-8')) #RECV 3 TOTAL CLIENT NUMBER
        for i in range(0, num_recipients):
            recipient = self.csocket.recv(2048) #RECV 4 CLIENT RECIPIENTS 
            recipient = recipient.decode()
            RECIPIENTS.append(recipient) #APPEND TO RECIPIENT LIST
        #SEND MESSAGE TO N RECIPIENTS
        message_n_in = str(self.csocket.recv(2048),'utf-8') #RECV 5 CLIENT MESSAGING 1-N
        message_n_in = message_n_in + "\t Sent From: "+userdata
        message_n_in = self.message_polling(message_n_in) #ADDING TIMESTAMP
        print("Recipients are: ", RECIPIENTS)
        print("Message is: ", message_n_in)
        #STORE MESSAGE IN EACH CLIENTS QUEUE
        for recipientname in RECIPIENTS:
            if recipientname in USERNAMES and recipientname in USER_QUEUES.keys():
                MESSAGE_QUEUE = USER_QUEUES[recipientname]
                MESSAGE_QUEUE.put(message_n_in)
                USER_QUEUES[recipientname] = MESSAGE_QUEUE
                print("Message stored for: ", recipientname," Message: ", message_n_in, " Size of Queue: ", MESSAGE_QUEUE.qsize())
            else:
                print("This Recipient Does Not Exist!")

    #CREATING 1-ALL COMPOSE MESSAGE FUNCTION
    #https://www.geeksforgeeks.org/simple-chat-room-using-python/ BROADCAST FUNCTION
    def composeall(self,userdata):
        
        message_all = self.csocket.recv(2048) #RECV 3 1-ALL MESSAGING MESSAGE
        message_all = message_all.decode()
        message_all = message_all + "\t Sent From: "+ userdata
        message_all = self.message_polling(message_all) #ADDING TIMESTAMP
        print("Message to All is: ", message_all)
        DONE_MSG = b'Sent To All'
        #SEND MESSAGE TO EVERYONE
        for USERS in USERNAMES:
            if USERS != userdata:
                if USERS in USER_QUEUES.keys():
                    MESSAGE_QUEUE = USER_QUEUES[USERS]
                    MESSAGE_QUEUE.put(message_all)
                    #STORE IN RESP MESSAGE QUEUE
                    USER_QUEUES[USERS] = MESSAGE_QUEUE
                    print("Message Stored for: ", USERS, "Message: ",message_all, "Queue Size: ", MESSAGE_QUEUE.qsize())
        self.csocket.sendall(DONE_MSG) #SEND 2 1-ALL SERVER ACK

    
    
    #CREATING FUNCTION TO CHECK MESSAGES
    def check_message(self, userdata):
        counter = 1
        if userdata in USER_QUEUES.keys():
            MESSAGE_QUEUE = USER_QUEUES[userdata]
            size = int(MESSAGE_QUEUE.qsize())
            print("Queue Size: ", size)
            self.csocket.sendall(bytes(str(size),'utf-8')) #SEND 2 QUEUE SIZE
            if size > 0:
                while counter <= size:
                    messages_send = MESSAGE_QUEUE.get()
                    print("Message: ",messages_send)
                    self.csocket.sendall(bytes((messages_send),'utf-8')) #SEND 3 QUEUE MESSAGES
                    counter+=1
            else:
                self.csocket.sendall(b"No Messages Found") #SEND 4 NO MESSAGES
        else:
            self.csocket.sendall(bytes(str(0),'utf-8')) #SEND 2 QUEUE SIZE
            self.csocket.sendall(b"Client Has No Messages And Did Not Exist Earlier") #SEND 4 CLENT DIDNT EXIST EARLIER
        

    #FUNCTION TO GET AND CHECK USERNAME
    def USERNAME_CHECK(self):
        USER_FLAG = False
        while not USER_FLAG:
            username = str(self.csocket.recv(4096),'utf-8')   #USERNAME CHECK RECV 1
            if (username in USERNAMES) and (username in ACTIVE_USERNAMES):
                message = b"Username Exists and is Active"
                self.csocket.sendall(message)  #SEND 1 USERNAME EXISTS
                continue
            USER_FLAG = True
        #CHECK IF USERNAME NOT ALREADY IN USERNAME LIST
        if username not in USERNAMES:
            USERNAMES.append(username)
        #GET USER QUEUE BASED ON USERNAME
        MAKE_QUEUE(username)      
        ACTIVE_USERNAMES.append(username)
        global USER_STATUS  #FOR UI UPDATE
        USER_STATUS = True  #FOR UI UPDATE
        global count
        count +=1 #FOR UI UPDATE
        message = b"Welcome"
        print("Welcome", username)
        self.csocket.sendall(message) #SEND 1 USERNAME NEW
        return username

    def run(self):
        global STOP_CLIENT_THREAD
        userdata = self.USERNAME_CHECK() #USERNAME FUNCTION CALL 1

        while True:

            choice = self.csocket.recv(2048) #RECV 2 CLIENT CHAT CHOICE
            choice = choice.decode()
            
            if choice == 'bye':
                ACTIVE_USERNAMES.remove(userdata)  #REMOVING ACTIVE USERNAME FROM LIST
                THREAD_DEL()
                if STOP_CLIENT_THREAD:
                    break
                                
            if choice == '1':
                self.compose_message(userdata)  #CHOICE 1 1-1 COMMUNICATION. CHECK FUNCTION ABOVE
            
            if choice == '2':
                self.composeall(userdata) #CHOICE 1-ALL COMMUNICATION. FUNCTION ABOVE

            if choice == '3':
                self.compose1n(userdata) #CHOICE 1-N COMMUNICATION. FUNCTION ABOVE
            
            if choice == '4':
                self.check_message(userdata) #CHOICE 4. FUNCTION ABOVE




if __name__ == "__main__":
    STOP_CLIENT_THREAD = False
    USER_STATUS = False
    count = 0
    userdata = ''
    USERNAMES = []
    ACTIVE_USERNAMES = []
    USER_QUEUES = {} #TO HANDLE USERNAMES AND QUEUES
    #CHECK IF DUMP FILE EXISTS, IF YES, LOAD FILE INTO DICTIONARY FOR PERSISTENCy
    if path.exists('USERNAME_QUEUES.pkl') == True:
        with (open('USERNAME_QUEUES.pkl', "rb")) as openfile:
            while True:
                try:
                    #https://dill.readthedocs.io/en/latest/dill.html
                    USER_QUEUES.update(dill.load(openfile))
                except EOFError:
                    break
    HOST = '127.0.0.1'
    PORT = 1395

    NULL = ''
    #http://net-informations.com/python/net/thread.htm
    try:
        myserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        myserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        myserver.bind((HOST,PORT))
        print("Starting Server at HOST: "+ HOST + " and PORT: ", PORT)
        start_new_thread(MAIN_DISPLAY,(NULL,))
        while True:
            myserver.listen(3)
            conn, addr = myserver.accept()
            newclientthread = ClientThread(addr, conn)
            newclientthread.start()
    except Exception:
        #https://dill.readthedocs.io/en/latest/dill.html
        dill.dump(USER_QUEUES,open('USERNAME_QUEUES.pkl','wb'))
    finally:
        myserver.close()
