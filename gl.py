import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame

from Model import Model
from obj import Obj
from Skybox import Skybox

class Renderer(object):
	def __init__(self, screen):
		_, _, self.width, self.height = screen.get_rect()

		self.clearColor = [0, 0, 0]

		glEnable(GL_DEPTH_TEST)
		glEnable(GL_CULL_FACE)
		# glGenerateMipmap(GL_TEXTURE_2D)
		glViewport(0, 0, self.width, self.height)

		self.model = None

		self.activeShader = None
		
		self.directionalLight = glm.vec3(0,0,-1)

		self.camPosition = glm.vec3(0,0,0)
		self.camRotation = glm.vec3(0,0,0)
		self.viewMatrix = self.getViewMatrix()

		self.projectionMatrix = glm.perspective(glm.radians(60), self.width / self.height, 0.1, 1000)
		
		self.time = 0.0
		
		self.envMap = None
		

	def setShader(self, vertex_shader, fragment_shader):
		if vertex_shader and fragment_shader:
			self.activeShader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER), compileShader(fragment_shader, GL_FRAGMENT_SHADER))
	
	def createModel(self, id, filename, textureFile = None, potition = (0,0,0), rotation = (0,0,0), scale = (1,1,1)):
		modelData = Obj(filename=filename)
		data = []
		
		for face in modelData.faces:
			vertCount = len(face)
			
			v0 = modelData.vertices[face[0][0] - 1]
			vt0 = modelData.texCoords[face[0][1] - 1]
			vn0 = modelData.normals[face[0][2] - 1]
			[data.append(i) for i in v0]
			[data.append(vt0[i]) for i in range (2)]
			[data.append(i) for i in vn0]
			
			v1 = modelData.vertices[face[1][0] - 1]
			vt1 = modelData.texCoords[face[1][1] - 1]
			vn1 = modelData.normals[face[1][2] - 1]
			[data.append(i) for i in v1]
			[data.append(vt1[i]) for i in range (2)]
			[data.append(i) for i in vn1]	
			
			v2 = modelData.vertices[face[2][0] - 1]
			vt2 = modelData.texCoords[face[2][1] - 1]
			vn2 = modelData.normals[face[2][2] - 1]
			[data.append(i) for i in v2]
			[data.append(vt2[i]) for i in range (2)]
			[data.append(i) for i in vn2]
			
			if vertCount == 4:
				v3 = modelData.vertices[face[3][0] - 1]
				vt3 = modelData.texCoords[face[3][1] - 1]
				vn3 = modelData.normals[face[3][2] - 1]
				
				[data.append(i) for i in v0]
				[data.append(vt0[i]) for i in range (2)]
				[data.append(i) for i in vn0]
				
				[data.append(i) for i in v2]
				[data.append(vt2[i]) for i in range (2)]
				[data.append(i) for i in vn2]
				
				[data.append(i) for i in v3]
				[data.append(vt3[i]) for i in range (2)]
				[data.append(i) for i in vn3]

		model = Model(id=id, data=data, potition=potition, rotation=rotation, scale=scale)
		if textureFile:
			model.loadTexture(textureFile)
		
		return model
		
	def setModel(self, model):
		self.model = model


	def getViewMatrix(self):
		identity = glm.mat4(1)

		translate = glm.translate(identity, self.camPosition)

		self.pitch = glm.rotate(identity, glm.radians(self.camRotation.x), glm.vec3(1,0,0))
		self.yaw = glm.rotate(identity, glm.radians(self.camRotation.y), glm.vec3(0,1,0))
		self.roll = glm.rotate(identity, glm.radians(self.camRotation.z), glm.vec3(0,0,1))

		rotation = self.pitch * self.yaw * self.roll

		return glm.inverse(translate * rotation)

	def loadEnvironmentMap(self, textureFile):
		self.envMap = Skybox(textureFile=textureFile)
	
	def updateViewMatrix(self):
		#self.viewMatrix = self.getViewMatrix()

		self.viewMatrix = glm.lookAt(self.camPosition, self.model.position, glm.vec3(0,1,0))
		
	def render(self):
		glClearColor(self.clearColor[0], self.clearColor[1], self.clearColor[2], 0.1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		if self.envMap:
			view = self.getViewMatrix()
			self.envMap.render(view, self.projectionMatrix)

		if self.activeShader:
			glUseProgram(self.activeShader)

			glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "viewMatrix"), 1, GL_FALSE, glm.value_ptr(self.viewMatrix))
			glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "projectionMatrix"), 1, GL_FALSE, glm.value_ptr(self.projectionMatrix))
			
			glUniform1f(glGetUniformLocation(self.activeShader, "time"), self.time)
			glUniform3fv(glGetUniformLocation(self.activeShader, "directionalLight"), 1, glm.value_ptr(self.directionalLight))
			
			resolution = glm.vec2(self.width, self.height)
			glUniform2fv(glGetUniformLocation(self.activeShader, "resolution"), 1, GL_FALSE, glm.value_ptr(resolution))

		if self.model:
			if self.activeShader:
				glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "modelMatrix"), 1, GL_FALSE, glm.value_ptr(self.model.getModelMatrix()))
			self.model.render()
		
	


