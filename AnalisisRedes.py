import subprocess as sub
import os
from time import sleep
from win10toast import ToastNotifier

def encontrar_ip():

    salida = sub.run("ipconfig", shell=False, capture_output=True, text=True)

    with open("pruebaPrueba.txt", "w") as archivo:
        archivo.write(salida.stdout)

    with open("pruebaPrueba.txt", "r") as text:
        contenido = text.readlines()

    seccion_wifi = None

    # Buscar la sección que contiene información sobre Wi-Fi
    for idx, linea in enumerate(contenido):
        if "Wi-Fi" in linea:
            seccion_wifi = contenido[idx:]
            break

    if seccion_wifi:
        with open("wifi.txt", "w") as archivo:
            for lines in seccion_wifi:
                archivo.write(lines)
                
        with open("wifi.txt", "r") as archivo:
            for lines in archivo:
                if "IPv4" in lines:
                    with open("IP.txt", "w") as ip:
                        ip.write(lines) 
                    ip = open("IP.txt", "r").read()
                    partes = ip.split(" ")
                    parte_ip = partes[-1]
                    with open("ip.txt", "w") as ip:
                        ip.write(parte_ip)
                    resultado = open("IP.txt", "r").read()
    else:
        print("No se encontró información sobre Wi-Fi.")
    
    if resultado:
        os.remove("wifi.txt")
        os.remove("pruebaPrueba.txt")
        return resultado
    else:
        print("Error: No se encontró información sobre Wi-Fi")

def ping(ip):
    for i in range(1, 256):
        direccion = f"{ip}.{i}"
        sub.Popen(["ping", "-n", "1", direccion], stdout=sub.PIPE, stderr=sub.PIPE, text=True)

    
def arp(nombre, ipI):
    salida = sub.run("arp -a", shell=False, capture_output=True, text=True)
    if salida.returncode != 0:
        print("Error al ejecutar el comando:")
    with open(nombre, "w") as primer:
        primer.write(salida.stdout) 
    
    # Leer el resultado del comando ARP y guardar solo las líneas que contienen los primeros tres octetos de la IP especificada
    with open(nombre, "r") as archivo:
        lineas = archivo.readlines()
        lineas_filtradas = [linea for linea in lineas if len(linea.split()) > 0 and ipI in linea.split()[0][:len(ipI)]]
    
    # Escribir las líneas filtradas de nuevo en el archivo
    with open(nombre, "w") as archivo:
        archivo.writelines(lineas_filtradas)

def comprobacion():
    # Leer el contenido de los archivos ARP previo y actual
    with open("PrimerResultado.txt", "r") as archivo1:
        contenido1 = archivo1.readlines()
    with open("SegundoResultado.txt", "r") as archivo2:
        contenido2 = archivo2.readlines()
    
    # Extraer las direcciones IP de las listas de contenido
    ips1 = [linea.split()[0] for linea in contenido1]
    ips2 = [linea.split()[0] for linea in contenido2]

    # Determinar quién se ha ido o quién se ha añadido
    ip_añadidas = [ip for ip in ips2 if ip not in ips1]
    ip_eliminadas = [ip for ip in ips1 if ip not in ips2]

    # Mostrar los resultados
    if ip_añadidas:
        for ip in ip_añadidas:
            mensaje1 = f"Se ha conectado la siguiente direcciones IP: {ip}"
            noti.show_toast("Warning", mensaje1, duration=5, threaded=True)

    if ip_eliminadas:
        for ip in ip_eliminadas:
            mensaje2 = f"Se ha desconectado la siguiente direcciones IP: {ip}"
            noti.show_toast("Warning", mensaje2, duration=5, threaded=True)
    
if __name__ == "__main__":
    noti = ToastNotifier()
    noti.show_toast("El programa esta en ejecución", "Bienvenido al escaneo de wifi. Se le avisará si se encuentra algún cambio.", duration=5, threaded = True)
    ip = encontrar_ip()
    partes = ip.split('.')
    ipI = ".".join(partes[:-1])
    ping(ipI)
    arp("PrimerResultado.txt", ipI)
    while True:
        ping(ipI)
        arp("SegundoResultado.txt", ipI)
        comprobacion()
        sleep(30)