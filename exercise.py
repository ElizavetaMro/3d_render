# -*- coding: utf-8 -*-
import sys
import numpy as np
from random import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import compileProgram, compileShader

# Вершинный шейдер
vertex_src = """
#version 330 core
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;

uniform mat4 u_transform;

out vec3 v_color;

void main()
{
    gl_Position = u_transform * vec4(a_position, 1.0);
    v_color = a_color;
}
"""

# Фрагментный шейдер
fragment_src = """
#version 330 core
in vec3 v_color;
out vec4 out_color;

void main()
{
    out_color = vec4(v_color, 1.0);
}
"""

# Глобальные переменные
program = None
VAO = VBO = None
transform_location = None
rotation = [0, 0, 0]
pointcolor = None

def init():
    global program, VAO, VBO, transform_location, pointcolor
    
    # Создаем шейдерную программу
    vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
    program = compileProgram(vertex_shader, fragment_shader)
    
    # Данные вершин и цветов
    vertices = np.array([
        [ 0.0,  0.5, 0.0],  # верхняя вершина
        [-0.5, -0.5, 0.0],  # левая нижняя
        [ 0.5, -0.5, 0.0]   # правая нижняя
    ], dtype=np.float32)
    
    pointcolor = np.array([
        [1.0, 1.0, 0.0],  # желтый
        [0.0, 1.0, 1.0],  # голубой
        [1.0, 0.0, 1.0]   # пурпурный
    ], dtype=np.float32)
    
    # Создаем VAO (Vertex Array Object)
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    
    # Создаем VBO для вершин
    VBO = glGenBuffers(2)
    
    # Вершины
    glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3*4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    # Цвета
    glBindBuffer(GL_ARRAY_BUFFER, VBO[1])
    glBufferData(GL_ARRAY_BUFFER, pointcolor.nbytes, pointcolor, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 3*4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    
    # Получаем location uniform-переменной
    transform_location =  glGetUniformLocation(program, "u_transform")
    
    # Начальная матрица преобразования
    glUseProgram(program)
    glUniformMatrix4fv(transform_location, 1, GL_FALSE, np.identity(4, dtype=np.float32))

def specialkeys(key, x, y):
    global rotation, pointcolor
    
    if key == GLUT_KEY_UP:
        rotation[0] += 5
    elif key == GLUT_KEY_DOWN:
        rotation[0] -= 5
    elif key == GLUT_KEY_LEFT:
        rotation[1] += 5
    elif key == GLUT_KEY_RIGHT:
        rotation[1] -= 5
    elif key == GLUT_KEY_END:
        # Обновляем цвета
        new_colors = np.array([[random(), random(), random()] 
                               for _ in range(3)], dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, VBO[1])
        glBufferSubData(GL_ARRAY_BUFFER, 0, new_colors.nbytes, new_colors)
        pointcolor = new_colors
    
    update_transform()

def update_transform():
    from math import radians, cos, sin
    
    # Создаем матрицу вращения
    rx = radians(rotation[0])
    ry = radians(rotation[1])
    
    # Матрица вращения вокруг X
    rot_x = np.array([
        [1, 0, 0, 0],
        [0, cos(rx), -sin(rx), 0],
        [0, sin(rx), cos(rx), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)
    
    # Матрица вращения вокруг Y
    rot_y = np.array([
        [cos(ry), 0, sin(ry), 0],
        [0, 1, 0, 0],
        [-sin(ry), 0, cos(ry), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)
    
    # Комбинированная матрица
    transform = rot_y @ rot_x
    
    # Передаем в шейдер
    glUseProgram(program)
    glUniformMatrix4fv(transform_location, 1, GL_FALSE, transform)

def draw():
    glClear(GL_COLOR_BUFFER_BIT)
    
    glUseProgram(program)
    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    
    glutSwapBuffers()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(300, 300)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"Modern OpenGL with Shaders")
    
    glClearColor(0.2, 0.2, 0.2, 1.0)
    
    init()
    
    glutDisplayFunc(draw)
    glutIdleFunc(draw)
    glutSpecialFunc(specialkeys)
    
    glutMainLoop()

if __name__ == "__main__":
    main()