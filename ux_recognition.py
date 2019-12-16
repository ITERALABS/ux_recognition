
# -- ------------------------------------------------------------------------------------------------------ #
# -- proyecto: Analisis de datos de reconocimiento facial para medición de pruebas UX
# -- codigo: ux_recognition.py
# -- autor: Francisco ME
# -- licencia: MIT
# -- repositorio: https://github.com/ITERALABS/ux_recognition
# -- ------------------------------------------------------------------------------------------------------ #

import pandas as pd                                       # Operaciones con DataFrames
import numpy as np                                        # Operaciones con arreglos
import time                                               # Operaciones con unidades de tiempo
from itertools import groupby                             # Funcion de agrupamiento iterativo
from operator import itemgetter                           # Funcion de obtencion de items en objetos
from pandas import ExcelWriter                            # Escribir hojas de excel

# -- Etapa inicial: Crear DataFrame para almacenar datos
# nombre de archivo con los datos
archivo = 'imotion_data.xlsx'
# Cantidad de hojas a leer
hojas_n = 12
# umbral de medicion (0-1)
umbral = 0.80
# usuarios que realizaron la prueba
usuarios = 12
# emociones que mide el software con su modulo de reconocimiento facial
emociones = ['engagement', 'joy', 'anger', 'surprise', 'fear', 'contempt', 'sadness', 'disgust']
# data frame
lista_u = list(np.repeat(['usuario_' + str(i+1) for i in range(0, usuarios)], len(emociones)))
lista_e = list([emociones[i] for i in range(0, len(emociones))])*usuarios
datos_ux = pd.DataFrame({'usuario': lista_u, 'emocion': lista_e})

# -- Etapa de procesamiento: Leer una hoja de datos, procesarlos y dejarlos listos para escribir excel final
for hojas in range(1, hojas_n+1):
    print('procesando datos de hoja: ' + str(hojas))
    # cargar datos
    datos = pd.read_excel('datos/' + archivo, sheet_name='Sujeto_' + str(hojas))

    # crear columa timestamp_v
    datos['Timestamp'] = [time.strftime('%M:%S', time.gmtime(i)) for i in datos['Timestamp']/30]

    # nuevo data frame para datos normalizados
    datos_norm = datos

    # cambiar nombres de columnas
    datos_norm.columns = ['timestamp'] + emociones

    # normalizacion de datos
    for j in range(0, len(emociones)):
        datos_norm[emociones[j]] = datos_norm[emociones[j]]/max(datos_norm[emociones[j]])

    # -- ciclo para cada emocion
    em = 1
    mensajes = list()

    for emocion in range(0, len(emociones)):
        # localizar primer valor que es > umbral
        data = list(np.where(datos_norm[emociones[emocion]] >= umbral)[0])

        # localizar los rangos de tiempos donde se presentaron mediciones por encima del umbral
        rangos = []
        for k, g in groupby(enumerate(data), lambda x: x[0]-x[1]):
            group = (map(itemgetter(1), g))
            group = list(map(int, group))
            rangos.append((group[0], group[-1]))

            # Construccion de parentesis con inicio y fin de periodo
            mensaje = [str('(' + str(datos_norm['timestamp'][rangos[i][0]]) + ', ' +
                       str(datos_norm['timestamp'][rangos[i][1]]) + ')') for i in range(0, len(rangos))]

        # Lista final de momentos de reconocimiento de emocion
        mensajes.append(mensaje)

    # enumeracion de ocurrencias para cada emocion
    o = 8*(hojas-1)
    for m in range(0, len(mensajes)):
        for n in range(1, len(mensajes[m])):
            datos_ux.loc[m+o, 'ocurrencia_' + str(n)] = mensajes[m][n]

# -- escribir en excel DataFrame final
writer = ExcelWriter('data_ux_p.xlsx')
datos_ux.to_excel(writer, 'datos', index=False)
writer.save()
