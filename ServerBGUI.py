import socket
import threading
import os
import time
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
from pathlib import Path
from PIL import Image, ImageTk

root = tk.Tk()
root.geometry("500x500")
root.title("Maria's Chatting App.")
root.config(background="rosy brown")
root.resizable(0, 0)

lb = tk.Label(root, text="Enter message:", width = 15, font=("times new romans", 10,"bold"), background="pink4")  
lb.place(x=35, y=20)  

msgEntry= tk.Entry(root)  
msgEntry.place(x=20, y=40)

textScroll= scrolledtext.ScrolledText(root, width=30, height= 30)
textScroll.place(x=200, y = 20)
textScroll.config(state=tk.DISABLED)

def on_exit():
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_exit)

def display_image():
    # Open the image file
    image_path = r"/home/kali/Desktop/meow.jpeg"

    image = Image.open(image_path)

    # Resize the image to fit the chat window
    width, height = 170, 250  # Adjust the size as needed
    image = image.resize((width, height), Image.ANTIALIAS)

    # Convert the image to a Tkinter-compatible format
    photo = ImageTk.PhotoImage(image)

    # Create a label to display the image
    image_label = tk.Label(root, image=photo)
    image_label.image = photo
    image_label.place(x=10, y=170)  # Adjust the position as needed

def browseFiles():
    filename = Path(filedialog.askopenfilename(initialdir = ".",
                                          title = "Select a file.",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("All files",
                                                        "*.*")))).name
    return filename
                                         
def add_message_UI(text):
    textScroll.config(state=tk.NORMAL)
    textScroll.insert(tk.END, text + '\n')
    textScroll.config(state=tk.DISABLED)

# user: Maria
# IP: 127.0.0.1 and port number 2223

ip, port = ("127.0.0.2", 2223)
name = "Adam"

filename=""

def send():
    global SeqNum
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
    message = msgEntry.get()
    if message == "quit":
        os._exit(1)
    elif message== "sendfile":
        sendfile()
    elif message== "":
        return
    else:
        sm = "{}:{}:{}".format('0', SeqNum, message)
        AckWeAreWaitingFor = SeqNum
        s.sendto(sm.encode(), (ip, int(port)))
        while True:
            time.sleep(0.25)
            if AckWeAreWaitingFor == SeqNum:
                add_message_UI(("Resending message."))
                s.sendto(sm.encode(), (ip, int(port)))
            else:
                #add_message_UI("Message sent.")
                add_message_UI(">>> " + message)
                break

def rec():
    global SeqNum
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
    s.bind(("127.0.0.1", 2223))
    while (True):
        message = s.recvfrom(1024)
        received = message[0].decode().split(":")
        ackBit = received[0]
        SequenceNum= received[1]
        SeqComplement = '0' if SeqNum =='1' else '1'
        if ackBit == '1' and SequenceNum == SeqNum:
            if SeqNum == '0':
               SeqNum = '1'
            else:
               SeqNum = '0'
        elif ackBit == '0' and SequenceNum == SeqNum:
            AcknowledgmentMessage = "Ack"
            sm = "{}:{}:{}".format('1', SeqNum, AcknowledgmentMessage)
            s.sendto(sm.encode(), (ip, int(port)))
            add_message_UI(">> From " + name + ": " + received[2])
            if SeqNum == '0':
               SeqNum = '1'
            else:
               SeqNum = '0'
        elif ackBit == '0' and SequenceNum == SeqComplement:
            AcknowledgmentMessage = "Ack"
            sm = "{}:{}:{}".format(1, SeqComplement, AcknowledgmentMessage)
            s.sendto(sm.encode(), (ip, int(port))) 

def sendfile():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.2', 8000))
    except ConnectionRefusedError:
        print("")
        exit()
    filename = browseFiles()
    while True:
        try:
            fi = open(filename, "rb")
            data = fi.read()
            if not data:
                break
            while data:
                sock.send(data)
                data = fi.read()
            add_message_UI(filename + " file was sent successfully.")
            fi.close()
            break;
        except IOError:
            add_message_UI("Failed to send.")

def receivefile(): 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 8080))
    fileno = 0
    while True:
        sock.listen(1)
        conn = sock.accept()
        fn = 'RcvFileFromAdam('+str(fileno)+')'
        fileno = fileno+1
        fo = open(fn, "wb")
        data = conn[0].recv(1024)
        while data:
                if not data:
                        break
                else:
                        fo.write(data)
                        data = conn[0].recv(1024)
        fo.close()
        add_message_UI(fn + " file was received successfully")
        conn[0].close()

global SeqNum
SeqNum = '0'
x2 = threading.Thread(target = rec)
x3 = threading.Thread(target = receivefile)

def send_message():
    x1 = threading.Thread(target = send)
    x1.start()

def send_file():
    x2 = threading.Thread(target = sendfile)
    x2.start()

b = tk.Button(root, text="Send", command=send_message,background="wheat3")
b.place(x=20, y=80)

bSendFile = tk.Button(root, text="Send File", command=send_file,background="wheat3")
bSendFile.place(x=20, y=120)


# Display the image
display_image() 

root.after(1000, x2.start)
root.after(1000, x3.start)
root.mainloop()







