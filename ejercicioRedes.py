import subprocess
from time import sleep
from win10toast import ToastNotifier 
def comando_arp(Archivo):
    resultado = subprocess.run("nmap -sn 100.70.192.0/24", shell=False, capture_output=True, text=True)
    if resultado.returncode != 0:
        print("Error al ejecutar el comando:")

    with open(Archivo, 'w') as archivo:
            archivo.write(resultado.stdout)
            
print("Se ha iniciado el programa de deteccion de red\nSe le avisara si se conecta o desconecta alguien")
contador = 0
n = ToastNotifier()
comando_arp("PrimerResultado.txt")
from datetime import datetime
while True:    
    start = datetime.now()
    print("Continuo examinando") 
    comando_arp("SegundoResultado.txt")
    with open("PrimerResultado.txt", 'r') as f1, open("SegundoResultado.txt", 'r') as f2:
        contenido1 = f1.readlines()
        contenido2 = f2.readlines()
    
    # [h, i, j, k, l]
    # [(0, h), (1, i), (2, j), (3, k), (4, l)]
    for i, line in enumerate(contenido1[1:-2]):
        if i == 0 or i % 2 != 0:
            ip = line.split(' ')[-1]
            print(f"Ip: {i}, {ip}")
        
    for linea1, linea2 in zip(contenido1, contenido2,):
        if linea1 != linea2:
            contador +=  1
            break
    
    if contador > 0:
        mensaje = f"Se ha conectado o desconectado un total de {contador} IPS"
        n.show_toast("Warning", mensaje, duration= 15, threaded=True)
        contador = 0
    print(f"Se tardo un total de {datetime.now() - start}s")
    