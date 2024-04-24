import subprocess as sub
import os
from time import sleep
import tkinter as tk
from tkinter import scrolledtext
import threading


def cerrar_ventana(root):
    global exit
    exit = True
    root.destroy()
    root.quit()


def mostrar_noti(mensaje, titulo):
    script = f'''
    Add-Type -AssemblyName System.Windows.Forms
    $balmsg = New-Object System.Windows.Forms.NotifyIcon
    $path = (Get-Process -id $pid).Path
    $balmsg.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon($path)
    $balmsg.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::None
    $balmsg.BalloonTipText = "{mensaje}"
    $balmsg.BalloonTipTitle = "{titulo}"
    $balmsg.Visible = $true
    $balmsg.ShowBalloonTip(10000)
    '''
    sub.Popen(['powershell', '-Command', script], creationflags=sub.CREATE_NO_WINDOW)

def actualizar_texto():
    global mensaje2, mensaje1
    if mensaje1:
        texto.insert(tk.END, mensaje1)
        mensaje1 = None
        sleep(1)   
    if mensaje2:
        texto.insert(tk.END, mensaje2)
        mensaje2 = None  
        sleep(1) 
        
def encontrar_ip():
    salida = sub.run("ipconfig", shell=False, capture_output=True, text=True, creationflags=sub.CREATE_NO_WINDOW)

    with open("pruebaPrueba.txt", "w") as archivo:
        archivo.write(salida.stdout)

    with open("pruebaPrueba.txt", "r") as text:
        contenido = text.readlines()

    seccion_wifi = None

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
        sub.Popen(["ping", "-n", "1", direccion], stdout=sub.DEVNULL, stderr=sub.DEVNULL,
                  creationflags=sub.CREATE_NO_WINDOW)


def arp(nombre, ipI):
    salida = sub.run("arp -a", shell=False, capture_output=True, text=True, creationflags=sub.CREATE_NO_WINDOW)
    if salida.returncode != 0:
        print("Error al ejecutar el comando:")
    with open(nombre, "w") as primer:
        primer.write(salida.stdout)

    with open(nombre, "r") as archivo:
        lineas = archivo.readlines()
        lineas_filtradas = [linea for linea in lineas if len(linea.split()) > 0 and ipI in linea.split()[0][:len(ipI)]]

    with open(nombre, "w") as archivo:
        archivo.writelines(lineas_filtradas)


def comprobacion():
    global mensaje1, mensaje2
    with open("PrimerResultado.txt", "r") as archivo1:
        contenido1 = archivo1.readlines()
    with open("SegundoResultado.txt", "r") as archivo2:
        contenido2 = archivo2.readlines()

    ips1 = [linea.split()[0] for linea in contenido1]
    ips2 = [linea.split()[0] for linea in contenido2]

    ip_añadidas = [ip for ip in ips2 if ip not in ips1]
    ip_eliminadas = [ip for ip in ips1 if ip not in ips2]

    if ip_añadidas:
        mensaje1 = f"\nSe han conectado las siguientes direcciones IP:\n{"\n".join(ip_añadidas)}\n"
        mostrar_noti(mensaje1, 'Aviso')
        sleep(1)
        

    if ip_eliminadas:
        mensaje2 = f"\nSe han desconectado las siguientes direcciones IP:\n{"\n".join(ip_eliminadas)}\n"
        mostrar_noti(mensaje2, 'Aviso')
        sleep(1)

    if ip_añadidas or ip_eliminadas:
        arp("PrimerResultado.txt", ipI)
        
        


def ejecutar_tareas_concurrentes():
    global exit
    while not exit:
        ping(ipI)
        arp("SegundoResultado.txt", ipI)
        comprobacion()
        actualizar_texto()
        sleep(30)
def guardar():
    contenido = texto.get("1.0", "end-1c")
    if contenido != "":
        with open("Resultado.txt", "w") as f:
            f.write(contenido)
        mostrar_noti("Se ha guardado correctamente en un txt.", "Aviso")
    else: 
        mostrar_noti("No se ha podido guardar correctamente.", "Aviso")
        

if __name__ == "__main__":
    global mensaje1, mensaje2
    mensaje1 = ""
    mensaje2 = ""
    mensaje_predeterminado = "Se ha ejecutado con éxito\n"
    mostrar_noti('Se le avisará si se conecta o desconecta alguien', 'Se ha iniciado con éxito el escáner de red.')
    exit = False
    ip = encontrar_ip()
    partes = ip.split('.')
    ipI = ".".join(partes[:-1])
    ping(ipI)
    arp("PrimerResultado.txt", ipI)
    t = threading.Thread(target=ejecutar_tareas_concurrentes)
    t.start()
    root = tk.Tk()
    root.title("Análisis de Red")
    root.geometry("500x400")
    root.configure(background="gray21")
    label = tk.Label(root, text="Aqui estan los resultados:", background="grey21", font=18, foreground='white')
    label.pack(pady=10)
    texto = scrolledtext.ScrolledText(root, width = 40, height = 10, wrap = tk.WORD)
    texto.insert(tk.END, mensaje_predeterminado)
    texto.pack(pady=10)
    frame_botones = tk.Frame(root, background="grey21")
    frame_botones.pack(padx=10, pady=10)
    boton = tk.Button(frame_botones, text="cerrar", command=lambda : cerrar_ventana(root), cursor='hand2', height= 2, width=15)
    boton.pack(pady=50, padx=5, side=tk.LEFT)
    boton_guardar = tk.Button(frame_botones, text="guardar resultados", command=lambda : guardar(), cursor= "hand2", height=2, width=15)
    boton_guardar.pack(pady=50, padx=5, side=tk.RIGHT)
    root.mainloop()
    exit = True 
    t.join()
    os.remove("IP.txt")
    os.remove("PrimerResultado.txt")
    os.remove("SegundoResultado.txt")
