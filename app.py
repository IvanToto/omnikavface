from multiprocessing import Process
from flask import Flask, render_template, request
server = Flask(__name__)
k = 0

print("hola")
def start_Flask():
    print("Starting server...")
    server.run(debug=True,port=5000,host='192.168.100.241')

@server.route("/")
def index():
    # Read GPIO Status
    a = 1
    b = 1
    c = 1
    d = 1
    e = 1
    templateData = {
            'ah'  : a,
            'bh'  : b,
            'ch'  : c,
            'dh'  : d,
            'eh'  : e,
        }
    return render_template('index.html', **templateData)
    
@server.route("/<deviceName>/<action>")
def action(deviceName, action):
    global k
    print(deviceName)
    print(action)

    if deviceName == 'startcap':
        print("SE INICIA PROCESO DE CAPTURA")
    if deviceName == 'newuser':
        print("SE ABRE EL AREA CAPTURA")
    if deviceName == 'recap':
        print("SE INICIA PROCESO DE SOBREESCRITURA")
    if action == "0":
        k = k + 1
        
    a = 1 + k
    b = 1 + k
    c = 1 + k
    d = 1 + k
    e = 1 + k
    templateData = {
            'ah'  : a,
            'bh'  : b,
            'ch'  : c,
            'dh'  : d,
            'eh'  : e,
    }
    return render_template('index.html', **templateData)

if __name__ == '__main__':
    p1 = Process(target = start_Flask)    # assign Flask to a process
    p1.start()
