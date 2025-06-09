from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Ponto import *

import random
import math

class Objeto3D:

    def __init__(self):
        self.vertices = []
        self.faces    = []
        self.speed    = []
        self.angle    = []
        self.radius   = []
        self.position = Ponto(0,0,0)
        self.rotation = (0,0,0,0)
        self.particulas = []
        self.estado_particulas = 0 # 0: parado, 1: caindo, 2: reconstruindo
        self.original_vertices_positions = [] # Para armazenar as posicoess originais dos vertices
        pass

    def LoadFile(self, file:str):
        f = open(file, "r")

        # leitor de .obj baseado na descrição em https://en.wikipedia.org/wiki/Wavefront_.obj_file
        for line in f:
            values = line.split(' ')
            # dividimos a linha por ' ' e usamos o primeiro elemento para saber que tipo de item temos

            if values[0] == 'v':
                # item é um vértice, os outros elementos da linha são a posição dele
                p = Ponto(float(values[1]),
                          float(values[2]),
                          float(values[3]))
                self.vertices.append(p)
                self.original_vertices_positions.append(Ponto(p.x, p.y, p.z)) # Armazena a posição original
                self.speed.append((random.random() + 0.1))


                self.angle.append(math.atan2(float(values[3]), float(values[1])))
                self.radius.append(math.hypot(float(values[1]), float(values[3])))


            if values[0] == 'f':
                # item é uma face, os outros elementos da linha são dados sobre os vértices dela
                self.faces.append([])
                for fVertex in values[1:]:
                    fInfo = fVertex.split('/')
                    # dividimos cada elemento por '/'
                    self.faces[-1].append(int(fInfo[0]) - 1) # primeiro elemento é índice do vértice da face
                    # ignoramos textura e normal

            # ignoramos outros tipos de items, no exercício não é necessário e vai só complicar mais
        pass

    def DesenhaVertices(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(.0, .0, .0)
        glPointSize(8)

        for v in self.vertices:
            glPushMatrix()
            glTranslate(v.x, v.y, v.z)
            glutSolidSphere(.05, 20, 20)
            glPopMatrix()

        glPopMatrix()
        pass

    def DesenhaWireframe(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0, 0, 0)
        glLineWidth(2)

        for f in self.faces:
            glBegin(GL_LINE_LOOP)
            for iv in f:
                v = self.vertices[iv]
                glVertex(v.x, v.y, v.z)
            glEnd()

        glPopMatrix()
        pass

    def Desenha(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0.34, .34, .34)
        glLineWidth(2)

        for f in self.faces:
            glBegin(GL_TRIANGLE_FAN)
            for iv in f:
                v = self.vertices[iv]
                glVertex(v.x, v.y, v.z)
            glEnd()

        glPopMatrix()
        pass

    def ProximaPos(self):
        for i in range(len(self.vertices)):
            self.angle[i] += self.speed[i] * (1/30)

            x = self.radius[i] * math.cos(self.angle[i])
            z = self.radius[i] * math.sin(self.angle[i])

            self.vertices[i].x = x
            self.vertices[i].z = z

    def AtivarParticulas(self):
        self.particulas = []
        # Offset para garantir que as partículas comecem acima do objeto,
        # dando mais espaço para a animação de queda.
        # Ajuste este valor conforme necessário para a altura de início desejada.
        initial_spawn_height_offset = 2.0 #
        for i, v in enumerate(self.vertices):
             p = Particula(v)
             # Define a posição inicial da partícula para a posição original do vértice,
             # mas com um offset no eixo Y.
             p.pos = [v.x, v.y + initial_spawn_height_offset, v.z] #
             self.particulas.append(p)
        self.estado_particulas = 1 # Define o estado como caindo
        # Garante que as partículas estejam ativas ao iniciar a queda
        for p in self.particulas:
             p.ativa = True

    def ReconstruirParticulas(self):
        self.estado_particulas = 2 # Define o estado como reconstruindo
        for i, p in enumerate(self.particulas):
            p.ativa = True # Ativa todas as partículas para a reconstrução
            # Resetar velocidade ou ajustar, dependendo do efeito desejado
            # Por simplicidade, vamos permitir que as partículas "ignorem" a velocidade anterior e se movem para o destino.
            # Você pode adicionar uma lógica mais complexa aqui para transições mais suaves.

    def AtualizaParticulas(self, dt): # dt é passado como argumento
        GRAVIDADE = -19.8 # Aumentado para uma queda mais rápida. Ajuste se necessário.

        if self.estado_particulas == 1: # Caindo
            for p in self.particulas:
                if not p.ativa:
                    continue

                # Aplicar gravidade
                p.vel[1] += GRAVIDADE * dt

                # Atualizar posição
                for i in range(3):
                    p.pos[i] += p.vel[i] * dt

                # Colisão com o chão (y = -1.0)
                if p.pos[1] <= -1.0:
                    p.pos[1] = -1.0
                    p.vel[1] *= -0.5  # quique
                    # Limiar menor para a desativação, para que quiquem mais antes de parar
                    if abs(p.vel[1]) < 0.05: # Reduzido de 0.1 para 0.05
                        p.ativa = False
                        p.vel = [0.0, 0.0, 0.0]
        elif self.estado_particulas == 2: # Reconstruindo (Tornado invertido)
            reconstruction_speed = 0.05 # Ajuste a velocidade da reconstrução
            spiral_tightness = 5.0 # Ajuste a "apertura" da espiral
            spiral_height_factor = 2.0 # Ajuste o quão rápido a partícula sobe no Y

            for i, p in enumerate(self.particulas):
                target_pos = self.original_vertices_positions[i]
                current_pos = Ponto(p.pos[0], p.pos[1], p.pos[2])

                # Vetor do alvo para a posição atual
                direction = Ponto(target_pos.x - current_pos.x,
                                  target_pos.y - current_pos.y,
                                  target_pos.z - current_pos.z)

                distance = math.sqrt(direction.x**2 + direction.y**2 + direction.z**2)

                if distance > 0.01: # Se não chegou muito perto do alvo
                    # Normalizar a direção
                    direction.x /= distance
                    direction.y /= distance
                    direction.z /= distance

                    # Adicionar um componente espiral (tornado invertido)
                    # Isso é uma simplificação, você pode usar rotações mais complexas
                    # para um espiral mais realista.
                    # Para um "tornado invertido", queremos que elas girem enquanto sobem.
                    angle = math.atan2(current_pos.z, current_pos.x) + dt * spiral_tightness
                    r = math.hypot(current_pos.x, current_pos.z)

                    new_x = r * math.cos(angle)
                    new_z = r * math.sin(angle)

                    p.pos[0] = p.pos[0] * (1 - reconstruction_speed) + new_x * reconstruction_speed # move em direção ao centro e gira
                    p.pos[1] = p.pos[1] * (1 - reconstruction_speed) + target_pos.y * reconstruction_speed * spiral_height_factor # move para cima
                    p.pos[2] = p.pos[2] * (1 - reconstruction_speed) + new_z * reconstruction_speed # move em direção ao centro e gira

                    # Ajuste fino para o movimento em direção ao alvo original
                    p.pos[0] += (target_pos.x - p.pos[0]) * reconstruction_speed
                    p.pos[2] += (target_pos.z - p.pos[2]) * reconstruction_speed

                    # Certifique-se de que a altura Y também se move para a posição alvo
                    p.pos[1] += (target_pos.y - p.pos[1]) * reconstruction_speed


                else:
                    # Chegou ao destino, travar na posição original
                    p.pos[0] = target_pos.x
                    p.pos[1] = target_pos.y
                    p.pos[2] = target_pos.z
                    p.ativa = False # Desativa a partícula quando ela chega ao destino
                    # Poderíamos verificar se todas as partículas estão inativas para mudar o estado novamente.

    def DesenhaParticulas(self):
        glColor3f(0, 0, 0)
        glPointSize(6)
        glBegin(GL_POINTS)
        # Condição de desenho para garantir que todas as partículas sejam vistas,
        # mesmo as que já pararam, se o estado for de reconstrução.
        # No estado caindo (1), só desenha as ativas para simular a "desintegração"
        for p in self.particulas:
            if p.ativa or self.estado_particulas == 2: # Desenha todas se estiver reconstruindo
                glVertex3f(p.pos[0], p.pos[1], p.pos[2])
        glEnd()


class Particula:
    def __init__(self, ponto):
        self.pos = [ponto.x, ponto.y, ponto.z]
        # Ajuste a velocidade inicial Y se as partículas estiverem indo muito alto ou muito baixo
        self.vel = [random.uniform(-1, 1), random.uniform(2, 5), random.uniform(-1, 1)]
        self.ativa = True
