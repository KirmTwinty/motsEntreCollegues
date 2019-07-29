#!/usr/bin/env python3
from tkinter import *
import math
from PIL import Image, ImageTk
import numpy as np
images = []  # to hold the newly created image
import re
import socket
import pickle
from threading import Thread
from time import sleep
import datetime
import argparse

def alpha_rectangle(canvas, window, x1, y1, x2, y2, **kwargs):
    if 'alpha' in kwargs:
        alpha = int(kwargs.pop('alpha') * 255)
        fill = kwargs.pop('fill')
        fill = window.winfo_rgb(fill) + (alpha,)
        image = Image.new('RGBA', (x2-x1, y2-y1), fill)
        images.append(ImageTk.PhotoImage(image))
        canvas.create_image(x1, y1, image=images[-1], anchor='nw')
    canvas.create_rectangle(x1, y1, x2, y2, **kwargs)



class PopupConf(object):
    def __init__(self,master):
        top=self.top=Toplevel(master)

        self.labelName=Label(top,text="Your name")
        self.labelName.grid(row=0, sticky=W)
    # self.labelName.pack()
        self.entryName=Entry(top)
        self.entryName.grid(row=0, column=1)
    # self.entryName.pack()
        self.entryName.focus_set()

        self.labelAddress=Label(top,text="Your address")
        self.labelAddress.grid(row=1, sticky=W)
    # self.labelAddress.pack()
        self.entryAddress=Entry(top)
        self.entryAddress.grid(row=1, column=1)
    # self.entryAddress.pack()

        self.labelPort=Label(top,text="Your port")
        self.labelPort.grid(row=2, sticky=W)
    # self.labelPort.pack()
        self.entryPort=Entry(top)
        self.entryPort.grid(row=2, column=1)
    # self.entryPort.pack()

        self.isServer = IntVar()
        self.isServer.set(1)
        self.checkServer=Checkbutton(top, text="I am hosting", 
                                     variable=self.isServer, 
                                     command=self.check_action)
        self.checkServer.grid(row=3, sticky=W)
        #self.checkServer.pack()

        self.labelServerAddress=Label(top,text="Server address")
        self.entryServerAddress=Entry(top)

        self.labelServerPort=Label(top,text="Server port")
        self.entryServerPort=Entry(top)

        self.b=Button(top,text='Ok',command=self.cleanup)
        self.b.grid(row = 3, column = 1)

        # default values
        self.entryName.insert(0, "PlayerName")
        self.entryAddress.insert(0, "127.0.0.1")
        self.entryPort.insert(0, "6789")
        self.entryServerAddress.insert(0, "127.0.0.1")
        self.entryServerPort.insert(0, "6789")

    def check_action(self):
        if self.isServer.get():
            self.labelServerAddress.grid_remove()
            self.entryServerAddress.grid_remove()
            self.labelServerPort.grid_remove()
            self.entryServerPort.grid_remove()
        else:
            self.labelServerAddress.grid(row = 4, sticky = W)
            self.entryServerAddress.grid(row = 4, column = 1)
            self.labelServerPort.grid(row = 5, sticky = W)
            self.entryServerPort.grid(row = 5, column = 1)

    def cleanup(self):
        self.name=self.entryName.get()
        self.address=self.entryAddress.get()
        self.port = int(self.entryPort.get())
        self.isServer = self.isServer.get()
        if self.isServer:
            self.serverAddress = self.entryAddress.get()
            self.serverPort = int(self.entryPort.get())
        else:
            self.serverAddress = self.entryServerAddress.get()
            self.serverPort = int(self.entryServerPort.get())
        self.top.destroy()

class PopupJoker(object):
    def __init__(self,master):
        top=self.top=Toplevel(master)
        self.l=Label(top,text="Choose the joker's letter")
        self.l.grid(row=0, sticky=W)
        self.e=Entry(top)
        self.e.grid(row=0, column = 1)
        self.e.focus_set()
        self.b=Button(top,text='Ok',command=self.cleanup)
        self.b.grid(row=1)
    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()


