from __future__ import print_function
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty

from kivy.uix.widget import Widget
import os

from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from datetime import datetime
from collections import deque

import threading
import cv2
import numpy as np
import json
import training  #codigo de entrenamiento
import requests
import serial
import time

from PiVideoStream import PiVideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
#import imutils

from flask import Flask, render_template, request
server = Flask(__name__)

#time.sleep(1) #delay function (segundos)
#import sys #llamando sys.exit() se termina el programa

#SERIAL_PORT = '/dev/ttyACM0'   # identificación de puerto seria, verificar en Arduino IDE
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_RATE = 115200 
counter = 0
runstate = 1
dateTimeObj = datetime.now()
currentregister = ""
User_temp = {}
CheckinID = 0
distg = 0
tempg = '0.0'
btn1 = 0
btn2 = 0
btn3 = 0
userin = 0
facemask = 3
k = 0
weborder = '000'
webid = '000'
counter3 = 0

#Datos del servidor:
system = ''               # TODO: Put the system that it will use.
apiBaseUrl = ''   # TODO: Put base API URL.
idOffice = ''   

Window.fullscreen = True
#Window.size = (1245, 700)

from subprocess import check_output
myip = str(check_output(['hostname', '--all-ip-addresses']))
myip = myip.replace("'", " ").split(" ")
print (myip[1])
MyHost = myip[1]
#MyHost = '192.168.100.241'
#MyHost = '127.0.1.2'



#SERVIDOR EN PARALELO------------------------------------------------------------------------------------

@server.route("/")
def index():
    a = 1
    b = 1
    c = 1
    d = 1
    e = 1
    templateData = {'ah':a,'bh':b,'ch':c,'dh':d,'eh':e,}
    return render_template('index.html', **templateData)
    
@server.route("/<deviceName>/<action>")
def action(deviceName, action):
    global k
    global weborder
    global webid
    print(deviceName)
    print(action)
    weborder = deviceName
    webid = action
    
    if action == "0":
        k = k + 1
    
    a = 1 + k
    b = 1 + k
    c = 1 + k
    d = 1 + k
    e = 1 + k
    templateData = {'ah':a,'bh':b,'ch':c,'dh':d,'eh':e,}
    return render_template('index.html', **templateData)

def start_server():
    print("Starting server...")
    server.run(debug=False,port=5000,host=MyHost)

#SERVIDOR ----------------------------------------------------------------

