from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

import RPi.GPIO as GPIO
import time
import rsa
import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import subprocess
from subprocess import call

import os
from werkzeug.utils import secure_filename

import requests

from pruebaook import ook, fsk

app = Flask(__name__)

# Para una mejor proteccion
app.secret_key = 'your secret key'

# Detalles de la base de datos a utilizar
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'stoke_user'
app.config['MYSQL_PASSWORD'] = '1997'
app.config['MYSQL_DB'] = 'STOKES'

#Asignacion de la ruta de la llave
UPLOAD_FOLDER = '/home/pi/Desktop/Exito/Asimetrico'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Inicializacmos mysql
mysql = MySQL(app)

pin=7
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, True)

# Redireccionamiento a la pagina de Ingreso
@app.route('/', methods=['GET', 'POST'])
def ingreso():
    
    msg = ''
    # Verifica si las solicitudes POST del Usuario y la Contraseña existen
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Crea las variables de accceso
        username = request.form['username']
        password = request.form['password']
        # Verifica si la cuenta existe usando MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE username = %s AND password = %s', (username, password,))
        # Busca los registros y retorna los resultados
        account = cursor.fetchone()
        # Verificamos si los datos de la cuenta existen en la base de datos
        if account:
            # Crea los datos de la sesion
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirecciona a lka pagina de Home
            return redirect(url_for('home'))
        else:
            # Despliegue de mensaje al poner contrasela o usuario erroneo
            msg = 'Usuario o contraseña erronea!'
    # Muestra la pagina de Ingreso
    return render_template('index.html', msg=msg)

# Redirreciona a la pagina de desconectado redireccionando a la pagina de ingreso
@app.route('/salida')
def salida():
    # remueve los datos de la sesion del usuario para desconectarlo
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Se redirecciona a la pagina de Ingreso
   return redirect(url_for('ingreso'))


# Redireccionamiento a la pagina de Home para los usuarios certificados
@app.route('/home', methods=['GET', 'POST'])
def home():
    # Verificamos si el usuario esta loggeado
    if 'loggedin' in session:
        # Se muestra la pagina Home con el usuario adjunto.
        return render_template('home.html', username=session['username'])
    # Si no esta loggeado lo redirecciona a la pagina de ingreso
    return redirect(url_for('ingreso'))



@app.route('/proxyScript', methods=['GET', 'POST'])
def indexProxy():
    if request.method == "POST":
        ip=request.form['ip']
        file = request.files['file']
        formulario = {}
        if len(ip) <= 0:
            print('ip is not defined')
            #return render_template('home.html', username=session['username'])
            #return '{ "error": true}'
            return render_template('home.html', username=session['username'])
        
       
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            #return render_template('home.html', username=session['username'])
            return '{ "error": true}'
        else: 
            #Setting values
            #formulario['frecuencia'] = request.form['frecuencia']
            formulario['frecuencia'] = request.form.get('frecuencia')
            formulario['modulacion'] = request.form.get('modulacion')
            #formulario['file'] = request.files['file']
            #To do
            #enviar el file del formulario por post a la ip escrita en el formulario
            #url = 'http://httpbin.org/post'
            #files = {'file': open('public.key', 'rb')}
            #r = requests.post(url, files=files)
            file = request.files['file'].name
            print(file)
            r = requests.post("http://"+ip+":5000/execScript", files=request.files ,data=formulario)            
            return render_template('home.html', username=session['username'])
        return '{ "error": false}'


@app.route('/execScript', methods=['GET', 'POST'])
def index():
    print(request.form['frecuencia'])
    if request.method == "POST":
        
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            #return render_template('home.html', username=session['username'])
            return '{ "error": true}'
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            #return render_template('home.html', username=session['username'])
            return '{ "error": true}'
        frecuencia = request.form.get('frecuencia')
        print(len(frecuencia))
        if len(frecuencia) <= 0:
            print('Frecuencia is not defined')
            #return render_template('home.html', username=session['username'])
            return '{ "error": true}'
        #Guardar archivo
        filename = secure_filename(file.filename)
        print("file:" + filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        #Validando clave
        """with open("file", "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        message = open("claves.txt", "rb").read()
        signature = open("test.encrypted", "rb").read()
        """
        try:
            """verify = public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            """
            os.system("gpg -d /home/pi/Desktop/Exito/Asimetrico/Luminarias.gpg > /home/pi/Desktop/Exito/Asimetrico/claves.txt")
            print("Ha sido verificada la firma")
            print ("Transmitiendo\n")
            print(frecuencia)
            F=int(frecuencia)
            #archivo= mmesage.name()
            #print(archivo)
            #pin=7
            select = request.form.get('modulacion')

            
            if (select=="OOK"):
                
                print(select)
                ook(F, pin, "claves.txt")
                GPIO.output(pin, True)
                #subprocess.call(["./a.out", frecuencia]) 
            else:
                print(select)
                fsk(F, pin, "claves.txt")
                GPIO.output(pin, True)
                #subprocess.call(["./FSK", frecuencia]) 

        except:
            print("Advertencia!!!, no se ha verificado la firma")

    #return render_template('home.html', username=session['username'])
    return '{ "error": false}'

GPIO.output(pin, True)

if __name__=='__main__':

    #Ejecutar el servidor en Debug
    app.run(debug = True, host='0.0.0.0')