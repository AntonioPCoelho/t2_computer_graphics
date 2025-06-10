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
        self.estado_particulas = 0 # 0: parado/objeto inteiro, 1: caindo, 2: reconstruindo 3: morfando para Maurer Rose, 4: morfado em Maurer Rose
        self.original_vertices_positions = [] # Para armazenar as posições originais dos vértices
        self.morph_target_positions = []
        self.spiral_targets = [] # Para armazenar os alvos da espiral
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

    def AtivarParticulas(self):
        # Checa se as partículas já foram criadas, se não, cria uma nova lista de partículas (uma para cada vértice).
        if not self.particulas or len(self.particulas) != len(self.vertices):
            self.particulas = []
            for v in self.vertices:
                self.particulas.append(Particula(v))

        for i, p in enumerate(self.particulas):
             original_v_pos = self.original_vertices_positions[i]
             p.pos = [original_v_pos.x, original_v_pos.y, original_v_pos.z]
             p.vel = [random.uniform(-1, 1), random.uniform(2, 5), random.uniform(-1, 1)] 
             p.ativa = True 

        self.estado_particulas = 1 #canindo

    def ReconstruirParticulas(self):
      self.estado_particulas = 2
      self.morph_target_positions.clear()
      self.estado_particulas = 2
      self.espiral_concluida = False
      self.spiral_targets.clear()
      # calcula os alvos da espiral vertical
      altura_entre = 0.02              # altura incremental por partícula
      raio_espiral = 1.5               # raio fixo
      for i, p in enumerate(self.particulas):
          ang = i * 0.3                # espaçamento angular
          x = raio_espiral * math.cos(ang)
          z = raio_espiral * math.sin(ang)
          y = -1.0 + i * altura_entre  # começa no chão y=-1
          self.spiral_targets.append([x, y, z])
      # define o target inicial de cada partícula como o ponto na espiral
      for i, p in enumerate(self.particulas):
          p.ativa = True
          p.target = self.spiral_targets[i].copy()

    def ResetState(self): 
        self.estado_particulas = 0  
        self.morph_target_positions.clear()
        if not self.particulas or len(self.particulas) != len(self.vertices):
            self.particulas = []
            for v in self.vertices:
                self.particulas.append(Particula(v))

        for i, p in enumerate(self.particulas):
            original_v_pos = self.original_vertices_positions[i]
            p.pos = [original_v_pos.x, original_v_pos.y, original_v_pos.z] 
            p.vel = [0.0, 0.0, 0.0] 
            p.ativa = False

    def AtualizaParticulas(self, dt):
        GRAVIDADE = -9.8 
        if self.estado_particulas == 1: # Caindo
            for p in self.particulas:
                if not p.ativa:
                    continue
                p.vel[1] += GRAVIDADE * dt
                for i in range(3):
                    p.pos[i] += p.vel[i] * dt
                if p.pos[1] <= -1.0:
                    p.pos[1] = -1.0
                    p.vel[1] *= -0.5 
                    if abs(p.vel[1]) < 0.05:
                        p.ativa = False
                        p.vel = [0.0, 0.0, 0.0]
        elif self.estado_particulas == 2:  # Reconstruindo em duas fases
          speed = 1.0      # controla velocidade da interpolação
          all_done = True              
          for p in self.particulas:
              if not p.ativa:
                  continue
              for k in range(3):
                  diff = p.target[k] - p.pos[k]
                  p.pos[k] += diff * speed * dt
              if all(abs(p.pos[k] - p.target[k]) < 0.01 for k in range(3)):
                  p.pos = p.target.copy()
                  p.ativa = False
              else:
                  all_done = False              
          if not self.espiral_concluida and all_done:
              self.espiral_concluida = True
              for i, p in enumerate(self.particulas):
                  orig = self.original_vertices_positions[i]
                  p.ativa = True
                  p.target = [orig.x, orig.y, orig.z]
              return               
          if self.espiral_concluida and all_done:
              self.estado_particulas = 0
              for i, v in enumerate(self.vertices):
                  orig = self.original_vertices_positions[i]
                  v.set(orig.x, orig.y, orig.z)              
        elif self.estado_particulas == 3: # Maurer Rose
            morph_speed = 0.03 
            all_morphed = True
            for i, p in enumerate(self.particulas):
                if not p.ativa:
                    continue
                target_pos = self.morph_target_positions[i]
                distance = math.sqrt((target_pos[0] - p.pos[0])**2 +
                                     (target_pos[1] - p.pos[1])**2 +
                                     (target_pos[2] - p.pos[2])**2)
                if distance > 0.02:
                    all_morphed = False
                    p.pos[0] = p.pos[0] * (1 - morph_speed) + target_pos[0] * morph_speed
                    p.pos[1] = p.pos[1] * (1 - morph_speed) + target_pos[1] * morph_speed
                    p.pos[2] = p.pos[2] * (1 - morph_speed) + target_pos[2] * morph_speed
            if all_morphed:
                print("Transformação completa.")
                self.estado_particulas = 4 # Morfado em MR
        elif self.estado_particulas == 4: 
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
        if self.estado_particulas not in [0, 2]:
            print("O objeto precisa estar reconstruído ou em reconstrução para se transformar.")
            return
        print("Ativando a transformação para Rosa de Maurer.")
        self.morph_target_positions.clear()
        if self.estado_particulas == 0:
            for i, v in enumerate(self.original_vertices_positions):
                self.particulas[i].pos = [v.x, v.y, v.z]
                self.particulas[i].ativa = True
        # Generate target positions on the Maurer Rose curve
        total_steps = len(self.vertices)
        for i in range(total_steps):
            theta_degrees = (i / total_steps) * 360 * d
            k = theta_degrees * math.pi / 180
            r = scale * math.sin(n * k)
            x = r * math.cos(k)
            y = 0.5 
            z = r * math.sin(k)
            self.morph_target_positions.append([x, y, z])
        
        self.estado_particulas = 3
class Particula:
    def __init__(self, ponto):
        self.pos = [ponto.x, ponto.y, ponto.z]
        self.vel = [random.uniform(-1, 1), random.uniform(2, 5), random.uniform(-1, 1)]
        self.ativa = True
        self.target = self.pos.copy()
        self.espiral_concluida = False      
        self.spiral_targets = []            
