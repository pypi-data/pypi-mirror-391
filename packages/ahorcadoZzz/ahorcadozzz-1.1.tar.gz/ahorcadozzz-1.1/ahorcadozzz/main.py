import tkinter as tk
import random

# CONSTANTES
CANTIDAD_VIDAS = 7
PALABRAS = [
    "hola", "adios", "python", "ejercicio", "ejemplo", "desayuno", "java", "c++", "verse", "computadora",
    "teclado", "pantalla", "codigo", "variable", "funcion", "clase", "objeto", "bucle", "condicion", "algoritmo",
    "buenosdias", "buenasnoches", "gracias", "porfavor", "hasta_luego", "programacion", "desarrollo", "software", "hardware", "red",
    "internet", "nube", "datos", "base", "servidor", "cliente", "aplicacion", "movil", "web", "frontend",
    "backend", "debug", "error", "solucion", "compilador", "interprete", "sintaxis", "semantica", "cafe", "almorzar"
]

# VARIABLES GLOBALES
palabraOculta = "" # se almacena la palabra que ha tocado de forma aleatoria
palabraActual = "" # se almacena lo que va introduciendo el usuario
vidas = CANTIDAD_VIDAS
letrasUsadas = []
palabrasAcertadas = 0
palabrasFalladas = 0
estadoPartida = 0 # 0 -> jugando, 1 -> ganado, 2 -> perdido

# Para la UI
entry = None # lo declaramos como nada para luego inicializarlo
label_acertadas = None
label_falladas = None
label_vidas = None
label_mensaje = None
label_letras = None
label_palabra = None

def init():
    global entry, label_acertadas, label_falladas, label_vidas, label_mensaje, label_letras, label_palabra

    # VENTANA PRINCIPAL
    root = tk.Tk()
    root.title("AHORCADOZzz")
    root.geometry("900x700")
    root.configure(bg="#F4F4F4")

    # CONFIGURAR GRID PARA CENTRAR
    for i in range(7):
        root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # INTERFACES
    # parte superior: verde(palabrasAcertadas) | rojo(palabrasFalladas)
    frame_superior = tk.Frame(root, bg="#F4F4F4")
    frame_superior.grid(row=0, column=0, sticky="ew", pady=10)

    label_acertadas = tk.Label(frame_superior, text="ACERTADAS: 0", bg="green", fg="white", font=("Arial", 14, "bold"), width=18)
    label_acertadas.pack(side="left", expand=True)

    label_falladas = tk.Label(frame_superior, text="FALLADAS: 0", bg="red", fg="white", font=("Arial", 14, "bold"), width=18)
    label_falladas.pack(side="right", expand=True)

    # parte superior baja: vidas restantes
    frame_vidas = tk.Frame(root, bg="#F4F4F4")
    frame_vidas.grid(row=1,column=0, sticky="nsew")

    label_vidas = tk.Label(frame_vidas, text=f"VIDAS: {vidas}", font=("Arial", 14, "bold"), width=18)
    label_vidas.pack(expand=True)

    # parte central alta: mensaje para el usuario
    frame_mensaje = tk.Frame(root, bg="#F4F4F4")
    frame_mensaje.grid(row=2,column=0, sticky="nsew")

    label_mensaje = tk.Label(frame_mensaje, text="¡Bienvenido a AhorcadoZzz!", font=("Arial", 14))
    label_mensaje.pack(expand=True)

    # parte central: input
    frame_input = tk.Frame(root, bg="#F4F4F4")
    frame_input.grid(row=3, column=0, sticky="nsew", pady=10)

    entry = tk.Entry(frame_input, font=("Arial", 18), width=10, justify="center")
    entry.pack(expand=True)
    entry.focus()
    entry.bind("<Return>", procesar_letra)

    # parte central baja: letras usadas
    frame_letras = tk.Frame(root, bg="#F4F4F4")
    frame_letras.grid(row=4, column=0, sticky="nsew")

    label_letras = tk.Label(frame_letras, text="LETRAS USADAS: -", font=("Arial", 14), bg="#F4F4F4")
    label_letras.pack(expand=True)

    # parte baja arriba: palabra oculta
    frame_palabra = tk.Frame(root, bg="#F4F4F4")
    frame_palabra.grid(row=5, column=0, sticky="nsew", pady=10)

    label_palabra = tk.Label(frame_palabra, text="_ _ _ _", font=("Arial", 24, "bold"), bg="#F4F4F4")
    label_palabra.pack(expand=True)

    # parte baja: botón volver a jugar
    frame_boton = tk.Frame(root, bg="#F4F4F4")
    frame_boton.grid(row=6, column=0, sticky="nsew", pady=10)

    btn_reiniciar = tk.Button(frame_boton, text="Volver a jugar", font=("Arial", 14), width=20, height=2, command=empezar_juego)
    btn_reiniciar.pack(expand=True)

    empezar_juego()

    root.mainloop()

