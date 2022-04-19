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

from math import ceil, sqrt
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import Ponto, Polygon
from Faixa import *
from random import randrange, uniform
import time

# ***********************************************************************************
Mapa = Polygon()
ConvexHull = Polygon()

EspacoDividido = ConjuntoDeFaixas()
numeroDeFaixas = 10
quantidadePontos = 200

# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()
PontoClicado = Ponto()

contadorInterseccao = 0
contadorProdVetorial = 0
dentro = []
dentroConvex = []
fora = []
pontos = []

def pegaMenorMaior():
    menorX = 0
    maiorX = 0
    menorY = 0
    maiorY = 0
    for i in range(Mapa.getNVertices()):
        p = Mapa.getVertice(i);
        if Mapa.getVertice(menorX).x > p.x: menorX = i
        if Mapa.getVertice(menorY).y > p.y: menorY = i
        if Mapa.getVertice(maiorX).x < p.x: maiorX = i
        if Mapa.getVertice(maiorY).y < p.y: maiorY = i
    return [menorX, maiorX, menorY, maiorY]

def prodVetorial (v1, v2):
    global contadorProdVetorial
    contadorProdVetorial += 1
    
    vresult = Ponto()
    vresult.x = v1.y * v2.z - (v1.z * v2.y)
    vresult.y = v1.z * v2.x - (v1.x * v2.z)
    vresult.z = v1.x * v2.y - (v1.y * v2.x)
    
    return vresult

def prodEscalar(v1, v2):
    return v1.x*v2.x + v1.y*v2.y+ v1.z*v2.z;

def anguloEscalar(v1, v2):
    prod = prodEscalar(v1,v2)
    v1N = sqrt(v1.x*v1.x + v1.y*v1.y)
    v2N = sqrt(v2.x*v2.x + v2.y*v2.y)
    return prod/(v1N*v2N)

def quickHull():
    global dentroConvex
    menorMaior = pegaMenorMaior()
    poligono = Polygon()
    poligono.inserePonto(Mapa.getVertice(menorMaior[0]))
    poligono.inserePonto(Mapa.getVertice(menorMaior[3]))
    poligono.inserePonto(Mapa.getVertice(menorMaior[1]))
    poligono.inserePonto(Mapa.getVertice(menorMaior[2]))
    
    dentro = []
    for atual in range(Mapa.getNVertices()):
        if atual in menorMaior:
            pass
        elif  inclusaoPontoConvexo(Mapa.getVertice(atual), poligono):
            dentro += [atual]
    vBase = Ponto(0, 0)
    atual = menorMaior[0]
    convexRetorno = [atual]
    incompleto = True
    while incompleto:
        if atual in menorMaior:
            if atual == menorMaior[0]:#menor X
                vBase = Ponto(0,1)
            elif atual == menorMaior[1]:#maior X
                vBase = Ponto(0,-1)
            elif atual == menorMaior[2]:#menor Y
                vBase = Ponto(-1,0)
            elif atual == menorMaior[3]:# maior Y
                vBase = Ponto(1,0)
        proximoAnguloMenor = 0.0
        proximo = 0
        for i in range(Mapa.getNVertices()):
            if i != atual and i not in dentro:
                p2 = Mapa.getVertice(i)
                v2 = p2 - Mapa.getVertice(atual)
                anguloAtual = anguloEscalar(vBase, v2)
                if(anguloAtual > proximoAnguloMenor): 
                    proximo = i
                    proximoAnguloMenor = anguloAtual
        if(proximo == convexRetorno[0]):
            incompleto = False
        else: 
            atual = proximo
            convexRetorno += [atual]
    return convexRetorno

def minimoMaximoLocal(p,pe,pd):
    if(pe.y > p.y and pd.y > p.y): return True
    if(pe.y < p.y and pd.y < p.y): return True
    return False

def inclusaoPontoConvexo(ponto:Ponto, poligono: Polygon):
    for i in range(poligono.getNVertices()):
        P1, P2 = poligono.getAresta(i)
        v1 = P2 - P1
        v2 = ponto - P1
        vr = prodVetorial(v1, v2)
        #print(vr.z)
        if(vr.z > 0): return False
    return True

