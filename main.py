from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import sys
import time

from Objeto3D import *

o: Objeto3D
tempo_antes = time.time()
soma_dt = 0

eyeO = [0.0, 2.0, 8.0]  
focalPoint = [0.0, 0.0, 0.0]  
vup = [0.0, 1.0, 2.0]  

CAM_STEP = 0.5

def AtualizaCamera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(eyeO[0], eyeO[1], eyeO[2],
              focalPoint[0], focalPoint[1], focalPoint[2],
              vup[0],   vup[1],   vup[2])


def init():
    global o
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)

    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    o = Objeto3D()
    o.LoadFile('Human_Head.obj')

    DefineLuz()
    PosicUser()


def DefineLuz():
    # Define cores para um objeto dourado
    luz_ambiente = [0.4, 0.4, 0.4]
    luz_difusa = [0.7, 0.7, 0.7]
    luz_especular = [0.9, 0.9, 0.9]
    posicao_luz = [2.0, 3.0, 0.0]  # PosiÃ§Ã£o da Luz
    especularidade = [1.0, 1.0, 1.0]

    # ****************  Fonte de Luz 0

    glEnable(GL_COLOR_MATERIAL)

    #Habilita o uso de iluminaÃ§Ã£o
    glEnable(GL_LIGHTING)

    #Ativa o uso da luz ambiente
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)
    # Define os parametros da luz nÃºmero Zero
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glEnable(GL_LIGHT0)

    # Ativa o "Color Tracking"
    glEnable(GL_COLOR_MATERIAL)

    # Define a reflectancia do material
    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)

    # Define a concentraÃ§Ã£oo do brilho.
    # Quanto maior o valor do Segundo parametro, mais
    # concentrado serÃ¡ o brilho. (Valores vÃ¡lidos: de 0 a 128)
    glMateriali(GL_FRONT, GL_SHININESS, 51)

def PosicUser():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Configura a matriz da projeção perspectiva (FOV, proporção da tela, distância do mínimo antes do clipping, distância máxima antes do clipping
    # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
    gluPerspective(60, 16/9, 0.01, 50)  # Projecao perspectiva
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #Especifica a matriz de transformação da visualização
    # As três primeiras variáveis especificam a posição do observador nos eixos x, y e z
    # As três próximas especificam o ponto de foco nos eixos x, y e z
    # As três últimas especificam o vetor up
    # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
    AtualizaCamera()

def reshape(w, h):
    if h == 0:
        h = 1
    aspect = w / h

    glViewport(0, 0, w, h)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, aspect, 0.01, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # câmera mais baixa e centralizada no objeto
    AtualizaCamera()

def DesenhaLadrilho():
    glColor3f(0.5, 0.5, 0.5)  # desenha QUAD preenchido
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

    glColor3f(1, 1, 1)  # desenha a borda da QUAD
    glBegin(GL_LINE_STRIP)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

def DesenhaPiso():
    glPushMatrix()
    glTranslated(-20, -1, -10)
    for x in range(-20, 20):
        glPushMatrix()
        for z in range(-20, 20):
            DesenhaLadrilho()
            glTranslated(0, 0, 1)
        glPopMatrix()
        glTranslated(1, 0, 0)
    glPopMatrix()

def DesenhaCubo():
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslated(0, 0.5, 0)
    glutSolidCube(1)

    glColor3f(0.5, 0.5, 0)
    glTranslated(0, 0.5, 0)
    glRotatef(90, -1, 0, 0)
    glRotatef(45, 0, 0, 1)
    glutSolidCone(1, 1, 4, 4)
    glPopMatrix()

# Função chamada constantemente (idle) para atualizar a animação
def Animacao():
    global soma_dt, tempo_antes

    tempo_agora = time.time()
    delta_time = tempo_agora - tempo_antes
    tempo_antes = tempo_agora

    soma_dt += delta_time

    if soma_dt > 1.0 / 30:  # Aproximadamente 30 quadros por segundo
        soma_dt = 0
        
        o.ProximaPos()
        glutPostRedisplay()

def desenha():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)

    DesenhaPiso()
    #DesenhaCubo()    
    # o.Desenha()
    # o.DesenhaWireframe()
    o.DesenhaVertices()

    glutSwapBuffers()
    pass

def teclado(key, x, y):
    global eyeO, focalPoint, vup
    mod = glutGetModifiers()
    step = CAM_STEP * (-1 if (mod & GLUT_ACTIVE_SHIFT) else 1)
    if key == b'1':    eyeO[0]   += step
    elif key == b'2':  eyeO[1]   += step
    elif key == b'3':  eyeO[2]   += step
    elif key == b'4':  focalPoint[0]+= step
    elif key == b'5':  focalPoint[1]+= step
    elif key == b'6':  focalPoint[2]+= step
    elif key == b'7':  vup[0], vup[1] = vup[1], -vup[0]
    
    elif key == b'!': eyeO[0]   -= CAM_STEP  
    elif key == b'@': eyeO[1]   -= CAM_STEP  
    elif key == b'#': eyeO[2]   -= CAM_STEP  
    elif key == b'$': focalPoint[0] -= CAM_STEP  
    elif key == b'%': focalPoint[1] -= CAM_STEP  
    elif key == b'^': focalPoint[2] -= CAM_STEP  
    elif key == b'&': vup[0], vup[1] = -vup[1], vup[0]
 
    AtualizaCamera()
    #o.rotation = (1, 0, 0, o.rotation[3] + 2)    

    glutPostRedisplay()
    pass

def main():

    glutInit(sys.argv)

    # Define o modelo de operacao da GLUT
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH)

    # Especifica o tamnho inicial em pixels da janela GLUT
    glutInitWindowSize(640, 480)

    # Especifica a posição de início da janela
    glutInitWindowPosition(100, 100)

    # Cria a janela passando o título da mesma como argumento
    glutCreateWindow(b'Computacao Grafica - 3D')

    # Função responsável por fazer as inicializações
    init()

    # Registra a funcao callback de redesenho da janela de visualizacao
    glutDisplayFunc(desenha)

    # Registra a funcao callback para tratamento das teclas ASCII
    glutKeyboardFunc(teclado)

    glutIdleFunc(Animacao)

    try:
        # Inicia o processamento e aguarda interacoes do usuario
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()