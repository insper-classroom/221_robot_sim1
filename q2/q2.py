#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Este NÃO é um programa ROS

from __future__ import print_function, division 

import cv2
import os,sys, os.path
import numpy as np
from object_detection_webcam import detect

from hough_helper import desenha_circulos

print("Rodando Python versão ", sys.version)
print("OpenCV versão: ", cv2.__version__)
print("Diretório de trabalho: ", os.getcwd())

# Arquivos necessários
video = "dogtraining.mp4"

if __name__ == "__main__":

    # Inicializa a aquisição da webcam
    cap = cv2.VideoCapture(video)


    print("Se a janela com a imagem não aparecer em primeiro plano dê Alt-Tab")

    distancia_ant = 9e99
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if ret == False:
            #print("Codigo de retorno FALSO - problema para capturar o frame")
            #cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            break
            

        # Our operations on the frame come here
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Identificar o cachorro
        img, resultados = detect(frame)
        # Identificar a bola por Hough Circles
        circles = cv2.HoughCircles(gray, method=cv2.HOUGH_GRADIENT, dp=1, minDist=12, param1=100, param2=30, minRadius=38, maxRadius=50)
        img = desenha_circulos(img, circles)

        #Centro do cachorro
        if len(resultados) > 0 and circles is not None and len(circles) > 0:
            x_dog = (resultados[0][2][0] + resultados[0][3][0])/2
            y_dog = (resultados[0][2][1] + resultados[0][3][1])/2
            x_ball = circles[0][0][0]
            y_ball = circles[0][0][1]
            distancia = ((x_dog-x_ball)**2 + (y_dog-y_ball)**2)**0.5 
            cv2.putText(img, f'Distancia: {distancia:.2f}', (10,50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)

            if distancia > distancia_ant:
                cv2.putText(img, f'REX, CORRE!!!!', (100,150), cv2.FONT_HERSHEY_COMPLEX, 3, (0,0,255), 2)

            distancia_ant = distancia

        # NOTE que em testes a OpenCV 4.0 requereu frames em BGR para o cv2.imshow
        cv2.imshow('imagem', img)

        # Pressione 'q' para interromper o video
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

