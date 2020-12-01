from __future__ import print_function
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ObjectProperty, NumericProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window

import sys
import requests
import json
import os

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from datetime import datetime
from collections import deque

import threading
import cv2
import numpy as np
import training  #codigo de entrenamiento
import time
import serial

from PiVideoStream import PiVideoStream
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse

#Window.fullscreen = True
#Window.size = (1245, 700)
Window.size = (720, 480)
Builder.load_file("windows.kv")

#VARIABLES GLOBALES 
flowCounter = '0'
currentUser = ''
userCount = ''
pendingUserList = []
runstate = 0
counter = 0
counter2 = 0
counter3 = 0
currentregister = ""
dbRequest = ''
userTemp = '0'
botonAir = '0'
userDist = '0'
userSig = '0'

#Guardar Propiedades 
MyDbId = ''
MyDbKey = ''
propsFile = open('propiedades.json', 'r')
propsDb = json.loads(propsFile.read())
MyDbId = propsDb['Id']
MyDbKey = propsDb['Key']
propsFile.close()

print(MyDbId)
print(MyDbKey)


'''
#Construcción de Servidor------------------------------------------------------------------------------------
from flask import Flask, render_template, request
server = Flask(__name__)

#Verificación de IP -----------------------------------------------------------------------------------------
from subprocess import check_output
myip = str(check_output(['hostname', '--all-ip-addresses']))
myip = myip.replace("'", " ").split(" ")
print (myip[1])
MyHost = myip[1]

#SERVIDOR EN PARALELO---------------------------------------------------------------------------------------
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
    print("Iniciando Servidor...")
    server.run(debug=False,port=5000,host=MyHost)
    
#SERVIDOR ----------------------------------------------------------------------
'''




#CLASE DE VENTAS----------------------------------------------------------------

class MainScreen(Screen):
    hue = NumericProperty(0)
    def endApp(self):
        ser.close() #cierra el UART al cerrar la app, el servidor se extingue solo al dejar de llamar por threading
        sys.exit()
        

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,RecycleBoxLayout):
    pass

class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        global currentUser
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            print ("SE HA SELECCIONADO UN USUARIO")
            currentUser = rv.data[index]
            print (currentUser)
        else:
            print("selection removed for {0}".format(rv.data[index]))

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        #self.data = [{'text':'0'}]
        
class userListScreen(Screen):
    userList = ObjectProperty(None)
    label09 = ObjectProperty(None)
    global pendingUserList
    
    def drawPendingUserList(self):
        print('HA ACTUALIZADO RV SCREEN')
        self.label09.text = 'Actualizando base de usuarios...'
        OMNIApp().updateUsers()
        self.userList.data = pendingUserList
        self.label09.text = 'Seleccione un usuario :'
        #self.userList.data = [{'text':'jesus'},{'text':'1'},{'text':'2'}]

class userPreCaptureScreen(Screen):
    global currentUser
    label11 = ObjectProperty(None)
    
    def captureUser(self):
        try:
            self.label11.text = currentUser['text']
        except:
            self.label11.text = 'NO SELECCIONO USUARIO'
        
    def demoFunction(self): 
        print('INICIANDO ENTRENAMIENTO')
        self.label11.text = 'Actualizando la base de datos local... espere'
        time.sleep(0.5)
        training.trainning() #Ejecuta entrenamiento de la base de datos
        print('ENTRENAMIENTO TERMINADO')
        self.parent.current = 'mainScreen'
        