class MainWindow(Screen):
    namk = ObjectProperty(None)
    
    def touchcheck(self):
        print("maintc start")
        refresh_time = .1
        Clock.schedule_interval(self.panstate, refresh_time)
         
    def panstate(self,dt):
        global weborder
        if btn1 == '1':
            kv.current = "checkin"
            Clock.unschedule(self.panstate)
        if btn3 == '1':
            kv.current = "lista"
            Clock.unschedule(self.panstate)
        if weborder == 'newuser':
            kv.current = "lista"
            Clock.unschedule(self.panstate)
            weborder = '0'
    
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        refresh_time = .1
        Clock.schedule_interval(self.sysstate, refresh_time)
        Clock.schedule_interval(self.panstate, refresh_time)
        self.checkvar()
        self.sync()
        
    def sysstate(self, dt):
        global btn1
        global btn2
        global btn3
        global userin
        global distg
        global tempg
        if ser.in_waiting>0:  #si hay más de 0 bytes en el bufer serial.
            reading = ser.readline().decode('utf-8') #Crea una string, de la entrada UART    
            inputdata = reading.split(',')   #separa por comar y crea una lista
            distg = inputdata[0]
            tempg = inputdata[1]
            btn1 = inputdata[3]
            btn2 = inputdata[4]
            btn3 = inputdata[5]
            print (inputdata)
        #reading = ser.readline().decode('utf-8') #Crea una string, de la entrada UART
        #print(reading)
        #print(counter)
        #print(Clock.get_fps())
    
    def serialRele1():   
        command = "e"
        ser.write(command.encode('utf-8'))
    
    def serialRele2(): 
        command = "d"
        ser.write(command.encode('utf-8'))
 
    def serialLamp(): 
        command = "c"
        ser.write(command.encode('utf-8'))
    
    def serialPlum(): 
        command = "b"
        ser.write(command.encode('utf-8'))
        
    def serialTemp(): 
        command = 'a'
        ser.write(command.encode('utf-8'))
        
    def serialCapture(): 
        command = '(0,                    ,14:50     25/07/2020,  Leyendo  Usuario  ,f,100,100,100,0)'
        ser.write(command.encode('utf-8'))
        
    def serialNOMASK(): 
        command = '(0,                    ,14:50     25/07/2020,     Sin MASCARA    ,f,100,100,100,0)'
        ser.write(command.encode('utf-8'))
        
    def serialMASK(): 
        command = '(0,                    ,14:50     25/07/2020, MASCARA VERIFICADA ,f,100,100,100,0)'
        ser.write(command.encode('utf-8'))     
    
    def serialLCDclean(): 
        command = '(0,                    ,14:50     25/07/2020,                    ,a,5,10,10,0)'
        ser.write(command.encode('utf-8'))
    
    def serialNewUser():
        localusers= {}
        file5 = open('registrolocal.json', 'r')
        locales = json.loads(file5.read())
        file5.close()
        for user in locales:
            localusers[str(user['id'])] = user['name']
        command = '(0,'+ localusers[str(CheckinID)] +',14:50     25/07/2020,     Confirmar?     ,a,5,5,30,0)'
        print(command)
        ser.write(command.encode('utf-8'))
        
    def serialBegin(): 
        command = '(0,     Bienvenido     ,14:50     25/07/2020,   deliza la mano   ,a,5,5,30,0)'
        ser.write(command.encode('utf-8')) 
    
    def capin(self):
        self.namk.text = "fine"
        
    def capout(self):
        self.namk.text = "done"
        
    def checkvar(self):
        global system
        global apiBaseUrl
        global idOffice
        with open('servidor.txt', 'r') as document:
            var = {}
            for line in document:
                key, value = line.rstrip("\n").split(":")
                var[key] = value
        document.close()
        system = var['system']
        apiBaseUrl = var['apiBaseUrl']
        idOffice = var['idOffice']

    def sync(self):
        URL = 'https://' + apiBaseUrl + '/api/v1/sync/customers/public/' + idOffice
        print (URL)
        r = requests.post(url = URL, headers = {'accept': 'application/json'},verify=False) 
        data = r.json()
        
        fverapi = open('apiresponse.json', 'w')            
        json.dump(data, fverapi, ensure_ascii=False)            
        fverapi.close()

        fRegisteredUsers = open('registrolocal.json', 'r')
        registeredUsers = json.loads(fRegisteredUsers.read())
        fRegisteredUsers.close()

        if not data['error']:
            users = data['data']
            pendingUsers = [];
            for user in users:
                otherProof = user['other_proof']
                del user['expiry']
                del user['other_proof']
                if not otherProof:
                    pendingUsers.append(user)
                """
                if not otherProof:    
                    inArray = False
                    for registeredUser in registeredUsers:
                        if registeredUser['id'] == user['id']:
                            inArray = True
                            break
                    if not inArray:
                        pendingUsers.append(user)
                """
            fUsers = open('users.json', 'w')
            fPendingUsers = open('pending.json', 'w')
            
            json.dump(users, fUsers, ensure_ascii=False)
            json.dump(pendingUsers, fPendingUsers, ensure_ascii=False)
            
            fUsers.close()
            fPendingUsers.close()
            
        print(pendingUsers)

    def resetFace(key):
        URL = 'https://' + apiBaseUrl + '/api/v1/reset/finger/public/' + idOffice
        r = requests.post(url = URL, headers = {'accept': 'application/json'}, data = {'customer': key, 'system': system, 'mac': '00:00:00:00:00:00'},verify=False) 
        data = r.json()
        if data['error']:
            print('Error al reiniciar huella')   # TODO: Handle this
        else:
            print('Huella reiniciada correctamente')
        
    def saveFace(key):
        
        URL = 'https://' + apiBaseUrl + '/api/v1/up/finger/public'
        r = requests.post(url = URL, headers = {'accept': 'application/json'}, data = {'finger': 'face', 'customer': key, 'logged_user_id': '', 'system': system, 'id': idOffice, 'mac': '00:00:00:00:00:00'},verify=False)
        data = r.json()
        if data['error']:
            print('Error al guardar huella')   # TODO: Handle this
        else:
            print('Huella guardada correctamente')
            
    def makeCheckin(user):
        
        URL = 'https://' + apiBaseUrl + '/api/v1/customers/checkinFinger/public'
        r = requests.post(url = URL, headers = {'accept': 'application/json'}, data = {'id':str(user), 'id_office': idOffice},verify=False)
        data = r.json()
        if data['error']:
            print('Error al hacer check in')   # TODO: Handle this
            print(data)
        else:
            print('Check In correcto')
            print(data)
        
    
