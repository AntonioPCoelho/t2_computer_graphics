from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import sys
import time
import math
import os

from Objeto3D import *

o: Objeto3D
tempo_antes = time.time()
soma_dt = 0

eyeO = [0.0, 2.0, 8.0]
focalPoint = [0.0, 0.0, 0.0]
vup = [0.0, 1.0, 2.0]

CAM_STEP = 0.5
CAMERA_ROTATION_SPEED = 0.5

# Novas variáveis para controle de animação
current_animation_mode = "NORMAL" # Estados: "NORMAL", "PAUSED", "FAST_FORWARD", "REWINDING"
animation_speed_multiplier = 1.0 #

# As flags modo_particulas e modo_reconstrucao se tornarão redundantes com estado_particulas em Objeto3D
# Mas as manteremos por enquanto para compatibilidade com o código existente na Animacao,
# embora o controle principal passe a ser via o.estado_particulas

def AtualizaCamera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(eyeO[0], eyeO[1], eyeO[2],
              focalPoint[0], focalPoint[1], focalPoint[2],
              vup[0],   vup[1],   vup[2])

def reset_to_initial_state():
    global o, current_animation_mode, animation_speed_multiplier
    o.ResetState() # Chama o novo método em Objeto3D para resetar o estado do objeto
    current_animation_mode = "PAUSED" # Após o reset, pausa a animação
    animation_speed_multiplier = 1.0 # Reseta a velocidade
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
    o.LoadFile('Human_Head.obj') # Certifique-se de que este arquivo existe

    DefineLuz()
    PosicUser()
    # No início, o objeto deve estar completo, então resetamos o estado
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
    if h == 0:
        h = 1
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

def Animacao():
    global soma_dt, tempo_antes, modo_reconstrucao, current_animation_mode, animation_speed_multiplier

    tempo_agora = time.time()
    delta_time = tempo_agora - tempo_antes
    tempo_antes = tempo_agora

    # Ajusta o delta_time com base no multiplicador de velocidade
    effective_dt = delta_time * animation_speed_multiplier

    soma_dt += effective_dt

    if soma_dt > 1.0 / 30: # Aproximadamente 30 quadros por segundo
        soma_dt = 0

        if current_animation_mode == "PAUSED":
            pass # Não faz nada, a animação está pausada
        elif current_animation_mode == "REWINDING":
            # No modo REWINDING, a ação já foi tomada pela função reset_to_initial_state() no teclado.
            # Aqui, apenas garantimos que a tela seja redesenhada para refletir o estado resetado.
            glutPostRedisplay()
            return # Sai da função para evitar processamento adicional de movimento
        else: # "NORMAL" ou "FAST_FORWARD"
            if o.estado_particulas == 1: # Caindo
                o.AtualizaParticulas(effective_dt)
            elif o.estado_particulas == 2: # Reconstruindo
                o.AtualizaParticulas(effective_dt)
            # Se o.estado_particulas for 0 (objeto inteiro), nenhuma atualização de partícula é feita aqui,
            # mas você pode adicionar outras animações para o objeto inteiro se desejar.

            glutPostRedisplay()

def desenha():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)

    DesenhaPiso()
    # Desenha o objeto ou as partículas com base no estado do objeto
    if o.estado_particulas == 0: # Objeto inteiro
        o.DesenhaVertices() # Desenha o objeto completo (cabeça)
    elif o.estado_particulas == 1 or o.estado_particulas == 2: # Caindo ou Reconstruindo
        o.DesenhaParticulas()
    glutSwapBuffers()
    pass

def teclado(key, x, y):
    global eyeO, focalPoint, vup, current_animation_mode, animation_speed_multiplier

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

    elif key == b'\x1b': # ESC key
        glutLeaveMainLoop() # Sai do loop principal do GLUT
        print("Saindo da aplicação.")

    # Controles da Animação
    elif key == b' ': # Espaço: Togglar Play/Pause
        if current_animation_mode == "PAUSED":
            current_animation_mode = "NORMAL"
        else:
            current_animation_mode = "PAUSED"
        animation_speed_multiplier = 1.0 # Reseta a velocidade para normal ao pausar/despausar
        print(f"Modo de animação: {current_animation_mode}")

    elif key == b'[': # Rewind (voltar ao estado inicial)
        current_animation_mode = "REWINDING"
        reset_to_initial_state() # Chama a função para resetar
        print("Modo de animação: REWIND (resetado para o estado inicial)")

    elif key == b']': # Fast Forward
        current_animation_mode = "FAST_FORWARD"
        animation_speed_multiplier = 3.0 # Exemplo: 3x velocidade. Ajuste conforme necessário.
        print(f"Modo de animação: {current_animation_mode} ({animation_speed_multiplier}x velocidade)")

    elif key == b'\\': # Backslash: Resetar velocidade para normal
        current_animation_mode = "NORMAL"
        animation_speed_multiplier = 1.0
        print("Modo de animação: NORMAL")


    # Controles específicos da animação de cabeça (mantidos, mas influenciados pelos novos modos)
    elif key == b'p': # Ativar partículas (destruir cabeça)
        o.AtivarParticulas()
        current_animation_mode = "NORMAL" # Começa a cair em velocidade normal
        animation_speed_multiplier = 1.0
        print("Estado da cabeça: Caindo")

    elif key == b'r': # Reconstruir cabeça
        o.ReconstruirParticulas()
        current_animation_mode = "NORMAL" # Começa a reconstruir em velocidade normal
        animation_speed_multiplier = 1.0
        print("Estado da cabeça: Reconstruindo")


    AtualizaCamera()
    glutPostRedisplay()
    pass

def main():

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b'Computacao Grafica - 3D')

    init()

    glutDisplayFunc(desenha)
    glutKeyboardFunc(teclado)
    glutIdleFunc(Animacao)

    try:
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()
