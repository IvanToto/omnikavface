from subprocess import check_output
myip = str(check_output(['hostname', '--all-ip-addresses']))
myip = myip.replace("'", " ").split(" ")
print (myip[1])