class SecondWindow(Screen):
    pass

class ThirdWindow(Screen):
    img1 = ObjectProperty(None)
    #Toda esta estructura convierta al frame de la camara de open CV en una textura que pasa a Kivy, 
    #por eso el despliege es de una imagen, en lugar de la funcion camara por defecto de Kivy.
    def buildcam(self):
        if (runstate == 0):
            self.capture.release()
            print("cam DESTROYED-----------------------------------------")
            print(dateTimeObj)
            Clock.unschedule(self.update)
            return
        self.capture = cv2.VideoCapture(0)
        #cv2.namedWindow("CV2 Image")
        Clock.schedule_interval(self.update, 1.0/33.0) #1/33.0 es un Frame Rate de 33 por segundo
        print("BUILD cam request-----------------------------------------")

    def update(self, dt):
        if (runstate == 0):
           self.capture.release()
           print("update-cam-off")
           return
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        #cv2.imshow("CV2 Image", frame) convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
        #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1
        print("update-cam-on")
        
    def openprocess(self):
        global runstate
        runstate = 1
        print(runstate)
        
    def closeprocess(self):
        global runstate
        runstate = 0
        print(runstate)   

class FourthWindow(Screen): #CAMARA IDENTIFICADORA DE ROSTROS........................................................
    img2 = ObjectProperty(None)
    lab4 = ObjectProperty(None)
    botoni4 = ObjectProperty(None)
    botonc4 = ObjectProperty(None)
    botond4 = ObjectProperty(None)
    
    def touchcheck(self):
        refresh_time = 0.1
        Clock.schedule_interval(self.panstate, refresh_time)
    
    def panstate(self,dt):
        global btn1
        global btn2
        global btn3
        global weborder
        
        if btn1 == '1':
            if self.ids.idcapnow.text in self.User_active:
                btn1 = 0
                self.checkindone()
                self.ids.idcapnow.focus = True
                Clock.unschedule(self.panstate)
            else:
                self.lab4.text = 'Usuario no activo'
                self.ids.idcapnow.text = ''
                self.img2.source = 'check4.png'
                btn1 = 0
        
        if btn3 == '1':
            btn3 = 0
            self.newindone()
            Clock.unschedule(self.panstate)
        
        if btn2 == '1':
            btn2 = 0
            kv.current = "main"
            Clock.unschedule(self.panstate)
            
        if weborder == 'open1':
            weborder = '0'
            MainWindow.serialRele1()
            
        if weborder == 'open2':
            weborder = '0'
            MainWindow.serialRele2()
            
    def panstate2(self,dt):
        global btn1
        global btn2 
        global btn3
        global weborder
        
        if btn2 == '1':
            btn2 = '0'
            MainWindow.serialPlum()
            self.ids.idcapnow.focus = True
            
        if btn1 == '1':
            btn1 = 0
            MainWindow.serialRele1()
            self.ids.idcapnow.focus = True
            self.lab4.text = ''
            time.sleep(1)
            self.botoni4.text = 'Check-In'
            self.botond4.text = 'Escanear'
            self.botonc4.text = 'Main'
            Clock.schedule_interval(self.panstate, 0.1)
            Clock.unschedule(self.panstate2)
            
        if btn3 == '1':
            btn3 = 0
            MainWindow.serialRele2()
            self.ids.idcapnow.focus = True
            self.lab4.text = ''
            time.sleep(1)
            self.botoni4.text = 'Check-In'
            self.botond4.text = 'Escanear'
            self.botonc4.text = 'Main'
            Clock.schedule_interval(self.panstate, 0.1)
            Clock.unschedule(self.panstate2)
        
        if weborder == 'open1':
            weborder = '0'
            MainWindow.serialRele1()
            
        if weborder == 'open2':
            weborder = '0'
            MainWindow.serialRele2()
            
    def panstate3(self,dt):
        global btn2
        global tempg
        if btn2 == '1':
            btn2 = '0'
            Clock.unschedule(self.readfaceupdate)  #<<---------------------------END ID
            self.cam.stop()
            self.botoni4.text = 'Check-In'
            self.botonc4.text = 'Main'
            self.botond4.text = 'Repetir'
            self.ids.idcapnow.text = ''
            self.img2.source = 'check4.png' 
            self.ids.idcapnow.focus = True
            facemask = 3
            if not tempg == '0.0':
                        self.lab4.text = 'Temperatura: '+ tempg + '°C     Bienvenido :)'
                        self.lab4.font_size = 60
                        tempg = '0.0'
            Clock.unschedule(self.panstate3)
            Clock.schedule_interval(self.panstate, 0.1)

            
    def readface(self):
        if (runstate == 0):
            self.cam.stop()
            print("cam DESTROYED-----------------------------------------")
            Clock.unschedule(self.readfaceupdate)
            return
        print("READFACE requested, ....PREPARING TRAINING FILES...")
        print(datetime.now())
        self.recognizer = cv2.face.LBPHFaceRecognizer_create() # Create LocalBinaryPatternsHistograms for face recognization
        self.recognizer.read('trainer/trainer.yml')          # Load the trained mode
        cascadePath = "haarcascade_frontalface_default.xml"           # Load prebuilt model for Frontal Face
        self.faceCascade = cv2.CascadeClassifier(cascadePath);          # Create classifier from prebuilt model
        self.mouth_cascade = cv2.CascadeClassifier('haarcascade_mcs_mouth.xml')
        self.font = cv2.FONT_HERSHEY_SIMPLEX   #define fuente
        #self.cam = cv2.VideoCapture(0)         # Initialize and start the video frame capture
        self.buildcam()
        Clock.schedule_interval(self.readfaceupdate, 1.0/24.0) #1/24.0 es un Frame Rate de 24 por segundo
        print("READFACE Start-----------------------------------------")
        print(datetime.now())
        self.count2 = 0
        #-----------------------Obtiene los Usuarios Locales Actuales para correlacionar con Id en el Loop:
        self.User_check = {}
        file3 = open('registrolocal.json', 'r')
        locales = json.loads(file3.read())
        file3.close()
        for user in locales:
            self.User_check[str(user['id'])] = user['name']
        print(self.User_check)
        #-----------------------Obtiene los Usuarios Activos Actuales para correlacionar con Id en el Loop:
        self.User_active= {}
        file4 = open('users.json', 'r')
        activos = json.loads(file4.read())
        file4.close()
        for user in activos:
            self.User_active[str(user['id'])] = user['name']
        print(self.User_active)

    def buildcam (self):
        #self.cam = cv2.VideoCapture(0)         # Initialize and start the video frame capture
        #vs = PiVideoStream().start()
        #time.sleep(1.0)
        self.cam = PiVideoStream().start()
        time.sleep(0.5)
        MainWindow.serialLamp()
        MainWindow.serialTemp()
        self.botonc4.text = 'Cancelar'
        Clock.schedule_interval(self.panstate3, 0.1)

        # Loop que crea el video, reconoce cara y crea Id:
    def readfaceupdate(self, dt):
        global CheckinID
        global tempg
        global facemask

        frame = self.cam.read()
        frame = cv2.flip(frame, 1)
        #frame = imutils.resize(frame, width=640)
        #ret, frame =self.cam.read()  # crea la variable frame (o elegida) que caputura una imagen de la camara.
        cv2.rectangle(frame,(0,0), (80,480), (0,0,0), -1) #Dibuja Barras Negrarduicas a los lados de la captura
        cv2.rectangle(frame,(560,0), (640,480), (0,0,0), -1) #Dibuja Barras Negras a los lados de la captura
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)          # Convert the captured frame into grayscale
        faces = self.faceCascade.detectMultiScale(gray, 1.3,5) # Get all face from the video frame
        mouth_rects = self.mouth_cascade.detectMultiScale(gray, 1.3, 5)
        # For each face in faces
        if len(faces) == 0: #la variable faces es un arreglo [], esta vacio cuando no hay caras detectadas. 
            print("----SIN CARAS----")
        else:    
            print ("CARAS DETECTADAS: " + str(faces))
            for(x,y,w,h) in faces:
                cv2.rectangle(frame, (x-20,y-20), (x+w+20,y+h+20), (121,210,121), 4) #DIBUJA UN RECTANGULO EN frame, para face
                Id = self.recognizer.predict(gray[y:y+h,x:x+w]) # Crea Id Recognize the face belongs to which ID
                print (Id)
                if(len(mouth_rects) == 0 and facemask == 3):
                    facemask = 2
                    self.lab4.text = 'Gracias por usar Cubreboca'
                elif(facemask == 3):
                    for (mx, my, mw, mh) in mouth_rects:
                        if(my > 0.9*h and y < my < y + h):
                            cv2.rectangle(frame, (mx, my), (mx + mw, my + mh), (0,0,225), 3)
                            self.lab4.text = 'Sin Cubreboca'
                if(len(mouth_rects) == 0 and facemask == 2):
                    self.lab4.text = 'Cubreboca Confirmado'
                if (Id[1]<70): #Id[1] es la precisión de la detección
                    if str(Id[0]) not in self.User_active:
                        rostro = "No activo"
                    else:
                        rostro = self.User_active[str(Id[0])]
                        self.count2 += 1
                    cv2.rectangle(frame, (x-40,y-90), (x+w+40, y-22), (121,210,121), -1)  #Dibuja Rectangulo para etiqueta de ID
                    cv2.putText(frame,rostro, (x-20,y-40), self.font, 1, (0,51,0), 2)  #Dibuja Texto con ID
                else:
                    cv2.rectangle(frame, (x-40,y-90), (x+w+40, y-22), (121,210,121), -1)  #Dibuja Rectangulo para etiqueta de ID
                    cv2.putText(frame, "No identificado", (x-20,y-40), self.font, 1, (0,51,0), 2)  #Dibuja Texto con ID       
                
                if (self.count2>2 and Id[1]<70 and facemask == 2): 
                    CheckinID = Id[0]
                    Clock.unschedule(self.readfaceupdate)  #<<---------------------------END ID
                    Clock.unschedule(self.panstate3)
                    self.cam.stop()
                    self.botoni4.text = 'Check-In'
                    self.botonc4.text = 'Main'
                    self.botond4.text = 'Repetir'
                    self.ids.idcapnow.text = str(CheckinID)
                    self.ids.idcapnow.focus = True
                    facemask = 3
                    if not tempg == '0.0':
                        self.lab4.text = 'Temperatura: '+ tempg + '°C     Bienvenido :)'
                        self.lab4.font_size = 60
                        tempg = '0.0'
                    Clock.schedule_interval(self.panstate, 0.1)
                    if str(Id[0]) in self.User_active: #Verific a si el usuario detectado esta en la lista de activos (user.json)
                        print("CHECK IN VERIFICADO --------------- !!!!!!!!!!!!!!!!!!!!!!!")
                    else:
                        print("USUARIO NO ACTIVO XXXXX")    
                
                if (self.count2>20):
                    Clock.unschedule(self.readfaceupdate)  #<<---------------------------END ID
                    Clock.unschedule(self.panstate3)
                    self.cam.stop()
                    self.botoni4.text = 'Check-In'
                    self.botonc4.text = 'Main'
                    self.botond4.text = 'Repetir'
                    self.ids.idcapnow.focus = True
                    facemask = 3
                    if not tempg == '0.0':
                        self.lab4.text = 'Temperatura: '+ tempg + '°C     Bienvenido :)'
                        self.lab4.font_size = 60
                        tempg = '0.0'
                    Clock.schedule_interval(self.panstate, 0.1)
                    print("USUARIO NO RECONOCIDO")
        
        #convierte frame a una textura para enviarla a KiVy
        frame = cv2.flip(frame, 0)
        buf = frame.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') #Crea el área de dibujo para la textura
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')   #imprime los pixeles (blit pixel) en el área de dibujo
        self.img2.texture = texture1         # despliega la texture creada
        print("faceupdate-cam-on")
        print(self.count2)
    
    def checkindone(self):
        global btn1
        global btn3
        btn1 = 0
        btn3 = 0
        MainWindow.makeCheckin(self.ids.idcapnow.text)
        print(CheckinID) #<<-------------------MAKE CHECK IN Function.
        self.count2 = 0
        self.img2.texture = Texture.create(size=(640, 480))
        self.img2.source = ''
        self.img2.source = 'check1.png'         # display image from the texture
        self.lab4.text = '¿Qúe Torniquete Abrir?'
        self.lab4.font_size = 90
        self.botoni4.text = 'Torre 1'
        self.botonc4.text = 'Sanitizante'
        self.botond4.text = 'Torre 2'
        refresh_time = .1
        Clock.schedule_interval(self.panstate2, refresh_time)
        self.ids.idcapnow.text = ''
        self.ids.idcapnow.focus = True
        
    def newindone(self):  #!!!! FALTA PONER UN COUNTDOWN PARA SABER EL ESTATUS DEL CHEQUEO, un 5,4,3,2,1,. en Label
        global btn1
        global btn3
        btn1 = 0
        btn3 = 0
        self.botoni4.text = ''
        self.botond4.text = ''
        self.botonc4.text = 'Main'
        self.buildcam()
        print("NEW USER")
        self.count2 = 0
        Clock.schedule_interval(self.readfaceupdate, 1.0/24.0) #FALTA APLICARLE UNA VERIFICACION DE SI LA CAMARA YA ENCENDIO !!!!!!!!!!!!!!!
        self.lab4.text = 'Identificando Usuario... Centrar el Rostro'
        self.lab4.font_size = 45
        self.ids.idcapnow.text = ''
        self.ids.idcapnow.focus = True
                                                                #FALTA APLICARLE UNA VERIFICACION DE SI LA CAMARA YA ENCENDIO !!!!!!!!!!!!!!!
        '''                                                    #COMO EN ESTA PARTE COMENTADA
        if self.cam.isOpened():
            Clock.schedule_interval(self.readfaceupdate, 1.0/33.0)
            self.lab4.text = 'Identificando Usuario... Centrar el Rostro'
            self.lab4.font_size = 45
         ''' 
    def openprocess(self):
        global runstate
        runstate = 1
        print(runstate)
    
    def closeprocess(self):
        global runstate
        runstate = 0
        print(runstate)

