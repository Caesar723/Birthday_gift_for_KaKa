import pygame
from pygame.locals import DOUBLEBUF , OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image,ImageSequence
import time
import os
from numba import jit


from rotate import *
#from camera import Camera

ORGPATH=os.path.dirname(os.path.abspath(__file__))
PATH=ORGPATH+"/{}"


def time_recore(func):
    
    def function(*args):
        
        t=time.time()
        answer=func(*args)
        print(time.time()-t)
        return answer
    return function
def load_stl(name,to_vertices=0):
    filename=PATH.format(f"stl/{name}.stl")
    with open(filename, 'rb') as file:
        file.read(80)  # 跳过 STL 文件头部的80字节内容

        # 读取三角面片的数量
        count_bytes = file.read(4)
        count = np.frombuffer(count_bytes, dtype=np.uint32)[0]
        # 读取三角面片的数据
        dtype = np.dtype([
            ('normal', np.float32, (3,)),
            ('vertex1', np.float32, (3,)),
            ('vertex2', np.float32, (3,)),
            ('vertex3', np.float32, (3,)),
            ('attribute_byte_count', np.uint16)
        ])
        data = np.fromfile(file, dtype=dtype, count=count)
    if to_vertices:
        arr=[]
        for i in range(len(data['vertex1'])):
            arr.append(data['vertex1'][i])
            arr.append(data['vertex2'][i])
            arr.append(data['vertex3'][i])
        vertices=np.array(arr)
        return vertices
    else:
        return data
    
def handle_event(event,camera,firework,running,thread_cache):
    
    if event.type == pygame.MOUSEMOTION and camera.eye_flag:
        dx, dy = event.rel
        if camera.rotation_x+dy<90 and camera.rotation_x+dy>-90:
            camera.rotation_x += dy/5
        camera.rotation_y += dx/5
    elif event.type == pygame.MOUSEBUTTONDOWN:
        camera.eye_flag=1
        pos= pygame.mouse.get_pos()
        if pos[0]<50 and pos[1]<50:
            running[0] = False

    elif event.type == pygame.MOUSEBUTTONUP:
        camera.eye_flag=0
    elif event.type == pygame.KEYDOWN:  # 键盘按下事件
        if event.key in camera.move_flag_dict:
            camera.move_flag=event.key
        elif event.key in camera.fly_flag_dict:
            camera.fly_flag=camera.fly_flag_dict[event.key]
        
            #firework.start_auto_fire()
        elif event.key==pygame.K_f:
            firework.generate_firework(
                firework.get_random_position(),
                firework.get_random_velocity()
                )

        elif event.key==pygame.K_v:
            thread=firework.start_auto_fire_new_year_eve_v2()
            thread_cache.append(thread)
    elif event.type == pygame.KEYUP:  # 键盘按下事件
        if event.key in camera.move_flag_dict:
            camera.move_flag=0
        elif event.key in camera.fly_flag_dict:
            camera.fly_flag=0

        

def setDraw(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (width / height), 0.1, 300.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)

def setLight():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)


    
    



def setMateral(material_ambient=(0.5,0.5,0.5, 0.5),
               material_diffuse=(0.5,0.5,0.5),
               material_specular=(0.5,0.5,0.5, 0.5),
               material_shininess=(32.0,)):
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)
    

    

def drawPicture(stl_vertices,move_x,
                move_y,move_z,rotate_x,
                rotate_y,rotate_z,scale_x,
                scale_y,scale_z,material_ambient=(0.5,0.5,0.5, 0.5),
               material_diffuse=(0.5,0.5,0.5),
               material_specular=(0.5,0.5,0.5, 0.5),
               material_shininess=(32.0,)):#数组，x轴平移，y轴平移，z轴平移，x轴旋转，y轴旋转，z轴旋转，x轴放大，y轴放大，z轴放大
    glPushMatrix()
    glTranslatef(move_x, move_y, move_z)
    glRotatef(rotate_x, 1, 0, 0)
    glRotatef(rotate_y, 0, 1, 0)
    glRotatef(rotate_z, 0, 0, 1)
    glScalef(-scale_x,scale_y,scale_z)

    setMateral(material_ambient,
               material_diffuse,
               material_specular,
               material_shininess)
    
    
    glBegin(GL_TRIANGLES)
    
    for i in range(0, len(stl_vertices['vertex1'])):
        glNormal3fv(stl_vertices['normal'][i])
        glVertex3fv(stl_vertices['vertex1'][i])
        glVertex3fv(stl_vertices['vertex2'][i])
        glVertex3fv(stl_vertices['vertex3'][i])
    
    glEnd()
    glPopMatrix()

def create_display_list(func):
    def newfunc(*args):
        list_id = glGenLists(1)
        glNewList(list_id, GL_COMPILE)
        func(*args)
        glEndList()
        return list_id

    return newfunc


def drawGraphs(imgs):
    for img in imgs:
        img.display()



def to_one(nums,final=-1):
    if final!=-1:
        return (nums[0]/255,nums[1]/255,nums[2]/255,final)
    else:
        return (nums[0]/255,nums[1]/255,nums[2]/255)
    
def to_np_array(arr):
    arr_np=np.array([
                [arr[0]],
                [arr[1]],
                [arr[2]]
            ],dtype='float64')#x.y.z
    return arr_np
    
def create_vbo(vertices):
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo

    



# def draw_vbo_model(vbo_vertices, vertex_count,color):
#     glEnable(GL_COLOR_MATERIAL)
#     glDisable(GL_LIGHTING)
#     glDisable(GL_LIGHT0)
#     glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
#     glEnableClientState(GL_VERTEX_ARRAY)
#     glVertexPointer(3, GL_FLOAT, 0, None)
    
    
    
#     glBindBuffer(GL_ARRAY_BUFFER, 0)
#     glEnable(GL_BLEND)
#     glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

#     glColor4f(*color)  # 设置颜色和透明度
#     glDrawArrays(GL_TRIANGLES, 0, vertex_count)

#     glDisableClientState(GL_VERTEX_ARRAY)
#     glDisable(GL_BLEND)
#     glDisable(GL_COLOR_MATERIAL)
#     glEnable(GL_LIGHTING)
#     glEnable(GL_LIGHT0)

def load_glf(name):
    
    path=PATH.format(f"img/{name}.GIF")
    # 加载GIF图像
    gif_image = Image.open(path)
    gif_frames = gif_image.n_frames

    # 将GIF图像转换为纹理
    textures = []
    
    for i in range(gif_frames):
        gif_image.seek(i)
        frame = gif_image.convert("RGBA")
        flipped_image = frame.transpose(Image.FLIP_TOP_BOTTOM)
        
        data = np.array(flipped_image)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, frame.width, frame.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        textures.append(texture_id)
        
    return textures


def img2texture(data,size):
    
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size[0], size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    
    return texture_id


def update_thread(update_list,running):# thread
    t=time.time()
    while running[0]:
        if time.time()-t>=0.02:
            t=time.time()
            for obj in update_list:
                obj.update()

def getIcon():
    return pygame.image.load(PATH.format("img/app.png"))

def update(update_list):# thread
    
    for obj in update_list:
        obj.update()
    