class userCaptureScreen(Screen):
    global currentUser
    img3 = ObjectProperty(None)
    
    def updateCapUser(self): 
        global dbRequest
        global userCount
        userName = currentUser['text']
        userID = ''
        pendingFile = open('pending.json', 'r')
        pendingUsers = json.loads(pendingFile.read())
        pendingFile.close()
        
        for user in pendingUsers:
            if user == userName:
                userID = pendingUsers[user]
        print(userName)
        print(userID)
        OMNIApp().updateUserReg(userID,'done')
        
        if (dbRequest == 'PASS'):
            #Abre el registro local, asigna una nueva id local consecutiva y reescribe el nuevo usuario local.
            localFile = open('local.json', 'r')
            localUsers = json.loads(localFile.read())
            localFile.close()
            
            if (len(localUsers) == 0):
                newLocalCount = '0'
            else:
                k = np.array([])
                for i in localUsers:
                    d = np.array([int(i)])
                    k = np.append(k, d)
                newLocalCount = str(int(np.amax(k)+1))
                
            userCount = newLocalCount 
            localUsers[newLocalCount]={"Nombre": userName, "UserId": userID}
            localFileUp = open('local.json', 'w')
            json.dump(localUsers,localFileUp, ensure_ascii=False) 
            localFileUp.close()
            
            #Inicia la captura:
            self.newface()
        
        else: 
            print('No se pudo actualizar la DB, reintente')
            self.parent.current = 'userPreCaptureScreen'
        
    def newface(self):
        global userCount
        if (runstate == 0):
            self.cam.release()
            print("cam DESTROYED-----------------------------------------")
            Clock.unschedule(self.newfaceupdate)
            return
        self.face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.face_id =userCount
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.cam = cv2.VideoCapture(0)
        Clock.schedule_interval(self.newfaceupdateprepare, 1.0/24.0) #1/33.0 es un Frame Rate de 33 por segundo
        print("READFACE Start-----------------------------------------")
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
        #cv2.rectangle(frame,(80,60), (560,80), (10,250,243), -1) #Dibuja Barras Negras a los lados de la captura
        #cv2.rectangle(frame,(80,400), (560,420), (10,250,243), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(80,420), (560,480), (255,255,255), -1) #Dibuja Barras Negras a los lados de la captura
        
        cv2.rectangle(frame, (180,100), (460,380), (10,250,243), 3)
        
        cv2.rectangle(frame,(0,0), (80,480), (0,0,0), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(560,0), (640,480), (0,0,0), -1) #Dibuja Barras Negras a los lados de la captura
        
        cv2.putText(frame, "Centra el rostro hasta", (150,25), self.font, 1, (0,0,0), 2)        
        cv2.putText(frame, "llenar el cuadro amarillo", (130,55), self.font, 1, (0,0,0), 2)
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
            OMNIApp().serialLampOn()
    
    def newfaceupdate(self, dt):
        
        frame = 0
        ret, frame =self.cam.read()
        frame = cv2.flip(frame, 1)
        cv2.rectangle(frame,(0,0), (130+20,480), (0,0,0), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(510-20,0), (640,480), (0,0,0), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(80,0), (560,60+20), (255,255,255), -1) #Dibuja Barras Negras a los lados de la captura
        cv2.rectangle(frame,(80,420-20), (560,480), (255,255,255), -1) #Dibuja Barras Negras a los lados de la captura
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.5, 5)
        
        if len(faces) == 0: #la variable faces es un arreglo [], esta vacio cuando no hay caras detectadas. 
            cv2.putText(frame, "SIN ROSTROS", (110,200), self.font, 2, (255,255,255), 3)
        else: 
            for (x,y,w,h) in faces:
                self.count += 1
                self.timer += 1
                if self.timer>3:
                    self.timer = 0
                    self.countdown -=1       
                cv2.rectangle(frame, (x-20,y-20), (x+w+20,y+h+20), (0,255,0), 2)
                cv2.putText(frame, str(self.countdown), (x+60,y-20), self.font, 2, (255,255,255), 3)
                cv2.putText(frame, "id:" + str(self.face_id), (x+40,y-80), self.font, 0.75, (255,255,255), 2)
                cv2.imwrite("dataset/User." + str(self.face_id) + '.' + str(self.count) + ".jpg", gray[y-15:y+h+15,x-15:x+w+15])
        
        frame = cv2.flip(frame, 0)
        buf = frame.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img3.texture = texture1
        if self.count>19:          # If image taken reach 100, stop taking video
            Clock.unschedule(self.newfaceupdate)
            #self.updateuserpenlist() #Actualiza la base de datos y el registro del usuario. 
            self.closeprocess()
            self.newface()
            self.parent.current = 'userPreCaptureScreen' #Retorna a la ventan anterior al terminar
            
            #MainWindow.saveFace(currentregister)
            #kv.current = "lista"

            
    def updateuserpenlist(self):
        pass
       
        
    def openprocess(self):
        global runstate
        runstate = 1
        print(runstate)
    
    def closeprocess(self):
        global runstate
        runstate = 0
        print(runstate)