class FifthWindow(Screen):  #LISTA PARA SELECCION DE USARIOS PARA ALTA----------------------------------ALTAS-------------
    userlist = ObjectProperty(None)
    lab5 = ObjectProperty(None)
    img5 = ObjectProperty(None)
       
    def getpendingusers(self):
        global User_temp
        self.img5.source = 'check2.png'
        self.img5.size_hint_y = None  # Tells the layout to ignore the size_hint in y dir
        self.img5.pos_hint = {'x':0, 'y':.67}
        self.img5.height = 100
        self.lab5.text = 'Usuarios por caputurar en ' + MyHost +':5000'
        file = open('pending.json', 'r')
        pending = json.loads(file.read())
        file.close()
        for user in pending:
            User_temp[str(user['id'])] = user['name']
        #User_pend = [{'text': "Ivan"},{'text': "Carlos"},{'text': "Jorge"}]
        User_pend = [{'text': "id: " + i +" ,  "+ User_temp[i]} for i in User_temp] #i refers to each Key in teh dict.
        self.userlist.data = User_pend
        print(User_temp)
        Clock.schedule_interval(self.webpanstate, 0.1)
        Clock.schedule_interval(self.panstate, 0.1)

    def panstate(self,dt):
        global btn1
        if btn1 == '1':
            btn1 = 0
            kv.current = "main"
            Clock.unschedule(self.panstate)
            Clock.unschedule(self.webpanstate)
    
    def webpanstate(self,dt):
        global weborder
        if weborder == 'newuser':
            weborder = '0'
            MainWindow.sync(self)
            self.getpendingusers()
        if weborder == 'capture':
            weborder = '0'
            self.getid()
        if weborder == 'end':
            weborder = '0'
            self.traincv()
            Clock.unschedule(self.webpanstate)
        if weborder == 'open1':
            weborder = '0'
            MainWindow.serialRele1()
            MainWindow.makeCheckin(webid)
        if weborder == 'open2':
            weborder = '0'
            MainWindow.serialRele2()
            MainWindow.makeCheckin(webid)
            
        self.ids.idcap.text = webid
        
    def actualizarentrenamiento(self): 
        print(test)
        
    def getid(self):
        global currentregister
        currentregister = self.ids.idcap.text
        print(currentregister)
        if currentregister in User_temp:
            kv.current = "getnewface"
        else:
            self.lab5.text = 'Id no existente'
            
    def printtype(self):
        ctype = self.ids.idcap.text
        print(ctype)
        
    def traincv(self):
        self.traincounter = 0
        self.lab5.text = 'Actualizando base local...'
        self.img5.source = 'check.png'
        self.img5.size = (100,100)
        Clock.schedule_interval(self.traincount, 0.1)
        
    def traincount(self,dt):
        self.traincounter += 1
        if(self.traincounter>10):
            training.trainning()
            print("Entrenamiento Terminado")
            self.traincounter = 0
            Clock.unschedule(self.traincount)
            kv.current = "main"

    def updatetext(self):
        self.lab5.text = 'Actualizando base local...'
        self.img5.source = 'check.png'
        self.img5.size = (100,100)
        #time.sleep(1)
    
    def donetext(self):
        self.lab5.text = 'Base Guardada'
        self.img5.source = 'check1.png'
        self.img5.size = (100,100)

    