class Mec(object):
    "Defines the main application object class"
    WORD_TRIPLE = 0
    WORD_DOUBLE = 1
    LETTER_TRIPLE = 2
    LETTER_DOUBLE = 3
    START = 4

    EAST = 1
    SOUTH = 2

    # Read dictionnary
    with open('officielMecLarousse.txt') as file:
        DICTIONNARY = file.read().splitlines()

    VALUES = {
        "`" : 0, #chr(96) for the joker
        "a" : 1, 
        "b" : 3, 
        "c" : 3, 
        "d" : 2, 
        "e" : 1, 
        "f" : 4, 
        "g" : 2, 
        "h" : 4, 
        "i" : 1, 
        "j" : 8, 
        "k" : 10, 
        "l" : 1, 
        "m" : 2, 
        "n" : 1, 
        "o" : 1, 
        "p" : 3, 
        "q" : 8, 
        "r" : 1, 
        "s" : 1, 
        "t" : 1, 
        "u" : 1, 
        "v" : 4, 
        "w" : 10, 
        "x" : 10, 
        "y" : 10, 
        "z" : 10,
    }

    BAG = {
        "`" : 2, #chr(96)
        "a" : 9, 
        "b" : 2, 
        "c" : 2, 
        "d" : 3, 
        "e" : 15, 
        "f" : 2, 
        "g" : 2, 
        "h" : 2, 
        "i" : 8, 
        "j" : 1, 
        "k" : 1, 
        "l" : 5, 
        "m" : 3, 
        "n" : 6, 
        "o" : 6, 
        "p" : 2, 
        "q" : 1, 
        "r" : 6, 
        "s" : 6, 
        "t" : 6, 
        "u" : 6, 
        "v" : 2, 
        "w" : 1, 
        "x" : 1, 
        "y" : 1, 
        "z" : 1
    }

    def __init__(self, parent, conf, width, height):
        "Constructor of the Mec"

        # Here we put the GUI properties
        self.root = parent
        strTitle = "Python Mec - " + conf.name
        if conf.isServer:
            strTitle = strTitle + " (hosting)"
        self.root.title(strTitle)
        self.root.geometry(str(width+310)+"x"+str(height))
        self.width = width
        self.height = height


        # Now the gaming properties
        self.players = []
        self.myId = 0
        self.currentPlayer = 0

        self.clicked = False
        self.direction = Mec.EAST
        self.currentCases = []
        self.currentWord = ""
        self.currentPts = 0
        self.wordBonus = [0,0]
        self.minPos = []
        self.maxPos = []
        self.conf = conf

        self.myTurn = False
        if conf.isServer:
            self.myTurn = True

        self.exit = False
        # Generate board
        self.board = []
        for i in range(15):
            for j in range(15):
                self.board.append(Case((i,j), -1, -1))
        
        #init bag
        self.bag = Mec.BAG

        self.offsetX = 10
        self.offsetY = 10
        self.caseWidth = math.floor((500 - self.offsetY)/15)
        self.boardHeight = 15 * self.caseWidth;
        self.boardWidth = self.boardHeight;

        self.players.append(Player(self.conf.name, self.conf.address, self.conf.port, 0))
        self.players[0].letters = self.draw_from_bag(7) # Init letters
        # Init the game here
        self.init_game()

        # Init server
        self.init_server()

    def rxThread(self):
        #Generate a UDP socket
        rxSocket = socket.socket(socket.AF_INET, #Internet
                                 socket.SOCK_DGRAM) #UDP

        #Bind to any available address on port *portNum*
        rxSocket.bind((self.conf.address, self.conf.port))

        #Prevent the socket from blocking until it receives all the data it wants
        #Note: Instead of blocking, it will throw a socket.error exception if it
        #doesn't get any data

        rxSocket.setblocking(0)

        print("RX: Receiving data on UDP port " + str(self.conf.port))
        print("")

        while not self.exit:
            try:
                #Attempt to receive up to 1024 bytes of data
                data,addr = rxSocket.recvfrom(self.BYTES_SIZE) 
                data = pickle.loads(data)
                print("Received: " + data.__class__.__name__)
                if data.__class__.__name__ is "Turn" and not self.conf.isServer:
                    self.myTurn = True
                    self.log("[Network:] It is your turn")
                    self.draw_all()

                if data.__class__.__name__ is "NewPlayer" and not self.conf.isServer:
                    self.log("[Network:] "+data.players[len(data.players)-1].name +" connected")
                    self.players = data.players
                    self.draw_all()

                if data.__class__.__name__ is "RequestGame":
                    self.log("[Network:] Received request for game")
                    self.players.append(Player(data.name, data.address, data.port, len(self.players)))
                    l = Label(self.infoFrame, text=data.name)
                    l.grid(row = 2 + len(self.players), sticky=W)
                    self.log(data.name + " connected and added to the game.")
                    self.players[len(self.players)-1].letters = self.draw_from_bag(7) # Init letters
                    # send back letters and id to the player plus other players info
                    rxSocket.sendto(pickle.dumps(GameInformation(len(self.players)-1, 
                                                                 self.players)), 
                                    (self.players[len(self.players)-1].address, 
                                     self.players[len(self.players)-1].port))

                    sleep(.1)
                    for idx, p in enumerate(self.players):
                        if idx != 0 and idx != (len(self.players)-1):
                            rxSocket.sendto(pickle.dumps(NewPlayer(self.players)), (p.address, p.port))

                if data.__class__.__name__ is "GameInformation":
                    # The server sends player information for us
                    self.log("[Network:] Got game information")
                    self.myId = data.myId
                    self.players = data.players
                    self.draw_all()

                if data.__class__.__name__ is "GameData":
                    self.log("[Network:] Got game data")
                    # Update the game data
                    self.board = data.board
                    self.bag = data.bag
                    self.players = data.players
                    if self.conf.isServer:
                        # need to send the information to everyone
                        for idx, p in enumerate(self.players):
                            if idx != 0 and idx != self.currentPlayer:
                                print("Sending to " + p.name)
                                rxSocket.sendto(pickle.dumps(data), (p.address, p.port))
                        # Need to send next player its turn
                        self.log("Next player sets")
                        self.next_player()
                        if not self.myTurn:
                            self.log("[Network:] Sending to " + self.players[self.currentPlayer].name + " to play")
                            rxSocket.sendto(pickle.dumps(Turn(self.players[self.currentPlayer].playerId)), (self.players[self.currentPlayer].address, self.players[self.currentPlayer].port))
                    self.draw_all()



            except socket.error:
                #If no data is received, you get here, but it's not an error
                #Ignore and continue
                pass

            sleep(.1)

    def init_game(self):
        self.canvas = Canvas(self.root, width = self.width, height=self.height)
        self.canvas.grid(row=0, sticky=W, rowspan=10,columnspan=10)

        # Frame on the right
        self.infoFrame = Frame(self.root, width=300, height=400)
        self.infoFrame.grid(row = 0, column = 11)
        # ensure a consistent GUI size
        self.infoFrame.grid_propagate(False)
        # implement stretchability
        self.infoFrame.grid_rowconfigure(0, weight=1)
        self.infoFrame.grid_columnconfigure(0, weight=1)

        # create a Text widget for logging
        self.console = Text(self.infoFrame, borderwidth=3, relief="sunken")
        self.console.config(font=("consolas", 8), undo=True, wrap='word', state=DISABLED)
        self.console.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # create a Scrollbar and associate it with txt
        self.scrollBar = Scrollbar(self.infoFrame, command=self.console.yview)
        self.scrollBar.grid(row=0, column=1, sticky='nsew')
        self.console['yscrollcommand'] = self.scrollBar.set
        self.buttonPass = Button(self.infoFrame, text="Pass", command = self.pass_turn)
        self.buttonPass.grid(row = 1, column = 0, columnspan=2)
        # Players labels
        self.playersLabels = []

        self.canvas.bind('<Motion>', self.mouse_motion)
        self.canvas.bind('<Button-1>', self.mouse_clicked)
        self.root.bind('<Key>', self.key_pressed)
        self.root.bind('<Right>', self.right_pressed)
        self.root.bind('<Down>', self.down_pressed)
        self.root.bind('<BackSpace>', self.backspace_pressed)
        self.root.bind('<Return>', self.verify_board)

        

        # draw now
        self.canvas.create_rectangle(self.offsetX, self.offsetY, 
                                     self.boardWidth + self.offsetX, 
                                     self.boardHeight + self.offsetY)
        self.canvas.create_rectangle(self.offsetX-2, self.offsetY-2, 
                                     self.boardWidth + self.offsetX+2, 
                                     self.boardHeight+self.offsetY+2)
        self.canvas.create_rectangle(self.offsetX-3, self.offsetY-3, 
                                     self.boardWidth + self.offsetX+3, 
                                     self.boardHeight+self.offsetY+3)
        self.draw_all()

        # self.buttonPass.grid(column=11, row=1)
        # self.console.grid(column = 11, row = 2)
        # self.scroll.grid(column = 12, row=2)


    @staticmethod
    def get_special(i,j):
        if i > 7:
            i = abs(14 - i)
        if j > 7:
            j = abs(14 - j)

        # TRIPLE WORD
        if i == 0:
            if j == 0 or j == 7:
                return(Mec.WORD_TRIPLE)
        if i==7 and j == 0:
            return(Mec.WORD_TRIPLE)
        # DOUBLE WORD
        if i==j and i > 0 and i < 5:
            return(Mec.WORD_DOUBLE)
        # DOUBLE LETTER
        if i==0 or i==7:
            if j==3:
                return(Mec.LETTER_DOUBLE)
        if i==6:
            if j==2 and j==6:
                return(Mec.LETTER_DOUBLE)
        if i==3:
            if j==0 or j==7:
                return(Mec.LETTER_DOUBLE)
        if i==2 and j==6:
            return(Mec.LETTER_DOUBLE)
        if i==6 and j==2:
            return(Mec.LETTER_DOUBLE)
        if i==6 and j==6:
            return(Mec.LETTER_DOUBLE)
        if j==5:
            if i==5 or i==1:
                return(Mec.LETTER_TRIPLE)
        if i == 5 and j ==1:
            return(Mec.LETTER_TRIPLE)
        if i==7 and j==7:
            return(Mec.START)
        return(-1)

    def init_server(self):


        self.BYTES_SIZE = 20000
        #Generate a transmit socket object
        self.txSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #Do not block when looking for received data (see above note)
        self.txSocket.setblocking(0)
        self.udpRxThreadHandle = Thread(target=self.rxThread)    
        self.udpRxThreadHandle.start()
        sleep(.1)
        
        if not self.conf.isServer:
            # Must send connection request
            self.log("Sending request for game")
            req = RequestGame(conf.name, conf.address, conf.port)
            self.txSocket.sendto(pickle.dumps(req), (self.conf.serverAddress, self.conf.serverPort))
            sleep(.1)


    def mouse_motion(self, event):
        self.draw_board()
        x, y = event.x, event.y
        i = math.floor((x - self.offsetX) / self.caseWidth)
        j = math.floor((y - self.offsetY) / self.caseWidth)
        if i >= 0 and i < 15 and j >= 0 and j < 15:
            alpha_rectangle(self.canvas, 
                            self.root, 
                            self.offsetX + self.caseWidth * (i), self.offsetY + self.caseWidth * (j), 
                            self.offsetX + self.caseWidth * (i+1), self.offsetY + self.caseWidth * (j+1), 
                            fill = '#1a1a1a',
                            alpha = .5)
    def mouse_clicked(self, event):
        x, y = event.x, event.y
        i = math.floor((x - self.offsetX) / self.caseWidth)
        j = math.floor((y - self.offsetY) / self.caseWidth)
        if i >= 0 and i < 15 and j>=0 and j < 15:
            self.maxPos = 15 * i + j
            if self.board[i*15 + j].value == -1 and not self.currentCases:
                self.clicked = [i,j]
                if self.direction == Mec.EAST:
                    i = i -1
                    while i > 0 and self.board[i*15 + j].value != -1:
                        self.currentWord = self.board[i*15 + j].value + self.currentWord
                        if self.board[i*15+j].special == Mec.LETTER_TRIPLE:
                            self.currentPts = self.currentPts + self.board[i*15 + j].points * 3
                        elif self.board[i*15+j].special == Mec.LETTER_DOUBLE:
                            self.currentPts = self.currentPts + self.board[i*15 + j].points * 2
                        elif self.board[i*15+j].special == Mec.WORD_DOUBLE:
                            self.wordBonus[Mec.WORD_DOUBLE] = self.wordBonus[Mec.WORD_DOUBLE] + 1
                        elif self.board[i*15+j].special == Mec.WORD_TRIPLE:
                            self.wordBonus[Mec.WORD_TRIPLE] = self.wordBonus[Mec.WORD_TRIPLE] + 1
                        else:
                            self.currentPts = self.currentPts + self.board[i*15 + j].points
                        i = i -1
                if self.direction == Mec.SOUTH:
                    j = j -1
                    while j > 0 and self.board[i*15 + j].value != -1:
                        self.currentWord = self.board[i*15 + j].value + self.currentWord
                        if self.board[i*15+j].special == Mec.LETTER_TRIPLE:
                            self.currentPts = self.currentPts + self.board[i*15 + j].points * 3
                        elif self.board[i*15+j].special == Mec.LETTER_DOUBLE:
                            self.currentPts = self.currentPts + self.board[i*15 + j].points * 2
                        elif self.board[i*15+j].special == Mec.WORD_DOUBLE:
                            self.wordBonus[Mec.WORD_DOUBLE] = self.wordBonus[Mec.WORD_DOUBLE] + 1
                        elif self.board[i*15+j].special == Mec.WORD_TRIPLE:
                            self.wordBonus[Mec.WORD_TRIPLE] = self.wordBonus[Mec.WORD_TRIPLE] + 1
                        else:
                            self.currentPts = self.currentPts + self.board[i*15 + j].points

                        j = j -1
                self.minPos = 15 * (i+1) + j

            if self.direction==Mec.EAST:
                self.right_pressed(event)
            if self.direction == Mec.SOUTH:
                self.down_pressed(event)

    def key_pressed(self, event):
        if self.clicked:
            code = repr(event.char)
            l = event.char.lower()
            if l in self.players[self.myId].letters:
                self.players[self.myId].letters.remove(l)
                self.players[self.myId].onBoard.append(l)
                self.currentCases.append(self.clicked[0]*15 + self.clicked[1])
                self.board[self.clicked[0]*15 + self.clicked[1]].value = l
                self.board[self.clicked[0]*15 + self.clicked[1]].player = self.myId
                self.board[self.clicked[0]*15 + self.clicked[1]].points = Mec.VALUES[l]
                while(self.board[self.clicked[0]*15 + self.clicked[1]].value != -1):
                    self.currentWord = self.currentWord + self.board[self.clicked[0]*15 + self.clicked[1]].value
                    if self.board[self.clicked[0]*15 + self.clicked[1]].special == Mec.LETTER_TRIPLE:
                        self.currentPts = self.currentPts + self.board[self.clicked[0]*15 + self.clicked[1]].points * 3
                    elif self.board[self.clicked[0]*15 + self.clicked[1]].special == Mec.LETTER_DOUBLE:
                        self.currentPts = self.currentPts + self.board[self.clicked[0]*15 + self.clicked[1]].points * 2
                    elif self.board[self.clicked[0]*15 + self.clicked[1]].special == Mec.WORD_DOUBLE:
                        self.wordBonus[Mec.WORD_DOUBLE] = self.wordBonus[Mec.WORD_DOUBLE] + 1
                    elif self.board[self.clicked[0]*15 + self.clicked[1]].special == Mec.WORD_TRIPLE:
                        self.wordBonus[Mec.WORD_TRIPLE] = self.wordBonus[Mec.WORD_TRIPLE] + 1
                    else:
                        self.currentPts = self.currentPts + self.board[self.clicked[0]*15 + self.clicked[1]].points
                    if self.direction == Mec.EAST:
                        if  self.clicked[0] == 14:
                            self.clicked = False
                            break
                        self.clicked[0] = self.clicked[0] + 1
                    if self.direction == Mec.SOUTH:
                        if  self.clicked[1] == 14:
                            self.clicked = False
                            break
                        self.clicked[1] = self.clicked[1] + 1
                if self.direction == Mec.EAST:
                    self.maxPos = (self.clicked[0]-1)*15+self.clicked[1]
                else:
                    self.maxPos = self.clicked[0]*15+self.clicked[1]-1
        else:
            self.log('Select a case on the board first')
        self.draw_all()

    def right_pressed(self, event):
        if not self.currentCases:
            self.currentWord = ""
            self.currentPts = 0
            self.direction = Mec.EAST
            i = self.clicked[0]
            j = self.clicked[1]
            i = i -1
            while i > 0 and self.board[i*15 + j].value != -1:
                self.currentWord = self.board[i*15 + j].value + self.currentWord
                if self.board[i*15+j].special == Mec.LETTER_TRIPLE:
                    self.currentPts = self.currentPts + self.board[i*15 + j].points * 3
                elif self.board[i*15+j].special == Mec.LETTER_DOUBLE:
                    self.currentPts = self.currentPts + self.board[i*15 + j].points * 2
                elif self.board[i*15+j].special == Mec.WORD_DOUBLE:
                    self.wordBonus[Mec.WORD_DOUBLE] = self.wordBonus[Mec.WORD_DOUBLE] + 1
                elif self.board[i*15+j].special == Mec.WORD_TRIPLE:
                    self.wordBonus[Mec.WORD_TRIPLE] = self.wordBonus[Mec.WORD_TRIPLE] + 1
                else:
                    self.currentPts = self.currentPts + self.board[i*15 + j].points

                i = i -1
            self.minPos = 15 * i + j
        self.draw_all()

    def down_pressed(self, event):
        if not self.currentCases:
            self.currentWord = ""
            self.currentPts = 0
            self.direction = Mec.SOUTH
            i = self.clicked[0]
            j = self.clicked[1]
            j = j -1
            while j > 0 and self.board[i*15 + j].value != -1:
                self.currentWord = self.board[i*15 + j].value + self.currentWord
                if self.board[i*15+j].special == Mec.LETTER_TRIPLE:
                    self.currentPts = self.currentPts + self.board[i*15 + j].points * 3
                elif self.board[i*15+j].special == Mec.LETTER_DOUBLE:
                    self.currentPts = self.currentPts + self.board[i*15 + j].points * 2
                elif self.board[i*15+j].special == Mec.WORD_DOUBLE:
                    self.wordBonus[Mec.WORD_DOUBLE] = self.wordBonus[Mec.WORD_DOUBLE] + 1
                elif self.board[i*15+j].special == Mec.WORD_TRIPLE:
                    self.wordBonus[Mec.WORD_TRIPLE] = self.wordBonus[Mec.WORD_TRIPLE] + 1
                else:
                    self.currentPts = self.currentPts + self.board[i*15 + j].points

                j = j -1
            self.minPos = 15 * i + j
        self.draw_all()

    def backspace_pressed(self, event):
        self.reset_letters()

    def reset_letters(self):
        for l in self.players[self.myId].onBoard:
            self.players[self.myId].letters.append(l)
        for c in self.currentCases:
            self.board[c].value = -1
            self.board[c].player = -1
        self.currentCases = []
        self.currentWord = ""
        self.currentPts = 0
        self.wordBonus = [0,0]
        self.players[self.myId].onBoard = []
        self.draw_all()

    def draw_from_bag(self, n):
        "Draw n letters from letters' bag"
        i = 0
        l = []
        while i < n and sum(self.bag.values()) > 0:
            char = chr(np.random.randint(27) + 96)
            if self.bag[char] > 0:
                self.bag[char] = self.bag[char] - 1
                l.append(char)
                i = i +1
        return(l)

    def log(self, msg):
        self.console.config(state=NORMAL)
        strTime = datetime.datetime.now().strftime("[%B %d - %H:%M:%S]")
        self.console.insert(INSERT, strTime + " " + msg + "\n")
        self.console.yview(END)
        self.console.config(state=DISABLED)
        # print(msg)

    def pass_turn(self):
        if self.myTurn:
            self.reset_letters()
            for l in self.players[self.myId].letters:
                self.bag[l] = self.bag[l] + 1
            self.players[self.myId].letters = self.draw_from_bag(7)
            # send game data
            self.myTurn = False
            data = GameData(self.board, 0, self.bag, self.players) # current player is set by the server not by the player
            if self.conf.isServer:
                # need to send the information to everyone
                for idx,p in enumerate(self.players):
                    if idx != 0:
                        self.txSocket.sendto(pickle.dumps(data), (p.address, p.port))
                                        # Need to send next player its turn
                self.log("Next player sets")
                self.next_player()
                self.log("[Network:] Sending to " + self.players[self.currentPlayer].name + " to play")
                self.txSocket.sendto(pickle.dumps(Turn(self.players[self.currentPlayer].playerId)), (self.players[self.currentPlayer].address, self.players[self.currentPlayer].port))
            else:
                self.txSocket.sendto(pickle.dumps(data), (self.conf.serverAddress, self.conf.serverPort))
            self.draw_all()
    # Game checking
    def verify_board(self, event):
        # Check for a joker
        jokerPos = self.currentWord.find('`')
        print(self.currentWord)
        print(str(jokerPos))
        while jokerPos >= 0:
            while True:
                popup = PopupJoker(self.root)
                self.root.wait_window(popup.top)
                jokerValue = popup.value
                if len(jokerValue) == 1:
                    if jokerValue.isalpha():
                        jokerValue = jokerValue.upper()
                        break
            self.currentWord = self.currentWord.replace('`', jokerValue)
            self.board[self.currentCases[jokerPos]].value = jokerValue
            jokerPos = self.currentWord.find('`')

        self.currentWord = self.currentWord.upper()
        # First check the current word
        if(self.check_word(self.currentWord)):
            if self.wordBonus[Mec.WORD_TRIPLE] > 0:
                self.currentPts = self.currentPts * pow(3,self.wordBonus[Mec.WORD_TRIPLE])
            if self.wordBonus[Mec.WORD_DOUBLE] > 0:
                self.currentPts = self.currentPts * pow(2,self.wordBonus[Mec.WORD_DOUBLE])     

            self.log(self.currentWord + " ok: " + str(self.currentPts))
            
            # Now we check the adjacent words
            d = Mec.SOUTH
            deltaPos = 15
            if self.direction == Mec.SOUTH:
                d = Mec.EAST
                deltaPos = 1
            check = True
            adjacentPts = 0
            for pos in range(self.minPos, self.maxPos+1, deltaPos):
                b, pts = self.check_adjacent(pos, d)
                adjacentPts = adjacentPts + pts
                check = check and b

            if not check:
                self.log("Unable to get adjacent correspondance")
            else:
                self.players[self.myId].points = self.players[self.myId].points + self.currentPts + adjacentPts
                self.currentWord = ""
                self.currentPts = 0
                self.wordBonus = [0,0]
                self.currentCases = []
                self.minPos = []
                self.maxPos = []
                self.players[self.myId].onBoard = []
                self.players[self.myId].letters.extend(self.draw_from_bag(7-len(self.players[self.myId].letters)))
                self.myTurn = False
                data = GameData(self.board, 0, self.bag, self.players) # current player is set by the server not by the player
                self.txSocket.sendto(pickle.dumps(data), (self.conf.serverAddress, self.conf.serverPort))
                    

        else:
            self.log("Word '" + self.currentWord + "' is not in the dictionnary!")
        self.draw_all()

    def next_player(self):
        self.currentPlayer = self.currentPlayer + 1
        self.log("CurrentPlayer is "+str(self.currentPlayer))
        if self.currentPlayer >= len(self.players):
            self.currentPlayer = 0
            self.myTurn = True

    def check_adjacent(self, pos, d):
        # We check it only if it has been added
        if pos in self.currentCases:
            i = math.floor(pos/15)
            j = pos - i * 15
            minPos = pos
            maxPos = pos
            w = self.board[i*15 + j].value
            if self.board[i*15+j].special == Mec.LETTER_TRIPLE:
                points = self.board[i*15 +j].points * 3
            elif self.board[i*15+j].special == Mec.LETTER_DOUBLE:
                points = self.board[i*15 +j].points * 2
            else:
                points = self.board[i*15 +j].points
            if w == -1:
                return(True)
            if d == Mec.EAST:
                i = i -1
                while i > 0 and self.board[i*15 + j].value != -1:
                    w = self.board[i*15 + j].value + w
                    points = points + self.board[i*15+j].points
                    i = i -1
                minPos = (i + 1) * 15 + j
            if d == Mec.SOUTH:
                j = j -1
                while j > 0 and self.board[i*15 + j].value != -1:
                    w = self.board[i*15 + j].value + w
                    points = points + self.board[i*15+j].points
                    j = j -1
                minPos = i * 15 + j + 1
            i = math.floor(pos/15)
            j = pos - i * 15
            if d == Mec.EAST:
                i = i + 1
                while i < 14 and self.board[i*15 + j].value != -1:
                    w = w + self.board[i*15 + j].value
                    points = points + self.board[i*15+j].points
                    i = i + 1
                maxPos = (i - 1) * 15 + j
            if d == Mec.SOUTH:
                j = j + 1
                while j < 14 and self.board[i*15 + j].value != -1:
                    w = w + self.board[i*15 + j].value
                    points = points + self.board[i*15+j].points
                    j = j + 1
                maxPos = i * 15 + j - 1
            if len(w) == 1:
                return((True, 0))
            w = w.upper()
            b = self.check_word(w)

            i = math.floor(pos/15)
            j = pos - i * 15
            if self.board[i*15+j].special == Mec.WORD_TRIPLE:
                points = points * 3
            elif self.board[i*15+j].special == Mec.WORD_DOUBLE:
                points = points * 2
            if not b:
                self.log("Word '" + w + "' is not in the dictionnary!")
            else:
                self.log(w + " ok (" + str(points) + " points)")
            return((b, points))
        else:
            return((True,0))

    def check_word(self, w):
        if len(w) == 1:
            return True
        w = w.replace('`', '[A-Z]')
        p = re.compile(w, re.IGNORECASE)
        if w.upper() in Mec.DICTIONNARY:
            return(True)
        return(False)

    # All drawing
    def draw_all(self):
        self.draw_board()
        self.draw_player_letters()
        self.draw_information()

    def draw_rectangle(self, i1, j1, i2, j2, fillColor):
        self.canvas.create_rectangle(self.offsetX + self.caseWidth * i1, self.offsetY + self.caseWidth * j1, 
                                    self.offsetX + self.caseWidth * i2, self.offsetY + self.caseWidth * j2, 
                                    fill = fillColor)

    def draw_text(self, i, j, fill, text, font):
        self.canvas.create_text(self.offsetX + self.caseWidth * i+self.caseWidth/2, 
                                self.offsetY + self.caseWidth * j+self.caseWidth/2, 
                                fill=fill, font=font, text=text)
    def draw_information(self):
        if self.myTurn:
            self.draw_rectangle(13,16,14,17,"#009900")
        else:
            self.draw_rectangle(13,16,14,17,"#990000")
        for idx,p in enumerate(self.players):
            l = Label(self.infoFrame, text=p.name + " - "+str(p.points) + " points")
            l.grid(row = 3 + idx, sticky=W)



    def draw_player_letters(self):
        p = self.players[self.myId]
        self.canvas.create_rectangle(self.offsetX + self.caseWidth, self.offsetY + self.caseWidth*16, 
                                self.offsetX + self.caseWidth * 8, self.offsetY + self.caseWidth * (17), 
                                fill="#d9d9d9")
        fillColor  = "#fdecbe"
        for idx, l in enumerate(p.letters):
            self.canvas.create_rectangle(self.offsetX + self.caseWidth * (1+idx), self.offsetY + self.caseWidth * (16), 
                                    self.offsetX + self.caseWidth * (2+idx), self.offsetY + self.caseWidth * (17), 
                                    fill = fillColor)
            self.canvas.create_text(self.offsetX + self.caseWidth * (1+idx)+self.caseWidth/2, self.offsetY + self.caseWidth * (16)+self.caseWidth/2, 
                               fill="darkblue",font="Times 14 italic bold",
                               text=l.upper())
            self.canvas.create_text(self.offsetX + self.caseWidth * (1+idx)+self.caseWidth/1.2, self.offsetY + self.caseWidth * (16)+self.caseWidth/1.2, 
                               fill="darkblue",font="Times 7 italic bold",
                               text=str(Mec.VALUES[l.lower()]))
    
    def draw_board(self):
        for case in self.board:
            if case.value == -1:
                fillColor = '#898b80'
                if case.special == Mec.WORD_TRIPLE:
                    fillColor = '#cb374d'
                elif case.special == Mec.WORD_DOUBLE:
                    fillColor = '#cf939d'
                elif case.special == Mec.LETTER_TRIPLE:
                    fillColor = '#07759a'
                elif case.special == Mec.LETTER_DOUBLE:
                    fillColor = '#84b4c0'
                elif case.special == Mec.START:
                    fillColor = '#dfe07e'

                self.draw_rectangle(case.coords[0], case.coords[1], 
                                    case.coords[0]+1, case.coords[1]+1, 
                                    fillColor)
                if case.special == Mec.WORD_TRIPLE:
                    self.draw_text(case.coords[0], case.coords[1], "black", "MT", "Arial 10 bold")
                elif case.special == Mec.WORD_DOUBLE:
                    self.draw_text(case.coords[0], case.coords[1], "black", "MD", "Arial 10 bold")
                elif case.special == Mec.LETTER_TRIPLE:
                    self.draw_text(case.coords[0], case.coords[1], "black", "LT", "Arial 10 bold")
                elif case.special == Mec.LETTER_DOUBLE:
                    self.draw_text(case.coords[0], case.coords[1], "black", "LD", "Arial 10 bold")

            else:
                fillColor  = "#fdecbe"
                l = case.value
                self.draw_rectangle(case.coords[0], case.coords[1], 
                                    case.coords[0]+1, case.coords[1]+1, 
                                    fillColor)
                self.draw_text(case.coords[0], case.coords[1], "darkblue", l.upper(), "Times 14 italic bold")
                self.canvas.create_text(self.offsetX + self.caseWidth * (case.coords[0])+self.caseWidth/1.2, self.offsetY + self.caseWidth * (case.coords[1])+self.caseWidth/1.2, 
                                   fill="darkblue",font="Times 7 italic bold",
                                   text=str(case.points))

                
        if self.clicked:
            alpha_rectangle(self.canvas, 
                            self.root,
                            self.offsetX + self.caseWidth * (self.clicked[0]), 
                            self.offsetY + self.caseWidth * (self.clicked[1]), 
                            self.offsetX + self.caseWidth * (self.clicked[0]+1), 
                            self.offsetY + self.caseWidth * (self.clicked[1]+1), 
                            fill = '#ee1111',
                            alpha = .8)
            if self.direction == Mec.SOUTH:
                self.canvas.create_line(self.offsetX + self.caseWidth * (self.clicked[0]) + self.caseWidth/2, 
                                   self.offsetY + self.caseWidth * (self.clicked[1]), 
                                   self.offsetX + self.caseWidth * (self.clicked[0]) + self.caseWidth/2, 
                                   self.offsetY + self.caseWidth * (self.clicked[1]+1), 
                                   arrow=LAST)
            elif self.direction == Mec.EAST:
                self.canvas.create_line(self.offsetX + self.caseWidth * (self.clicked[0]), 
                                   self.offsetY + self.caseWidth * (self.clicked[1])+ self.caseWidth/2, 
                                   self.offsetX + self.caseWidth * (self.clicked[0]+1), 
                                   self.offsetY + self.caseWidth * (self.clicked[1])+ self.caseWidth/2, 
                                   arrow=LAST)



