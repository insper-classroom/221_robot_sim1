#! /usr/bin/env python3
# -*- coding:utf-8 -*-

# Rodar com 
# roslaunch my_simulation rampa.launch


from __future__ import print_function, division
import rospy
import numpy as np
import numpy
import tf
import math
import cv2
import time
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image, CompressedImage, LaserScan
from cv_bridge import CvBridge, CvBridgeError
from numpy import linalg
from tf import transformations
from tf import TransformerROS
import tf2_ros
from geometry_msgs.msg import Twist, Vector3, Pose, Vector3Stamped

from nav_msgs.msg import Odometry
from std_msgs.msg import Header


import visao_module


bridge = CvBridge()

cv_image = None
media = []
centro = []
area = 0.0 # Variavel com a area do maior contorno

distancia = 10000

resultados = [] # Criacao de uma variavel global para guardar os resultados vistos

x = 0
y = 0
z = 0 
id = 0

topico_odom = "/odom"

# Apenas valores para inicializar
x = -1000
y = -1000
z = -1000

def recebeu_leitura(dado):
    """
        Grava nas variáveis x,y,z a posição extraída da odometria
        Atenção: *não coincidem* com o x,y,z locais do drone
    """
    global x
    global y 
    global z 

    x = dado.pose.pose.position.x
    y = dado.pose.pose.position.y
    z = dado.pose.pose.position.z


def scaneou(dado):
    global distancia
    print("Faixa valida: ", dado.range_min , " - ", dado.range_max )
    print("Leituras:")
    print(np.array(dado.ranges).round(decimals=2))
    distancia = dado.ranges[0]
    #print("Intensities")
    #print(np.array(dado.intensities).round(decimals=2))

# A função a seguir é chamada sempre que chega um novo frame
def roda_todo_frame(imagem):
    print("frame")
    global cv_image
    global media
    global centro
    global area
    global resultados

    now = rospy.get_rostime()
    imgtime = imagem.header.stamp
    lag = now-imgtime # calcula o lag
    delay = lag.nsecs

    try:
        temp_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        cv_image = temp_image.copy()
        centro, media, area = visao_module.identifica_cor(cv_image)
        # ATENÇÃO: ao mostrar a imagem aqui, não podemos usar cv2.imshow() dentro do while principal!! 
        cv2.imshow("cv_image", cv_image)
        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)
    
if __name__=="__main__":
    rospy.init_node("Q3")

    topico_imagem = "/camera/image/compressed"

    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
    recebe_scan = rospy.Subscriber("/scan", LaserScan, scaneou)
    # Cria um subscriber que chama recebeu_leitura sempre que houver nova odometria
    recebe_odo = rospy.Subscriber(topico_odom, Odometry , recebeu_leitura)
    print("Usando ", topico_imagem)

    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)

    try:
        vel = Twist(Vector3(0,0,0), Vector3(0,0,0))
        
        voltando = False
        while not rospy.is_shutdown():

            print (area)

            if area <  50:
                # Nao encontrei o objeto, entao, gira
                vel = Twist(Vector3(0,0,0), Vector3(0,0,math.radians(10)))
            elif centro[0] - 20 < media[0] < centro[0] + 20:
                # Esta centralizado, vai para frente
                vel = Twist(Vector3(0.2,0,0), Vector3(0,0,0))
                # Leitura do lidar
                if distancia <= .3:
                    voltando = True
                if voltando:    
                    vel = Twist(Vector3(-0.2,0,0), Vector3(0,0,0))
                    # Verificar a odometria
                    if (x**2 + y**2)**0.5 < .20:
                        vel = Twist(Vector3(0,0,0), Vector3(0,0,0))
            else:
                # Encontrei, mas nao estou centralizado
                if media[0] > centro[0]:
                    # Vai para a direita
                    vel = Twist(Vector3(0,0,0), Vector3(0,0,-0.2))
                if media[0] < centro[0]:
                    # Vai para a esquerda
                    vel = Twist(Vector3(0,0,0), Vector3(0,0,0.2))
                
            velocidade_saida.publish(vel)
            rospy.sleep(0.1)

    except rospy.ROSInterruptException:
        print("Ocorreu uma exceção com o rospy")


