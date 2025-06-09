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
        self.estado_particulas = 0 # 0: parado/objeto inteiro, 1: caindo, 2: reconstruindo
        self.original_vertices_positions = [] # Para armazenar as posições originais dos vértices
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
        # Este método não é usado no fluxo de partículas, mas pode ser útil para outras animações
        for i in range(len(self.vertices)):
            self.angle[i] += self.speed[i] * (1/30)

            x = self.radius[i] * math.cos(self.angle[i])
            z = self.radius[i] * math.sin(self.angle[i])

            self.vertices[i].x = x
            self.vertices[i].z = z

    def AtivarParticulas(self):
        # Se as partículas ainda não foram criadas ou se queremos reiniciá-las completamente
        if not self.particulas or len(self.particulas) != len(self.vertices):
            self.particulas = []
            for v in self.vertices:
                self.particulas.append(Particula(v))

        # Define uma altura inicial fixa para todas as partículas, bem acima do chão.
        fixed_spawn_height = 3.0 # Ajuste este valor. O chão está em -1.0.
        for i, p in enumerate(self.particulas):
             original_v_pos = self.original_vertices_positions[i]
             # Define a posição inicial da partícula: XZ original, Y fixo e alto.
             p.pos = [original_v_pos.x, fixed_spawn_height, original_v_pos.z]
             p.vel = [random.uniform(-1, 1), random.uniform(2, 5), random.uniform(-1, 1)] # Redefine a velocidade para iniciar a queda
             p.ativa = True # Garante que todas as partículas estejam ativas para começar a cair.

        self.estado_particulas = 1 # Define o estado como caindo


    def ReconstruirParticulas(self):
        self.estado_particulas = 2 # Define o estado como reconstruindo
        for i, p in enumerate(self.particulas):
            p.ativa = True # Ativa todas as partículas para a reconstrução
            # No modo reconstrução, a velocidade é menos relevante,
            # o movimento é controlado pela interpolação para o ponto original.

    def ResetState(self): # Novo método para resetar o objeto para seu estado inicial
        self.estado_particulas = 0 # Define o estado como objeto inteiro
        # Para um reset limpo, garantimos que as partículas estejam na posição dos vértices originais
        # e inativas, e que a lista de partículas exista.
        if not self.particulas or len(self.particulas) != len(self.vertices):
            self.particulas = []
            for v in self.vertices:
                self.particulas.append(Particula(v))

        for i, p in enumerate(self.particulas):
            original_v_pos = self.original_vertices_positions[i]
            p.pos = [original_v_pos.x, original_v_pos.y, original_v_pos.z] # Volta para a posição original
            p.vel = [0.0, 0.0, 0.0] # Zera a velocidade
            p.ativa = False # Desativa as partículas

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
                    if abs(p.vel[1]) < 0.05:
                        p.ativa = False
                        p.vel = [0.0, 0.0, 0.0]
        elif self.estado_particulas == 2: # Reconstruindo (Tornado invertido)
            reconstruction_speed = 0.05 # Ajuste a velocidade da reconstrução
            spiral_tightness = 5.0 # Ajuste a "apertura" da espiral
            spiral_height_factor = 2.0 # Ajuste o quão rápido a partícula sobe no Y

            # Verifique se todas as partículas atingiram seu destino
            all_reconstructed = True

            for i, p in enumerate(self.particulas):
                if not p.ativa: # Se a partícula já foi reconstruída e desativada
                    continue

                target_pos = self.original_vertices_positions[i]
                current_pos = Ponto(p.pos[0], p.pos[1], p.pos[2])

                # Vetor do alvo para a posição atual
                direction = Ponto(target_pos.x - current_pos.x,
                                  target_pos.y - current_pos.y,
                                  target_pos.z - current_pos.z)

                distance = math.sqrt(direction.x**2 + direction.y**2 + direction.z**2)

                if distance > 0.01: # Se não chegou muito perto do alvo
                    all_reconstructed = False # Ainda há partículas para reconstruir

                    # Adicionar um componente espiral (tornado invertido)
                    angle = math.atan2(current_pos.z, current_pos.x) # Ângulo atual da partícula
                    
                    # Interpolar a posição para o alvo, adicionando o movimento em espiral
                    # O raio e o ângulo do espiral devem convergir para o do target_pos também
                    target_angle = math.atan2(target_pos.z, target_pos.x)
                    target_r = math.hypot(target_pos.x, target_pos.z)
                    current_r = math.hypot(current_pos.x, current_pos.z)


                    # Interpolando o raio (distância ao centro XZ)
                    new_r = current_r * (1 - reconstruction_speed) + target_r * reconstruction_speed
                    
                    # Interpolando o ângulo (para girar em direção ao ângulo alvo)
                    # Adiciona um componente de espiral extra
                    new_angle_spiral = angle + dt * spiral_tightness
                    new_angle_interpolated = (angle * (1 - reconstruction_speed) + target_angle * reconstruction_speed) + dt * spiral_tightness


                    # Recalcular X e Z baseados no novo raio e ângulo interpolado
                    p.pos[0] = new_r * math.cos(new_angle_interpolated)
                    p.pos[2] = new_r * math.sin(new_angle_interpolated)


                    # Interpolando a altura Y em direção ao alvo, com um fator de altura espiral
                    p.pos[1] = p.pos[1] * (1 - reconstruction_speed) + target_pos.y * reconstruction_speed * spiral_height_factor

                    # Garantir que se movem em direção ao alvo final suavemente (misturando com a interpolação anterior)
                    # p.pos[0] += (target_pos.x - p.pos[0]) * reconstruction_speed # Isso pode duplicar o movimento, remover ou ajustar
                    # p.pos[1] += (target_pos.y - p.pos[1]) * reconstruction_speed
                    # p.pos[2] += (target_pos.z - p.pos[2]) * reconstruction_speed


                else:
                    # Chegou ao destino, travar na posição original
                    p.pos[0] = target_pos.x
                    p.pos[1] = target_pos.y
                    p.pos[2] = target_pos.z
                    p.ativa = False # Desativa a partícula quando ela chega ao destino
            
            if all_reconstructed:
                self.estado_particulas = 0 # Volta para o estado parado/objeto se todas reconstruíram


    def DesenhaParticulas(self):
        glColor3f(0, 0, 0)
        glPointSize(6)
        glBegin(GL_POINTS)
        for p in self.particulas:
            if p.ativa or self.estado_particulas == 2: # Desenha todas se estiver reconstruindo
                glVertex3f(p.pos[0], p.pos[1], p.pos[2])
        glEnd()


class Particula:
    def __init__(self, ponto):
        self.pos = [ponto.x, ponto.y, ponto.z]
        self.vel = [random.uniform(-1, 1), random.uniform(2, 5), random.uniform(-1, 1)]
        self.ativa = True