class Turn:
    def __init__(self, playerId):
        self.playerId = playerId

class NewPlayer:
    def __init__(self, players):
        self.players = players

class Player:
    def __init__(self, name, address, port, playerId):
        self.name = name
        self.letters = []
        self.onBoard = []
        self.address = address
        self.port = int(port)
        self.playerId = playerId
        self.points = 0

class Case:
    "Defines a case with current letter and player and if it is a special one"
    def __init__(self, coords, value, player):
        self.coords = coords
        self.value = value
        self.player = player
        if value==-1:
            self.points = 0
        else:
            self.points = Mec.VALUES[value]
        self.special = Mec.get_special(coords[0], coords[1])
class GameData:
    "The game data to be sent"
    def __init__(self, board, currentPlayer, bag, players):
        self.board = board
        self.currentPlayer = currentPlayer
        self.bag = bag
        self.players = players
        
class GameInformation:
    "The game information when a new player is connected"
    def __init__(self, myId, players):
        self.myId = myId
        self.players = players


class RequestGame:
    "Request a game from a distant host"
    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.port = port

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == "__main__":
    root = Tk()
    root.withdraw()

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, 
                        help = "Player's name")
    parser.add_argument("-a", "--address", type=str, 
                        help = "Address of the client")
    parser.add_argument("-p", "--port", type=str, 
                        help = "Port of the client")
    parser.add_argument("-s", "--server", type=str2bool, nargs='?', 
                        const=True, default=False,
                        help = "True if hosting the server")
    parser.add_argument("-sa", "--serverAddress", type=str, 
                        help = "Address of the server (useless if hosting)")
    parser.add_argument("-sp", "--serverPort", type=str, 
                        help = "Port of the server (useless if hosting)")
    args = parser.parse_args()


    
    skipPopup = True
    if not args.name or not args.address or not args.port:
        skipPopup = False
    if not args.server and (not args.serverAddress or not args.serverPort):
        skipPopup = False
    
    conf = PopupConf(root)
    if args.name:
        conf.entryName.delete(0, END)
        conf.entryName.insert(0,args.name)
    if args.address:
        conf.entryAddress.delete(0, END)
        conf.entryAddress.insert(0,args.address)
    if args.port:
        conf.entryPort.delete(0, END)
        conf.entryPort.insert(0,args.port)
    if args.serverAddress:
        conf.entryServerAddress.delete(0, END)
        conf.entryServerAddress.insert(0,args.serverAddress)
    if args.serverPort:
        conf.entryServerPort.delete(0, END)
        conf.entryServerPort.insert(0,args.serverPort)
    if args.server:
        conf.isServer.set(0)
    else:
        conf.isServer.set(1)
    if skipPopup:
        conf.cleanup()
    else:
        root.wait_window(conf.top)

    root.deiconify()
    app = Mec(root, conf, 500, 600)
    root.mainloop()
