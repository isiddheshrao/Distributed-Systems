

import socket
import sys
import tkinter as tk


#WORKING ON DISPLAY
#FUNCTION TO PRINT ON UI
def PRINT_LABEL(VALUE):
    label1 = tk.Label(frame, text = VALUE)
    label1.pack()

#FUNCTION TO HANDLE UI INPUTS
def UI_INPUT(Button, IntVal):
    Button.wait_variable(IntVal)
    INPUT = Entry1.get()
    Entry1.delete(0,'end')
    return INPUT


#FUNCTION TO HANDLE QUIT
def QUIT(top):
    USERNAME_STATUS = False
    top.destroy()
    sys.exit(0)


#FUNCTION TO GET USERNAME UI
def GET_USERNAME():
    USERNAME_STATUS = False
    while not USERNAME_STATUS:
        PRINT_LABEL("Enter Your Username")  #INPUT TO PRINT LABEL FUNCTION ABOVE
        username = UI_INPUT(Button1,int_var)
        myclient.send(str.encode(username))  #UI SEND 1 CLIENTNAME
        response = str(myclient.recv(1024),'utf-8') #UI RECV 1 USERNAME CHECK
        if response == 'Username Exists and is Active':
            Label1 = tk.Label(frame, text='Username Taken & Active')
            Label1.pack()
            continue
        USERNAME_STATUS = True
    return USERNAME_STATUS, username



def setup():
    #https://realpython.com/python-sockets/
    myclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    myclient.connect((HOST, PORT))
    return myclient, HOST, PORT

if __name__ == "__main__":

    HOST = '127.0.0.1'
    PORT = 1395

    #ADDING CODE FOR DISPLAY
    ##https://www.python-course.eu/tkinter_labels.php
    top = tk.Tk()
    top.title("Client")
    int_var = tk.IntVar() #TO STORE INTEGER VAR
    main = tk.Canvas(top, height = 500, width = 600)
    main.pack()
    frame = tk.Frame(main) #BUILD FRAME
    frame.place(relwidth = 1, relheight = 0.9)
    myclient, HOST, PORT = setup()  #GETTING SETUP DETAILS
    Entry1 = tk.Entry(frame)
    Entry1.pack()
    Button1 = tk.Button(frame, text = 'Enter', command = lambda: int_var.set(1))
    Button1.pack()
    USERNAME_STATUS, username = GET_USERNAME() #CHECK ABOVE SEND AND RECV 1 UI
    if USERNAME_STATUS:
        PRINT_LABEL(str("Client "+username+" Has been connected"))

        #MAKE CHOICE LOOP
        while USERNAME_STATUS != False:
            PRINT_LABEL("Enter 1: Client to Client (1-1), 2: 1-To-All, 3: 1-toN 4: Check Messages ")
            PRINT_LABEL("'bye' To Quit ")
            Choice = UI_INPUT(Button1, int_var)  #Get Numerical Choice
            SERVER_RESPONSE = myclient.send(str.encode(Choice))  #UI SEND 2. CHOICE

            #QUIT HANDLING
            if Choice == 'bye':
                QUIT(top)
            
            #1-1 Messaging
            if Choice == '1':
                PRINT_LABEL("Enter Recipient")
                recipient = UI_INPUT(Button1, int_var)
                myclient.send(str.encode(recipient)) #UI SEND 3 1-1 MESSAGE
                PRINT_LABEL("Enter Message")
                message = UI_INPUT(Button1, int_var)
                myclient.send(str.encode(message)) #UI SEND 4 1-1 Message

            #1-ALL MESSAGING
            elif Choice == '2':
                PRINT_LABEL("Enter Message")
                Message = UI_INPUT(Button1, int_var)
                myclient.send(str.encode(Message)) #UI SEND 3 1-ALL MESSAGE
                ACK = str(myclient.recv(1024),'utf-8') #UI RECV 2 SERVER ACK 1-ALL

            #1-N MESSAGING
            elif Choice == '3':
                PRINT_LABEL("Enter Number of Recipients")
                num_recipients = UI_INPUT(Button1, int_var)
                myclient.send(bytes(str(num_recipients),'utf-8')) #UI SEND 3 NUM RECIPIENTS 1-N
                for i in range(0, int(num_recipients)):
                    PRINT_LABEL("Enter Recipient Name")
                    Recipient_name = UI_INPUT(Button1, int_var)
                    myclient.send(str.encode(Recipient_name)) #UI SEND 4 RECIPIENT NAMES LOOP
                PRINT_LABEL("Enter Message")
                message = UI_INPUT(Button1, int_var)
                myclient.send(str.encode(message)) #UI SEND 5 MESSAGE

            #CHECK MESSAGE
            elif Choice == '4':
                i = 1
                QUEUE_SIZE = int(str(myclient.recv(1024),'utf-8'))  #RECV 2 CHECK SIZE
                print(QUEUE_SIZE)
                if QUEUE_SIZE > 0:
                    while i<= QUEUE_SIZE:
                        MESSAGE_GET = str(myclient.recv(1024),'utf-8') #RECV 3 (3 ON UI) MESSAGES
                        PRINT_LABEL(MESSAGE_GET)
                        i+=1
                else:
                    REPLY = str(myclient.recv(1024),'utf-8') #RECV 3 NO MESSAGE 
                    PRINT_LABEL(REPLY)

            Button2 = tk.Button(frame, text = 'Quit', command = lambda: QUIT(top))
            Button2.pack()
            

        PRINT_LABEL("Client Disconnected")
        top.mainloop()