def empezar_juego():
    global PALABRAS, label_mensaje, palabraOculta

    label_mensaje.config(text="Nueva palabra generada, intenta adivinarla")

    reiniciar_juego()

    # obtenemos palabras aleatoria
    palabraIdx = random.randint(1,len(PALABRAS))-1
    palabraOculta = PALABRAS[palabraIdx].upper()
    actualizar_palabraActual()

def obtener_palabra():
    global palabraOculta, palabraActual

    letrasAcertadas = 0
    palabraActual = ""
    
    for i in range(0,len(palabraOculta)):
        caracterAgregar = "_"
        # si la partida ha termina y ha perdido, se muestra la palabra oculta
        if estadoPartida == 2:
            caracterAgregar = palabraOculta[i]

        # si la letra de la palabra ha sido usada por el usuario
        if palabraOculta[i] in letrasUsadas:
            letrasAcertadas += 1
            caracterAgregar = palabraOculta[i]
            
        if i == 0:
            palabraActual += caracterAgregar
        else:
            palabraActual += f" {caracterAgregar}"

    if letrasAcertadas == len(palabraOculta):
        victoria()

    return palabraActual

def procesar_letra(event):
    global entry, label_mensaje, letrasUsadas, vidas

    try:
        letra = entry.get()[0].upper() # nos quedamos unicamente con el primer caracter y lo pasamos a mayúsculas
    except IndexError:
        label_mensaje.config(text="Debes introducir al menos una letra")
    else:
        entry.delete(0, tk.END)
        if estadoPartida == 0:
            # comprobamos si la letra NO ha sido usada ya
            if not letra in letrasUsadas:
                letrasUsadas += letra
                if letra in palabraOculta:
                    label_mensaje.config(text="Esa letra está en la palabra oculta")
                    actualizar_palabraActual()
                else:
                    label_mensaje.config(text="Esa letra no está en la palabra oculta, prueba con otra")
                    vidas -= 1
                    if vidas == 0:
                        derrota()
                    actualizar_vidas()
                    actualizar_letrasUsadas()
            else:
                label_mensaje.config(text="Esa letra ya la has usado, prueba con otra")
        else:
            if estadoPartida == 1:
                label_mensaje.config(text="¡Has acertado la palabra! Si quieres volver a jugar pulsa el botón de la parte inferior")
            else:
                label_mensaje.config(text="No has acertado la palabra, si quieres volver a intentarlo pulsa el botón de la parte inferior")

def actualizar_letrasUsadas():
    global letrasUsadas, label_letras

    nuevoTexto = "LETRAS USADAS: "
    # mostramos unicamente las letras que no están en la palabra oculta
    if len(letrasUsadas) > 0:
        esLaPrimeraLetraQueSeMuestra = True
        for c in letrasUsadas:
            if not c in palabraOculta:
                if esLaPrimeraLetraQueSeMuestra:
                    esLaPrimeraLetraQueSeMuestra = False
                    nuevoTexto += c
                else:
                    nuevoTexto += f", {c}"
    else:
        nuevoTexto += "-"

    label_letras.config(text=nuevoTexto)

def actualizar_palabraActual():
    global label_palabra

    label_palabra.config(text=obtener_palabra())

def actualizar_vidas():
    global vidas, label_vidas

    label_vidas.config(text=f"VIDAS: {vidas}")

def victoria():
    global palabrasAcertadas, label_mensaje, label_acertadas, estadoPartida, label_palabra

    estadoPartida = 1
    palabrasAcertadas += 1

    label_acertadas.config(text=f"ACERTADAS: {palabrasAcertadas}")
    label_palabra.config(fg="#00CE00")

    label_mensaje.config(text="¡Has acertado la palabra! Si quieres volver a jugar pulsa el botón de la parte inferior")

def derrota():
    global label_mensaje, palabrasFalladas, label_falladas, estadoPartida, label_palabra

    estadoPartida = 2
    palabrasFalladas += 1

    label_falladas.config(text=f"FALLADAS: {palabrasFalladas}")
    label_palabra.config(fg="#FF0000") # cambiamos el color del texto

    label_mensaje.config(text="No has acertado la palabra, si quieres volver a intentarlo pulsa el botón de la parte inferior")

    actualizar_palabraActual()

def reiniciar_juego():
    global CANTIDAD_VIDAS, vidas, letrasUsadas, palabraOculta, palabraActual, label_palabra, estadoPartida

    vidas = CANTIDAD_VIDAS
    letrasUsadas = []
    palabraOculta = ""
    palabraActual = ""
    estadoPartida = 0
    label_palabra.config(fg="#000000")

    actualizar_letrasUsadas()
    actualizar_vidas()

init()