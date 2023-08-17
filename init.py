#!/usr/bin/env python3

# Creamos un archivo .env
archivo = open(".env", "w")

# Pedimos al usuario que ingrese otro string
string2 = input("Enter BOT TOKEN ID: ")

archivo.write("TOKEN="+string2 + "\n")

# Cerramos el archivo
archivo.close()

# Mostramos un mensaje de confirmación
print("Data Saved!!!")
