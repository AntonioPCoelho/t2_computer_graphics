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

current_animation_mode = "NORMAL"
animation_speed_multiplier = 1.0

def AtualizaCamera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(eyeO[0], eyeO[1], eyeO[2],
              focalPoint[0], focalPoint[1], focalPoint[2],
              vup[0],   vup[1],   vup[2])

def reset_to_initial_state():
    global o, current_animation_mode, animation_speed_multiplier
    o.ResetState()
    current_animation_mode = "PAUSED"
    animation_speed_multiplier = 1.0
    print("Estado resetado para inicial. Animação Pausada.")

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
    reset_to_initial_state()

def DefineLuz():
    luz_ambiente = [0.4, 0.4, 0.4]
    luz_difusa = [0.7, 0.7, 0.7]
    luz_especular = [0.9, 0.9, 0.9]
    posicao_luz = [2.0, 3.0, 0.0]
    especularidade = [1.0, 1.0, 1.0]

    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)
    glMateriali(GL_FRONT, GL_SHININESS, 51)

def PosicUser():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 16/9, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    AtualizaCamera()

def reshape(w, h):
    if h == 0: h = 1
    aspect = w / h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, aspect, 0.01, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    AtualizaCamera()

def DesenhaLadrilho():
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

    glColor3f(1, 1, 1)
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


def Animacao():
    global soma_dt, tempo_antes, current_animation_mode, animation_speed_multiplier

    tempo_agora = time.time()
    delta_time = tempo_agora - tempo_antes
    tempo_antes = tempo_agora

    # Verifica o modo de animação atual
    if current_animation_mode == "PAUSED":
        glutPostRedisplay() # Redesenha a tela, mas não atualiza a animação
        return

    effective_dt = delta_time * animation_speed_multiplier
    soma_dt += effective_dt

    if soma_dt > 1.0 / 60: # Aproximadamente 60 FPS
        soma_dt = 0
        if o.estado_particulas in [1, 2, 3]: # Caindo, Reconstruindo ou Morfando
            o.AtualizaParticulas(effective_dt)
        
    glutPostRedisplay()

def desenha():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)

    DesenhaPiso()
    
    if o.estado_particulas == 0: # Objeto inteiro
        o.DesenhaVertices() # Desenha o objeto como vértices (pontos)
    else: # Caindo, Reconstruindo ou morfando
        o.DesenhaParticulas()
        
    glutSwapBuffers()

def teclado(key, x, y):
    global eyeO, focalPoint, vup, current_animation_mode, animation_speed_multiplier

    mod = glutGetModifiers()
    step = CAM_STEP * (1 if not (mod & GLUT_ACTIVE_SHIFT) else -1)
    if key == b'1':    eyeO[0] += step
    elif key == b'2':  eyeO[1] += step
    elif key == b'3':  eyeO[2] += step
    elif key == b'4':  focalPoint[0] += step
    elif key == b'5':  focalPoint[1] += step
    elif key == b'6':  focalPoint[2] += step
    elif key == b'7':  vup[0], vup[1] = vup[1], -vup[0]
    elif key == b'\x1b': glutLeaveMainLoop() # ESC para sair

    elif key == b'!': eyeO[0]   -= CAM_STEP
    elif key == b'@': eyeO[1]   -= CAM_STEP
    elif key == b'#': eyeO[2]   -= CAM_STEP
    elif key == b'$': focalPoint[0] -= CAM_STEP
    elif key == b'%': focalPoint[1] -= CAM_STEP
    elif key == b'^': focalPoint[2] -= CAM_STEP
    elif key == b'&': vup[0], vup[1] = -vup[1], vup[0]

    elif key == b' ': # Play/Pause
        if current_animation_mode != "PAUSED":
            current_animation_mode = "PAUSED"
            print(f"Modo de animação: {current_animation_mode}")
        else:
            current_animation_mode = "NORMAL"
            animation_speed_multiplier = 1.0
            print(f"Modo de animação: {current_animation_mode}")

    elif key == b'[': # Rewind (Reset)
        reset_to_initial_state()
        print("Animação resetada.")

    elif key == b']': # Fast Forward
        current_animation_mode = "FAST_FORWARD"
        animation_speed_multiplier = 3.0
        print(f"Modo de animação: {current_animation_mode} ({animation_speed_multiplier}x)")

    elif key == b'\\': # Velocidade Normal
        current_animation_mode = "NORMAL"
        animation_speed_multiplier = 1.0
        print("Modo de animação: NORMAL")

    elif key == b'p': # Ativar Partículas (Explodir)
        o.AtivarParticulas()
        current_animation_mode = "NORMAL"
        animation_speed_multiplier = 1.0
        print("Estado: Partículas Caindo")

    elif key == b'r': # Reconstruir Objeto
        o.ReconstruirParticulas()
        current_animation_mode = "NORMAL"
        animation_speed_multiplier = 1.0
        print("Estado: Reconstruindo Objeto")

    elif key == b'm': # Morph to Maurer Rose
        o.ActivateMorphToMaurerRose()
        current_animation_mode = "NORMAL"
        animation_speed_multiplier = 1.0

    AtualizaCamera()
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH) 
    glutInitWindowSize(400, 400) 
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b'Computacao Grafica - Particulas')
    init()
    glutDisplayFunc(desenha)
    glutKeyboardFunc(teclado)
    glutIdleFunc(Animacao)
    glutReshapeFunc(reshape)
    glutMainLoop()

if __name__ == '__main__':
    main()
