import subprocess as sub
import os
from time import sleep
import tkinter as tk
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
    global mensaje2, mensaje1, mensaje_predeterminado
    if mensaje1:
        label1.config(text=mensaje1)
    if mensaje2:
        label2.config(text=mensaje2)
        
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
        mensaje1 = f"Se ha conectado la siguiente direcciones IP: {"\n".join(ip_añadidas)}"
        mostrar_noti(mensaje1, 'Aviso')
        sleep(1)

    if ip_eliminadas:
        mensaje2 = f"Se ha desconectado la siguiente direcciones IP: {"\n".join(ip_eliminadas)}"
        mostrar_noti(mensaje2, 'Aviso')
        sleep(1)

    if ip_añadidas or ip_eliminadas:
        arp("PrimerResultado.txt", ipI)
        
    with open("Resultado.txt", "a") as f:
        f.write("Ips ip_añadidas:\n")
        for ip in ip_añadidas:
            f.write(ip)
    with open("Resultado.txt", "a") as f:
        f.write("\nIps ip_eliminadas:\n")
        for ip in ip_eliminadas:
            f.write(ip)

def ejecutar_tareas_concurrentes():
    global exit
    while not exit:
        ping(ipI)
        arp("SegundoResultado.txt", ipI)
        comprobacion()
        actualizar_texto()
        sleep(30)



if __name__ == "__main__":
    global mensaje1, mensaje2
    mensaje1 = "Todo normal"
    mensaje2 = ""
    mensaje_predeterminado = "Se ha ejecutado con éxito"
    mostrar_noti('Se le avisará si se conecta o desconecta alguien', 'Se ha iniciado con éxito el escáner de red.')
    exit = False
    ip = encontrar_ip()
    partes = ip.split('.')
    ipI = ".".join(partes[:-1])
    ping(ipI)
    arp("PrimerResultado.txt", ipI)
    root = tk.Tk()
    root.title("Análisis de Red")
    root.geometry("500x400")
    root.configure(background="gray21")
    label1 = tk.Label(root, text=mensaje_predeterminado, foreground="white", background="grey21", font=18)
    label2 = tk.Label(root, text=mensaje2, foreground="white", background="grey21", font=18)
    label1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    boton_cerrar = tk.Button(root, text="Cerrar", command=lambda: cerrar_ventana(root), cursor="hand2", width=8, height=2)
    boton_cerrar.grid(row=1, column=0, pady=10)

    t = threading.Thread(target=ejecutar_tareas_concurrentes)
    t.start()
    
    root.mainloop()
    exit = True 
    t.join()
    os.remove("IP.txt")
    os.remove("PrimerResultado.txt")
    os.remove("SegundoResultado.txt")
