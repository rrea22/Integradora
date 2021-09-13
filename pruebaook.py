import manchester_code
from manchester_code import encode, decode, decode_bits
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
def ook(frecuencia, pin, filename):
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    #GPIO.output(pin, True)
    #GPIO.output(pin, True)
    T=1/frecuencia
    datos=[]
    with open(filename) as fname:
        for lineas in fname:
            line=lineas.split()
            datos.append(line)
        fname.close()
    #print(datos)   
    for i in datos[0]:
        #codificar=i.encode("utf-8")  -->0 --> /b0
        #m=encode(i.encode("utf-8"))   ->> bZU
        manchester=''.join(['{:08b}'.format(j) for j in encode(i.encode("utf-8"))]) # 
        #print(manchester)
        print(manchester[::-1])
        
        for j in manchester[::-1]:
            if j=='1':
                GPIO.output(pin, True)
                time.sleep(T)
                #print(True)
            else:
                GPIO.output(pin, False)
                time.sleep(T)
                #print(False)

    return "Se ha transmitido la clave al usuario"

def fsk(frecuencia, pin, filename):
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    #GPIO.output(pin, True)
    #GPIO.output(pin, True)
    T_0=1/(frecuencia*1.5)
    T_1=1/frecuencia
    datos=[]
    with open(filename) as fname:
        for lineas in fname:
            line=lineas.split()
            datos.append(line)
        fname.close()
       
    for i in datos[0]:
        manchester=''.join(['{:08b}'.format(j) for j in encode(i.encode("utf-8"))])
        print(manchester[::-1])
        
        for j in manchester[::-1]:
            if j=='1':
                GPIO.output(pin, True)
                time.sleep(T_1)
                #print(True)
            else:
                GPIO.output(pin, False)
                time.sleep(T_0)
                #print(False)

    return "Se ha transmitido la clave con exito al usuario"