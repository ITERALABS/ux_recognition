
# -- ---------------------------------------------------------------------------------------------------------------- #
# -- proyecto:
# -- codigo:
# -- repositorio:
# -- ---------------------------------------------------------------------------------------------------------------- #

# cargar librerias
import pandas as pd
import numpy as np
import time
from itertools import groupby
from operator import itemgetter
from pandas import ExcelWriter

# crear cuadro de datos
umbral = 0.80
usuarios = 12
emociones = ['engagement', 'joy', 'anger', 'surprise', 'fear', 'contempt', 'sadness', 'disgust']
datos_ux = pd.DataFrame({'usuario': list(np.repeat(['usuario_' + str(i+1) for i in range(0, usuarios)], len(emociones))),
                         'emocion': list([emociones[i] for i in range(0, len(emociones))])*usuarios})

# datos_ux = pd.concat([datos_ux, pd.DataFrame(columns=['ocurrencia_' + str(i) for i in range(1, 21)])], axis=1)

for hojas in range(1, 13):
    hojas = 1
    print(hojas)
    # cargar datos
    datos = pd.read_excel('datos/imotion_data.xlsx', sheet_name='Sujeto_' + str(hojas))

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

    for l in range(0, len(emociones)):
        # localizar primer valor que es > umbral
        data = list(np.where(datos_norm[emociones[l]] >= umbral)[0])

        # localizar los rangos de tiempos donde se presentaron mediciones por encima del umbral
        rangos = []
        for k, g in groupby(enumerate(data), lambda x: x[0]-x[1]):
            group = (map(itemgetter(1), g))
            group = list(map(int, group))
            rangos.append((group[0], group[-1]))

            mensaje = [str('(' + str(datos_norm['timestamp'][rangos[i][0]]) + ', ' +
                       str(datos_norm['timestamp'][rangos[i][1]]) + ')') for i in range(0, len(rangos))]

        mensajes.append(mensaje)

    o = 8*(hojas-1)
    for m in range(0, len(mensajes)):
        for n in range(1, len(mensajes[m])):
            datos_ux.loc[m+o, 'ocurrencia_' + str(n)] = mensajes[m][n]

writer = ExcelWriter('data_ux.xlsx')
datos_ux.to_excel(writer, 'datos', index=False)
writer.save()