class SixthWindow(Screen):   #Camara para capturar nuevo usuarios-------------------------------------------
    img3 = ObjectProperty(None)
    
    def lamp(self):
        MainWindow.serialLamp()
    
    def newface(self):
        if (runstate == 0):
            self.cam.release()
            print("cam DESTROYED-----------------------------------------")
            Clock.unschedule(self.newfaceupdate)
            return
        print("BEGIN CAPTURE USER")
        print(datetime.now())
        self.face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.face_id =currentregister #Id de prueba
        self.face_name = User_temp[currentregister] #Id de prueba
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.cam = cv2.VideoCapture(0)
        Clock.schedule_interval(self.newfaceupdateprepare, 1.0/24.0) #1/33.0 es un Frame Rate de 33 por segundo
        print("READFACE Start-----------------------------------------")
        print(datetime.now())
        self.count = 0     # Initialize sample face image
        self.timer = 0
        self.countdown = 6
        self.timer2 = 0
    
    def newfaceupdateprepare(self, dt):
        global counter3
        frame = 0
        # Read the video frame
        ret, frame =self.cam.read()
        frame = cv2.flip(frame, 1)
        
        cv2.rectangle(frame,(80,0), (560,60), (255,255,255), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(80,60), (560,80), (10,250,243), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(80,400), (560,420), (10,250,243), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(80,420), (560,480), (255,255,255), -1) #Dibuja Barras Negras a los lados de la captura
        
        cv2.rectangle(frame,(0,0), (80,480), (0,0,0), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(560,0), (640,480), (0,0,0), -1) #Dibuja Barras Negras a los lados de la captura
        
        cv2.putText(frame, "Mira al frente y pon el rostro", (85,25), self.font, 1, (0,0,0), 2)        
        cv2.putText(frame, "entre las lineas amarillas", (120,55), self.font, 1, (0,0,0), 2)
        cv2.putText(frame, "iniciando captura en:", (150,445), self.font, 1, (0,0,0), 2)        
        if(counter3%24 == 0):
            self.timer2 += 1
        cv2.putText(frame,str(6-self.timer2), (300,475), self.font, 1, (0,0,0), 2)
        
        frame = cv2.flip(frame, 0)
        buf = frame.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img3.texture = texture1
        counter3 += 1
        
        if(counter3>144):
            counter3 = 0
            self.timer2 = 0
            Clock.unschedule(self.newfaceupdateprepare)
            Clock.schedule_interval(self.newfaceupdate, 1.0/24.0) #1/33.0 es un Frame Rate de 33 por segundo
            MainWindow.serialLamp()
    
    def newfaceupdate(self, dt):
        frame = 0
        ret, frame =self.cam.read()
        frame = cv2.flip(frame, 1)
        cv2.rectangle(frame,(0,0), (80,480), (0,0,0), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(560,0), (640,480), (0,0,0), -1) #Dibuja Barras Negras a los lados de la captura
        #Convert the captured frame into grayscale
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        #Get all face from the video frame
        faces = self.face_detector.detectMultiScale(gray, 1.5, 5)

        # For each face in faces
        for (x,y,w,h) in faces:
            self.count += 1
            self.timer += 1
            if self.timer>3:
                self.timer = 0
                self.countdown -=1       
            cv2.rectangle(frame, (x-20,y-20), (x+w+20,y+h+20), (0,255,0), 2)
            cv2.putText(frame, str(self.countdown), (x+60,y-20), self.font, 2, (255,255,255), 3)
            cv2.putText(frame, str(self.face_name) + ", id:" + str(self.face_id), (x+40,y-80), self.font, 0.75, (255,255,255), 2)
            cv2.imwrite("dataset/User." + str(self.face_id) + '.' + str(self.count) + ".jpg", gray[y-15:y+h+15,x-15:x+w+15])
            frame = cv2.flip(frame, 0)
            buf = frame.tostring()
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img3.texture = texture1
        print("faceupdate-cam-on")
        if self.count>19:          # If image taken reach 100, stop taking video
            Clock.unschedule(self.newfaceupdate)
            self.closeprocess()
            self.newface()
            self.updateuserpenlist()
            MainWindow.saveFace(currentregister)
            kv.current = "lista"
            
    def updateuserpenlist(self):
        global User_temp
        #Actualiza la lista de usuarios locales y servidor
        User_local = {}
        file2 = open('registrolocal.json', 'r')
        locallist = json.loads(file2.read())
        file2.close()
        for user in locallist:
            User_local[str(user['id'])] = user['name']
        if currentregister in User_local:
            print("this will execute")
            MainWindow.resetFace(currentregister)
        else:
            User_local[currentregister] = User_temp[currentregister]       
            MainWindow.saveFace(currentregister)

        print(User_local)
        User_localToSave = []
        for i in User_local:
            User_localToSave.append({'id': int(i), 'name': User_local[i]})
        file = open("registrolocal.json", "w")
        json.dump(User_localToSave, file, ensure_ascii=False)
        file.close()
        
        #Actualiza la lista de usuarios pendientes
        User_temp.pop(currentregister)
        User_tempToSave = []
        for i in User_temp:
            User_tempToSave.append({'id': int(i), 'name': User_temp[i]})
        file = open("pending.json", "w")
        json.dump(User_tempToSave, file, ensure_ascii=False)
        file.close()
        print("done, usuarios pendientes actualizados")    
        
    def openprocess(self):
        global runstate
        runstate = 1
        print(runstate)
    
    def closeprocess(self):
        global runstate
        runstate = 0
        print(runstate)
        
class SepthWindow(Screen):
    pass

class EigthWindow(Screen):
    pass

class WindowManager(ScreenManager):
    pass

kv = Builder.load_file("windows.kv")

class MainAppV1(App):
    def build(self):
        return kv
                
if __name__ == "__main__":
    threading.Thread(target=start_server).start() #inicializa servidor web en un segundo hilo
    ser = serial.Serial(SERIAL_PORT, SERIAL_RATE) #inicializa comunicacion serial UART
    MainAppV1().run()
    ser.close() #cierra el UART al cerrar la app, el servidor se extingue solo al dejar de llamar por threading