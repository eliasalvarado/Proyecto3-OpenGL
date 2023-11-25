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

uniform samplerCube skybox;

out vec4 fragColor;

in vec3 TexCoords;

void main()
{    
	fragColor = texture(skybox, TexCoords);
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
	
		self.activeShader = compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER), compileShader(fragmentShader, GL_FRAGMENT_SHADER))
		self.enviromentBuffer = glGenTextures(1)
		glBindTexture(GL_TEXTURE_CUBE_MAP, self.enviromentBuffer)
		
		self.loadEnvironmentMap(textureFile=textureFile)
		
	def loadEnvironmentMap(self, textureFile):
		faces = ["posx.jpg", "negx.jpg","posy.jpg",  "negy.jpg", "posz.jpg", "negz.jpg", ]
		
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
		
		glBindTexture(GL_TEXTURE_CUBE_MAP, self.enviromentBuffer)
		
		glDrawArrays(GL_TRIANGLES, 0, 36)
		
		glDepthMask(GL_TRUE)
		




