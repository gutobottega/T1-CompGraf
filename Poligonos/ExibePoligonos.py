# ***********************************************************************************
#   ExibePoligonos.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa exibe um polígono em OpenGL
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Sugere-se consultar também as páginas listadas
#   a seguir:
#   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#
#   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#   conforme a descrição que está nestes links:
#   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
# ***********************************************************************************

import copy
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import Ponto, Polygon
from Faixa import *

# ***********************************************************************************
Mapa = Polygon()
ConvexHull = Polygon()

EspacoDividido = ConjuntoDeFaixas()

# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()
PontoClicado = Ponto()

def minimoMaximoLocal(p,pe,pd):
    if(pe.y > p.y and pd.y > p.y): return True
    if(pe.y < p.y and pd.y < p.y): return True
    return False


def inclusaoPonto(ponto:Ponto):
    
    interseccao = 0
    conta = True
    Dir = Ponto(-1,0)
    ponto2 = ponto + Dir * 100
    DesenhaLinha(ponto, ponto2)
    arestasValidas = []
    for i in range(Mapa.getNVertices()):
        P1, P2 = Mapa.getAresta(i)
        if((P1.y <= ponto.y and P2.y >= ponto.y) or (P1.y >= ponto.y and P2.y <= ponto.y)):
            arestasValidas += [i]
    for i in  arestasValidas:
        P1, P2 = Mapa.getAresta(i)
        if HaInterseccao(ponto,ponto2, P1, P2):
            if(P1.y == ponto.y):
                px1, px2 = Mapa.getAresta(i - 1)
                if(minimoMaximoLocal(P1, px1, P2)):
                    interseccao += 1
            else: interseccao += 1
    return interseccao % 2 != 0

# ********************************************************************** */
#                                                                        */
#  Calcula a interseccao entre 2 retas (no plano "XY" Z = 0)             */
#                                                                        */
# k : ponto inicial da reta 1                                            */
# l : ponto final da reta 1                                              */
# m : ponto inicial da reta 2                                            */
# n : ponto final da reta 2                                              */
# 
# Retorna:
# 0, se não houver interseccao ou 1, caso haja                                                                       */
# int, valor do parâmetro no ponto de interseção (sobre a reta KL)       */
# int, valor do parâmetro no ponto de interseção (sobre a reta MN)       */
#                                                                        */
# ********************************************************************** */
def intersec2d(k: Ponto, l: Ponto, m: Ponto, n: Ponto):
    det = (n.x - m.x) * (l.y - k.y)  -  (n.y - m.y) * (l.x - k.x)

    if (det == 0.0):
        return 0, None, None # não há intersecção

    s = ((n.x - m.x) * (m.y - k.y) - (n.y - m.y) * (m.x - k.x))/ det
    t = ((l.x - k.x) * (m.y - k.y) - (l.y - k.y) * (m.x - k.x))/ det

    return 1, s, t # há intersecção

# **********************************************************************
# HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto)
# Detecta interseccao entre os pontos
#
# **********************************************************************
def HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto) -> bool:
    ret, s, t = intersec2d( k,  l,  m,  n)

    if not ret: return False

    return s>=0.0 and s <=1.0 and t>=0.0 and t<=1.0



def DesenhaLinha (P1, P2):
    glBegin(GL_LINES)
    glVertex3f(P1.x,P1.y,P1.z)
    glVertex3f(P2.x,P2.y,P2.z)
    glEnd()

