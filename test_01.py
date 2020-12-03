import requests
import json
import sys

def getAllUsers():
    url = 'https://us-central1-omnikav-dashboard.cloudfunctions.net/getUsers'
    r = requests.post(url, headers = {'accept': 'application/json'}, data = {'Id': 'sINCLfOKnrgTVux', 'Key': 'G8Rbn6ikkX'}, timeout=1)
    rawUsers = r.json()
    data = r.json()
    print(r)
    print(data)
    sys.exit()

def updateUser(user,reg):
    URL = 'https://us-central1-omnikav-dashboard.cloudfunctions.net/changeUser'
    r = requests.post(url = URL, headers = {'accept': 'application/json'}, data = {'Id':'sINCLfOKnrgTVux','Key':'G8Rbn6ikkX','UserId':user,'Reg':reg})
    data = r.json()
    #print(r)
    print(data)
    
def checkIn(user,temp,count):
    URL = 'https://us-central1-omnikav-dashboard.cloudfunctions.net/readDevice'
    r = requests.post(url = URL, headers = {'accept': 'application/json'}, data = {'Id':'0aBbbbKCiosauN8','Key':'3R0n5HnKnE','user_Id':user,'user_Temp':temp,'user_Count':count,'sys_Temp':temp,'sys_Hum':temp,'sys_Day':'Nan','sys_Hour':'Nan'})
    data = r.json()
    #print(r)
    print(data)
    
def saveFace(Id,Name):
    updateUser(Id,'done')
    
        
def demofun(a):
    print(a)
        
def updateUsers():
    #----------STEP-01-------------: Get users from DB
    url = 'https://us-central1-omnikav-dashboard.cloudfunctions.net/getUsers'
    r = requests.post(url, data = {'Id': 'sINCLfOKnrgTVux', 'Key': 'G8Rbn6ikkX'},verify=False)
    rawUsers = r.json()
   
    #----------STEP-02-------------: filter pending/done and save pending Users
    pendingUsers = {}
    activeUsers = []
    for user in rawUsers:
        userProp = rawUsers[user]
        print (user)
        print (userProp['Registro'])
        if userProp['Registro'] == 'pending':
            pendingUsers[user]= userProp['UserId']
        else:
            activeUsers.append(userProp['UserId'])
    print(pendingUsers)
    print(activeUsers)
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
    
        
getAllUsers()
#updateUser('jjHQjJT1og50PlOcteSL','done')
#checkIn('user002','34.4','45')
#saveFace()
#updateUsers()