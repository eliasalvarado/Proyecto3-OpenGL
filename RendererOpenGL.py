from glm import cos, sin
import pygame as pg
from math import pi
from pygame.locals import *
from OpenGL.GL import GL_TRUE, glReadPixels, GL_RGB, GL_UNSIGNED_BYTE
from gl import Renderer
from shaders import *

width = 960
height = 540

pg.init()

screen = pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)
clock = pg.time.Clock()

renderer = Renderer(screen)

model1 = renderer.createModel(id="Narsil",
                   filename="narsil.obj",
                   textureFile="narsil.bmp",
                   potition=(0,0,-5),
                   rotation=(-90,0,0),
                   scale=(2,2,2))

model2 = renderer.createModel(id="Sauron",
                   filename="sauron.obj",
                   textureFile="sauron.jpeg",
                   potition=(0,0,-5),
                   rotation=(0,0,0),
                   scale=(1,1,1))

model3 = renderer.createModel(id="Dardo",
                   filename="dardo.obj",
                   textureFile="dardo.bmp",
                   potition=(0,0,-5),
                   rotation=(90,-45,0),
                   scale=(0.5,0.5,0.5))

model4 = renderer.createModel(id="Anillo del poder",
                   filename="powerRing.obj",
                   textureFile="powerRing.bmp",
                   potition=(0,0,-5),
                   rotation=(0,0,0),
                   scale=(1,1,1))


# Manejo de modelos, shaders y sonidos
models = [model1, model2, model3, model4]
currModel = 0
vertexs = [vertexShader, distortionVertex, clockVertex]
currVertex = 0
fragments = [fragmentShaderWithLight, colorFulFragment, theMatrixFragment, powerFragment, shininessFragment, reflectionShader, refractionShader]
currFrag= 0
envMusic = ["narsilSound.wav", "sauronSound.wav", "dardoSound.wav", "ringSound.wav"]


# Configuracion inicial
pg.display.set_caption("Proyecto 3 - OpenGL")
renderer.setShader(vertex_shader= vertexs[currVertex],
                   fragment_shader= fragments[currFrag] )
renderer.loadEnvironmentMap("env")
renderer.setModel(models[currModel])
renderer.target = models[currModel].position


# Musica
pg.mixer.music.load("sounds/" + envMusic[currModel])
pg.mixer.music.play(-1)
pg.mixer.music.set_volume(1)

speed = 10
angle = 0
radio = 5
limit = 5
isRunning = True
while isRunning:

    keys = pg.key.get_pressed()
    deltaTime = clock.tick(60) / 1000
    renderer.target = models[currModel].position

    for event in pg.event.get():
        if event.type == pg.QUIT:
            isRunning = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                isRunning = False
            # Guardar imagen
            elif event.key == pg.K_x:
                size = screen.get_size()
                buffer = glReadPixels(0, 0, *size, GL_RGB, GL_UNSIGNED_BYTE)
                pg.display.flip()
                screen_surf = pg.image.fromstring(buffer, size, "RGB", GL_TRUE)
                pg.image.save(screen_surf, "output.jpg")
            # Cambiar de modelo
            elif event.key == pg.K_SPACE:
                currModel = (currModel + 1) % len(models)
                renderer.setModel(models[currModel])
                pg.mixer.music.load("sounds/" + envMusic[currModel])
                pg.mixer.music.play(-1)
            # Cambiar de vertex shader
            elif event.key == pg.K_q:
                currVertex = (currVertex + 1) % len(vertexs)
                renderer.setShader(vertexs[currVertex], fragments[currFrag])
            # Cambiar de fragment shader
            elif event.key == pg.K_e:
                currFrag = (currFrag + 1) % len(fragments)
                renderer.setShader(vertexs[currVertex], fragments[currFrag])
        
        # Acercar y alejar camara
        elif event.type == pg.MOUSEWHEEL:
            temp = renderer.camPosition.z - event.y
            if temp <= limit and temp >= renderer.model.position.z + 1:
                renderer.camPosition.z -= event.y
        # Cambiar puntero
        elif event.type == pg.MOUSEBUTTONDOWN:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_SIZEALL)
        elif event.type == pg.MOUSEBUTTONUP:
            pg.mouse.set_cursor()
    
    # Rotacion del modelo
    if pg.mouse.get_pressed()[0]:
        moved = pg.mouse.get_rel()
        if renderer.model.id == "Narsil":
            renderer.model.rotation.z += moved[0]
            renderer.model.rotation.x += moved[1]
        else:
            renderer.model.rotation.y += moved[0]
            renderer.model.rotation.x += moved[1]
        

    if keys[K_RIGHT]:
        angle += 1
        renderer.camPosition.x = renderer.target.x + radio * sin(angle * pi / 180)
        renderer.camPosition.z = renderer.target.z + radio * cos(angle * pi / 180)
        #renderer.camRotation.y += deltaTime * speed * 10
    elif keys[K_LEFT]:
        angle -= 1
        renderer.camPosition.x = renderer.target.x + radio * sin(angle * pi /180)
        renderer.camPosition.z = renderer.target.z + radio * cos(angle * pi /180)
        #renderer.camRotation.y -= deltaTime * speed * 10
    if keys[K_UP]:
        angle += 1
        renderer.camPosition.y = renderer.target.x + radio * sin(angle * pi /180)
        renderer.camPosition.z = renderer.target.z + radio * cos(angle * pi /180)
        #renderer.camRotation.x += deltaTime * speed * 10
    elif keys[K_DOWN]:
        angle -= 1
        renderer.camPosition.y = renderer.target.x + radio * sin(angle * pi /180)
        renderer.camPosition.z = renderer.target.z + radio * cos(angle * pi /180)
        #renderer.camRotation.x -= deltaTime * speed * 10
    
    if keys[K_RIGHT] or keys[K_LEFT]:
        #print(renderer.camPosition.xyz)
        #print(abs(renderer.model.position.z - renderer.camPosition.z))
        pass
    
    # Movimiento de la camara
    if keys[K_a]:
        if renderer.camPosition.x >= -limit:
            renderer.camPosition.x -= deltaTime * speed
    elif keys[K_d]:
        if renderer.camPosition.x <= limit:
            renderer.camPosition.x += deltaTime * speed
    if keys[K_w]:
        if renderer.camPosition.y <= limit:
            renderer.camPosition.y += deltaTime * speed
    elif keys[K_s]:
        if renderer.camPosition.y >= -limit:
            renderer.camPosition.y -= deltaTime * speed

    if keys[K_j]:
        renderer.camRotation.y += deltaTime * speed ** 2
    elif keys[K_l]:
        renderer.camRotation.y -= deltaTime * speed ** 2
    if keys[K_i]:
        renderer.camRotation.x += deltaTime * speed ** 2
    elif keys[K_k]:
        renderer.camRotation.x -= deltaTime * speed ** 2
    
    renderer.time += deltaTime
    
    # print("position")
    # print(renderer.camPosition)
    # print("rotation")
    # print(renderer.camRotation)
        
    renderer.updateViewMatrix()
    renderer.render()
    # Texto
    renderer.addText(models[currModel].id, width / 2 - width * 0.05, height - height * 0.1)
    pg.display.flip()


pg.quit()