def inclusaoPontoConcavo(ponto:Ponto, poligono: Polygon):
    interseccao = 0
    Dir = Ponto(-1,0)
    ponto2 = ponto + Dir * 1000
    arestasValidas = []
    for i in range(poligono.getNVertices()):
        P1, P2 = poligono.getAresta(i)
        if((P1.y <= ponto.y and P2.y >= ponto.y) or (P1.y >= ponto.y and P2.y <= ponto.y)):
            arestasValidas += [i]
    for i in  arestasValidas:
        P1, P2 = poligono.getAresta(i)
        if HaInterseccao(ponto,ponto2, P1, P2):
            if(P1.y == ponto.y):
                px1, __ = poligono.getAresta(i - 1)
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
def HaInterseccao(k: Ponto, l: Ponto, m: Ponto, n: Ponto):
    global contadorInterseccao
    contadorInterseccao += 1
    ret, s, t = intersec2d( k,  l,  m,  n)
    if not ret: 
        return False
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
    global PontoClicado, pontos, dentro, fora, dentroConvex

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glColor3f(1.0, 1.0, 0.0)
    Mapa.desenhaPoligono()
    glColor3f(1.0, 1.0, 1.0)
    ConvexHull.desenhaPoligono()

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
    #DesenhaLinha(PontoClicado, Esq)
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
    glPointSize(5)

    glColor3f(1,1,0)
    glBegin(GL_POINTS);
    for p in dentroConvex: 
        glVertex3f(p.x,p.y,p.z)
    glEnd();
    
    glColor3f(0,0,1)
    glBegin(GL_POINTS);
    for p in dentro:
        glVertex3f(p.x,p.y,p.z)
    glEnd();


    glColor3f(1,0,0)
    glBegin(GL_POINTS);
    for p in fora:
        glVertex3f(p.x,p.y,p.z)
    glEnd();
    
    
    glColor3f(1,0,0) # R, G, B  [0..1]
    #Mapa.desenhaVertices()
    glutSwapBuffers()

def processoInteiro(pts):
    print('\nTeste Forca Bruta com Faixas:')
    ConvexHull = Polygon()
    inicio = time.perf_counter()
    dentro, fora = testeFaixaForcaBruta(pts)
    total = time.perf_counter() - inicio
    print('Produto Vetorial:', contadorProdVetorial)
    print('Intersecção:', contadorInterseccao)
    print('Tempo execução:', total)
    print('\nTeste ConvexHull:')
    inicio = time.perf_counter()
    dentro, fora, dentroConvex = testeConvexHull(pts)
    total = time.perf_counter() - inicio
    print('Produto Vetorial:', contadorProdVetorial)
    print('Intersecção:', contadorInterseccao)
    print('Tempo execução:', total)
    print('\nTeste Força Bruta:')
    ConvexHull = Polygon()
    inicio = time.perf_counter()
    dentro, fora = testeForcaBruta(pts)
    total = time.perf_counter() - inicio
    print('Produto Vetorial:', contadorProdVetorial)
    print('Intersecção:', contadorInterseccao)
    print('Tempo execução:', total)


ESCAPE = b'\x1b'
def keyboard(*args):
    global dentro, dentroConvex, fora, pontos, contadorInterseccao, contadorProdVetorial, ConvexHull, Min, Max, quantidadePontos
    contadorInterseccao = 0
    contadorProdVetorial = 0
    if args[0] == b'z':
        print('\n Com 200 pontos:')
        processoInteiro(geraPontos(200))
        print('\n Com 2000 pontos:')
        processoInteiro(geraPontos(2000))
        print('\n Com 20000 pontos:')
        processoInteiro(geraPontos(20000))
    if args[0] == b'1':
        pontos = geraPontos(200)
        quantidadePontos = 200 
    if args[0] == b'2':
        pontos = geraPontos(2000)
        quantidadePontos = 2000 
    if args[0] == b'3':
        pontos = geraPontos(20000) 
        quantidadePontos = 20000  
    if args[0] == b't':
        dentroConvex = []
        print('Teste Forca Bruta com Faixas:')
        ConvexHull = Polygon()
        inicio = time.perf_counter()
        dentro, fora = testeFaixaForcaBruta(pontos)
        total = time.perf_counter() - inicio
        print('Produto Vetorial:', contadorProdVetorial)
        print('Intersecção:', contadorInterseccao)
        print('Tempo execução:', total)
    if args[0] == b'y':
        print('Teste ConvexHull:')
        inicio = time.perf_counter()
        dentro, fora, dentroConvex = testeConvexHull(pontos)
        total = time.perf_counter() - inicio
        print('Produto Vetorial:', contadorProdVetorial)
        print('Intersecção:', contadorInterseccao)
        print('Tempo execução:', total)
    if args[0] == b'u':
        dentroConvex = []
        print('Teste Força Bruta:')
        ConvexHull = Polygon()
        inicio = time.perf_counter()
        dentro, fora = testeForcaBruta(pontos)
        total = time.perf_counter() - inicio
        print('Produto Vetorial:', contadorProdVetorial)
        print('Intersecção:', contadorInterseccao)
        print('Tempo execução:', total)
    if args[0] == b'x':
        dentro = []
        ConvexHull = Polygon()
        fora = [] 
    if args[0] == b'a':
        Min, Max = Mapa.LePontosDeArquivo("PoligonoDeTeste2.txt")
    if args[0] == ESCAPE:
        os._exit(0)
    dialogo()
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
    glutPostRedisplay()
    return

def ImprimeFaixas():
    global EspacoDividido
    f = Faixa()
    for i in range(numeroDeFaixas):
        print("Faixa", i,"-> ", end='')
        f = EspacoDividido.getFaixa(i)
        for a in range (f.getNroDeArestas()):
            print(f.getAresta(a), end=' ')
        print()


