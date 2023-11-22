import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
from numpy import array, float32


vertexShader = '''
#version 450 core

layout (location = 0) in vec3 aPos;

out vec3 TexCoords;

uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

void main()
{
	TexCoords = aPos;
	gl_Position = projectionMatrix * viewMatrix * vec4(aPos, 1.0);
} 
'''

fragmentShader = '''
#version 450 core

layout (binding = 0) uniform samplerCube skybox;

out vec4 FragColor;

in vec3 TexCoords;

void main()
{    
	FragColor = texture(skybox, TexCoords);
}
'''


class Skybox(object):
	def __init__(self, textureFile):
		data = [       
			-1.0,  1.0, -1.0,
			-1.0, -1.0, -1.0,
			 1.0, -1.0, -1.0,
			 1.0, -1.0, -1.0,
			 1.0,  1.0, -1.0,
			-1.0,  1.0, -1.0,

			-1.0, -1.0,  1.0,
			-1.0, -1.0, -1.0,
			-1.0,  1.0, -1.0,
			-1.0,  1.0, -1.0,
			-1.0,  1.0,  1.0,
			-1.0, -1.0,  1.0,

			 1.0, -1.0, -1.0,
			 1.0, -1.0,  1.0,
			 1.0,  1.0,  1.0,
			 1.0,  1.0,  1.0,
			 1.0,  1.0, -1.0,
			 1.0, -1.0, -1.0,

			-1.0, -1.0,  1.0,
			-1.0,  1.0,  1.0,
			 1.0,  1.0,  1.0,
			 1.0,  1.0,  1.0,
			 1.0, -1.0,  1.0,
			-1.0, -1.0,  1.0,

			-1.0,  1.0, -1.0,
			 1.0,  1.0, -1.0,
			 1.0,  1.0,  1.0,
			 1.0,  1.0,  1.0,
			-1.0,  1.0,  1.0,
			-1.0,  1.0, -1.0,

			-1.0, -1.0, -1.0,
			-1.0, -1.0,  1.0,
			 1.0, -1.0, -1.0,
			 1.0, -1.0, -1.0,
			-1.0, -1.0,  1.0,
			 1.0, -1.0,  1.0
		]
		self.vertBuffer = array(data, dtype=float32)

		self.VBO = glGenBuffers(1)
		self.VAO = glGenVertexArrays(1)

		self.position = glm.vec3(0,0,0)
		self.rotation = glm.vec3(0,0,0)
		self.scale = glm.vec3(1,1,1)
		
		self.loadEnvironmentMap(textureFile=textureFile)
		#glDepthMask(GL_FALSE)
	
		self.activeShader = compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER), compileShader(fragmentShader, GL_FRAGMENT_SHADER))
		
	def getModelMatrix(self):
		identity = glm.mat4(1)

		translate = glm.translate(identity, self.position)

		pitch = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
		yaw = glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
		roll = glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

		rotation = pitch * yaw * roll

		scale = glm.scale(identity, self.scale)

		return translate * rotation * scale
		
	def loadEnvironmentMap(self, textureFile):
		faces = ["posx.jpg", "negx.jpg","posy.jpg",  "negy.jpg", "posz.jpg", "negz.jpg", ]

		enviromentBuffer = glGenTextures(1)
		glActiveTexture(GL_TEXTURE0);
		glBindTexture(GL_TEXTURE_CUBE_MAP, enviromentBuffer)
		
		for i in range(6):
			image = pygame.image.load(textureFile + "/" + faces[i])
			imageData = pygame.image.tostring(image, "RGB")
			glTexImage2D(
				GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
				0, GL_RGB, image.get_width(), image.get_height(), 0, GL_RGB, GL_UNSIGNED_BYTE, imageData
			)
			
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
		
	def render(self, viewMatrix, projectionMatrix):
		#self.activeShader = compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER), compileShader(fragmentShader, GL_FRAGMENT_SHADER))
		
		glDepthMask(GL_FALSE)
		glUseProgram(self.activeShader)
		
		skyeVM = glm.mat4(glm.mat3(viewMatrix))
		
		glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "viewMatrix"), 1, GL_FALSE, glm.value_ptr(skyeVM))
		glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "projectionMatrix"), 1, GL_FALSE, glm.value_ptr(projectionMatrix))
		
		glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
		glBindVertexArray(self.VAO)

		glBufferData(GL_ARRAY_BUFFER, self.vertBuffer.nbytes, self.vertBuffer, GL_STATIC_DRAW)
		
		arrayDim = 3
		
		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 4 * arrayDim, ctypes.c_void_p(0))
		glEnableVertexAttribArray(0)
		
		glDrawArrays(GL_TRIANGLES, 0, 36)
		
		glDepthMask(GL_TRUE)
		




