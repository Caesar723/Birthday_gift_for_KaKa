import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *

import numpy as np

from functions import load_stl




# 创建 Pygame 窗口
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

# 设置透视投影
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

# 将视点移动一点
glTranslatef(0.0, 0.0, -5)

# 假设 'vertices' 是一个 Numpy 数组，包含你的球体的顶点数据
vertices = load_stl("circle")

# 创建和填充 VBO
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

# 假设你有10个球体，每个球体有一个颜色和位置
num_spheres = 10
colors = np.random.rand(num_spheres, 3)  # 随机颜色
positions = np.random.rand(num_spheres, 3) * 2 - 1  # 随机位置

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # 绘制每个球体
    for i in range(num_spheres):
        # 设置顶点位置属性
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # 设置颜色属性
        glColor3f(colors[i][0], colors[i][1], colors[i][2])  # 直接使用颜色值

        # 设置位置属性
        glPushMatrix()
        glTranslatef(positions[i][0], positions[i][1], positions[i][2])  # 使用 glTranslate 来移动球体

        glDrawArrays(GL_TRIANGLES, 0, len(vertices))  # 绘制球体

        glPopMatrix()

    pygame.display.flip()
    pygame.time.wait(10)