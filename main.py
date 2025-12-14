import pygame
from pygame.locals import DOUBLEBUF, OPENGL,FULLSCREEN

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

import datetime
import threading


from rotate import Rx, Ry, Rz
from Font import Font
from functions import *
from light import Sun
from camera import Camera
from cake import Cake
from kaka import KaKa
from firework import Firework_generator
from schedule import Table
from favourite_img import Favourite_Img



SIZE_TEXT=4

def getAnniversary():
    anniversary=datetime.datetime(2023, 5, 3)
    today = datetime.datetime.now()
    change=today-anniversary
    return change.days

def anniversary_days(anniversary:str):
    print(anniversary)
    length=len(anniversary)
    texts=[]
    for i in range(length):
        
        texts.append(Font((length*SIZE_TEXT/2-SIZE_TEXT/2-(SIZE_TEXT*i),10,0), anniversary[i], (1, 1, 1), (153, 130, 108)))
    return texts

def getAge():  # return age,whether birthday
    birthday_flag = False
    birthday = datetime.datetime(2005, 8, 30)
    year_b, month_b, day_b = birthday.year, birthday.month, birthday.day
    today = datetime.datetime.now()
    year_n, month_n, day_n = today.year, today.month, today.day

    if datetime.date(2005,month_n,day_n)==datetime.date(2005,month_b,day_b):
    
    #if month_n <= month_b and day_n == day_b:
        birthday_flag = True
        age = year_n - year_b
    elif datetime.date(2005,month_n,day_n)>datetime.date(2005,month_b,day_b):
        age = year_n - year_b
    else:
        age = year_n - year_b - 1
    return (age, birthday_flag)


def initinal_imgs():
    age, birth_flag = getAge()
    
    sun = Sun((10.0, 100.0, -80.0, 1), 10)
    name = Font((0, 0, 0), "name", (1, 1, 1), (98, 0, 98))
    
    if birth_flag:
        happy = Font((0, 17, 0), "H", (1, 1, 1), (153, 130, 108))
        birthday = Font((0, 10, 0), "B", (1, 1, 1), (153, 130, 108))
        arr = [happy, birthday, sun, name]

    else:
        love = Font(
            (10, 0, 0), "love", (4, 4, 4), (255, 10, 10), (0.9, 0.1, 0.1), (0, 0, 0)
        )
        texts=anniversary_days(str(getAnniversary()))
        #table=Table((-25,0,-7),40)
        #img=Favourite_Img((19,0,-7),320)
        #arr = [sun, name, love,img]+texts
        arr = [sun, name, love]+texts
    str_age = str(age)
    for i in range(len(str_age)):
        arr.append(
            Font(
                (1.6 - i * 3, -11.3, 0),
                str_age[i],
                (0.7, 0.7, 0.7),
                (98, 30, 30),
                (0.9, 0.1, 0.1),
            )
        )
    cake = Cake((0, -10, 0), age)
    arr.append(cake)
    return arr, cake


def initinal_update_list(camera, cake,firework):
    arr = [camera,firework]
    for candle in cake.candles:
        for light in candle.lights:
            arr.append(light)
    return arr

def pick_display_smart(prefer_non_primary=False):
    """
    prefer_non_primary=False: 默认选最大面积屏（更“智能”）
    prefer_non_primary=True : 优先选非主屏，否则再选最大面积
    """
    n = pygame.display.get_num_displays()
    sizes = pygame.display.get_desktop_sizes()  # list[(w,h)]

    if n <= 1:
        return 0, sizes[0]

    # 计算每块屏的面积
    areas = [w * h for (w, h) in sizes]
    biggest = max(range(n), key=lambda i: areas[i])

    if prefer_non_primary:
        # 优先非0屏；若存在多个非0，挑面积最大的非0
        non_primary = [i for i in range(n) if i != 0]
        if non_primary:
            best_non0 = max(non_primary, key=lambda i: areas[i])
            return best_non0, sizes[best_non0]

    return biggest, sizes[biggest]

def create_fullscreen_on(display_idx):
    sizes = pygame.display.get_desktop_sizes()
    # 越界直接回退主屏
    if display_idx < 0 or display_idx >= len(sizes):
        display_idx = 0

    w, h = sizes[display_idx]
    screen = pygame.display.set_mode((w, h), DOUBLEBUF | OPENGL | FULLSCREEN, display=display_idx)

    # OpenGL 关键：viewport 要同步
    glViewport(0, 0, w, h)

    # 你的投影矩阵/正交矩阵如果依赖 w,h，也要在这里重算
    # update_projection(w, h)

    return screen, display_idx, w, h

def main():
    running = [True]
    thread_cache=[]
    pygame.init()
    pygame.mixer.init()
    # 1400,800
    #sizes = pygame.display.get_desktop_sizes()
    display_idx, (width, height) = pick_display_smart(prefer_non_primary=True)
    screen_info = pygame.display.Info()
    #screen_width, screen_height = screen_info.current_w, screen_info.current_h
    width, height = screen_info.current_w, screen_info.current_h
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | FULLSCREEN, display=display_idx)
    pygame.display.set_caption("Gift for KaKa❤️")
    pygame.display.set_icon(getIcon())

    age,birth_flag=getAge()
    img_list, cake = initinal_imgs()

    initinal_cam_pos = np.array([0, 0, -50])
    camera = Camera(initinal_cam_pos)
    firework=Firework_generator(running,age,birth_flag)
    kaka = KaKa(10, 15, (0, -10, 20), cake,firework)
    

    
    img_list.append(kaka)
    img_list.append(firework)

    
    update_list = initinal_update_list(camera, cake,firework)

    setDraw(width, height)
    setLight()
    # setMateral()

    # thread = threading.Thread(target=update_thread, args=(update_list, running))
    # thread.start()    


    time_record=time.time()
    while running[0]:
        if time.time()-time_record>=0.02:
            time_record=time.time()

            
            update(update_list)
            
            for event in pygame.event.get():
                
                if event.type == pygame.QUIT:
                    running[0] = False
                    # for thread in thread_cache:
                    #     thread.stop()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                    n = pygame.display.get_num_displays()
                    if n > 1:
                        display_idx = (display_idx + 1) % n
                        screen, display_idx, w, h = create_fullscreen_on(display_idx)
                handle_event(event, camera, kaka,firework,running,thread_cache)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            
            gluLookAt(
                *camera.getPosition(camera.position), 
                *camera.getPosition(camera.getResult_target()), 
                0, 1, 0
            )

            # (166/255,213/255,243/255)
            #8 / 255, 16 / 255, 55 / 255
            glClearColor(8 / 255, 16 / 255, 55 / 255, 0.7)

            drawGraphs(img_list)
            pygame.display.flip()

    #thread.join()
    pygame.quit()


if __name__ == "__main__":
    #getAnniversary()
    main()