class userCheckInScreen(Screen):
    img2= ObjectProperty(None)
    label12= ObjectProperty(None)
    
    def readface(self):
        if (runstate == 0):
            self.cam.stop()
            print("cam DESTROYED-----------------------------------------")
            Clock.unschedule(self.readfaceupdate)
            return
        print("READFACE requested, ....PREPARING TRAINING FILES...")
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
        self.count2 = 0
        
        #-----------------------Obtiene los Usuarios Locales Actuales para correlacionar con Id en el Loop:
        self.User_check = {}
        self.User_Ids = {}
        localFile = open('local.json', 'r')
        locales = json.loads(localFile.read())
        localFile.close()
        for user in locales:
            userData = locales[user]
            self.User_check[user]= userData['Nombre']
            self.User_Ids[user]= userData['UserId']
        print(self.User_check)
        print(self.User_Ids)
        

    def buildcam (self):
        #self.cam = cv2.VideoCapture(0)         # Initialize and start the video frame capture
        #vs = PiVideoStream().start()
        #time.sleep(1.0)
        self.cam = PiVideoStream().start()
        time.sleep(0.5)
        #OMNIApp().serialLampOn()
        OMNIApp().serialUserTemp()
        #MainWindow.serialLamp()
        #MainWindow.serialTemp()
        #self.botonc4.text = 'Cancelar'
        #Clock.schedule_interval(self.panstate3, 0.1)

        # Loop que crea el video, reconoce cara y crea Id:
    def readfaceupdate(self, dt):
        global userTemp
        global userDist
        global userSig
        global flowCounter
        global dbRequest
        
        tempg = 0
        facemask = 0 
    
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
                
                if(len(mouth_rects) == 0):
                    facemask = 1
                    print('Bien, tienes cubreboca')
                else:
                    cv2.rectangle(frame, (x-40,y-90), (x+w+40, y-22), (0,0,225), -1)  #(b,g,r)
                    cv2.putText(frame,'USE CUBREBOCAS', (x-20,y-40), self.font, 1, (250,250,250), 2)
                    print('MAL, no tienes cubreboca')
                    for (mx, my, mw, mh) in mouth_rects:
                        if(my > 0.9*h and y < my < y + h):
                            cv2.rectangle(frame, (mx, my), (mx + mw, my + mh), (0,0,225), 3)

                if(facemask == 1):
                    self.count2 += 1
                    #USUARIO IDENTIFICADO
                    if (Id[1]<70): #Id[1] es la precisión de la detección                    
                        rostro = self.User_check[str(Id[0])]
                        cv2.rectangle(frame, (x-40,y-90), (x+w+40, y-22), (121,210,121), -1)  #Dibuja Rectangulo para etiqueta de ID
                        cv2.putText(frame,rostro, (x-20,y-40), self.font, 1, (0,51,0), 2)  #Dibuja Texto con ID
                        if (self.count2>3):
                            UserId = self.User_Ids[str(Id[0])]
                            Clock.unschedule(self.readfaceupdate)  #<<---------------------------END ID
                            self.cam.stop()
                            facemask = 0
                            Clock.schedule_interval(self.botonAirCheck, 0.1)
                            self.count2 = 0;
                            newFlow = int(flowCounter)+1
                            flowCounter = str(newFlow)
                            #temp = 0.4835*float(userSig)-126.15+0.2*float(userDist)
                            temp = 0.4*float(userSig)-95+0.05*float(userDist)
                            if (temp<35.0):
                                temp=35.0
                            tempr = round(temp,2)
                            userTemp = str(tempr)
                            OMNIApp().serialPumpOn()
                            OMNIApp().userCheckIn(UserId,flowCounter)
                            if (dbRequest == 'PASS'):
                                if(float(userTemp)<38):
                                    self.label12.text = 'Acceso Exitoso, su temperatura es:'+userTemp+'°C'
                                else: 
                                    self.label12.text = 'Temperatura Alta: '+userTemp+'°C, Administrador notificado'
                                    
                            else:
                                self.label12.text = 'No se pudo registrar su acceso, vuelva a checar'
                    #USUARIO NO IDENTIFICADO
                    else:
                        cv2.rectangle(frame, (x-40,y-90), (x+w+40, y-22), (121,210,121), -1)  #Dibuja Rectangulo para etiqueta de ID
                        cv2.putText(frame, "No identificado", (x-20,y-40), self.font, 1, (0,51,0), 2)  #Dibuja Texto con ID       
                        if (self.count2>20):
                            Clock.unschedule(self.readfaceupdate)  #<<---------------------------END ID
                            self.cam.stop()
                            facemask = 0
                            Clock.schedule_interval(self.botonAirCheck, 0.1)
                            self.count2 = 0;
                               
        #convierte frame a una textura para enviarla a KiVy
        frame = cv2.flip(frame, 0)
        buf = frame.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') #Crea el área de dibujo para la textura
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')   #imprime los pixeles (blit pixel) en el área de dibujo
        self.img2.texture = texture1         # despliega la texture creada
        print("faceupdate-cam-on")
        print(self.count2)


    def botonAirCheck (self,dt): 
        global botonAir
        if (botonAir == '1'):
            Clock.unschedule(self.botonAirCheck)
            botonAir = '0'
            self.buildcam()
            Clock.schedule_interval(self.readfaceupdate, 1.0/24.0) #1/24.0 es un Frame Rate de 24 por segundo
            print("READFACE Start-----------------------------------------")
                
    def openprocess(self):
        global runstate
        runstate = 1
        print(runstate)
    
    def closeprocess(self):
        global runstate
        runstate = 0
        print(runstate)

