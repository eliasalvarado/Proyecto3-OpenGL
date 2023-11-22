from re import M
import pygame as pg
import math
from pygame.locals import *
from OpenGL.GL import GL_TRUE, glReadPixels, GL_RGB, GL_UNSIGNED_BYTE, GL_TRUE

from gl import Renderer
from shaders import *



width = 960
height = 540

pg.init()

screen = pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)
clock = pg.time.Clock()

renderer = Renderer(screen)

renderer.setShader(vertex_shader= vertexShader,
                   fragment_shader= fragmentShader )

model1 = renderer.createModel(id="model1",
                   filename="narsil.obj",
                   textureFile="narsil.bmp",
                   potition=(0,0,-5),
                   rotation=(-90,0,0),
                   scale=(2,2,2))

model2 = renderer.createModel(id="model3",
                   filename="prueba.obj",
                   textureFile="man.jpg",
                   potition=(0,0,-5),
                   rotation=(0,0,0),
                   scale=(0.1,0.1,0.1))

model3 = renderer.createModel(id="model3",
                   filename="dardo.obj",
                   textureFile="dardo.bmp",
                   potition=(0,0,-5),
                   rotation=(0,0,0),
                   scale=(1,1,1))

model4 = renderer.createModel(id="model4",
                   filename="powerRing.obj",
                   textureFile="powerRing.bmp",
                   potition=(0,0,-5),
                   rotation=(0,0,0),
                   scale=(1,1,1))

renderer.loadEnvironmentMap("env")
renderer.setModel(model2)


speed = 10

isRunning = True
while isRunning:

    keys = pg.key.get_pressed()
    deltaTime = clock.tick(60) / 1000

    for event in pg.event.get():
        if event.type == pg.QUIT:
            isRunning = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                isRunning = False
            elif event.key == pg.K_SPACE:
                size = screen.get_size()
                buffer = glReadPixels(0, 0, *size, GL_RGB, GL_UNSIGNED_BYTE)
                pg.display.flip()
                screen_surf = pg.image.fromstring(buffer, size, "RGB", GL_TRUE)
                pg.image.save(screen_surf, "output.jpg")
            elif event.key == pg.K_h:
                renderer.setModel(model1)
            elif event.key == pg.K_j:
                renderer.setModel(model2)
            elif event.key == pg.K_k:
                renderer.setModel(model3)
            elif event.key == pg.K_l:
                renderer.setModel(model4)
        elif event.type == pg.MOUSEWHEEL:
            renderer.camPosition.z -= event.y
        elif event.type == pg.MOUSEBUTTONDOWN:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_SIZEALL)
        elif event.type == pg.MOUSEBUTTONUP:
            pg.mouse.set_cursor()
    
    if pg.mouse.get_pressed()[0]:
        moved = pg.mouse.get_rel()
        if renderer.model.id == "model1":
            renderer.model.rotation.z += moved[0]
            renderer.model.rotation.x += moved[1]
        else:
            renderer.model.rotation.y += moved[0]
            renderer.model.rotation.x += moved[1]
        

    if keys[K_RIGHT]:
        renderer.camPosition.x += deltaTime * speed
        #renderer.camRotation.y += deltaTime * speed * 10
    elif keys[K_LEFT]:
        renderer.camPosition.x -= deltaTime * speed
        #renderer.camRotation.y -= deltaTime * speed * 10
    if keys[K_UP]:
        renderer.camPosition.y += deltaTime * speed
        #renderer.camRotation.x += deltaTime * speed * 10
    elif keys[K_DOWN]:
        renderer.camPosition.y -= deltaTime * speed
        #renderer.camRotation.x -= deltaTime * speed * 10
    if keys[K_MINUS]:
        renderer.camPosition.z += deltaTime * speed
    elif keys[K_PERIOD]:
        renderer.camPosition.z -= deltaTime * speed
    
    if keys[K_RIGHT] or keys[K_LEFT]:
        #print(renderer.camPosition.xyz)
        #print(abs(renderer.model.position.z - renderer.camPosition.z))
        pass
    
    if keys[K_a]:
        renderer.camRotation.y += deltaTime * speed ** 2
        #renderer.pitch += deltaTime * speed ** 2
    elif keys[K_d]:
        renderer.camRotation.y -= deltaTime * speed ** 2
        #renderer.pitch -= deltaTime * speed ** 2
    if keys[K_w]:
        renderer.camRotation.x += deltaTime * speed ** 2
        #renderer.yaw += deltaTime * speed ** 2
    elif keys[K_s]:
        renderer.camRotation.x -= deltaTime * speed ** 2
        #renderer.yaw -= deltaTime * speed ** 2
        

    if keys[K_1]:
        renderer.setShader(vertex_shader= distortionVertex,
                   fragment_shader= colorFulFragment)
    elif keys[K_2]:
        renderer.setShader(vertex_shader= clockVertex,
                   fragment_shader= theMatrixFragment)
    elif keys[K_3]:
        renderer.setShader(vertex_shader= vertexShader,
                   fragment_shader= powerFragment)
    elif keys[K_4]:
        renderer.setShader(vertex_shader= vertexShader,
                   fragment_shader= shininessFragment )

    renderer.time += deltaTime
        
    renderer.updateViewMatrix()
    renderer.render()
    pg.display.flip()


pg.quit()

