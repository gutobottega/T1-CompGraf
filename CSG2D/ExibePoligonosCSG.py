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
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import *

# ***********************************************************************************
Mapa = Polygon()

A = Polygon()
B = Polygon()
Uniao = Polygon()
Intersecao = Polygon()
Diferenca = Polygon()

# Limites lógicos da área de desenho
Min = Ponto()
Max = Ponto()

#Ponto = Ponto()
Meio = Ponto()
Terco = Ponto()
Largura = Ponto()

# ***********************************************************************************
def ProdEscalar(v1, v2):
    return v1.x*v2.x + v1.y*v2.y+ v1.z*v2.z;

# ***********************************************************************************
def ProdVetorial (v1, v2, vresult):
    vresult.x = v1.y * v2.z - (v1.z * v2.y)
    vresult.y = v1.z * v2.x - (v1.x * v2.z)
    vresult.z = v1.x * v2.y - (v1.y * v2.x)

# ***********************************************************************************
def reshape(w,h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Cria uma folga na Janela de Seleção, com 10% das dimensões do polígono
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    #glOrtho(Min.x-BordaX, Max.x+BordaX, Min.y-BordaY, Max.y+BordaY, 0.0, 1.0)
    glOrtho(Min.x, Max.x, Min.y, Max.y, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def DesenhaEixos():
    glBegin(GL_LINES);
    # eixo horizontal
    glVertex2f(Min.x,Meio.y)
    glVertex2f(Max.x,Meio.y)
    #  eixo vertical 1
    glVertex2f(Min.x + Terco.x,Min.y)
    glVertex2f(Min.x + Terco.x,Max.y)
    #  eixo vertical 2
    glVertex2f(Min.x + 2*Terco.x,Min.y)
    glVertex2f(Min.x + 2*Terco.x,Max.y)
    glEnd()

# ***********************************************************************************
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(1);
    DesenhaEixos()
    
    glPushMatrix();
    glTranslatef(0, Meio.y, 0);
    glScalef(0.33, 0.5, 1);
    glLineWidth(2);
    glColor3f(1,1,0); # R, G, B  [0..1]
    A.desenhaPoligono()
    glColor3f(1.0, 0.0, 0.0)
    B.desenhaPoligono()
    glPopMatrix()

    #Desenha o polígono A no meio, acima
    glPushMatrix()
    glTranslatef(Terco.x, Meio.y, 0)
    glScalef(0.33, 0.5, 1)
    glLineWidth(2)
    glColor3f(1,1,0) # R, G, B  [0..1]
    A.desenhaPoligono()
    glPopMatrix()

    # Desenha o polígono B no canto superior direito
    glPushMatrix()
    glTranslatef(Terco.x*2, Meio.y, 0)
    glScalef(0.33, 0.5, 1)
    glLineWidth(2)
    glColor3f(1,0,0); # R, G, B  [0..1]
    B.desenhaPoligono()
    glPopMatrix()
    
    # Desenha o polígono A no canto inferior esquerdo
    glPushMatrix()
    glTranslatef(0, 0, 0)
    glScalef(0.33, 0.5, 1)
    glLineWidth(2)
    glColor3f(1,1,0); # R, G, B  [0..1]
    A.desenhaPoligono()
    glPopMatrix()
    
    # Desenha o polígono B no meio, abaixo
    glPushMatrix()
    glTranslatef(Terco.x, 0, 0)
    glScalef(0.33, 0.5, 1)
    glLineWidth(2)
    glColor3f(1,0,0) # R, G, B  [0..1]
    B.desenhaPoligono()
    glPopMatrix()

    glutSwapBuffers()

# ***********************************************************************************
# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
#ESCAPE = '\033'
ESCAPE = b'\x1b'
def keyboard(*args):
    #print (args)
    # If escape is pressed, kill everything.
    if args[0] == b'q':
        os._exit(0)
    if args[0] == ESCAPE:
        os._exit(0)
    if args[0] == b'p':
        Mapa.imprimeVertices()
    if args[0] == b'a':
        LePontosDeArquivo()
# Força o redesenho da tela
    glutPostRedisplay()

# ***********************************************************************************
# LePontosDeArquivo(Nome):
#  Realiza a leitura de uam arquivo com as coordenadas do polígono
# ***********************************************************************************
def LePontosDeArquivo(Nome, P):

    Pt = Ponto()
    infile = open(Nome)
    line = infile.readline()
    number = int(line)
    for line in infile:
        words = line.split() # Separa as palavras na linha
        x = float (words[0])
        y = float (words[1])
        P.insereVertice(x,y,0)
        #Mapa.insereVertice(*map(float,line.split))
    infile.close()
    #print ("Após leitura do arquivo:")
    #Min.imprime()
    #Max.imprime()

def ObtemMaximo (P1, P2):
    Max = copy.deepcopy(P1);
    
    if (P2.x > Max.x):
        Max.x = P2.x

    if (P2.y > Max.y):
        Max.y = P2.y

    if (P2.z > Max.z):
        Max.z = P2.z

    return Max;

def ObtemMinimo (P1, P2):
    Min = copy.deepcopy(P1);
    
    if (P2.x < Min.x):
        Min.x = P2.x
    
    if (P2.y < Min.y):
        Min.y = P2.y
    
    if (P2.z < Min.z):
        Min.z = P2.z

    return Min;

def init():
    global Min, Max, Meio, Terco, Largura  # Variáveis usadas para definir os limites da Window
    
    LePontosDeArquivo("Retangulo.txt", A)
    Min, Max = A.getLimits()
    LePontosDeArquivo("Triangulo.txt", B)
    MinAux, MaxAux = B.getLimits()
    # Atualiza os limites globais após cada leitura
    Min = ObtemMinimo(Min, MinAux)
    Max = ObtemMaximo(Max, MaxAux)

    # Ajusta a largura da janela lógica em função do tamanho dos polígonos
    Largura.x = Max.x-Min.x;
    Largura.y = Max.y-Min.y;
    
    # Calcula 1/3 da largura da janela
    Terco = Largura;
    fator = 1.0/3.0;
    Terco = Terco * fator
    
    #Calcula 1/2 da largura da janela
    Meio.x = (Max.x+Min.x)/2;
    Meio.y = (Max.y+Min.y)/2;
    Meio.z = (Max.z+Min.z)/2;

    V1 = Ponto(1,0,0)
    V2 = Ponto(0,1,0)
    V3 = Ponto()
    
    ProdVetorial(V1, V2, V3)
    print ("Produto Vetorial: ")
    V3.imprime("Prod Vet:")

# ***********************************************************************************
# Programa Principal
# ***********************************************************************************



init()
glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(1000, 500)
glutInitWindowPosition(100, 100)
wind = glutCreateWindow("Exibe Polignos")
glutDisplayFunc(display)
#glutIdleFunc(showScreen)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)

try:
    glutMainLoop()
except SystemExit:
    pass