class OMNIApp(App):
    def __init__(self, **kwargs):
        super(OMNIApp, self).__init__(**kwargs)
        refresh_time = 0.1
        Clock.schedule_interval(self.serialListener, refresh_time)
        #self.checkvar()
        #self.sync()
    
    def build(self):
        root = ScreenManager()
        root.add_widget(MainScreen(name='mainScreen'))
        root.add_widget(userListScreen(name='userListScreen'))
        root.add_widget(userCaptureScreen(name='userCaptureScreen'))
        root.add_widget(userCheckInScreen(name='userCheckInScreen'))
        root.add_widget(userPreCaptureScreen(name='userPreCaptureScreen'))
        return root
        
    def updateUsers(self):
        global dbRequest
        dbRequest = ''
        #----------STEP-01-------------: Get users from DB
        try:
            url = 'https://us-central1-omnikav-dashboard.cloudfunctions.net/getUsers'
            r = requests.post(url, headers = {'accept': 'application/json'}, data = {'Id': MyDbId, 'Key': MyDbKey},timeout=(0.5,3))
            rawUsers = r.json()
            dbRequest = 'PASS'
        except requests.exceptions.ReadTimeout:
            print ('No se pudo actualiza DB, ocurrio ReadTimeout')
            dbRequest = 'ERROR'
            return
       
        #----------STEP-02-------------: filter pending/done and save pending Users
        pendingUsers = {}
        activeUsers = []
        global pendingUserList
        pendingUserList = []
        for user in rawUsers:
            userProp = rawUsers[user]
            print (user)
            print (userProp['Registro'])
            if userProp['Registro'] == 'pending':
                pendingUsers[user]= userProp['UserId']
                pendingUserList.append({'text':user})
            else:
                activeUsers.append(userProp['UserId'])
        print(r)
        print (pendingUserList)
        pendingFile = open('pending.json', 'w')        
        json.dump(pendingUsers,pendingFile, ensure_ascii=False)        
        pendingFile.close()
        
        #----------STEP-03-------------: filter and update/delete local Users/Files
        localFile = open('local.json', 'r')
        localUsers = json.loads(localFile.read())
        localFile.close()
        print(localUsers)
        deletedUsers = []
        #Checa si hay usuarios locales por eliminar
        for user in localUsers:
            localUser = localUsers[user]
            if localUser['UserId'] in activeUsers:
                print ('Se mantienen las fotos y registros del usuario '+user+' con Id '+localUser['UserId'])
            else:
                deletedUsers.append(user)
        #ejecuta la eliminacion
        for i in deletedUsers:
            print ('Se eliminaron las fotos y registro del usuario '+i)
            localUsers.pop(i)
        
        print(localUsers)
        newLocalFile = open('local.json', 'w')        
        json.dump(localUsers,newLocalFile, ensure_ascii=False)        
        newLocalFile.close()   
        
    def updateUserReg(self,userId,reg):
        global dbRequest
        dbRequest = ''
        
        try:
            url = 'https://us-central1-omnikav-dashboard.cloudfunctions.net/changeUser'
            r = requests.post(url = url, headers = {'accept': 'application/json'}, data = {'Id':MyDbId,'Key':MyDbKey,'UserId':userId,'Reg':reg},timeout=(0.5,3))
            data = r.json()
            print(r)
            print(data)
            dbRequest = 'PASS'
        except requests.exceptions.ReadTimeout:
            print ('No se pudo actualiza el usuario, ocurrio ReadTimeout')
            dbRequest = 'ERROR'
            return
    
    def userCheckIn(self,Id,flow): 
        global dbRequest
        dbRequest = ''
        try:
            url = 'https://us-central1-omnikav-dashboard.cloudfunctions.net/readDevice'
            dataout = {'Id':MyDbId,'Key':MyDbKey,'user_Id':Id,'user_Temp':userTemp,'user_Count':flow,'sys_Temp':'35.5','sys_Hum':'25','sys_Day':'Nan','sys_Hour':'Nan'}
            r = requests.post(url = url, headers = {'accept': 'application/json'}, data = dataout,timeout=(0.5,3))
            data = r.json()
            print(r)
            print(data)
            dbRequest = 'PASS'
        except requests.exceptions.ReadTimeout:
            print ('No se pudo actualiza el usuario, ocurrio ReadTimeout')
            dbRequest = 'ERROR'
            return
            
        print('Datos Enviados')
            
    def serialListener(self, dt):
        global userTemp
        global botonAir
        global userDist
        global userSig
        if ser.in_waiting>0:  #si hay más de 0 bytes en el bufer serial.
            reading = ser.readline().decode('utf-8') #Crea una string, de la entrada UART    
            inputdata = reading.split(',')   #separa por comar y crea una lista
            userTemp = inputdata[1]
            botonAir = inputdata[2]
            userDist = inputdata[3]
            userSig = inputdata[4]
            print (inputdata)
    
    def serialUserTemp(self): 
        command = "a"
        ser.write(command.encode('utf-8'))
        
    def serialBuzzerOn(self): 
        command = "b"
        ser.write(command.encode('utf-8'))
    
    def serialReleOn(self):   
        command = "c"
        ser.write(command.encode('utf-8'))
        
    def serialLampOn(self): 
        command = "d"
        ser.write(command.encode('utf-8'))
    
    def serialPumpOn(self): 
        command = "g"
        ser.write(command.encode('utf-8'))
               
if __name__ == '__main__':
    #threading.Thread(target=start_server).start()  #inicializa servidor web en un segundo hilo
    SERIAL_PORT = '/dev/ttyUSB0'
    SERIAL_RATE = 115200 
    ser = serial.Serial(SERIAL_PORT, SERIAL_RATE) #inicializa comunicacion serial UART
    OMNIApp().run()

