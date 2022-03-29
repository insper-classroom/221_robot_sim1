#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import math

import biblioteca

def segmenta_linha_azul(bgr):
    """Não mude ou renomeie esta função
        deve receber uma imagem e segmentar as faixas brancas
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mini = (210//2, 50, 50)
    maxi = (260//2, 255, 255)
    mask = cv2.inRange(hsv, mini, maxi)
    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, np.ones((3,3),dtype=np.uint8))
    mask = cv2.morphologyEx(mask,cv2.MORPH_CLOSE, np.ones((3,3),dtype=np.uint8))
    
    return mask

def estimar_linha_nas_faixas(img, mask):
    """Não mude ou renomeie esta função
        deve receber uma imagem preta e branca e retorna dois pontos que formen APENAS uma linha em cada faixa. Desenhe cada uma dessas linhas na iamgem.
         formato: [[(x1,y1),(x2,y2)], [(x1,y1),(x2,y2)]]
    """

    edges = cv2.Canny(mask,50,100)
    mask[:] = edges[:]
    lines = cv2.HoughLinesP(edges,1,math.radians(1),50,None,100,25)

    if lines is None or len(lines) < 1:
        return None

    
    len_L2 = 0
    len_L1 = 0
    len_L3 = 0
    x1_1, y1_1, x2_1, y2_1 = 0, 0, 0, 0
    x1_2, y1_2, x2_2, y2_2 = 0, 0, 0, 0
    x1_3, y1_3, x2_3, y2_3 = 0, 0, 0, 0
    
    for ((x1,y1,x2,y2),) in lines:
        m = (y2-y1)/(x2-x1)
        len2 = (y2-y1)**2 + (x2-x1)**2

        if m > 0 and len2 > len_L2:
            len_L2 = len2
            x1_2 = x1
            y1_2 = y1
            x2_2 = x2
            y2_2 = y2
        elif m < -0.86 and len2 > len_L1 :
            len_L1 = len2
            x1_1 = x1
            y1_1 = y1
            x2_1 = x2
            y2_1 = y2
        elif m < 0 and m > -0.86 and len2 > len_L3:
            len_L3 = len2
            x1_3 = x1
            y1_3 = y1
            x2_3 = x2
            y2_3 = y2

    if len_L1 > 0:
        cv2.line(img, (int(x1_1), int(y1_1)), (int(x2_1), int(y2_1)),(0,128,0),5)
        
    if len_L2 > 0:
        cv2.line(img, (int(x1_2), int(y1_2)), (int(x2_2), int(y2_2)),(0,128,0),5)

    if len_L3 > 0:
        cv2.line(img, (int(x1_3), int(y1_3)), (int(x2_3), int(y2_3)),(0,128,0),5)
    
    return [[(x1_1, y1_1),(x2_1, y2_1)],[(x1_2, y1_2),(x2_2, y2_2)],[(x1_3, y1_3),(x2_3, y2_3)]]


def calcular_equacao_das_retas(linhas):
    """Não mude ou renomeie esta função
        deve receber dois pontos que estejam em cada uma das faixas e retornar a equacao das duas retas. Onde y = h + m * x. Formato: [(m1,h1), (m2,h2)]
    """

    (linha_1, linha_2, linha_3) = linhas
    ((x1_1, y1_1),(x2_1, y2_1)) = linha_1
    ((x1_2, y1_2),(x2_2, y2_2)) = linha_2
    ((x1_3, y1_3),(x2_3, y2_3)) = linha_3

    m1 = (y2_1 - y1_1)/(x2_1 - x1_1)
    h1 = y1_1 - m1 * x1_1

    m2 = (y2_2 - y1_2)/(x2_2 - x1_2)
    h2 = y1_2 - m2 * x1_2

    m3 = (y2_3 - y1_3)/(x2_3 - x1_3)
    h3 = y1_3 - m3 * x1_3

    return [(m1,h1), (m2,h2), (m3,h3)]

def calcular_ponto_de_fuga(img, equacoes):
    """Não mude ou renomeie esta função
        deve receber duas equacoes de retas e retornar o ponto de encontro entre elas. Desenhe esse ponto na imagem.
    """

    ((m1,h1), (m2,h2), (m3,h3)) = equacoes

    xf1 = (h2-h1)/(m1-m2)
    yf1 = m1*xf1 + h1

    xf2 = (h3-h2)/(m2-m3)
    yf2 = m2*xf2 + h2

    if img is not None:
        cv2.circle(img,(int(xf1),int(yf1)),5,(0,255,0),-1)
        cv2.circle(img,(int(xf2),int(yf2)),5,(0,0,255),-1)

    return img, (xf1,yf1), (xf2,yf2)


if __name__ == "__main__":
    linhas = [[(3,2.5),(4,0.6)],[(1,2.4),(0.6,1.1)]]
    equa = calcular_equacao_das_retas(linhas)
    print(equa)
    _, pontof = calcular_ponto_de_fuga(None, equa)
    print(pontof)