# ***********************************************************************************
def reshape(w,h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Cria uma folga na Janela de Selecão, com 10% das dimensoes do poligono
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    glOrtho(Min.x-BordaX, Max.x+BordaX, Min.y-BordaY, Max.y+BordaY, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

# ***********************************************************************************
def display():
    global PontoClicado

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glColor3f(1.0, 1.0, 0.0)
    Mapa.desenhaPoligono()

    glColor3f(1.0, 0.0, 0.0)
    
    Esq = Ponto(0,0)
    Dir = Ponto (-1,0)

    
    #Dir.imprime("Dir:")

    # Calcula o ponto da esquerda
    #Esq.x = PontoClicado.x + Dir.x * 100
    #Esq.y = PontoClicado.y + Dir.y * 100
    Esq = PontoClicado + Dir * 100

    # desenha linha horizontal
    glColor3f(0,1,0) # R, G, B  [0..1]
    DesenhaLinha(PontoClicado, Esq)
    #Esq.imprime("Esq")
    
    #F = CalculaFaixa(PontoClicado);

    glColor3f(1,0,0) # R, G, B  [0..1]
    # Testa a interseccao da linha horizontal com cada aresta do poligono
    # Qdo ocorrer interseccao, pinta a aresta em vermelho
    for i in range(Mapa.getNVertices()):
        P1, P2 = Mapa.getAresta(i)
        #if(PassaPelaFaixa(i,F))
        if HaInterseccao(PontoClicado,Esq, P1, P2):
            Mapa.desenhaAresta(i)

    #Mapa.desenhaVertices()
    glutSwapBuffers()

# ***********************************************************************************
# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
#ESCAPE = '\033'
ESCAPE = b'\x1b'
def keyboard(*args):
    print (args)
    # If escape is pressed, kill everything.
    if args[0] == b'q':
        os._exit(0)
    if args[0] == ESCAPE:
        os._exit(0)
    if args[0] == b'p':
        Mapa.imprimeVertices()
    if args[0] == b'a':
        Mapa.LePontosDeArquivo("EstadoRS.txt")
    if args[0] == b'1':
        P1, P2 = Mapa.getAresta(9)
        P1.imprime()
        P2.imprime()

# Forca o redesenho da tela
    glutPostRedisplay()
# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        pass
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        pass
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        pass
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        pass

    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouse(button: int, state: int, x: int, y: int):
    global PontoClicado
    if (state != GLUT_DOWN): 
        return
    if (button != GLUT_RIGHT_BUTTON):
        return
    #print ("Mouse:", x, ",", y)
    # Converte a coordenada de tela para o sistema de coordenadas do 
    # universo definido pela glOrtho
    vport = glGetIntegerv(GL_VIEWPORT)
    mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    realY = vport[3] - y
    worldCoordinate1 = gluUnProject(x, realY, 0, mvmatrix, projmatrix, vport)

    PontoClicado = Ponto (worldCoordinate1[0],worldCoordinate1[1], worldCoordinate1[2])
    PontoClicado.imprime("Ponto Clicado:")

    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouseMove(x: int, y: int):
    #glutPostRedisplay()
    return

def ImprimeFaixas():
    global EspacoDividido
    f = Faixa()
    for i in range(10):
        print("Faixa", i,"-> ", end='')
        f = EspacoDividido.getFaixa(i)
        for a in range (f.getNroDeArestas()):
            print(f.getAresta(a), end=' ')
        print()


def CriaFaixas():
    global EspacoDividido
 
    EspacoDividido.CriaFaixas(10)
    # Exemplos de teste. O primeiro parametro da CadastraArestaNaFaixa
    # eh a faixa o segundo eh a arestra
    EspacoDividido.CadastraArestaNaFaixa(5,222)
    EspacoDividido.CadastraArestaNaFaixa(2,10)
    for i in range (100):
        EspacoDividido.CadastraArestaNaFaixa(5,i)
    EspacoDividido.CadastraArestaNaFaixa(3,11)
    for i in range (20):
        EspacoDividido.CadastraArestaNaFaixa(9,i)

def init():
    # Define a cor do fundo da tela (AZUL)
    glClearColor(0, 0, 1, 1)
    global Min, Max
    Min, Max = Mapa.LePontosDeArquivo("PoligonoDeTeste.txt")
    #Mapa.imprimeVertices()
    # p = Ponto(15,8)
    # p2 = Ponto(15,2)
    # p3 = Ponto(7,2)
    # p4 = Ponto(8,5)
    
    # p = Ponto(16,7)
    # p2 = Ponto(2,4)
    # p3 = Ponto(5,4)
    # p4 = Ponto(16,4)
    
    # p = Ponto(10,8)
    # p2 = Ponto(15,0)
    # p3 = Ponto(15,5)
    # p4 = Ponto(11,2)
    
    # p = Ponto(5,3)
    # p2 = Ponto(2,2)
    # p3 = Ponto(7,1)
    # p4 = Ponto(3,1)
    
    p = Ponto(20,7)
    p2 = Ponto(2,4)
    p3 = Ponto(12,1)
    p4 = Ponto(16,1)
    
    p.imprime(inclusaoPonto(p))
    p2.imprime(inclusaoPonto(p2))
    p3.imprime(inclusaoPonto(p3))
    p4.imprime(inclusaoPonto(p4))
   
    
    #CriaFaixas()
    #ImprimeFaixas()


# ***********************************************************************************
# Programa Principal
# ***********************************************************************************


glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(500, 500)
glutInitWindowPosition(100, 100)
wind = glutCreateWindow("Exibe Polignos")
glutDisplayFunc(display)
#glutIdleFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
init()

try:
    glutMainLoop()
except SystemExit:
    pass
