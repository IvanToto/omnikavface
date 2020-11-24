import requests

#Datos del servidor:
system = 'dev'               # TODO: Put the system that it will use.
apiBaseUrl = 'dev.wfit.io'   # TODO: Put base API URL.
idOffice = '1'   

URL = 'https://' + apiBaseUrl + '/api/v1/customers/checkinFinger/public'
print(URL)
data = {'id': 'DEV0714', 'id_office': idOffice}
print(data)
r = requests.post(url = URL, headers = {'accept': 'application/json'}, data = data)

data = r.json()
if data['error']:
    print('Error al hacer check in')   # TODO: Handle this
    print(data)
else:
    print('Check In correcto')
    print(data)
