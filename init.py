#!/usr/bin/env python3

# Creamos un archivo .env
archivo = open(".env", "w")

# Pedimos al usuario que ingrese un string
string1 = input("Envieme su API de OpenAi: ")

# Pedimos al usuario que ingrese otro string
string2 = input("Envieme el token de Telegram: ")

# Añadimos los strings al archivo
archivo.write("API_KEY="+string1 + "\n")
archivo.write("TOKEN="+string2 + "\n")

# Cerramos el archivo
archivo.close()

# Mostramos un mensaje de confirmación
print("Listo, ya puede continuar con el proximo paso")