def CriaFaixas():
    global EspacoDividido
    EspacoDividido.CriaFaixas(numeroDeFaixas)
    
    alturaFaixas = ceil((Max.y - Min.y + numeroDeFaixas)/numeroDeFaixas)
    arestas = list(range(Mapa.getNVertices()))
    
    for i in range(numeroDeFaixas):
        alturaAtual = (alturaFaixas * i) + Min.y 
        alturaProxima = alturaAtual + alturaFaixas
        for j in arestas:
            p1, p2 = Mapa.getAresta(j)
            if(
            (p1.y <= alturaProxima and p1.y >= alturaAtual) or 
            (p2.y <= alturaProxima and p2.y >= alturaAtual) or 
            (p2.y>= alturaProxima and p1.y <= alturaProxima) or 
            (p2.y<= alturaAtual and p1.y >= alturaAtual)):
                EspacoDividido.CadastraArestaNaFaixa(i,j)
    

def geraPontos(qtd):
    pontos = []
    for i in range(qtd):
        y = uniform(round(Min.y), round(Max.y))
        x = uniform(round(Min.x), round(Max.x))
        pontos += [Ponto(x, y)]
    return pontos

#Força bruta, calculando o número de de interseções
def testeForcaBruta(pontos):
    dentro = []
    fora = []
    for p in pontos:
        if(inclusaoPontoConcavo(p,Mapa)):
            dentro += [p]
        else: 
            fora += [p]
    return dentro, fora

#Teste de inclusão em polígono convexo, usando o Convex Hull
def testeConvexHull(pontos):
    dentro = []
    dentroConvex = []
    fora = []
    
    convexIds = quickHull()
    
    for i in convexIds:
        ConvexHull.inserePonto(Mapa.getVertice(i))
        
    for p in pontos:
        if(inclusaoPontoConvexo(p,ConvexHull)):
            dentroConvex += [p]
        else: 
            fora += [p]
    
    for p in dentroConvex:
        if(inclusaoPontoConcavo(p,Mapa)):
            dentro += [p]
        
    return dentro, fora, dentroConvex

#Teste de força bruta, considerando apenas as arestas que estão na faixa onde fica o ponto
def testeFaixaForcaBruta(pontos):
    alturaFaixas = ceil((Max.y - Min.y + numeroDeFaixas)/numeroDeFaixas)
    dentro = []
    fora = []
    for p in pontos:
        for i in range(numeroDeFaixas):
            alturaAtual = (alturaFaixas * i) + Min.y 
            alturaProxima = alturaAtual + alturaFaixas
            if(p.y <= alturaProxima and p.y >= alturaAtual):
                faixa = EspacoDividido.getFaixa(i)
                interseccao = 0
                for j in range(faixa.getNroDeArestas()): 
                    p1, p2 = Mapa.getAresta(faixa.getAresta(j))
                    Dir = Ponto(-1,0)
                    pEsq = p + Dir * 1000
                    if HaInterseccao(p1, p2, p, pEsq):
                        if(p1.y == p.y):
                            px1, __ = Mapa.getAresta(faixa.getAresta(j) - 1)
                            if(minimoMaximoLocal(p, px1, p2)):
                                interseccao += 1
                        else: interseccao += 1
                if interseccao % 2 != 0:
                    dentro += [p]
                else: fora += [p]
    return dentro, fora

def dialogo():
    print('\n\n\n\n')
    print('Escolha entre as opções a baixo (case sensitive):\n')
    print('\'z\': Todos os testes para cada uma das quantidades de pontos (Cuidado!!! Pode demorar..)')
    print('     Quantidade de Pontos (Atual:', quantidadePontos, '):')
    print('     \'1\': 200 Pontos')
    print('     \'2\': 2.000 Pontos')
    print('     \'3\': 20.000 Pontos')
    print('\'t\': Teste Forca Bruta com Faixas')
    print('\'y\': Teste ConvexHull')
    print('\'u\': Teste Força Bruta')
    print('\'x\': Resetar o mapa')
    print('\'a\': Usa exemplo reduzido')
    print('\'Esq\': Finalizar programa')
    
def init():
    # Define a cor do fundo da tela (AZUL)
    glClearColor(0, 0, 0, 0)
    global Min, Max, pontos, dentro, fora, quantidadePontos
    
    #Min, Max = Mapa.LePontosDeArquivo("PoligonoDeTeste2.txt")

    Min, Max = Mapa.LePontosDeArquivo("EstadoRS.txt")
    
    
    pontos = geraPontos(quantidadePontos)
    
    CriaFaixas()
    
    dialogo()
    
    #ImprimeFaixas()
    
    #TODO: VER OS OUTROS TODOS kK
    #TODO: FAZER OS CONTADORES
    #TODO: MODIFICAR LÓGICA PARA MOSTRAR CONVEXHULL
    #TODO: MONTAR CORES


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
