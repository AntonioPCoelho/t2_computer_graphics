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
        self.morph_target_positions = []
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
            p.vel = [0, 0, 0] # Zera a velocidade para o início da simulação de reconstrução

    def ResetState(self): # Novo método para resetar o objeto para seu estado inicial
        self.estado_particulas = 0 # Define o estado como objeto inteiro
        self.morph_target_positions.clear()
        # Para um reset bem bonitinho, garantimos que as partículas fiquem na posição dos vértices originais
        # Inativas e também garante que a lista de partículas existe
        if not self.particulas or len(self.particulas) != len(self.vertices):
            self.particulas = []
            for v in self.vertices:
                self.particulas.append(Particula(v))

        for i, p in enumerate(self.particulas):
            original_v_pos = self.original_vertices_positions[i]
            p.pos = [original_v_pos.x, original_v_pos.y, original_v_pos.z] # Volta para a posição original
            p.vel = [0.0, 0.0, 0.0] # Zera a velocidade
            p.ativa = False # Desativa as partículas

    def AtualizaParticulas(self, dt):
        GRAVIDADE = -19.8 # Aumentado para uma queda mais rápida

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
                    if abs(p.vel[1]) < 0.05:
                        p.ativa = False
                        p.vel = [0.0, 0.0, 0.0]

        elif self.estado_particulas == 2: # Reconstruindo
            reconstruction_speed = 0.05  # Velocidade da interpolação (mais alto = mais rápido)
            spiral_speed = 5.0         # Velocidade da rotação da espiral

            all_reconstructed = True
            for i, p in enumerate(self.particulas):
                if not p.ativa:
                    continue

                target_pos = self.original_vertices_positions[i]
                current_pos_vec = p.pos

                distance = math.sqrt((target_pos.x - current_pos_vec[0])**2 +
                                     (target_pos.y - current_pos_vec[1])**2 +
                                     (target_pos.z - current_pos_vec[2])**2)

                if distance < 0.01:
                    p.pos = [target_pos.x, target_pos.y, target_pos.z]
                    p.ativa = False
                    continue

                all_reconstructed = False

                # Interpolação de Altura (Y) e Raio (XZ)
                p.pos[1] = p.pos[1] * (1 - reconstruction_speed) + target_pos.y * reconstruction_speed

                current_r = math.hypot(current_pos_vec[0], current_pos_vec[2])
                target_r = math.hypot(target_pos.x, target_pos.z)
                new_r = current_r * (1 - reconstruction_speed) + target_r * reconstruction_speed

                # Cálculo de Ângulo
                current_angle = math.atan2(current_pos_vec[2], current_pos_vec[0])
                target_angle = math.atan2(target_pos.z, target_pos.x)

                # Calcula a menor distância entre os ângulos (para evitar que ele gire no sentido errado)
                angle_diff = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
                
                # Movimento para corrigir a direção
                angle_correction = angle_diff * reconstruction_speed
                # Movimento constante da espiral
                angle_spiral = dt * spiral_speed
                
                # O novo ângulo combina a correção com a espiral
                new_angle = current_angle + angle_correction + angle_spiral

                # Atualiza a posição XZ com base no novo raio e ângulo
                p.pos[0] = new_r * math.cos(new_angle)
                p.pos[2] = new_r * math.sin(new_angle)

            if all_reconstructed:
                self.estado_particulas = 0
                for i, v in enumerate(self.vertices):
                    original_pos = self.original_vertices_positions[i]
                    v.set(original_pos.x, original_pos.y, original_pos.z)
        elif self.estado_particulas == 3: # Morphing to Maurer Rose
            morph_speed = 0.03 # Adjust for desired morphing speed
            
            all_morphed = True
            for i, p in enumerate(self.particulas):
                if not p.ativa:
                    continue

                target_pos = self.morph_target_positions[i]
                
                # Calculate distance to see if we've arrived
                distance = math.sqrt((target_pos[0] - p.pos[0])**2 +
                                     (target_pos[1] - p.pos[1])**2 +
                                     (target_pos[2] - p.pos[2])**2)

                if distance > 0.02:
                    all_morphed = False
                    # Linearly interpolate each coordinate towards the target
                    p.pos[0] = p.pos[0] * (1 - morph_speed) + target_pos[0] * morph_speed
                    p.pos[1] = p.pos[1] * (1 - morph_speed) + target_pos[1] * morph_speed
                    p.pos[2] = p.pos[2] * (1 - morph_speed) + target_pos[2] * morph_speed

            if all_morphed:
                print("Transformação completa.")
                self.estado_particulas = 4 # New state: "Morphed"
        
        elif self.estado_particulas == 4: # Morphed state
            # Do nothing, just hold the particles in place
            pass

    def DesenhaParticulas(self):
        # Change the color based on the current state
        if self.estado_particulas == 3 or self.estado_particulas == 4:
            glColor3f(1.0, 0.0, 0.0) # Vermeio
        else:
            glColor3f(0.0, 0.0, 0.0) # Preto

        glPointSize(6)
        glBegin(GL_POINTS)
        for p in self.particulas:
            if p.ativa: 
                glVertex3f(p.pos[0], p.pos[1], p.pos[2])
        glEnd()

    def ActivateMorphToMaurerRose(self, n=5, d=97, scale=2.5):
        """Calculates Maurer Rose target points and activates the morphing state."""
        # Permite a transformação a partir do estado inicial (0) ou durante/após a reconstrução (2)
        if self.estado_particulas not in [0, 2]:
            print("O objeto precisa estar reconstruído ou em reconstrução para se transformar.")
            return

        print("Ativando a transformação para Rosa de Maurer.")
        self.morph_target_positions.clear()

        # Se estiver começando do estado sólido (0), as partículas precisam ser ativadas nas posições dos vértices.
        if self.estado_particulas == 0:
            for i, v in enumerate(self.original_vertices_positions):
                self.particulas[i].pos = [v.x, v.y, v.z]
                self.particulas[i].ativa = True
        
        # Se o estado for 2, as partículas já estão ativas e em movimento, então apenas damos a elas um novo alvo.

        # Generate target positions on the Maurer Rose curve
        total_steps = len(self.vertices)
        for i in range(total_steps):
            theta_degrees = (i / total_steps) * 360 * d
            k = theta_degrees * math.pi / 180
            r = scale * math.sin(n * k)
            
            # We map the 2D rose onto the XZ plane to match the floor
            x = r * math.cos(k)
            y = 0.5 # Lift the shape slightly above the floor
            z = r * math.sin(k)
            self.morph_target_positions.append([x, y, z])
        
        # Set the state to morphing
        self.estado_particulas = 3


class Particula:
    def __init__(self, ponto):
        self.pos = [ponto.x, ponto.y, ponto.z]
        self.vel = [random.uniform(-1, 1), random.uniform(2, 5), random.uniform(-1, 1)]
        self.ativa = True
