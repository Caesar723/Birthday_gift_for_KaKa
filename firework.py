import pygame
import numpy as np
import random
import threading
from numba import njit
import math
from datetime import datetime
from rotate import *
from functions import *
from obj import *


# def time_judge(func):# used to judge the time of function
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         print(f"function {func.__name__} Time taken: {end_time - start_time} seconds")
#         return result
#     return wrapper

TIME_INTERVAL=0.017

COLOR=[
        (144,220,108),#green
        (245,194,84),#yellow
        (205,45,65),#red
        (60,122,240),#blue
        (217,217,217),#white
        (171,37,200),#purple
           ]
COLOR_MATCH=[
    [
        (144,220,108),#green
        (245,194,84)#yellow
    ],
    [
        (245,194,84),
        (60,122,240)# yellow,blue
    ],
    [
        (60,122,240),
        (217,217,217)#blue ,white
    ],
    [
        (245,194,84),
        (205,45,65)#yellow, red
    ],
    [
        (171,37,200),
        (217,217,217)#purple,white
    ],
        
        
    ]
class Firework_arr:

    def __init__(self,size,num_each) -> None:
        self.size=size
        self.arr=np.zeros(size, dtype=np.float32)
        self.boolean=np.full(size[0], False)
        self.counter_index=0
        self.num_each=num_each

    def check_limit(self):
        if self.counter_index>=self.size[0]:
            self.counter_index=0

    # def create_new(self):
        
    #     check=False
    #     #for i in range(self.counter_index,self.counter_index+self.num_each):
    #     if self.boolean[self.counter_index]:
    #         check=True
        
    #     if check:
    #         self.counter_index+=self.num_each
    #         self.check_limit()
    #         return self.create_new()
    #     else:
    #         result=range(self.counter_index,self.counter_index+self.num_each)
    #         for i in result:
    #             self.boolean[i]=True
    #         self.counter_index+=self.num_each
    #         self.check_limit()
    #         return result

    def create_new(self):
        N = self.size[0]
        k = self.num_each

        while True:
            start = self.counter_index
            end = start + k

            # 若这段会越界，直接回到 0 再找
            if end > N:
                self.counter_index = 0
                continue

            # 必须检查整段是否空闲（而不是只检查 start）
            if self.boolean[start:end].any():
                self.counter_index = end
                if self.counter_index >= N:
                    self.counter_index = 0
                continue

            # 分配：一次性置 True（比 for 循环快）
            self.boolean[start:end] = True

            self.counter_index = end
            if self.counter_index >= N:
                self.counter_index = 0

            return range(start, end)


    def remove(self,index):
        self.boolean[index]=False

    def get_data(self,start=0,end=0):
        if end==0:
            return self.arr[self.boolean]
        else:
            return self.arr[self.boolean,start:end]
        

class Firework_generator():#it is used to create firework, like a rocket launcher

    def __init__(self,running,age,auto_fire=False) -> None:
        self.thread_cache=[]# this list is used to process the threading

        self.power=random.randint(10,20)

        self.particles=[]# it is used to store the Particle class
        self.effects=[]# it is used to store the Tail_Effect class
        
        self.setMusic()# initinal the music

        #vbo is used to improve the efficiency of firework
        self.vbo_tri = glGenBuffers(1)
        self.vbo_poin = glGenBuffers(1)

        self.particle_posiiton_np=Firework_arr((600000,23),3)#changed_position(3),color(3),velocity(3),angle,angle_change,live,live_change,size,size_change,org_position(3),change_tri,horizontal,vertical,time_counter,tail
        self.effect_position_np=Firework_arr((600000,11),1)#position,color,velocity,live,live_change

        #Firework_types include different kinds of Firework
        self.firework_type=Firework_types(age,self.particle_posiiton_np,self.effect_position_np)

        # auto_fire is true Firework_generator will send firework automately 
        self.auto_para=[auto_fire,running,age]

        self.auto=Auto_fire(self.auto_para[1],self,self.auto_para[2])
        

        
        #self.firework_ready=[]
    def start_auto_fire(self):
        
        if self.auto_para[0]:
            
            
            self.auto.start_auto_fire()
            self.auto_para[0]=False

    def start_auto_fire_new_year_eve(self):
          
        self.auto=Auto_fire(self.auto_para[1],self,self.auto_para[2])
        thread=self.auto.start_auto_fire_new_year_eve()
        return thread

    def start_auto_fire_new_year_eve_v2(self):
        self.auto=Auto_fire(self.auto_para[1],self,self.auto_para[2])
        thread=self.auto.start_auto_fire_new_year_eve_v2()
        return thread
        

    def setMusic(self):
        # store the path of files
        burst_path=("music/burst-sm-1.mp3","music/burst-sm-2.mp3","music/burst1.mp3","music/burst2.mp3")
        lift_path=("music/lift1.mp3","music/lift2.mp3","music/lift3.mp3")
        crackle_path="music/crackle-sm-1.mp3"
        
        self.burst_sounds=[pygame.mixer.Sound(PATH.format(path)) for path in burst_path]
        self.lift_sounds=[pygame.mixer.Sound(PATH.format(path)) for path in lift_path]
        self.crackle_sounds=[pygame.mixer.Sound(PATH.format(crackle_path))]

        

    def getMusic(self,musics):# get music randomly
        return musics[random.randint(0,len(musics)-1)]
    
    def generate_firework(self,position,velocity,types=0,color=(-1,-1,-1)):
        if types==0:
            types=self.firework_type.choose_random_type()# set firework type used

        #print(position,velocity,types,color)
        
        self.particles.append(
            frame_fire(
            position,# position of particle
            velocity,# velocity of particle
            COLOR[random.randint(0,len(COLOR)-1)] if color==(-1,-1,-1) else color,# color of particle
            True,# whether particle need tail effect
            self.getMusic(self.burst_sounds),# music used
            types,# the type of firework
            self.particle_posiiton_np,# the pointer of big array
            self.effect_position_np# the pointer of big array
            )
        )
        
        music=self.getMusic(self.lift_sounds)
        music.set_volume(0.5)
        music.play()# play music when send firework
    
    def generate_firework_thread(self,position,velocity,types=0,color=(-1,-1,-1)):# used in threading in order to match the main thread
        
        if types==0:
            types=self.firework_type.choose_random_type()

        self.thread_cache.append((position,velocity,types,color))
    #@time_judge
    def check_thread(self):# like wise
        for para in list(self.thread_cache):
            self.generate_firework(*para)
            self.thread_cache.remove(para)

    def get_random_position(self):
        position_z=random.uniform(-8,8)
        position_x=random.uniform(-20,20)
        position_y=random.uniform(-20,-10)
        return (position_x,position_y,position_z)

    def get_random_velocity(self):
        velocity_x=random.uniform(0,1)
        velocity_y=random.randint(25,30)
        velocity_z=random.uniform(0,1)
        return (velocity_x,velocity_y,velocity_z)

    
    #@time_judge
    def update(self):
        #print("particle size",len(self.effects))
        self.check_thread()# used in threading
        self.change_position_particle()# upate the state of particle
        
        self.change_position_effect()# upate the state of effect


    def change_position_effect(self):#position,color,velocity,live,live_change
        improved_change_position_effect(self.effect_position_np.arr,self.effect_position_np.boolean)
        

    def change_position_particle(self):#changed_position(3),color(3),velocity(3),angle,angle_change,live,live_change,size,size_change,org_position(3),change_tri,horizontal,vertical,time_counter,tail
        effects=improved_change_position_particle(self.particle_posiiton_np.arr,self.particle_posiiton_np.boolean)
        for i in range(effects.shape[0]//6):
            index=i*6
            Tail_Effect(effects[index,15:18].reshape(3,1)+np.random.rand(3, 1)*0.1,effects[index,3:6],self.effect_position_np)
        
      

        


    #@time_judge
    def display(self):# display particle and effect
        glEnable(GL_COLOR_MATERIAL)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
                
        vertices=self.particle_posiiton_np.get_data(0,6)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_tri)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_DYNAMIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(3, GL_FLOAT, 6 * vertices.itemsize, None)
        glColorPointer(3, GL_FLOAT, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))

        glDrawArrays(GL_TRIANGLES, 0, len(vertices))

        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)


        
        for particle in self.particles:

            particle.break_self(self)# check whether particle will break
        
        
        
        points=self.effect_position_np.get_data(0,6)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_tri)
        glBufferData(GL_ARRAY_BUFFER, points, GL_DYNAMIC_DRAW)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(3, GL_FLOAT, 6 * points.itemsize, None)
        glColorPointer(3, GL_FLOAT, 6 * points.itemsize, ctypes.c_void_p(3 * points.itemsize))

        glDrawArrays(GL_POINTS, 0, len(points))

        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        
        

        glDisable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)



###both are used to update the position and other attributes of particle and effect
# @njit
# def improved_change_position_effect(arr,arr_bool):
#     idx = np.nonzero(arr_bool)[0]
#     #orgData=arr[arr_bool]
#     if idx.size:
#         time_inter=TIME_INTERVAL
#         G=9.81
#         M=0.1
#         K_f=2
#         force_g=-G*M
#         force_friction=-arr[idx,6:9]*0.5*K_f
#         force_friction[:,1]+=force_g
#         acc=force_friction/M
#         arr[idx,6:9]+=acc*time_inter
#         arr[idx,0:3]+=arr[idx,6:9]*time_inter
#         arr[idx,9]-=arr[idx,10]
#         #arr[arr_bool]=orgData
#         for t in range(idx.size):
#             i = idx[t]
#             if arr[i, 9] < 0:
#                 arr_bool[i] = False

#@time_judge
@njit(fastmath=True, cache=True)
def improved_change_position_effect(arr, arr_bool):
    idx = np.nonzero(arr_bool)[0]
    if idx.size == 0:
        return

    dt = TIME_INTERVAL
    G = 9.81
    M = 0.1
    Kf = 2.0
    # 预计算常量，少做除法
    damp = 0.5 * Kf / M
    gacc = -G  # 因为 (force_g)/M = (-G*M)/M = -G

    for t in range(idx.size):
        i = idx[t]

        vx = arr[i, 6]; vy = arr[i, 7]; vz = arr[i, 8]

        # a = -v*0.5*Kf/M, y 方向再加重力加速度
        ax = -vx * damp
        ay = -vy * damp + gacc
        az = -vz * damp

        vx += ax * dt
        vy += ay * dt
        vz += az * dt

        arr[i, 6] = vx; arr[i, 7] = vy; arr[i, 8] = vz

        arr[i, 0] += vx * dt
        arr[i, 1] += vy * dt
        arr[i, 2] += vz * dt

        life = arr[i, 9] - arr[i, 10]
        arr[i, 9] = life
        if life < 0.0:
            arr_bool[i] = False
# @njit
# def improved_change_position_particle(arr,arr_bool):
#     idx = np.nonzero(arr_bool)[0]
#     #orgData=arr[arr_bool]
#     if idx.size:
#         time_inter=TIME_INTERVAL
#         G=9.81
#         M=1
#         K_f=0.7
#         force_g=-G*M
#         force_friction=-arr[idx,6:9]*0.5*K_f
#         force_friction[:,1]+=force_g
#         acc=force_friction/M
#         arr[idx,6:9]+=acc*time_inter
#         arr[idx,15:18]+=arr[idx,6:9]*time_inter
#         arr[idx,9]+=arr[idx,10]
#         arr[idx,11]-=arr[idx,12]
#         arr[idx,13]-=arr[idx,14]

#         arr[idx,0]=arr[idx,13]*np.cos(arr[idx,18]+arr[idx,9])+arr[idx,15]#15,16,17
#         arr[idx,1]=(arr[idx,13]*np.sin(arr[idx,18]+arr[idx,9])*arr[idx,19])+arr[idx,16]
#         arr[idx,2]=(arr[idx,13]*np.sin(arr[idx,18]+arr[idx,9])*arr[idx,20])+arr[idx,17]

#         arr[idx,21]+=arr[idx,22]


#         #print(orgData[:,:3])
        
#         #arr[arr_bool]=orgData

#         # arr_bool[arr[:,11]<0]=False
#         # arr_bool[arr[:,13]<0]=False
    
#     return arr[idx][arr[idx][:,21]%(40//(TIME_INTERVAL/0.001))==1]

#@time_judge
@njit(fastmath=True, cache=True)
def improved_change_position_particle(arr, arr_bool):
    idx = np.nonzero(arr_bool)[0]
    if idx.size == 0:
        return arr[0:0]  # 空

    dt = TIME_INTERVAL
    G = 9.81
    M = 1.0
    Kf = 0.7
    damp = 0.5 * Kf / M
    gacc = -G

    # 这个 period 建议在 Python 外面预先算好传进来（见第 3 点）
    period = int(40 // (TIME_INTERVAL / 0.001))

    # 先预分配“最多 idx.size 个”输出，最后切片
    out = np.empty((idx.size, arr.shape[1]), dtype=arr.dtype)
    out_n = 0

    for t in range(idx.size):
        i = idx[t]

        vx = arr[i, 6]; vy = arr[i, 7]; vz = arr[i, 8]

        ax = -vx * damp
        ay = -vy * damp + gacc
        az = -vz * damp

        vx += ax * dt
        vy += ay * dt
        vz += az * dt

        arr[i, 6] = vx; arr[i, 7] = vy; arr[i, 8] = vz

        arr[i, 15] += vx * dt
        arr[i, 16] += vy * dt
        arr[i, 17] += vz * dt

        arr[i, 9]  += arr[i, 10]
        arr[i, 11] -= arr[i, 12]
        arr[i, 13] -= arr[i, 14]

        ang = arr[i, 18] + arr[i, 9]
        s = math.sin(ang)
        c = math.cos(ang)

        r  = arr[i, 13]
        cx = arr[i, 15]; cy = arr[i, 16]; cz = arr[i, 17]
        k1 = arr[i, 19]; k2 = arr[i, 20]

        arr[i, 0] = r * c + cx
        arr[i, 1] = r * s * k1 + cy
        arr[i, 2] = r * s * k2 + cz

        arr[i, 21] += arr[i, 22]

        # 只筛一次，不要 arr[idx] 二次构造
        # 注意：arr[i,21] 是 float32，取模会慢且可能有精度问题（见第 3 点）
        if (int(arr[i, 21]) % period) == 1:
            out[out_n, :] = arr[i, :]
            out_n += 1

    return out[:out_n]



class Particle(Object):
    # break_number: when disappear, the number of particle appear
    # power : when break, the initinal velocity of particle
    # ini_vel: the initinal velocity of Particle
    # color : the color of particle
    #tail:True:it can use tail, False:can not use

    G=9.81
    M=1#1g
    K_f=0.7
    
    def __init__(self,position,ini_vel,color,tail,particle_arr:Firework_arr,effect_arr:Firework_arr) -> None:
        super().__init__(position)

        self.particle_arr=particle_arr# Firework_arr
        self.effect_arr=effect_arr# Firework_arr

        
        self.position_tri1_index=particle_arr.create_new()# find empty space of Firework_arr
        self.position_tri2_index=particle_arr.create_new()# find empty space of Firework_arr
        
        
        #print(self.vertices_vertical_tri)
        
        
        #self.tail_effects=[]# store 
        self.time_counter=0# used to add a effect in certain time
        
        self.color=color# color of particle
        self.change_angle=TIME_INTERVAL*50# speed of rotation
        self.angle=0# orginal angle
        self.size=0.1# size of particle
        self.tail=tail
        

        self.vel=to_np_array(ini_vel)

        self.live=0
        self.live_change=0

        #self.firework_type=Firework_types()
    def set_change_size(self,num):
        for index in self.position_tri1_index:
            self.particle_arr.arr[index][14]=num
        for index in self.position_tri2_index:
            self.particle_arr.arr[index][14]=num

        

        
    
    def break_self(self,Firework):
        for index in self.position_tri1_index:
            self.particle_arr.remove(index)
        for index in self.position_tri2_index:
            self.particle_arr.remove(index)
    
    @property
    def indexed_position(self):
        return self.particle_arr.arr[self.position_tri1_index[0]][15:18]
        

        
    

class Tail_Effect(Object):
    G=9.81
    M=0.1
    K_f=2
    def __init__(self,position,color,effect_arr:Firework_arr) -> None:
        self.live=random.randint(200,300)
        self.live_change=TIME_INTERVAL/0.001
        self.position=np.array(position)
        self.color=color
        self.to_one_color=to_one(color)
        self.vel=to_np_array((0,0,0))

        self.effect_arr=effect_arr
        self.effect_index=effect_arr.create_new()[0]
        #position,color,velocity,live,live_change
        self.effect_arr.arr[self.effect_index][0:3]=self.getPosition(position)
        self.effect_arr.arr[self.effect_index][3:6]=color
        self.effect_arr.arr[self.effect_index][9]=self.live
        self.effect_arr.arr[self.effect_index][10]=self.live_change




    
class frame_fire(Particle):
    
    G=9.81
    M=1#1g
    K_f=0.7
    def __init__(self, position, ini_vel, color, tail,music,fire_type,particle_arr:Firework_arr,effect_arr:Firework_arr) -> None:
        super().__init__(position, ini_vel, color, tail,particle_arr,effect_arr)
        self.music=music
        self.fire_type=fire_type#it is the function

        self.live=100
        self.live_change=1.25*TIME_INTERVAL*(self.live/(ini_vel[1]/self.G))#time.sleep(0.001)

        counter=0
        for index in self.position_tri1_index:#changed_position(3),color(3),velocity(3),angle,angle_change,live,live_change,size,size_change,org_position(3),change_tri,horizontal,vertical,time_counter,tail
            counter+=1
            self.particle_arr.arr[index][3:6]=to_one(color)
            self.particle_arr.arr[index][6:9]=ini_vel
            self.particle_arr.arr[index][9]=0
            self.particle_arr.arr[index][10]=self.change_angle
            self.particle_arr.arr[index][11]=100
            self.particle_arr.arr[index][12]=self.live_change
            self.particle_arr.arr[index][13]=0.1
            self.particle_arr.arr[index][15:18]=position
            self.particle_arr.arr[index][18]=2 * np.pi * counter / 3 

            self.particle_arr.arr[index][19]=1
            self.particle_arr.arr[index][20]=0
            self.particle_arr.arr[index][21]=0
            self.particle_arr.arr[index][22]=int(tail)

        counter=0
        for index in self.position_tri2_index:
            counter+=1
            self.particle_arr.arr[index][3:6]=to_one(color)
            self.particle_arr.arr[index][6:9]=ini_vel
            self.particle_arr.arr[index][9]=0
            self.particle_arr.arr[index][10]=self.change_angle
            self.particle_arr.arr[index][11]=100
            self.particle_arr.arr[index][12]=self.live_change
            self.particle_arr.arr[index][13]=0.1
            self.particle_arr.arr[index][15:18]=position
            self.particle_arr.arr[index][18]=2 * np.pi * counter / 3 

            self.particle_arr.arr[index][19]=0
            self.particle_arr.arr[index][20]=1
            self.particle_arr.arr[index][21]=0
            self.particle_arr.arr[index][22]=int(tail)

    def break_self(self, Firework):
        
        if self.particle_arr.arr[self.position_tri1_index[0],11]<=0 or self.particle_arr.arr[self.position_tri1_index[0],7]<0:
            super().break_self(Firework)
            Firework.particles.remove(self)
            
            Firework.particles+= self.fire_type(self)
            self.music.set_volume(0.5)
            
            
            if Firework.auto.type_firework.nothing!=self.fire_type:
                
                self.music.play()
            
            


class frame_break(Particle):
    G=9.81
    M=1#1g
    K_f=2
    def __init__(self, position, ini_vel, color, tail,fire_type,particle_arr:Firework_arr,effect_arr:Firework_arr) -> None:
        super().__init__(position, ini_vel, color, tail,particle_arr,effect_arr)
        self.change_size=TIME_INTERVAL*0.09

        
        self.fire_type=fire_type
        counter=0
        for index in self.position_tri1_index:#changed_position(3),color(3),velocity(3),angle,angle_change,live,live_change,size,size_change,org_position(3),change_tri,horizontal,vertical,time_counter,tail
            counter+=1

            self.particle_arr.arr[index][3:6]=to_one(color)
            self.particle_arr.arr[index][6:9]=ini_vel
            self.particle_arr.arr[index][9]=0
            self.particle_arr.arr[index][10]=self.change_angle
            
            self.particle_arr.arr[index][13]=0.1
            self.particle_arr.arr[index][14]=self.change_size
            self.particle_arr.arr[index][15:18]=position
            self.particle_arr.arr[index][18]=2 * np.pi * counter / 3 

            self.particle_arr.arr[index][19]=1
            self.particle_arr.arr[index][20]=0
            self.particle_arr.arr[index][21]=0
            self.particle_arr.arr[index][22]=int(tail)

        counter=0
        for index in self.position_tri2_index:
            counter+=1
            self.particle_arr.arr[index][3:6]=to_one(color)
            self.particle_arr.arr[index][6:9]=ini_vel
            self.particle_arr.arr[index][9]=0
            self.particle_arr.arr[index][10]=self.change_angle
            
            self.particle_arr.arr[index][13]=0.1
            self.particle_arr.arr[index][14]=self.change_size
            self.particle_arr.arr[index][15:18]=position
            self.particle_arr.arr[index][18]=2 * np.pi * counter / 3 

            self.particle_arr.arr[index][19]=0
            self.particle_arr.arr[index][20]=1
            self.particle_arr.arr[index][21]=0
            self.particle_arr.arr[index][22]=int(tail)
    
    


            


    def break_self(self, Firework):
        
        if self.particle_arr.arr[self.position_tri1_index[0]][13]<=0.01 :
            super().break_self(Firework)
            Firework.particles.remove(self)
            
            Firework.particles+= self.fire_type(self)
            

    def update(self, Firework):
        super().update(Firework)
        self.size-=self.change_size



def generate_func_type(func,arg):
    def newfunc(frame):
        return func(frame,arg)
    return newfunc


class Firework_types(Object):
    
    
    def __init__(self,age,particle_posiiton_np,effect_position_np) -> None:

        self.particle_posiiton_np=particle_posiiton_np
        self.effect_position_np=effect_position_np

        self.types_level1=[
            self.circle,
            self.random_color,
            self.ball,
            self.double_ball,
            self.planet_random_color,
            self.planet_ball,
            self.half_half_color_ball,
            self.mixed_color_ball,
            self.ball_up
                    ]
        self.types_level2=[
            self.love_2D,
            self.love_2D_odd,
            self.double_love_2D,
        ]
        self.types_level3=[
            self.love_3D,
            self.flower
        ]

        self.font= pygame.font.Font(None, 50)
        self.kaka=pygame.surfarray.array2d(
            self.font.render('kaka', True, (255, 255, 255),(0,0,0))
            ).T

        self.aray=pygame.surfarray.array2d(
            self.font.render('Aray', True, (255, 255, 255),(0,0,0))
            ).T
        self.age=pygame.surfarray.array2d(
            self.font.render(str(age), True, (255, 255, 255),(0,0,0))
            ).T
        
        self.h_b=pygame.surfarray.array2d(
            self.font.render("Happy Birthday", True, (255, 255, 255),(0,0,0))
            ).T
        self.new_year=pygame.surfarray.array2d(
            self.font.render("Happy New Year!", True, (255, 255, 255),(0,0,0))
            ).T
        self.this_year=pygame.surfarray.array2d(
            self.font.render(f"{datetime.now().year}", True, (255, 255, 255),(0,0,0))
            ).T
        
        self.love_you=pygame.surfarray.array2d(
            self.font.render("Love You", True, (255, 255, 255),(0,0,0))
            ).T
        self.forever=pygame.surfarray.array2d(
            self.font.render("Forever!", True, (255, 255, 255),(0,0,0))
            ).T

        self.font_chinese= pygame.font.Font(PATH.format("files/font.ttf"), 50)

        text_segments = [
            "祝纳纳节日快乐！",
            "转眼三年过去了。",
            "你还有半个学期就要毕业了。",
            "会有不舍，也会有期待。",
            "希望你在研究生阶段，",
            "以及更远的未来，",
            "都能越来越好。",
            "也希望你能跨过重重困难。",
            "心态慢慢变好，",
            "慢慢阳光起来。",
            "相信自己。",
            "你是最棒的。",
            "我会一直在。",
            "永远爱你。"
        ]

        self.text_arrays = [
            pygame.surfarray.array2d(
                self.font_chinese.render(seg, True, (255, 255, 255), (0, 0, 0))
            ).T
            for seg in text_segments
        ]



    def choose_random_type(self):
        percentage=random.randint(0,100)
        if percentage>95:
            types=self.types_level3
        elif percentage>80:
            types=self.types_level2
        else:
            types=self.types_level1

        return types[random.randint(0,len(types)-1)]
        #return self.extrimely_big_fire_1
    
    def find_matched_color(self,color_self):
        matched=[]
        for color in COLOR_MATCH:
            if color_self in color:
                matched.append(color)
        if matched:
            color_matched=matched[random.randint(0,len(matched)-1)]
            return color_matched[0] if color_matched[0]!=color_self else color[1]
        else:
            return color_self


    def get_vel_by_pos(self,position_org,position_target,time_need):
        G=9.81
        displacement=position_target-position_org
        dis_y=displacement[1,0]
        v_y=(dis_y/time_need)+(time_need*G/2)
        v_x=displacement[0,0]/time_need
        v_z=displacement[2,0]/time_need

        return (v_x,v_y,v_z)

    def nothing(self,frame):
        return []
    def circle(self,frame,radius=3,color=0,num_frame=0,time_reach=0.3):
        if color==0:
            color=frame.color
        position_org=frame.indexed_position
        angle_x=random.randint(0,180)
        angle_y=random.randint(0,180)
        angle_z=random.randint(0,180)

        if num_frame==0:
            num_frame=random.randint(3,4)*5
        
        ini_position=np.array([
            [0],
            [radius],
            [0]
        ])
        
        #print(np.array([ Rz(i*(360/num_frame))*ini_position for i in range(num_frame)]))
        ini_positions=np.array([ Rz(i*(360/num_frame))*ini_position for i in range(num_frame)]).transpose(1, 0, 2)
        
        final_positions=(Rz(angle_z)*Rx(angle_x)*Ry(angle_y)*ini_positions).T.reshape(num_frame, 3, 1)

        particles=[]
        for position in final_positions:
            velocity=self.get_vel_by_pos(np.zeros((3,1)),position.reshape(3, 1),time_reach)
            particle=frame_break(position_org,velocity,color,False,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np)
            particle.set_change_size(random.uniform(0.001,0.0015))
            particles.append(particle)
        return particles

    def random_color(self,frame,radius=3,num_particles=0,tail=True):
        position_org=frame.indexed_position
        if num_particles==0:
            num_particles=15

        # Generate uniform distribution for theta and phi
        # Generate random spherical coordinates
        theta = np.random.uniform(0, np.pi, num_particles)  # theta is randomly distributed between 0 and pi
        phi = np.random.uniform(0, 2*np.pi, num_particles)  # phi is randomly distributed between 0 and 2*pi

        # Convert spherical coordinates to Cartesian coordinates
        x = radius*np.sin(theta) * np.cos(phi)
        y = radius*np.sin(theta) * np.sin(phi)
        z = radius*np.cos(theta)


        particles=[]
        for i in range(num_particles):
            
            velocity=self.get_vel_by_pos(np.zeros((3,1)),to_np_array((x[i],y[i],z[i])),0.3)
            color=COLOR[random.randint(0,len(COLOR)-1)]
            particles.append(frame_break(position_org,velocity,color,tail,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        return particles
    

    def ball(self,frame,radius=5,color=0,num_particles=0,time_reach=0.3,tail=False):
        if color==0:
            color=frame.color
        position_org=frame.indexed_position

        if num_particles==0:

            num_particles=150

        # Generate uniform distribution for theta and phi
        # Generate random spherical coordinates
        theta = np.random.uniform(0, np.pi, num_particles)  # theta is randomly distributed between 0 and pi
        phi = np.random.uniform(0, 2*np.pi, num_particles)  # phi is randomly distributed between 0 and 2*pi

        # Convert spherical coordinates to Cartesian coordinates
        x = radius*np.sin(theta) * np.cos(phi)
        y = radius*np.sin(theta) * np.sin(phi)
        z = radius*np.cos(theta)


        particles=[]
        for i in range(num_particles):
            
            velocity=self.get_vel_by_pos(np.zeros((3,1)),to_np_array((x[i],y[i],z[i])),time_reach)
            particle=frame_break(position_org,velocity,color,tail,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np)
            particle.set_change_size(random.uniform(0.001,0.0015))
            particles.append(particle)
        return particles
    
    def double_ball(self,frame):
        color=frame.color
        matched_color=self.find_matched_color(color)
        particle_1=self.ball(frame,8,color)
        particle_2=self.ball(frame,4,matched_color)

        return particle_1+particle_2
    
    def planet_random_color(self,frame):
        particle_1=self.random_color(frame,3)
        particle_2=self.circle(frame,6,frame.color)
        return particle_1+particle_2
    

    def planet_ball(self,frame):
        color=frame.color
        matched_color=self.find_matched_color(color)
        particle_1=self.circle(frame,8,frame.color)
        particle_2=self.ball(frame,4,matched_color)
        return particle_1+particle_2
    
    def love_3D(self,frame,radius=5):
        color=(234,130,153)
        position_org=frame.indexed_position

        num=100
        # Create a range of values for x, y, z
        x_range = np.linspace(-1.5, 1.5, num)
        y_range = np.linspace(-1.5, 1.5, num)
        z_range = np.linspace(-1, 1, num)


        # Create a meshgrid for x, y, z
        x,y,z = np.meshgrid(x_range, y_range, z_range)

        f= (x**2 + (9/4)*y**2 + z**2 - 1)**3 - x**2*z**3 - (9/200)*y**2*z**3

        # Apply the mask to the x, y, and z coordinates
        x_heart = x[f < 0]*radius
        y_heart = y[f < 0]*radius
        z_heart = z[f < 0]*radius


        particles=[]
        indices = np.random.choice(len(x_heart), size=300)  # Randomly select 5 points
        for i in indices:
            velocity=self.get_vel_by_pos(np.zeros((3,1)),to_np_array((x_heart[i],z_heart[i],y_heart[i])),0.3)
            
            particles.append(frame_break(position_org,velocity,color,False,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        return particles
    
    def love_2D(self,frame,radius=0.6):
        color=(234,130,153)
        position_org=frame.indexed_position
        t = np.linspace(0, 2*np.pi, 1000)
        # Define the x and y coordinates of the heart
        x = (16*np.sin(t)**3)*radius
        y = (13*np.cos(t) - 5*np.cos(2*t) - 2*np.cos(3*t) - np.cos(4*t))*radius
        particles=[]
        indices = np.random.choice(len(x), size=150)  # Randomly select 5 points
        for i in indices:
            velocity=self.get_vel_by_pos(np.zeros((3,1)),to_np_array((x[i],y[i],0)),0.3)
            
            particles.append(frame_break(position_org,velocity,color,False,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        return particles
    

    def love_2D_odd(self,frame,radius=0.6):
        color=(234,130,153)
        position_org=frame.indexed_position
        t = np.linspace(0, 2*np.pi, 1000)
        # Define the x and y coordinates of the heart
        x = (16*np.sin(t)**3)*radius
        y = (13*np.cos(t) - 5*np.cos(2*t) - 2*np.cos(3*t) - np.cos(4*t))*radius
        z_odd=-3
        particles=[]
        indices = np.random.choice(len(x), size=50)  # Randomly select 5 points
        for i in indices:
            velocity=self.get_vel_by_pos(np.zeros((3,1)),to_np_array((x[i],y[i],z_odd)),0.3)
            
            particles.append(frame_break(position_org,velocity,color,True,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        return particles
    
    def double_love_2D(self,frame):
        particle_1=self.love_2D(frame,0.6)
        particle_2=self.love_2D_odd(frame,0.3)
        return particle_1+particle_2
            
    def half_half_color_ball(self,frame,radius=5,color=0):
        if color==0:
            color=frame.color
        matched_color=self.find_matched_color(color)
        position_org=frame.indexed_position

        angle_x=random.randint(0,180)
        angle_y=random.randint(0,180)
        angle_z=random.randint(0,180)

        num_particles=100

        # Generate uniform distribution for theta and phi
        # Generate random spherical coordinates
        theta = np.random.uniform(0, np.pi, num_particles)  # theta is randomly distributed between 0 and pi
        phi = np.random.uniform(np.pi, 2*np.pi, num_particles)  # phi is randomly distributed between 0 and 2*pi

        # Convert spherical coordinates to Cartesian coordinates
        x = radius*np.sin(theta) * np.cos(phi)
        y = radius*np.sin(theta) * np.sin(phi)
        z = radius*np.cos(theta)
        points_bott=np.array([x,y,z])


        theta = np.random.uniform(0, np.pi, num_particles)  # theta is randomly distributed between 0 and pi
        phi = np.random.uniform(0, np.pi, num_particles)  # phi is randomly distributed between 0 and 2*pi

        # Convert spherical coordinates to Cartesian coordinates
        x = radius*np.sin(theta) * np.cos(phi)
        y = radius*np.sin(theta) * np.sin(phi)
        z = radius*np.cos(theta)

        points_top=np.array([x,y,z])

        rotated_bott=Rx(angle_x)*Ry(angle_y)*Rz(angle_z)*points_bott
        rotated_top=Rx(angle_x)*Ry(angle_y)*Rz(angle_z)*points_top

        particles=[]
        for i in range(num_particles):
            
            velocity=self.get_vel_by_pos(np.zeros((3,1)),to_np_array((rotated_bott[0,i],rotated_bott[1,i],rotated_bott[2,i])),0.3)
            particles.append(frame_break(position_org,velocity,color,False,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))

            velocity=self.get_vel_by_pos(np.zeros((3,1)),to_np_array((rotated_top[0,i],rotated_top[1,i],rotated_top[2,i])),0.3)
            particle=frame_break(position_org,velocity,matched_color,False,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np)
            particle.set_change_size(random.uniform(0.001,0.0015))
            
            particles.append(particle)
            
        return particles

    def mixed_color_ball(self,frame):

        color=frame.color
        matched_color=self.find_matched_color(color)
        particle_1=self.ball(frame,5,color,75)
        particle_2=self.ball(frame,5,matched_color,75)
        return particle_1+particle_2
    
    def ball_up(self,frame,radius=3,color=0,num_particles=0):
        if color==0:
            color=frame.color
        position_org=frame.indexed_position

        if num_particles==0:

            num_particles=50

        displace=2.5

        # Generate uniform distribution for theta and phi
        # Generate random spherical coordinates
        theta = np.random.uniform(0, np.pi, num_particles)  # theta is randomly distributed between 0 and pi
        phi = np.random.uniform(0, 2*np.pi, num_particles)  # phi is randomly distributed between 0 and 2*pi

        # Convert spherical coordinates to Cartesian coordinates
        x = radius*np.sin(theta) * np.cos(phi)
        y = radius*np.sin(theta) * np.sin(phi)+displace
        z = radius*np.cos(theta)


        particles=[]
        for i in range(num_particles):
            
            velocity=self.get_vel_by_pos(np.zeros((3,1)),to_np_array((x[i],y[i],z[i])),0.3)
            
            particles.append(frame_break(position_org,velocity,color,True,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        return particles

    def ball_down(self,frame,radius=3,color=0,num_particles=0):
        if color==0:
            color=frame.color
        position_org=frame.indexed_position
        if num_particles==0:
            num_particles=50
        displace=-2.5
        theta = np.random.uniform(0, np.pi, num_particles)  # theta is randomly distributed between 0 and pi
        phi = np.random.uniform(0, 2*np.pi, num_particles)  # phi is randomly distributed between 0 and 2*pi
        x = radius*np.sin(theta) * np.cos(phi)
        y = radius*np.sin(theta) * np.sin(phi)+displace
        z = radius*np.cos(theta)

        particles=[]
        for i in range(num_particles):
            velocity=self.get_vel_by_pos(np.zeros((3,1)),to_np_array((x[i],y[i],z[i])),0.3)
            particles.append(frame_break(position_org,velocity,color,True,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        return particles

    def happy_birthday(self,frame,arr):
        
        start_pos=[-int(len(arr)/2),-int(len(arr[0])/2)]#y,x

        position_org=frame.indexed_position
        scale=0.15

        particles=[]
        for y in range(start_pos[0],-start_pos[0]):
            for x in range(start_pos[1],-start_pos[1]):
                if arr[y-start_pos[0],x-start_pos[1]] and random.randint(0,1):
                    x_final,y_final=-x*scale,-y*scale
                    pos=np.array([
                        [x_final],
                        [y_final],
                        [-10]
                    ])
                    velocity=self.get_vel_by_pos(np.zeros((3,1)),pos,0.3)
                    particles.append(frame_break(position_org,velocity,(255,0,255),False,fire_type=self.nothing,
                                                 particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        return particles

    def text_display(self,frame,arr):
        
        start_pos=[-int(len(arr)/2),-int(len(arr[0])/2)]#y,x

        position_org=frame.indexed_position
        scale=0.04

        particles=[]
        for y in range(start_pos[0],-start_pos[0]):
            for x in range(start_pos[1],-start_pos[1]):
                if arr[y-start_pos[0],x-start_pos[1]] and random.randint(0,1):
                    x_final,y_final=-x*scale,-y*scale
                    pos=np.array([
                        [x_final],
                        [y_final],
                        [-5]
                    ])
                    velocity=self.get_vel_by_pos(np.zeros((3,1)),pos,0.3)
                    particles.append(frame_break(position_org,velocity,(200,200,200),False,fire_type=self.nothing,
                                                 particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        return particles


    def flower(self,frame,radius=5):
        position_org=frame.indexed_position
        color=frame.color

        num_frame_ring=5*radius
        num_frame_bound=4*radius

        angle=45

        angle_x=random.randint(0,180)
        angle_y=random.randint(0,180)
        angle_z=random.randint(0,180)
        radian=angleConvert(angle)

        num_particles=75

        theta = np.random.uniform(0, radian, num_particles)  # theta is randomly distributed between 0 and pi
        phi = np.random.uniform(0, 2*np.pi, num_particles)  # phi is randomly distributed between 0 and 2*pi

        x = radius * np.sin(theta) * np.cos(phi)
        y = radius * np.sin(theta) * np.sin(phi)
        z = radius * np.cos(theta)

        z_limit=radius * np.cos(radian)
        y_limit=radius * np.sin(radian)
        x_limit=0

        points=np.array([x,y,z])

        boundary=np.array([
            [x_limit],
            [y_limit],
            [z_limit]
        ])
        ini_position=np.array([
            [0],
            [radius],
            [0]
        ])

        ini_positions=np.array([ Rz(i*(360/num_frame_ring))*ini_position for i in range(num_frame_ring)]).transpose(1, 0, 2)
        boundary=np.array([ Rz(i*(360/num_frame_bound))*boundary for i in range(num_frame_bound)]).transpose(1, 0, 2)
        
        points_1=Rz(angle_z)*Rx(angle_x)*Ry(angle_y)*points
        points_2=Rz(angle_z)*Rx(angle_x)*Ry(angle_y+180)*points
        ini_positions=Rz(angle_z)*Rx(angle_x)*Ry(angle_y)*ini_positions
        boundary_1=Rz(angle_z)*Rx(angle_x)*Ry(angle_y)*boundary
        boundary_2=Rz(angle_z)*Rx(angle_x)*Ry(angle_y+180)*boundary


        ini_positions = ini_positions.T.reshape(num_frame_ring, 3, 1)
        points_1=points_1.T.reshape(num_particles, 3, 1)
        points_2=points_2.T.reshape(num_particles, 3, 1)
        boundary_1=boundary_1.T.reshape(num_frame_bound, 3, 1)
        boundary_2=boundary_2.T.reshape(num_frame_bound, 3, 1)
 



        particles=[]
        for position in ini_positions:
            velocity=self.get_vel_by_pos(np.zeros((3,1)),position.reshape(3, 1),0.3)
            particles.append(frame_break(position_org,velocity,color,False,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        for position in points_1:
            velocity=self.get_vel_by_pos(np.zeros((3,1)),position.reshape(3, 1),0.3)
            particles.append(frame_break(position_org,velocity,(205,45,65),False,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        for position in points_2:
            velocity=self.get_vel_by_pos(np.zeros((3,1)),position.reshape(3, 1),0.3)
            particles.append(frame_break(position_org,velocity,(205,45,65),False,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        for position in boundary_1:
            velocity=self.get_vel_by_pos(np.zeros((3,1)),position.reshape(3, 1),0.3)
            particles.append(frame_break(position_org,velocity,(217,217,217),True,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        for position in boundary_2:
            velocity=self.get_vel_by_pos(np.zeros((3,1)),position.reshape(3, 1),0.3)
            particles.append(frame_break(position_org,velocity,(217,217,217),True,fire_type=self.nothing,
                                         particle_arr=self.particle_posiiton_np,effect_arr=self.effect_position_np))
        
        return particles

    def extrimely_big_fire_1(self,frame):
        color=frame.color
        matched_color=self.find_matched_color(color)
        particle_1=self.ball(frame,48,color,600,time_reach=1)
        particle_2=self.ball(frame,32,COLOR[random.randint(0,len(COLOR)-1)],100,time_reach=1,tail=True)
        particle_3=self.ball(frame,24,matched_color,600,time_reach=1)
        particle_4=self.circle(frame,54,COLOR[random.randint(0,len(COLOR)-1)],num_frame=100,time_reach=1)
        particle_5=self.circle(frame,54,COLOR[random.randint(0,len(COLOR)-1)],num_frame=100,time_reach=1)

        #print(COLOR[random.randint(0,len(COLOR)-1)])

        total_particles=particle_1+particle_2+particle_3+particle_4+particle_5

        for particle in total_particles:
            particle.set_change_size(0.0005)
            

        for particle in particle_2:
            particle.set_change_size(random.uniform(0.0007,0.0009))
            
            particle.fire_type=self.random_color


        return total_particles

    def extrimely_big_fire_3(self, frame):
        """
        超级壮观的8尺玉烟花 - 多层次爆炸、华丽光效
        设计理念：7层同心球体 + 4个彩色光环 + 二次爆炸 + 星芒效果
        """
        color = frame.color
        matched_color = self.find_matched_color(color)
        
        # ============ 第一阶段：主体球形爆炸（7层同心球，从外到内） ============
        # 最外层 - 巨大的金色外壳，带拖尾
        particle_outer = self.ball(frame, 65, (255, 215, 0), 800, time_reach=1.2, tail=True)
        
        # 第二层 - 主色大球
        particle_main = self.ball(frame, 55, color, 700, time_reach=1.1)
        
        # 第三层 - 随机彩色中球，带拖尾（形成流星效果）
        particle_meteor = self.ball(frame, 45, COLOR[random.randint(0, len(COLOR)-1)], 200, time_reach=1.0, tail=True)
        
        # 第四层 - 配色球
        particle_matched = self.ball(frame, 38, matched_color, 500, time_reach=0.9)
        
        # 第五层 - 银白色内球
        particle_silver = self.ball(frame, 30, (220, 220, 255), 400, time_reach=0.8)
        
        # 第六层 - 随机彩色小球，会二次爆炸
        particle_burst = self.ball(frame, 22, COLOR[random.randint(0, len(COLOR)-1)], 150, time_reach=0.7, tail=True)
        
        # 最内层 - 核心爆炸，超亮白色
        particle_core = self.ball(frame, 12, (255, 255, 255), 100, time_reach=0.5)
        
        # ============ 第二阶段：多层光环（4个不同角度的光环） ============
        ring_color_1 = COLOR[random.randint(0, len(COLOR)-1)]
        ring_color_2 = COLOR[random.randint(0, len(COLOR)-1)]
        ring_color_3 = COLOR[random.randint(0, len(COLOR)-1)]
        ring_color_4 = (255, 200, 100)  # 金色光环
        
        particle_ring_1 = self.circle(frame, 70, ring_color_1, num_frame=120, time_reach=1.2)
        particle_ring_2 = self.circle(frame, 60, ring_color_2, num_frame=100, time_reach=1.1)
        particle_ring_3 = self.circle(frame, 50, ring_color_3, num_frame=80, time_reach=1.0)
        particle_ring_4 = self.circle(frame, 40, ring_color_4, num_frame=60, time_reach=0.9)
        
        # ============ 第三阶段：随机彩色星芒 ============
        particle_stars = self.random_color(frame, 20, 120, tail=True)
        
        # ============ 合并所有粒子 ============
        total_particles = (particle_outer + particle_main + particle_meteor + 
                          particle_matched + particle_silver + particle_burst + particle_core +
                          particle_ring_1 + particle_ring_2 + particle_ring_3 + particle_ring_4 +
                          particle_stars)
        
        # ============ 设置粒子属性 ============
        # 外层粒子慢慢消失
        for particle in particle_outer:
            particle.set_change_size(random.uniform(0.0003, 0.0005))
            particle.fire_type = self.nothing
            
        # 主体粒子
        for particle in particle_main + particle_matched + particle_silver:
            particle.set_change_size(random.uniform(0.0004, 0.0006))
        
        # 流星粒子 - 二次爆炸成随机颜色
        for particle in particle_meteor:
            particle.set_change_size(random.uniform(0.0006, 0.0008))
            particle.fire_type = self.random_color
            
        # 爆裂粒子 - 二次爆炸成小球
        for particle in particle_burst:
            particle.set_change_size(random.uniform(0.0008, 0.0012))
            particle.fire_type = self.ball
            
        # 核心粒子 - 快速消失，但会二次爆炸
        for particle in particle_core:
            particle.set_change_size(random.uniform(0.0015, 0.002))
            particle.fire_type = self.random_color
            
        # 光环粒子
        for particle in particle_ring_1 + particle_ring_2 + particle_ring_3 + particle_ring_4:
            particle.set_change_size(random.uniform(0.0005, 0.0008))
            
        # 星芒粒子 - 长拖尾，二次爆炸
        for particle in particle_stars:
            particle.set_change_size(random.uniform(0.001, 0.0015))
            particle.fire_type = self.ball
        
        return total_particles

    def extrimely_big_fire_4(self, frame):
        """
        「千重菊」- 日式冠菊烟花
        设计理念：模仿真实的日本尺玉菊花烟花
        - 纯净的银白核心，缓缓绽放
        - 金色长芒向外延伸，末端带有柳叶下垂效果
        - 没有杂乱的颜色，只有金与银的优雅对话
        - 每一颗芒星都会在末端绽放成小花
        """
        position_org = frame.indexed_position
        
        # ============ 色彩定义 - 简约而不简单 ============
        pure_gold = (255, 200, 80)      # 纯金色
        warm_gold = (255, 180, 60)      # 暖金色
        pale_gold = (255, 220, 150)     # 淡金色
        silver_white = (240, 245, 255)  # 银白色
        soft_white = (255, 250, 245)    # 柔白色
        
        # ============ 第一层：银白核心 - 如月光绽放 ============
        particle_core = self.ball(frame, 8, silver_white, 60, time_reach=0.4)
        
        # ============ 第二层：金色菊芒 - 主体光芒 ============
        # 使用较少但更长的拖尾，模拟真实菊花烟花的优雅
        particle_golden_rays = self.ball(frame, 55, pure_gold, 180, time_reach=1.3, tail=True)
        
        # ============ 第三层：暖金色次芒 - 增加层次 ============
        particle_warm_rays = self.ball(frame, 45, warm_gold, 120, time_reach=1.1, tail=True)
        
        # ============ 第四层：淡金色点缀 ============
        particle_pale_dots = self.ball(frame, 35, pale_gold, 80, time_reach=0.9)
        
        # ============ 第五层：银色光环 - 如涟漪扩散 ============
        particle_ring_1 = self.circle(frame, 60, silver_white, num_frame=80, time_reach=1.2)
        particle_ring_2 = self.circle(frame, 50, soft_white, num_frame=60, time_reach=1.0)
        
        # ============ 合并粒子 ============
        total_particles = (particle_core + particle_golden_rays + particle_warm_rays + 
                          particle_pale_dots + particle_ring_1 + particle_ring_2)
        
        # ============ 设置粒子属性 - 关键在于消散速度的控制 ============
        
        # 核心 - 缓慢消散，像余烬一样持久
        for particle in particle_core:
            particle.set_change_size(random.uniform(0.0003, 0.0005))
        
        # 金色主芒 - 持久的拖尾，末端二次爆炸成小型金色花
        for particle in particle_golden_rays:
            particle.set_change_size(random.uniform(0.0004, 0.0006))
            particle.fire_type = self.ball_down if random.random() < 0.3 else self.nothing  # 末端绽放成双层小球
        
        # 暖金次芒 - 稍快消散，二次爆炸成更小的光点
        for particle in particle_warm_rays:
            particle.set_change_size(random.uniform(0.0005, 0.0007))
            particle.fire_type = self.ball_down if random.random() < 0.3 else self.nothing # 行星状二次爆炸
        
        # 淡金点缀 - 较快消散，不二次爆炸
        for particle in particle_pale_dots:
            particle.set_change_size(random.uniform(0.0006, 0.0008))
        
        # 银色光环 - 优雅地扩散后消失
        for particle in particle_ring_1 + particle_ring_2:
            particle.set_change_size(random.uniform(0.0005, 0.0007))
        
        return total_particles
    


    def extrimely_big_fire_2(self,frame):
        #color=frame.color
        #matched_color=self.find_matched_color(color)
        particle_1=self.ball(frame,58,COLOR[1],30,time_reach=1)#yellow
        particle_2=self.ball(frame,32,COLOR[1],100,time_reach=1,tail=True)
        particle_3=self.random_color(frame,10,70,tail=True)
        # particle_4=self.circle(frame,54,COLOR[random.randint(0,len(COLOR)-1)],num_frame=100,time_reach=1)
        # particle_5=self.circle(frame,54,COLOR[random.randint(0,len(COLOR)-1)],num_frame=100,time_reach=1)

        #print(COLOR[random.randint(0,len(COLOR)-1)])

        total_particles=particle_1+particle_2+particle_3

        for particle in particle_3:
            particle.set_change_size(random.uniform(0.001,0.0025))
            particle.fire_type=self.ball
            
        for particle in particle_1:
            particle.set_change_size(random.uniform(0.001,0.0015))
            particle.fire_type=self.ball
            

        for particle in particle_2:
            particle.set_change_size(random.uniform(0.00015,0.0003))
            


        return total_particles

    def extrimely_big_fire_5(self,frame):
        #color=frame.color
        #matched_color=self.find_matched_color(color)
        particle_1=self.ball(frame,58,COLOR[1],30,time_reach=1)#yellow
        particle_2=self.ball(frame,32,COLOR[1],100,time_reach=1,tail=True)
        particle_3=self.random_color(frame,10,70,tail=True)
        # particle_4=self.circle(frame,54,COLOR[random.randint(0,len(COLOR)-1)],num_frame=100,time_reach=1)
        # particle_5=self.circle(frame,54,COLOR[random.randint(0,len(COLOR)-1)],num_frame=100,time_reach=1)

        #print(COLOR[random.randint(0,len(COLOR)-1)])

        total_particles=particle_1+particle_2+particle_3

        for particle in particle_3:
            particle.set_change_size(random.uniform(0.001,0.0025))
            particle.fire_type=self.ball
            
        for particle in particle_1:
            particle.set_change_size(random.uniform(0.001,0.0015))
            particle.fire_type=self.ball
            

        for particle in particle_2:
            particle.set_change_size(random.uniform(0.00015,0.0003))
            


        return total_particles


class Auto_fire:

    def __init__(self,running,firework_generator:Firework_generator,age) -> None:
        self.running=running
        self.firework_generator=firework_generator
        self.type_firework=Firework_types(age,firework_generator.particle_posiiton_np,firework_generator.effect_position_np)

        self.types_level1=[
            self.single,
            self.double_random,
                    ]
        self.types_level2=[
            self.circle_each,
            self.double_one_range,
            self.mountain_2
        ]
        self.types_level3=[
            self.circle_together,
            self.mountain_1,
            self.fan,
            self.happy_birthday,
            # self.extrimely_big_fire_1,
            # self.extrimely_big_fire_2
            
        ]

        self.extrimely_big_fire=[
            self.extrimely_big_fire_1,
            self.extrimely_big_fire_2,
            self.extrimely_big_fire_3,
            self.extrimely_big_fire_4
        ]

    def choose_random_type(self):
        
        percentage=random.randint(0,100)
        if percentage>85:
            types=self.types_level3
        elif percentage>50:
            types=self.types_level2
        else:
            types=self.types_level1

        #return types[random.randint(0,len(types)-1)]
        return self.extrimely_big_fire_1
    def start_auto_fire(self):# threading
        thread=threading.Thread(target=self.generete_fire_auto,args=())
        thread.start()

    def start_auto_fire_new_year_eve(self):
        thread=threading.Thread(target=self.happy_new_year,args=(), daemon=True)
        thread.start()
        return thread

    def start_auto_fire_new_year_eve_v2(self):
        thread=threading.Thread(target=self.happ_new_year_v2,args=(), daemon=True)
        thread.start()
        return thread

    def generete_fire_auto(self):
        self.fan()
        #self.extrimely_big_fire[random.randint(0,len(self.extrimely_big_fire)-1)]()
        time.sleep(random.uniform(2,5))
        while self.running[0]:
            
            self.choose_random_type()()
            time.sleep(random.uniform(2,5))

    def mountain_1(self):
        type_1=self.type_firework.choose_random_type()
        for i in range(4):
            for unit in (-1,1):
                self.firework_generator.generate_firework_thread((unit*20-unit*i*3,0,-5),(0,15+i*3,0),type_1)
            time.sleep(0.3)
        
        type_2=self.type_firework.choose_random_type()
        self.firework_generator.generate_firework_thread((0,0,-5),(0,30,0),type_2)

        

    def mountain_2(self):
        type_1=self.type_firework.choose_random_type()
        for i in range(2):
            for unit in (-1,1):
                self.firework_generator.generate_firework_thread((unit*20-unit*i*4,0,-5),(0,15+i*3,0),type_1)
            time.sleep(0.3)
        for i in range(2,4):
            for unit in (-1,1):
                self.firework_generator.generate_firework_thread((unit*20-unit*i*4,0,-5),(0,10+i*3,0),type_1)
            time.sleep(0.3)
        
        type_2=self.type_firework.choose_random_type()
        self.firework_generator.generate_firework_thread((0,0,-5),(0,20,0),type_2)

    def circle_together(self):
        radius=10
        
        for i in range(11): 
            type_1=self.type_firework.choose_random_type()
            for unit in (-1,1):
                angle = 2 * np.pi * i / 10  # 计算每一份对应的角度(缓慢改变angle可以旋转)
                x = radius*np.sin(angle)  # 计算x坐标
                z=radius*np.cos(angle)  # 计算z坐标
                self.firework_generator.generate_firework_thread((unit*x,-10,z),(0,20+i*2,0),type_1)

            time.sleep(0.3)

    def circle_each(self):
        radius=10
        
        for i in range(1,6): 
            type_1=self.type_firework.choose_random_type()
            for unit in (-1,1):
                angle = 2 * np.pi * i / 10  # 计算每一份对应的角度(缓慢改变angle可以旋转)
                x = radius*np.sin(angle)  # 计算x坐标
                z=radius*np.cos(angle)  # 计算z坐标
                self.firework_generator.generate_firework_thread((unit*x,-10,z),(0,20+i*2,0),type_1)

            time.sleep(0.3)

    def circle_around(self):
        radius=30
        number_of_firework=30
        
        for i in range(1,number_of_firework): 
            type_1=self.type_firework.choose_random_type()
            for unit in (-1,1):
                angle =  np.pi * i / number_of_firework  # 计算每一份对应的角度(缓慢改变angle可以旋转)
                x = radius*np.sin(angle)  # 计算x坐标
                z=-radius*np.cos(angle)-20  # 计算z坐标
                self.firework_generator.generate_firework_thread((unit*x,-10,z),(0,20+i/number_of_firework*20,0),type_1)

            time.sleep(3/number_of_firework)

    def line_around(self):
        number_of_firework=30
        gap=1
       
        for i in range(number_of_firework):
            type_1=self.type_firework.choose_random_type()
            for unit in (-1,1):
                x=unit*(number_of_firework-i)*gap
                y=0
                z=-5
                self.firework_generator.generate_firework_thread((x,y,z),(0,15+i/number_of_firework*10,0),type_1)
            time.sleep(5/number_of_firework)
        
        type_2=self.type_firework.choose_random_type()
        self.firework_generator.generate_firework_thread((0,0,-5),(0,30,0),type_2)

    def fan_2(self):
        vel_left=np.array([
            [25],
            [25],
            [0]
        ])

        vel_right=np.array([
            [-25],
            [25],
            [0]
        ])
        number_of_firework=10
        for first in range(number_of_firework):
            type_1=self.type_firework.choose_random_type()
            
            vel_left=Rz(90/number_of_firework)*vel_left
            self.firework_generator.generate_firework_thread((-10,0,0),(vel_left[0,0],vel_left[1,0],vel_left[2,0]),type_1)

            vel_right=Rz(-90/number_of_firework)*vel_right
            self.firework_generator.generate_firework_thread((10,0,0),(vel_right[0,0],vel_right[1,0],vel_right[2,0]),type_1)


            time.sleep(0.3)

        
        for second in range(number_of_firework):
            type_2=self.type_firework.choose_random_type()
            
            vel_left=Rz(-90/number_of_firework)*vel_left
            self.firework_generator.generate_firework_thread((-10,0,0),(vel_left[0,0],vel_left[1,0],vel_left[2,0]),type_2)

            vel_right=Rz(90/number_of_firework)*vel_right
            self.firework_generator.generate_firework_thread((10,0,0),(vel_right[0,0],vel_right[1,0],vel_right[2,0]),type_2)


            time.sleep(0.3)

    def one_wave_show(self):

        number = 10
        base_speed = 35

        # ======================
        # 第一阶段：左右扇形展开
        # ======================
        vel_left = np.array([[0], [base_speed], [0]])
        vel_right = np.array([[0], [base_speed], [0]])

        for i in range(number):
            angle = 40 / number

            vel_left = Rz(angle) @ vel_left
            vel_right = Rz(-angle) @ vel_right

            fire_type = self.type_firework.choose_random_type()

            self.firework_generator.generate_firework_thread(
                (-12, 0, 0),
                (vel_left[0, 0], vel_left[1, 0], vel_left[2, 0]),
                fire_type
            )

            self.firework_generator.generate_firework_thread(
                (12, 0, 0),
                (vel_right[0, 0], vel_right[1, 0], vel_right[2, 0]),
                fire_type
            )

            time.sleep(0.18)

        time.sleep(0.6)

        # ======================
        # 第二阶段：左右交叉推进
        # ======================
        vel_left = np.array([[25], [base_speed], [0]])
        vel_right = np.array([[-25], [base_speed], [0]])

        for i in range(number):
            fire_type = self.type_firework.choose_random_type()

            self.firework_generator.generate_firework_thread(
                (-12, 0, 0),
                (vel_left[0,0], vel_left[1,0], vel_left[2,0]),
                fire_type
            )

            self.firework_generator.generate_firework_thread(
                (12, 0, 0),
                (vel_right[0,0], vel_right[1,0], vel_right[2,0]),
                fire_type
            )

            vel_left = Rz(-6) @ vel_left
            vel_right = Rz(6) @ vel_right

            time.sleep(0.15)

        time.sleep(0.5)

        # ======================
        # 第三阶段：中央爆发（高潮）
        # ======================
        for i in range(12):
            angle = np.random.uniform(-20, 20)
            speed = np.random.uniform(40, 50)

            vel = Rz(angle) @ np.array([[0], [speed], [0]])
            fire_type = self.type_firework.choose_random_type()

            self.firework_generator.generate_firework_thread(
                (0, 0, 0),
                (vel[0, 0], vel[1, 0], vel[2, 0]),
                fire_type
            )

            time.sleep(0.08)

    def one_wave_vortex(self):
        

        spiral_steps = 14
        base_speed = 28

        # ======================
        # 第一阶段：左右旋转上升（双螺旋）
        # ======================
        vel_left = np.array([[18], [base_speed], [0]])
        vel_right = np.array([[-18], [base_speed], [0]])

        for i in range(spiral_steps):
            fire_type = self.type_firework.choose_random_type()

            self.firework_generator.generate_firework_thread(
                (-14, 0, 0),
                (vel_left[0,0], vel_left[1,0], vel_left[2,0]),
                fire_type
            )

            self.firework_generator.generate_firework_thread(
                (14, 0, 0),
                (vel_right[0,0], vel_right[1,0], vel_right[2,0]),
                fire_type
            )

            vel_left = Rz(12) @ vel_left
            vel_right = Rz(-12) @ vel_right

            time.sleep(0.16)

        time.sleep(0.6)

        # ======================
        # 第二阶段：环形包围（半圆感）
        # ======================
        ring_count = 10
        ring_speed = 32

        for i in range(ring_count):
            angle = -90 + i * (180 / ring_count)
            vel = Rz(angle) @ np.array([[0], [ring_speed], [0]])

            fire_type = self.type_firework.choose_random_type()

            self.firework_generator.generate_firework_thread(
                (0, 0, 0),
                (vel[0, 0], vel[1, 0], vel[2, 0]),
                fire_type
            )

            time.sleep(0.12)

        time.sleep(0.4)

        # ======================
        # 第三阶段：中心高速击穿
        # ======================
        for i in range(8):
            speed = 48 + i * 2
            vel = np.array([[0], [speed], [0]])

            fire_type = self.type_firework.choose_random_type()

            self.firework_generator.generate_firework_thread(
                (0, 0, 0),
                (vel[0, 0], vel[1, 0], vel[2, 0]),
                fire_type
            )

            time.sleep(0.06)

    def one_wave_breathing_petal(self):
    

        petal_count = 14
        petal_count = max(1, int(petal_count))

        origin_radius = 16

        # 向上速度安全参数
        BASE_UP = 18.0
        MIN_VY = 6.0

        OUT_SPEED = 22.0
        IN_SPEED = 38.0

        # ======================
        # 第一阶段：花瓣展开（始终向上）
        # ======================
        for i in range(petal_count):
            angle = i * (360.0 / petal_count)
            rad = math.radians(angle)

            vx = OUT_SPEED * math.cos(rad)
            vy = BASE_UP + OUT_SPEED * abs(math.sin(rad))
            vy = max(vy, MIN_VY)

            self.firework_generator.generate_firework_thread(
                (
                    origin_radius * math.cos(rad),
                    origin_radius * math.sin(rad),
                    0.0
                ),
                (vx, vy, 0.0),
                self.type_firework.choose_random_type()
            )

        time.sleep(0.9)

        # ======================
        # 第二阶段：向心塌缩 + 抬升（更强向上）
        # ======================
        for i in range(petal_count):
            angle = i * (360.0 / petal_count)
            rad = math.radians(angle)

            vx = -IN_SPEED * math.cos(rad)
            vy = BASE_UP * 1.4 + IN_SPEED * abs(math.sin(rad))
            vy = max(vy, MIN_VY)

            self.firework_generator.generate_firework_thread(
                (
                    origin_radius * math.cos(rad),
                    origin_radius * math.sin(rad),
                    0.0
                ),
                (vx, vy, 0.0),
                self.type_firework.choose_random_type()
            )

            time.sleep(0.06)


    def one_wave_pendulum_clash(self):
        

        swing_steps = 14

        # 安全向上速度参数
        BASE_UP = 20.0
        MIN_VY = 8.0

        # 摆动参数
        MAX_SWING = 28.0
        SWING_DECAY = 0.85  # 摆幅逐渐减小

        left_x = -18.0
        right_x = 18.0

        swing = MAX_SWING

        # ======================
        # 第一阶段：左右钟摆对撞
        # ======================
        for i in range(swing_steps):
            fire_type = self.type_firework.choose_random_type()

            # 左侧 → 向右摆
            vx_l = swing
            vy_l = BASE_UP + abs(swing) * 0.4
            vy_l = max(vy_l, MIN_VY)

            self.firework_generator.generate_firework_thread(
                (left_x, 0.0, 0.0),
                (vx_l, vy_l, 0.0),
                fire_type
            )

            # 右侧 → 向左摆
            vx_r = -swing
            vy_r = BASE_UP + abs(swing) * 0.4
            vy_r = max(vy_r, MIN_VY)

            self.firework_generator.generate_firework_thread(
                (right_x, 0.0, 0.0),
                (vx_r, vy_r, 0.0),
                fire_type
            )

            swing *= SWING_DECAY
            time.sleep(0.18)

        time.sleep(0.6)

        # ======================
        # 第二阶段：中轴汇聚冲顶
        # ======================
        for i in range(8):
            vy = 36.0 + i * 3.0

            self.firework_generator.generate_firework_thread(
                (0.0, 0.0, 0.0),
                (0.0, vy, 0.0),
                self.type_firework.choose_random_type()
            )

            time.sleep(0.08)


    def one_wave_time_shifted_curtain(self):
        

        # ======================
        # 参数区
        # ======================
        layers = 3              # 垂直幕帘的层数
        shots_per_layer = 4     # 每一层的烟花数量

        BASE_UP = 16.0          # 最慢层向上速度
        SPEED_GAP = 10.0        # 每一层的速度差
        MIN_VY = 6.0

        x_positions = [-16, -8, 0, 8, 16]  # 幕帘宽度

        # ======================
        # 核心：时间错位释放
        # ======================
        for layer in range(layers):
            vy = BASE_UP + layer * SPEED_GAP
            vy = max(vy, MIN_VY)

            for _ in range(shots_per_layer):
                for x in x_positions:
                    self.firework_generator.generate_firework_thread(
                        (x, 0.0, 0.0),
                        (0.0, vy, 0.0),
                        self.type_firework.choose_random_type()
                    )

                # 同一层内部节奏很快
                time.sleep(0.05)

            # 不同层之间制造“追逐感”
            time.sleep(0.4)


    def one_wave_shockwave_climax(self):
        

        # ======================
        # 参数区（高潮专用）
        # ======================
        BASE_UP = 24.0
        MIN_VY = 10.0

        x_positions = [-12, -8, -4, 0, 4, 8, 12]

        # ======================
        # 第一阶段：空间压缩（密集立柱）
        # ======================
        for _ in range(4):
            for x in x_positions:
                self.firework_generator.generate_firework_thread(
                    (x, 0.0, 0.0),
                    (0.0, max(BASE_UP, MIN_VY), 0.0),
                    self.type_firework.choose_random_type()
                )
            time.sleep(0.12)

        time.sleep(0.35)

        # ======================
        # 第二阶段：横向冲击波爆裂
        # ======================
        for x in x_positions:
            vx = x * 1.8  # 离中心越远，冲击越强
            vy = BASE_UP + 8.0

            self.firework_generator.generate_firework_thread(
                (0.0, 0.0, 0.0),
                (vx, vy, 0.0),
                self.type_firework.choose_random_type()
            )

        time.sleep(0.25)

        # ======================
        # 第三阶段：顶点贯穿（高潮标志）
        # ======================
        for i in range(10):
            vy = 38.0 + i * 2.5

            self.firework_generator.generate_firework_thread(
                (0.0, 0.0, 0.0),
                (0.0, vy, 0.0),
                self.type_firework.choose_random_type()
            )

            time.sleep(0.05)


    def one_wave_sky_net_overload(self):
        

        # ======================
        # 参数区（高潮专用）
        # ======================
        BASE_UP = 22.0
        MIN_VY = 10.0

        # 横向铺网位置（非常宽）
        x_positions = [-18, -12, -6, 0, 6, 12, 18]

        # ======================
        # 第一阶段：天穹能量网（第一层）
        # ======================
        for _ in range(2):
            for x in x_positions:
                vx = x * 0.6
                vy = max(BASE_UP + abs(x) * 0.3, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    (x, 0.0, 0.0),
                    (vx, vy, 0.0),
                    self.type_firework.choose_random_type()
                )
            time.sleep(0.12)

        time.sleep(0.25)

        # ======================
        # 第二阶段：错位叠加网（第二层，更快）
        # ======================
        for _ in range(2):
            for x in x_positions:
                vx = -x * 0.8
                vy = max(BASE_UP + 10.0 + abs(x) * 0.4, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    (x * 0.5, 0.0, 0.0),
                    (vx, vy, 0.0),
                    self.type_firework.choose_random_type()
                )
            time.sleep(0.1)

        time.sleep(0.25)

        # ======================
        # 第三阶段：中央过载贯穿（最终高潮）
        # ======================
        for i in range(14):
            vy = 42.0 + i * 2.8

            self.firework_generator.generate_firework_thread(
                (0.0, 0.0, 0.0),
                (0.0, vy, 0.0),
                self.type_firework.choose_random_type()
            )

            time.sleep(0.045)



    def one_wave_helical_sphere_rupture(self):
        # ======================
        # 参数区
        # ======================
        layers = 5          # z 轴层数
        points_per_layer = 5

        BASE_UP = 26.0
        MIN_VY = 10.0

        RADIUS = 18.0
        Z_GAP = 6.0

        # ======================
        # 第一阶段：3D 螺旋球壳
        # ======================
        angle = 0.0
        angle_step = 360.0 / points_per_layer

        for layer in range(layers):
            z_offset = (layer - layers // 2) * Z_GAP

            for i in range(points_per_layer):
                angle += angle_step

                # 手动构造“旋转”，不用 sin/cos
                x_dir = (i - points_per_layer / 2) / points_per_layer
                z_dir = (layer - layers / 2) / layers

                vx = x_dir * RADIUS
                vz = z_dir * RADIUS

                vy = BASE_UP + abs(vx) * 0.4 + abs(vz) * 0.4
                vy = max(vy, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    (0.0, 0.0, z_offset),
                    (vx, vy, vz),
                    self.type_firework.choose_random_type()
                )

            time.sleep(0.12)

        time.sleep(0.35)

        # ======================
        # 第二阶段：球体失稳（更密更乱）
        # ======================
        for _ in range(2):
            for layer in range(layers):
                z_offset = (layer - layers // 2) * Z_GAP

                for i in range(points_per_layer):
                    vx = (i - points_per_layer / 2) * 2.2
                    vz = (layer - layers / 2) * 3.0

                    vy = BASE_UP + 12.0
                    vy = max(vy, MIN_VY)

                    self.firework_generator.generate_firework_thread(
                        (0.0, 0.0, z_offset),
                        (vx, vy, vz),
                        self.type_firework.choose_random_type()
                    )

            time.sleep(0.1)

        time.sleep(0.25)

        # ======================
        # 第三阶段：核心贯穿（空间撕裂）
        # ======================
        for i in range(16):
            vy = 44.0 + i * 2.6

            self.firework_generator.generate_firework_thread(
                (0.0, 0.0, 0.0),
                (0.0, vy, 0.0),
                self.type_firework.choose_random_type()
            )

            time.sleep(0.04)


    def one_wave_spatial_fault_collapse(self):
        # ======================
        # 参数区
        # ======================
        fault_count = 4          # 断层数量
        points_per_fault = 9     # 每条断层的烟花数

        BASE_UP = 28.0
        MIN_VY = 12.0

        FAULT_SPACING_Z = 10.0
        FAULT_LENGTH_X = 30.0

        # ======================
        # 第一阶段：断层显现（空间被切开）
        # ======================
        for f in range(fault_count):
            z_base = (f - (fault_count - 1) / 2) * FAULT_SPACING_Z

            # 每条断层有一个整体“倾斜方向”
            fault_vx = (f - (fault_count - 1) / 2) * 6.0
            fault_vz = (-1 if f % 2 == 0 else 1) * 8.0

            vy = max(BASE_UP, MIN_VY)

            for i in range(points_per_fault):
                x = -FAULT_LENGTH_X / 2 + i * (FAULT_LENGTH_X / (points_per_fault - 1))

                self.firework_generator.generate_firework_thread(
                    (x, 0.0, z_base),
                    (fault_vx, vy, fault_vz),
                    self.type_firework.choose_random_type()
                )

            time.sleep(0.18)

        time.sleep(0.5)

        # ======================
        # 第二阶段：断层整体上移（空间漂移）
        # ======================
        for f in range(fault_count):
            z_base = (f - (fault_count - 1) / 2) * FAULT_SPACING_Z

            fault_vx = (f - (fault_count - 1) / 2) * 10.0
            fault_vz = (-1 if f % 2 == 0 else 1) * 14.0
            vy = max(BASE_UP + 12.0, MIN_VY)

            for i in range(points_per_fault):
                x = -FAULT_LENGTH_X / 2 + i * (FAULT_LENGTH_X / (points_per_fault - 1))

                self.firework_generator.generate_firework_thread(
                    (x, 0.0, z_base),
                    (fault_vx, vy, fault_vz),
                    self.type_firework.choose_random_type()
                )

            time.sleep(0.12)

        time.sleep(0.3)

        # ======================
        # 第三阶段：核心贯穿（断层解体）
        # ======================
        for i in range(18):
            vy = 46.0 + i * 2.4

            self.firework_generator.generate_firework_thread(
                (0.0, 0.0, 0.0),
                (0.0, vy, 0.0),
                self.type_firework.choose_random_type()
            )

            time.sleep(0.04)



    def one_wave_volumetric_phase_explosion(self):
        # ======================
        # 参数区
        # ======================
        layers_z = 4
        rows_x = 5

        BASE_UP = 24.0
        MIN_VY = 10.0

        Z_GAP = 10.0
        X_GAP = 10.0

        # ======================
        # 第一阶段：体积冻结（稳定能量块）
        # ======================
        for z in range(layers_z):
            z_pos = (z - (layers_z - 1) / 2) * Z_GAP

            for x in range(rows_x):
                x_pos = (x - (rows_x - 1) / 2) * X_GAP

                self.firework_generator.generate_firework_thread(
                    (x_pos, 0.0, z_pos),
                    (0.0, max(BASE_UP, MIN_VY), 0.0),
                    self.type_firework.choose_random_type()
                )

        time.sleep(0.8)

        # ======================
        # 第二阶段：体相爆散（真正高潮）
        # ======================
        for z in range(layers_z):
            z_dir = (z - (layers_z - 1) / 2)

            for x in range(rows_x):
                x_dir = (x - (rows_x - 1) / 2)

                vx = x_dir * 14.0
                vz = z_dir * 14.0

                vy = BASE_UP + abs(vx) * 0.3 + abs(vz) * 0.3
                vy = max(vy, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    (x_dir * X_GAP * 0.5, 0.0, z_dir * Z_GAP * 0.5),
                    (vx, vy, vz),
                    self.type_firework.choose_random_type()
                )

        time.sleep(0.2)

        # ======================
        # 第三阶段：余波（整体上扬但继续发散）
        # ======================
        for z in range(layers_z):
            z_dir = (z - (layers_z - 1) / 2)

            for x in range(rows_x):
                x_dir = (x - (rows_x - 1) / 2)

                vx = x_dir * 18.0
                vz = z_dir * 18.0
                vy = max(BASE_UP + 16.0, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    (0.0, 0.0, 0.0),
                    (vx, vy, vz),
                    self.type_firework.choose_random_type()
                )


    def one_wave_quantum_crown_overdrive(self):
        # 你已 import：time, math
        # 约束：vy 不能为 0
        MIN_VY = 12.0

        # ========= 参数（烟花数量多一点） =========
        N = 18                 # 环上发射点数量（越大越“铺满天空”）
        SWEEPS = 5             # 扫描次数（越大越密集）
        R1 = 20.0              # 外环半径（x-z 平面）
        R2 = 12.0              # 内环半径
        UP = 26.0              # 基础向上速度
        RAD1 = 10.0            # 外环径向速度
        TAN1 = 16.0            # 外环切向速度（形成旋转王冠）
        RAD2 = 8.0             # 内环径向速度
        TAN2 = 22.0            # 内环切向速度（更强，形成双层编织）

        # 安全：防止你未来把 N 改成 0
        N = max(1, int(N))

        # ========= 第一段：3D 旋转王冠（外环） =========
        # x-z 平面一圈点，速度含：径向 + 切向 + 向上
        phase = 0.0
        for s in range(SWEEPS):
            phase += 0.55  # 每次 sweep 相位推进，让“王冠”在旋转

            for i in range(N):
                theta = (2.0 * math.pi) * (i / N) + phase

                cx = math.cos(theta)
                sz = math.sin(theta)

                # 发射位置：绕 y 轴的环（在 x-z 平面）
                pos = (R1 * cx, 0.0, R1 * sz)

                # 径向方向（向外）
                vx_r = RAD1 * cx
                vz_r = RAD1 * sz

                # 切向方向（绕圈旋转）：(-sin, cos)
                vx_t = -TAN1 * sz
                vz_t = TAN1 * cx

                vx = vx_r + vx_t
                vz = vz_r + vz_t

                # 向上速度：与横向幅度耦合，让整体更“炸”且 vy 永不为 0
                vy = UP + 0.22 * (abs(vx) + abs(vz))
                vy = max(vy, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    pos,
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )

            time.sleep(0.07)

        time.sleep(0.25)

        # ========= 第二段：双层反向编织（内环反向切向，制造“空间绳结”） =========
        phase = 0.0
        for s in range(SWEEPS):
            phase -= 0.75  # 反向推进，相当于“逆旋”织进去

            for i in range(N):
                theta = (2.0 * math.pi) * (i / N) + phase

                cx = math.cos(theta)
                sz = math.sin(theta)

                pos = (R2 * cx, 0.0, R2 * sz)

                # 径向略弱，但切向更强，形成“内层高速绞动”
                vx_r = RAD2 * cx
                vz_r = RAD2 * sz

                # 反向切向（注意符号与上一段相反）
                vx_t = TAN2 * sz
                vz_t = -TAN2 * cx

                vx = vx_r + vx_t
                vz = vz_r + vz_t

                vy = (UP + 8.0) + 0.25 * (abs(vx) + abs(vz))
                vy = max(vy, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    pos,
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )

            time.sleep(0.06)

        time.sleep(0.25)

        # ========= 第三段（高潮）：旋涡内扣崩解（不是中心贯穿） =========
        # 从外环位置发射，但速度“向内扣 + 强切向”，像把整个 3D 王冠拧碎
        CRUSH = 18.0    # 向心扣拢强度
        SPIN = 26.0     # 切向撕裂强度（越大越“酷炫”）
        for k in range(2):  # 两轮崩解，画面更爆
            for i in range(N * 2):  # 数量加倍
                theta = (2.0 * math.pi) * (i / (N * 2)) + (k * 0.4)

                cx = math.cos(theta)
                sz = math.sin(theta)

                # 位置仍在环上，但更大范围占据 z
                pos = (R1 * cx, 0.0, R1 * sz)

                # 向内（-径向）+ 强切向（制造“撕裂旋涡”）
                vx_in = -CRUSH * cx
                vz_in = -CRUSH * sz

                vx_spin = -SPIN * sz
                vz_spin = SPIN * cx

                vx = vx_in + vx_spin
                vz = vz_in + vz_spin

                # 向上更强，但不做“中心柱”连发
                vy = (UP + 18.0) + 0.18 * (abs(vx) + abs(vz))
                vy = max(vy, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    pos,
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )

                time.sleep(0.015)

            time.sleep(0.12)


    def one_wave_aurora_blossom_dome(self):
        MIN_VY = 10.0

        # ---------- 参数：温柔但壮观 ----------
        RINGS = [
            (24.0, 18, 10.0, 10.0, 22.0),  # (半径, 点数, 径向速度, 切向速度, 基础上升)
            (16.0, 16, 8.0,  8.0,  24.0),
            (9.0,  14, 6.0,  6.0,  26.0),
        ]
        SWEEPS = 3            # 扫描次数（越大越“铺满穹顶”）
        SLEEP_SWEEP = 0.10    # 温柔节奏

        # ========== 第一段：三层花穹缓慢铺开 ==========
        phase = 0.0
        for s in range(SWEEPS):
            phase += 0.35  # 缓慢相位推进，让穹顶像在“呼吸旋转”

            for (R, N, RAD, TAN, UP) in RINGS:
                N = max(1, int(N))
                for i in range(N):
                    theta = (2.0 * math.pi) * (i / N) + phase

                    cx = math.cos(theta)
                    sz = math.sin(theta)

                    # 位置：环（x-z），形成 3D 穹顶的“底座轮廓”
                    pos = (R * cx, 0.0, R * sz)

                    # 速度：径向 + 温柔切向 + 向上
                    vx = RAD * cx + (-TAN * sz)
                    vz = RAD * sz + ( TAN * cx)

                    # 温柔但稳定：vy 永远 > 0，且随横向幅度轻微抬升
                    vy = UP + 0.12 * (abs(vx) + abs(vz))
                    vy = max(vy, MIN_VY)

                    self.firework_generator.generate_firework_thread(
                        pos,
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

            time.sleep(SLEEP_SWEEP)

        time.sleep(0.45)

        # ========== 第二段：花瓣回拢（向心但仍上升） ==========
        # 这段是“温柔高潮”：不是炸，而是“整片天空回收聚光”
        phase = 0.0
        for s in range(2):
            phase += 0.25

            for (R, N, RAD, TAN, UP) in RINGS:
                N = max(1, int(N))
                for i in range(N):
                    theta = (2.0 * math.pi) * (i / N) + phase

                    cx = math.cos(theta)
                    sz = math.sin(theta)

                    pos = (R * cx, 0.0, R * sz)

                    # 向心（-径向）+ 更小的切向，形成“花瓣回拢”的柔和感
                    vx = -0.75 * RAD * cx + (-0.55 * TAN * sz)
                    vz = -0.75 * RAD * sz + ( 0.55 * TAN * cx)

                    vy = (UP + 8.0) + 0.10 * (abs(vx) + abs(vz))
                    vy = max(vy, MIN_VY)

                    self.firework_generator.generate_firework_thread(
                        pos,
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

            time.sleep(0.12)

        time.sleep(0.35)

        # ========== 第三段：余辉点缀（轻柔升华，不贯穿） ==========
        # 少量“上扬漂浮感”，让收尾更梦幻
        SPARKS = 18
        for i in range(SPARKS):
            # 交替在两圈位置点缀，z 轴参与
            sign = -1.0 if i % 2 == 0 else 1.0
            x = sign * (6.0 + (i % 3) * 2.0)
            z = -sign * (10.0 - (i % 4) * 2.0)

            vx = -0.25 * x
            vz = -0.25 * z
            vy = max(28.0 + (i % 5) * 1.6, MIN_VY)

            self.firework_generator.generate_firework_thread(
                (float(x), 0.0, float(z)),
                (float(vx), float(vy), float(vz)),
                self.type_firework.choose_random_type()
            )

            time.sleep(0.06)



    def one_wave_infinity_ribbon_lanterns(self, sparkle=True):
        # 依赖你已 import: time, math
        MIN_VY = 10.0

        # 丝带参数（数量可以很大但仍然“温柔”）
        STEPS = 46          # 越大越“壮观/铺满”
        SLEEP = 0.045       # 节奏偏柔和但不拖沓

        # 空间尺度
        AX = 20.0           # x 振幅（∞形横向）
        AZ = 14.0           # z 振幅（∞形纵向）
        DRIFT_Z = 10.0      # 两条丝带的 z 偏移，形成 3D 层次
        UP = 18.0           # 基础向上速度

        # 曲线推进
        w = 0.28            # 相位步进（控制∞的“密度/舒展”）
        t = 0.0

        # 两条丝带：同一条∞曲线，但相位相反 + z 分层
        for k in range(STEPS):
            t += w

            # Lemniscate（∞）的参数化：x = sin(t), z = sin(t)*cos(t)
            s = math.sin(t)
            c = math.cos(t)

            # ribbon A
            vx_a = AX * s
            vz_a = AZ * (s * c) + DRIFT_Z
            vy_a = UP + 0.22 * (abs(vx_a) + abs(vz_a))  # 永远 > 0
            vy_a = max(vy_a, MIN_VY)

            self.firework_generator.generate_firework_thread(
                (-10.0, 0.0, -8.0),
                (float(vx_a), float(vy_a), float(vz_a)),
                self.type_firework.nothing
            )

            # ribbon B（反相 + 另一层 z）
            vx_b = -AX * s
            vz_b = -AZ * (s * c) - DRIFT_Z
            vy_b = UP + 0.22 * (abs(vx_b) + abs(vz_b))
            vy_b = max(vy_b, MIN_VY)

            self.firework_generator.generate_firework_thread(
                (10.0, 0.0, 8.0),
                (float(vx_b), float(vy_b), float(vz_b)),
                self.type_firework.nothing
            )

            time.sleep(SLEEP)

        time.sleep(0.35)

        # 可选：轻轻“点亮”丝带节点（不做中心贯穿）
        # sparkle=False 则全程不炸，纯温柔光带
        if sparkle:
            # 选一些“∞ 的拐点/端点”附近，多点同时点亮，仍然温柔但壮观
            nodes = [
                (-18.0, 0.0, -10.0), (18.0, 0.0, 10.0),
                (-6.0,  0.0,  18.0), (6.0,  0.0, -18.0),
                (-22.0, 0.0,  6.0),  (22.0, 0.0, -6.0),
            ]

            for idx, pos in enumerate(nodes):
                # 轻柔上扬 + 少量侧向，避免“贯穿感”
                vx = (idx - len(nodes)/2) * 1.6
                vz = (len(nodes)/2 - idx) * 1.3
                vy = max(30.0 + (idx % 3) * 2.0, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    pos,
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )

            time.sleep(0.2)


    def one_wave_aurora_cathedral(self, sparkle=True):
        MIN_VY = 12.0

        # ====== 壮观程度参数（想更猛就调大）======
        CURTAINS = 6            # 幕帘数量（建议 5~8）
        LAYERS_Z = 5            # z 分层（建议 4~7）
        STRIP_POINTS = 9        # 每条幕帘的横向点数（建议 7~13）
        SWEEPS = 6              # 推进轮数（建议 5~9，越大越壮观）
        SLEEP = 0.06            # 越小越密、越“铺满天空”（0.045~0.08）

        # ====== 空间尺度 ======
        X_SPAN = 34.0           # 幕帘横向展开宽度
        Z_SPAN = 28.0           # 幕帘纵深宽度
        Z_GAP = 7.0             # 分层间距

        # ====== 速度尺度（温柔但宏大）======
        BASE_UP = 18.0
        WAVE_UP = 10.0          # 幕帘“呼吸”向上起伏
        FLOW_X = 16.0           # 横向流动
        FLOW_Z = 14.0           # 纵深流动

        # 相位推进（控制“极光流动感”）
        phase = 0.0
        phase_step = 0.42

        # 预计算一些常用
        CURTAINS = max(1, int(CURTAINS))
        LAYERS_Z = max(1, int(LAYERS_Z))
        STRIP_POINTS = max(1, int(STRIP_POINTS))
        SWEEPS = max(1, int(SWEEPS))

        # =========================================================
        # 第一段：3D 极光穹幕生成（多幕帘 + 多层深度 + 时间推进）
        # =========================================================
        for sweep in range(SWEEPS):
            phase += phase_step

            for c in range(CURTAINS):
                # 每一幕帘有自己的相位偏移和整体方向（避免“重复感”）
                c_phase = phase + c * 0.65
                c_bias = (c - (CURTAINS - 1) / 2.0) / max(1.0, (CURTAINS - 1) / 2.0)

                # 幕帘中心在 x 轴上分布，同时给一点 z 偏置（形成“教堂拱廊”）
                curtain_center_x = c_bias * (X_SPAN * 0.28)
                curtain_center_z = -c_bias * (Z_SPAN * 0.22)

                for z_layer in range(LAYERS_Z):
                    # 分层：前后景 (z) 产生体积感
                    z_bias = (z_layer - (LAYERS_Z - 1) / 2.0)
                    z_pos = curtain_center_z + z_bias * Z_GAP

                    # 每层给不同的流动方向，形成 3D 交错流
                    layer_phase = c_phase + z_layer * 0.55

                    for p in range(STRIP_POINTS):
                        # 横向点沿 x 轴排布（像幕帘的“褶皱”）
                        if STRIP_POINTS == 1:
                            x_pos = curtain_center_x
                            u = 0.0
                        else:
                            u = (p / (STRIP_POINTS - 1)) * 2.0 - 1.0  # [-1, 1]
                            x_pos = curtain_center_x + u * (X_SPAN * 0.5)

                        # —— 速度：不追求爆裂，追求“流动 + 呼吸 + 体积” ——
                        # 横向/纵深流动：用 sin/cos 产生连续波形（但避免中心贯穿套路）
                        vx = FLOW_X * (0.55 * math.sin(layer_phase + u * 1.6) + 0.35 * c_bias)
                        vz = FLOW_Z * (0.55 * math.cos(layer_phase * 0.9 + u * 1.2) - 0.30 * c_bias)

                        # 向上速度：基础上升 + “呼吸波”，确保永远 > 0
                        vy = BASE_UP + WAVE_UP * (0.6 + 0.4 * math.sin(layer_phase + u * 1.8))
                        # 让幅度越大越“亮”且更稳定上升
                        vy += 0.10 * (abs(vx) + abs(vz))
                        vy = max(vy, MIN_VY)

                        self.firework_generator.generate_firework_thread(
                            (float(x_pos), 0.0, float(z_pos)),
                            (float(vx), float(vy), float(vz)),
                            self.type_firework.nothing  # 不炸：极光帘
                        )

            time.sleep(SLEEP)

        time.sleep(0.45)

        # =========================================================
        # 第二段：穹顶“收束”——更温柔、更大气的合拢（仍不炸）
        # （让整片极光像拱顶一样向内收，画面会更“壮观且优雅”）
        # =========================================================
        for k in range(3):
            phase += 0.55

            for z_layer in range(LAYERS_Z):
                z_bias = (z_layer - (LAYERS_Z - 1) / 2.0)
                z_pos = z_bias * Z_GAP

                for p in range(STRIP_POINTS * 2):
                    u = (p / max(1, (STRIP_POINTS * 2 - 1))) * 2.0 - 1.0
                    x_pos = u * (X_SPAN * 0.58)

                    # “向内收束”速度：vx, vz 都朝向内侧，但保持流动感
                    vx = -14.0 * u + 6.0 * math.sin(phase + u * 1.8)
                    vz = -10.0 * (z_bias / max(1.0, (LAYERS_Z - 1) / 2.0)) + 5.0 * math.cos(phase * 0.9 + u)

                    vy = (BASE_UP + 10.0) + 6.0 * (0.6 + 0.4 * math.sin(phase + u * 2.0))
                    vy += 0.08 * (abs(vx) + abs(vz))
                    vy = max(vy, MIN_VY)

                    self.firework_generator.generate_firework_thread(
                        (float(x_pos), 0.0, float(z_pos)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

            time.sleep(0.10)

        time.sleep(0.35)

        # =========================================================
        # 第三段（可选）：轻柔点亮（不中心、不贯穿，点在“穹顶边缘”）
        # =========================================================
        if sparkle:
            EDGE = 26.0
            nodes = [
                (-EDGE, 0.0, -EDGE), (-EDGE, 0.0,  EDGE),
                ( EDGE, 0.0, -EDGE), ( EDGE, 0.0,  EDGE),
                (-EDGE, 0.0,  0.0),  ( EDGE, 0.0,  0.0),
                ( 0.0,  0.0, -EDGE), ( 0.0,  0.0,  EDGE),
            ]

            for i, pos in enumerate(nodes):
                # 轻柔上扬 + 轻微环向漂移（不做贯穿感）
                vx = 6.0 * math.sin(phase + i)
                vz = 6.0 * math.cos(phase * 0.9 + i * 0.7)
                vy = max(32.0 + (i % 3) * 2.0, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    pos,
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )

                time.sleep(0.06)


    def one_wave_tesseract_flip(self, sparkle=True):
        MIN_VY = 12.0

        # ====== 壮观/炫酷参数 ======
        FRAMES = 6              # “翻转帧数”，越大越像真的在旋转
        SLEEP = 0.06            # 帧间隔，越小越密更炫

        SIZE = 18.0             # 立方体半边长（x-z 平面尺度）
        OUT = 20.0              # 径向“撑开”速度
        SWIRL = 26.0            # 环绕切向速度（炫酷核心）
        BASE_UP = 22.0          # 基础向上
        UP_BOOST = 0.16         # 横向越大越抬升，避免塌

        # 立方体骨架点（12条边的端点/中点组合，避免全是“环/柱”那种重复观感）
        # 用 x-z 平面的“骨架”，再通过帧旋转形成强 3D 体感
        pts = []
        a = SIZE
        b = SIZE * 0.55

        # 外框四角 + 边中点（8点）
        pts += [(-a, -a), (-a,  a), ( a, -a), ( a,  a)]
        pts += [(-a,  0), ( a,  0), ( 0, -a), ( 0,  a)]

        # 内框四角（4点），像“内骨架”
        pts += [(-b, -b), (-b,  b), ( b, -b), ( b,  b)]

        def _norm2(x, z):
            m = math.sqrt(x*x + z*z)
            if m < 1e-6:
                return 1.0, 0.0, 1.0  # fallback
            return x / m, z / m, m

        for f in range(FRAMES):
            # 两个相位：一个绕 y 轴旋转，一个做“翻转感”的错相
            yaw = 0.55 * f
            twist = 0.85 * f + 0.6

            cy = math.cos(yaw)
            sy = math.sin(yaw)

            ct = math.cos(twist)
            st = math.sin(twist)

            # 这一帧用什么类型：大多数用 nothing 做骨架，最后一两帧点亮更炫
            frame_type = self.type_firework.nothing
            if sparkle and f >= FRAMES - 2:
                frame_type = self.type_firework.choose_random_type()

            # 发射“立方体骨架”
            for (px, pz) in pts:
                # 先把点本身也做一个“错相扭转”，让骨架像在翻转重组（不是简单绕圈）
                # 这里不改变 y，只通过 x/z 的混合制造“立体翻面”的错觉
                x0 = px * ct - pz * st
                z0 = px * st + pz * ct

                # 位置再绕 y 轴旋转（帧动画感）
                x = x0 * cy - z0 * sy
                z = x0 * sy + z0 * cy

                # outward（径向）+ swirl（切向，绕 y 轴）
                ox, oz, mag = _norm2(x, z)
                tx, tz = -oz, ox  # 切向单位方向

                vx = OUT * ox + SWIRL * tx
                vz = OUT * oz + SWIRL * tz

                vy = BASE_UP + UP_BOOST * (abs(vx) + abs(vz))
                vy = max(vy, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    (float(x), 0.0, float(z)),
                    (float(vx), float(vy), float(vz)),
                    frame_type
                )

            # “量子对角线裂解”：从四角沿对角线切开空间（不走中心贯穿）
            if f % 2 == 0:
                corners = [(-a, -a), (-a, a), (a, -a), (a, a)]
                for (cx0, cz0) in corners:
                    # 指向对角线的方向（跨空间“切割”感）
                    dx = -cx0
                    dz = cz0
                    nx, nz, _ = _norm2(dx, dz)

                    vx = 22.0 * nx
                    vz = 22.0 * nz
                    vy = max(BASE_UP + 14.0, MIN_VY)

                    self.firework_generator.generate_firework_thread(
                        (float(cx0), 0.0, float(cz0)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

            time.sleep(SLEEP)

        # 最后一拍：锁边“点亮”（不是中心柱，是边缘锁定）
        if sparkle:
            edge_nodes = [(-a, 0.0, 0.0), (a, 0.0, 0.0), (0.0, 0.0, -a), (0.0, 0.0, a)]
            for i, pos in enumerate(edge_nodes):
                vx = 10.0 * math.sin(0.9 * i)
                vz = 10.0 * math.cos(0.9 * i)
                vy = max(34.0 + (i % 2) * 3.0, MIN_VY)

                self.firework_generator.generate_firework_thread(
                    pos,
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )
                time.sleep(0.05)


    def one_wave_hypernova_storm(self, sparkle=True):
        MIN_VY = 12.0

        # =======================
        # 可调强度参数（想更炸就调大）
        # =======================
        GRID = [-18.0, -9.0, 0.0, 9.0, 18.0]   # 5x5 发射阵列（超壮观来源之一）
        BASE_UP = 22.0
        UP_GAIN = 0.12

        # “风暴”速度尺度
        OUT = 22.0       # 径向撑开
        SWIRL = 30.0     # 切向撕裂（炫酷核心）
        DEEP = 18.0      # z 轴纵深推送（3D 核心）

        # 节奏（越小越密越震撼）
        TICK_A = 0.05
        TICK_B = 0.035
        TICK_C = 0.02

        def clamp_vy(vy):
            return float(vy if vy > MIN_VY else MIN_VY)

        def norm2(x, z):
            m = math.sqrt(x * x + z * z)
            if m < 1e-6:
                return 1.0, 0.0, 1.0
            return x / m, z / m, m

        # =======================
        # 第一段：空间打开（5x5 3D 阵列同时“点亮光轨”）
        # 观感：像舞台灯阵瞬间铺满天空
        # =======================
        for pulse in range(2):
            phase = 0.8 + pulse * 0.6
            for x0 in GRID:
                for z0 in GRID:
                    # 以阵列点为“局部中心”，做 outward + swirl
                    ox, oz, _ = norm2(x0 + 0.1, z0 + 0.1)
                    tx, tz = -oz, ox

                    vx = OUT * ox + SWIRL * tx * (0.8 + 0.2 * math.sin(phase + z0 * 0.07))
                    vz = OUT * oz + SWIRL * tz * (0.8 + 0.2 * math.cos(phase + x0 * 0.07))

                    # 强化 3D：按 z0 给一个“纵深推送”
                    vz += (z0 / 18.0) * DEEP

                    vy = BASE_UP + UP_GAIN * (abs(vx) + abs(vz)) + 6.0
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(x0), 0.0, float(z0)),
                        (float(vx), vy, float(vz)),
                        self.type_firework.nothing
                    )
            time.sleep(TICK_A)

        time.sleep(0.25)

        # =======================
        # 第二段：三维反向旋涡墙（两层相反方向的“风暴面”）
        # 观感：空间像被两股相反旋涡撕开，非常炫
        # =======================
        WALL_Z = [-26.0, -13.0, 13.0, 26.0]   # 多层深度墙
        X_LINE = [-28.0, -21.0, -14.0, -7.0, 0.0, 7.0, 14.0, 21.0, 28.0]

        for layer in range(3):
            phase = 1.1 + layer * 0.7
            for zi, z0 in enumerate(WALL_Z):
                direction = -1.0 if zi % 2 == 0 else 1.0  # 相反旋向
                for x0 in X_LINE:
                    # 以“墙的中心线”为参考制造强烈切向流
                    ox, oz, _ = norm2(x0, z0)
                    tx, tz = -oz, ox

                    vx = (OUT * 0.7) * ox + direction * SWIRL * tx
                    vz = (OUT * 0.7) * oz + direction * SWIRL * tz

                    # 给墙一个“波动”让它活起来（但仍然结构化）
                    vx += 6.0 * math.sin(phase + x0 * 0.08 + z0 * 0.03)
                    vz += 6.0 * math.cos(phase * 0.9 + x0 * 0.05)

                    vy = (BASE_UP + 10.0) + UP_GAIN * (abs(vx) + abs(vz))
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(x0), 0.0, float(z0)),
                        (float(vx), vy, float(vz)),
                        self.type_firework.nothing
                    )
            time.sleep(TICK_B)

        time.sleep(0.22)

        # =======================
        # 第三段（高潮）：超新星闪爆环阵（不是中心贯穿，是“全空间同步爆闪”）
        # 观感：像一个巨大的 3D 星云在空中同时爆开
        # =======================
        RINGS = [
            (34.0, 28),   # (半径, 点数)
            (24.0, 24),
            (16.0, 20),
        ]
        Z_LAYERS = [-18.0, -6.0, 6.0, 18.0]   # 4 层纵深：真正 3D

        # 一次性强爆闪：如果你希望完全不炸，把 sparkle=False
        burst_type = self.type_firework.choose_random_type() if sparkle else self.type_firework.nothing

        for sweep in range(3):
            phase = 0.9 + sweep * 0.55
            for z0 in Z_LAYERS:
                for (R, N) in RINGS:
                    N = max(1, int(N))
                    for i in range(N):
                        theta = (2.0 * math.pi) * (i / N) + phase + (z0 * 0.02)

                        cx = math.cos(theta)
                        sz = math.sin(theta)

                        # 从环上发射：位置本身已经占据巨大体积
                        px = R * cx
                        pz = R * sz + z0

                        # outward + 强切向 + 纵深扰动：形成“星云爆散”
                        ox, oz, _ = norm2(px, pz)
                        tx, tz = -oz, ox

                        vx = (OUT * 1.1) * ox + (SWIRL * 1.15) * tx
                        vz = (OUT * 1.1) * oz + (SWIRL * 1.15) * tz

                        # 让不同 z 层有不同“推送” -> 立体爆开
                        vz += (z0 / 18.0) * (DEEP * 0.9)

                        vy = (BASE_UP + 18.0) + UP_GAIN * (abs(vx) + abs(vz))
                        vy = clamp_vy(vy)

                        self.firework_generator.generate_firework_thread(
                            (float(px), 0.0, float(pz)),
                            (float(vx), vy, float(vz)),
                            self.type_firework.choose_random_type() if random.random() < 0.15 else self.type_firework.nothing
                        )
            time.sleep(TICK_C)


    def one_wave_blooming_canopy(self, sparkle=True):
        MIN_VY = 12.0

        # ====== 壮观/漂亮参数（可按需微调）======
        BASES = [(-16.0, -16.0), (-16.0, 16.0), (16.0, -16.0), (16.0, 16.0)]  # (x, z)
        SWEEPS = 8            # 越大越“铺满穹顶”（6~10）
        POINTS = 13           # 每次扫出的“花瓣丝带”宽度（11~17）
        SLEEP = 0.06          # 越小越密更壮观（0.045~0.08）

        BASE_UP = 18.0        # 温柔上升
        FWD = 22.0            # 主推进（形成穹顶外扩）
        WIDTH = 18.0          # 花瓣展开宽度（3D 扇面）
        RIPPLE = 6.5          # 轻微涟漪（更梦幻，不刺眼）
        DEPTH = 10.0          # z 轴纵深增强（更 3D）

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        # ==========================
        # 第一段：四角“花瓣穹顶”同步绽放（主体不炸）
        # ==========================
        phase = 0.0
        for s in range(SWEEPS):
            phase += 0.42  # 缓慢相位推进：像在“呼吸旋转”

            for bi, (bx, bz) in enumerate(BASES):
                # 每个角有不同旋转相位，形成四朵花的错相绽放（避免重复感）
                yaw = phase + bi * (math.pi / 2.0)

                cy = math.cos(yaw)
                sy = math.sin(yaw)

                # forward / right（在 x-z 平面）
                fx, fz = cy, sy
                rx, rz = -sy, cy

                for p in range(POINTS):
                    # u in [-1, 1]：花瓣宽度方向
                    if POINTS == 1:
                        u = 0.0
                    else:
                        u = (p / (POINTS - 1)) * 2.0 - 1.0

                    # 让花瓣边缘更“轻”，中心更“稳”
                    edge = abs(u)

                    # 速度：主推进 + 横向展开 + 轻涟漪 + 纵深分层
                    vx = fx * FWD + rx * (u * WIDTH) + RIPPLE * math.sin(phase + u * 2.2 + bi)
                    vz = fz * FWD + rz * (u * WIDTH) + RIPPLE * math.cos(phase * 0.9 + u * 1.8 + bi)

                    # 强化 3D：四角花瓣在纵深上也有“推开”的感觉
                    vz += (bz / 16.0) * DEPTH * (0.7 + 0.3 * math.sin(phase + bi))

                    # vy：温柔上升 + 依据横向幅度轻微抬升（保证 vy>0 且更稳定）
                    vy = BASE_UP + 8.0 * (0.55 + 0.45 * math.sin(phase + bi * 0.7)) + 0.10 * (abs(vx) + abs(vz))
                    # 边缘更轻柔：稍微降低一点上升，形成“花瓣弧面”观感
                    vy -= edge * 2.5
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(bx), 0.0, float(bz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

            time.sleep(SLEEP)

        time.sleep(0.45)

        # ==========================
        # 第二段：穹顶“回拢”成拱（仍不炸，更漂亮）
        # 让四朵花的光带向内轻轻合拢，形成“顶棚”感
        # ==========================
        for k in range(3):
            phase += 0.55

            for bi, (bx, bz) in enumerate(BASES):
                yaw = phase * 0.85 + bi * (math.pi / 2.0)
                cy = math.cos(yaw)
                sy = math.sin(yaw)

                fx, fz = cy, sy
                rx, rz = -sy, cy

                for p in range(POINTS):
                    u = 0.0 if POINTS == 1 else (p / (POINTS - 1)) * 2.0 - 1.0

                    # 回拢：在 forward 的基础上加入“向中心”的分量（不需要中心贯穿）
                    to_center_x = -bx
                    to_center_z = -bz
                    m = math.sqrt(to_center_x * to_center_x + to_center_z * to_center_z) + 1e-6
                    cxn, czn = to_center_x / m, to_center_z / m

                    vx = fx * (FWD * 0.75) + rx * (u * WIDTH * 0.75) + cxn * 10.0 + 4.0 * math.sin(phase + u * 2.0 + bi)
                    vz = fz * (FWD * 0.75) + rz * (u * WIDTH * 0.75) + czn * 10.0 + 4.0 * math.cos(phase * 0.9 + u * 1.7 + bi)

                    vy = (BASE_UP + 10.0) + 0.08 * (abs(vx) + abs(vz))
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(bx), 0.0, float(bz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

            time.sleep(0.10)

        time.sleep(0.35)

        # ==========================
        # 第三段（可选）：边缘柔光点亮（不中心、不贯穿）
        # 点在“穹顶边缘”和“对角”，会非常漂亮
        # ==========================
        if sparkle:
            nodes = [
                (-28.0, 0.0, -10.0), (-28.0, 0.0, 10.0),
                (28.0,  0.0, -10.0), (28.0,  0.0, 10.0),
                (-10.0, 0.0, -28.0), (10.0, 0.0, -28.0),
                (-10.0, 0.0, 28.0),  (10.0, 0.0, 28.0),
            ]

            for i, pos in enumerate(nodes):
                vx = 7.0 * math.sin(phase + i * 0.8)
                vz = 7.0 * math.cos(phase * 0.9 + i * 0.7)
                vy = clamp_vy(32.0 + (i % 4) * 2.0)

                self.firework_generator.generate_firework_thread(
                    pos,
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )
                time.sleep(0.06)


    def one_wave_aurora_braid_marathon(self, sparkle=False):
        MIN_VY = 12.0

        # =========================
        # 可调强度（想更长/更密/更壮观就调这里）
        # =========================
        TICKS_A = 70          # 第一幕时长（铺场）
        TICKS_B = 100         # 第二幕时长（主编织，最长最炫）
        TICKS_C = 30          # 第三幕时长（穹顶加冕）
        SLEEP_A = 0.05
        SLEEP_B = 0.04
        SLEEP_C = 0.1

        EMITTERS = 6        # 环形发射点数量（建议 10~16）
        Z_LAYERS = 6          # z 分层数量（建议 5~8）

        R_EMIT = 13.0         # 发射环半径（x-z 平面）
        Z_SPAN = 20.0         # z 分层跨度
        BASE_UP = 18.0        # 基础上升速度（温柔）
        UP_GAIN = 0.10        # 横向越强，上升越强（稳定 & 更壮观）

        OUT = 8.0            # 径向撑开
        SWIRL = 18.0          # 切向旋流（炫的关键）
        DEEP_PUSH = 14.0      # 纵深推送（更 3D）
        RIPPLE = 7.0          # 波纹扰动（更梦幻/更漂亮）

        # 防御性保护
        EMITTERS = max(1, int(EMITTERS))
        Z_LAYERS = max(1, int(Z_LAYERS))

        def clamp_vy(vy):
            return float(vy if vy > MIN_VY else MIN_VY)

        def norm2(x, z):
            m = math.sqrt(x * x + z * z)
            if m < 1e-6:
                return 1.0, 0.0, 1.0
            return x / m, z / m, m

        # =========================================================
        # 第一幕：星环铺场（让空间先“亮起来”，全是光轨）
        # =========================================================
        phase = 0.0
        for t in range(TICKS_A):
            phase += 0.20

            # 每 tick 扫描一个 z 层（降低单帧压力，但整体很长很密）
            zi = t % Z_LAYERS
            z_bias = (zi / (Z_LAYERS - 1) * 2.0 - 1.0) if Z_LAYERS > 1 else 0.0
            z0 = z_bias * (Z_SPAN * 0.5)

            for i in range(EMITTERS):
                theta = (2.0 * math.pi) * (i / EMITTERS) + phase
                cx = math.cos(theta)
                sz = math.sin(theta)

                px = R_EMIT * cx
                pz = R_EMIT * sz + z0

                ox, oz, _ = norm2(px, pz)
                tx, tz = -oz, ox

                vx = OUT * ox + SWIRL * tx + RIPPLE * math.sin(phase + i * 0.7)
                vz = OUT * oz + SWIRL * tz + RIPPLE * math.cos(phase * 0.9 + i * 0.5)

                # 强化 3D：不同 z 层有不同纵深推送
                vz += z_bias * DEEP_PUSH

                vy = BASE_UP + 8.0 + UP_GAIN * (abs(vx) + abs(vz))
                vy = clamp_vy(vy)

                self.firework_generator.generate_firework_thread(
                    (float(px), 0.0, float(pz)),
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.nothing
                )

            time.sleep(SLEEP_A)

        time.sleep(0.35)

        # =========================================================
        # 第二幕：三股极光编织（主菜，最长、最炫、光轨最多）
        # 机制：同一批发射源同时输出 3 条“不同相位、不同旋向”的丝带
        # =========================================================
        phase = 0.0
        for t in range(TICKS_B):
            phase += 0.27

            # 每 tick 发两层 z（真正铺满空间）
            zi1 = t % Z_LAYERS
            zi2 = (t + Z_LAYERS // 2) % Z_LAYERS

            def z_at(zi):
                z_bias = (zi / (Z_LAYERS - 1) * 2.0 - 1.0) if Z_LAYERS > 1 else 0.0
                return z_bias * (Z_SPAN * 0.5), z_bias

            z1, zb1 = z_at(zi1)
            z2, zb2 = z_at(zi2)

            # 三条编织丝带的相位/旋向
            braids = [
                (phase,        1.0,  0.9),  # (相位, 旋向, 强度缩放)
                (phase + 1.9, -1.0,  1.0),
                (phase + 3.7,  1.0,  1.1),
            ]

            for i in range(EMITTERS):
                base_theta = (2.0 * math.pi) * (i / EMITTERS)

                for (ph, spin, amp) in braids:
                    theta = base_theta + ph
                    cx = math.cos(theta)
                    sz = math.sin(theta)

                    # 两层同时织（同一丝带在前后景出现，3D 爆炸）
                    for (z0, z_bias) in [(z1, zb1), (z2, zb2)]:
                        px = R_EMIT * cx
                        pz = R_EMIT * sz + z0

                        ox, oz, _ = norm2(px, pz)
                        tx, tz = -oz, ox

                        # 径向 + 切向（旋向可反）+ 波纹扰动（更炫）
                        vx = (OUT * ox + spin * SWIRL * tx) * amp + RIPPLE * math.sin(ph * 1.1 + i * 0.6)
                        vz = (OUT * oz + spin * SWIRL * tz) * amp + RIPPLE * math.cos(ph * 0.9 + i * 0.5)

                        # 纵深推送（使每条丝带在不同深度层“呼吸”）
                        vz += z_bias * (DEEP_PUSH * 1.15) + 4.0 * math.sin(ph + z_bias)

                        vy = (BASE_UP + 10.0) + UP_GAIN * (abs(vx) + abs(vz))
                        vy = clamp_vy(vy)

                        self.firework_generator.generate_firework_thread(
                            (float(px), 0.0, float(pz)),
                            (float(vx), float(vy), float(vz)),
                            self.type_firework.nothing
                        )

            # 可选：少量“点亮闪烁”（不做中心柱，只做空间闪点）
            if sparkle and (t % 24 == 0):
                # 在不同深度随机挑几处“边缘点”轻点一下
                for k in range(8):
                    a = (t * 0.15 + k) * 0.9
                    px = (R_EMIT + 8.0) * math.cos(a)
                    pz = (R_EMIT + 8.0) * math.sin(a) + (math.sin(a * 0.7) * (Z_SPAN * 0.35))

                    vx = 10.0 * math.sin(a)
                    vz = 10.0 * math.cos(a)
                    vy = clamp_vy(32.0 + (k % 3) * 2.0)

                    self.firework_generator.generate_firework_thread(
                        (float(px), 0.0, float(pz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.choose_random_type()
                    )

            time.sleep(SLEEP_B)

        time.sleep(0.45)

        # =========================================================
        # 第三幕：穹顶加冕（更“漂亮”的终章：大穹顶光轨覆盖全场）
        # 不贯穿、不中心，靠“穹顶结构 + 多层深度”收束
        # =========================================================
        phase = 0.0
        DOME_RINGS = [(34.0, 14), (26.0, 12), (18.0, 8)]
        DOME_Z = [-20.0, -10.0, 0.0, 10.0, 20.0]

        for t in range(TICKS_C):
            phase += 0.22

            for z0 in DOME_Z:
                for (R, N) in DOME_RINGS:
                    N = max(1, int(N))
                    for i in range(N):
                        theta = (2.0 * math.pi) * (i / N) + phase + z0 * 0.02
                        cx = math.cos(theta)
                        sz = math.sin(theta)

                        px = R * cx
                        pz = R * sz + z0

                        ox, oz, _ = norm2(px, pz)
                        tx, tz = -oz, ox

                        # 穹顶：偏向“柔和流动”，减少撕裂感，增加“漂亮”
                        vx = (OUT * 0.9) * ox + (SWIRL * 0.8) * tx + 4.5 * math.sin(phase + i * 0.3)
                        vz = (OUT * 0.9) * oz + (SWIRL * 0.8) * tz + 4.5 * math.cos(phase * 0.9 + i * 0.25)

                        # 纵深轻推，保持 3D 层次
                        vz += (z0 / 20.0) * (DEEP_PUSH * 0.8)

                        vy = (BASE_UP + 14.0) + 0.08 * (abs(vx) + abs(vz))
                        vy = clamp_vy(vy)

                        self.firework_generator.generate_firework_thread(
                            (float(px), 0.0, float(pz)),
                            (float(vx), float(vy), float(vz)),
                            self.type_firework.nothing
                        )

            time.sleep(SLEEP_C)


    def one_wave_meteor_cathedral_rain(self, sparkle=False):
        MIN_VY = 12.0

        # =========================
        # 可调强度（更长/更密/更壮观）
        # =========================
        DURATION = 220          # 总 tick（更长就加到 300+）
        SLEEP = 0.06           # 越小越密越炫（0.03~0.06）

        # “幕帘”数量与深度层
        CURTAINS = 6           # 同时存在的流星帘数量（6~10）
        Z_LAYERS = 5            # 深度层（5~9）

        # 空间尺度
        X_SPAN = 70.0           # 从左到右扫过的宽度
        Z_SPAN = 44.0           # 前后纵深
        ORIGIN_Y = 0.0

        # 速度尺度（流星感：强斜向 + 仍上升）
        BASE_UP = 16.0          # 仍然向上（温柔不坠落）
        MIN_UP_BOOST = 8.0      # 确保 vy 不会接近 0
        DRIFT_X = 34.0          # 主斜向速度（横向扫过）
        DRIFT_Z = 22.0          # 纵深扫过（3D）
        RIPPLE = 10.0           # 流星帘的波动（更炫）

        # 每 tick 发射量（越大光轨越多）
        STREAKS_PER_TICK = 8   # 8~18

        CURTAINS = max(1, int(CURTAINS))
        Z_LAYERS = max(1, int(Z_LAYERS))
        STREAKS_PER_TICK = max(1, int(STREAKS_PER_TICK))

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        # =========================================================
        # 核心思路：
        # - 多条“流星帘”（不同相位/不同方向）
        # - 每条帘在多个 z 深度层出现（强 3D）
        # - 发射位置沿 x 方向不断推进（形成“雨幕扫过”）
        # =========================================================
        phase = 0.0
        for t in range(DURATION):
            phase += 0.23

            # 让雨幕从左向右“推进”，同时缓慢来回摆动（避免单调）
            sweep = (t / max(1, (DURATION - 1)))  # 0..1
            base_x = -X_SPAN * 0.55 + sweep * X_SPAN
            base_x += 8.0 * math.sin(phase * 0.45)  # 轻摆动更漂亮

            for c in range(CURTAINS):
                c_phase = phase + c * 0.85
                c_bias = (c - (CURTAINS - 1) / 2.0) / max(1.0, (CURTAINS - 1) / 2.0)

                # 不同帘有不同斜向方向（让天空“交叉雨幕”更壮观）
                dir_x = 1.0 if (c % 2 == 0) else -1.0
                dir_z = -1.0 if (c % 3 == 0) else 1.0

                # 每个 tick，这条帘发射多条“流星线”
                for k in range(STREAKS_PER_TICK):
                    # 在帘内部做一个横向偏移（形成一整片雨幕）
                    u = (k / max(1, (STREAKS_PER_TICK - 1))) * 2.0 - 1.0

                    # 深度层：循环选层，保证每时刻都有前后景
                    zi = (t + c + k) % Z_LAYERS
                    z_bias = (zi / (Z_LAYERS - 1) * 2.0 - 1.0) if Z_LAYERS > 1 else 0.0
                    z0 = z_bias * (Z_SPAN * 0.5) + c_bias * 6.0

                    # 发射位置：沿 sweep 推进 + 帘内展开 + 深度层
                    px = base_x + c_bias * 10.0 + u * 10.0
                    pz = z0

                    # 速度：强斜向扫过 + 波动（帘在“呼吸”）
                    vx = dir_x * DRIFT_X + RIPPLE * math.sin(c_phase + u * 2.1) + 6.0 * c_bias
                    vz = dir_z * DRIFT_Z + RIPPLE * math.cos(c_phase * 0.9 + u * 1.7) + 6.0 * z_bias

                    # vy：温柔上升（流星不坠落），并随斜向幅度轻微增加
                    vy = BASE_UP + MIN_UP_BOOST + 0.06 * (abs(vx) + abs(vz))
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(px), ORIGIN_Y, float(pz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

            # 可选：偶尔点亮“流星核心”（不贯穿、不中心）
            if sparkle and (t % 28 == 0):
                for j in range(10):
                    a = (phase * 0.8 + j) * 0.9
                    px = base_x + 18.0 * math.sin(a)
                    pz = 14.0 * math.cos(a * 0.7)

                    vx = 8.0 * math.sin(a)
                    vz = 8.0 * math.cos(a)
                    vy = clamp_vy(30.0 + (j % 4) * 2.0)

                    self.firework_generator.generate_firework_thread(
                        (float(px), 0.0, float(pz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.choose_random_type()
                    )

            time.sleep(SLEEP)

    def one_wave_pulse_bouquet(self, sparkle=True):
        MIN_VY = 12.0

        # ====== 性能友好参数（想更省就再减）======
        TRAIL_RINGS = 4         # 光轨环层数（1~3）
        TRAIL_POINTS = 14        # 每层点数（8~14）
        TRAIL_SLEEP = 0.06

        BURST_NODES = 12          # 爆炸点数量（6~12）
        BURST_SLEEP = 0.07

        FINISH_TRAILS = 46       # 收尾光轨数量（8~16）
        FINISH_SLEEP = 0.05

        # ====== 运动参数（偏“花束”而不是“撕裂”）======
        R = 18.0                 # 光轨环半径（x-z）
        BASE_UP = 18.0
        UP_GAIN = 0.10

        OUT = 14.0               # 径向撑开（柔）
        SWIRL = 18.0             # 切向（轻旋）
        DEEP = 10.0              # z 轴纵深（3D）

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def norm2(x, z):
            m = math.sqrt(x * x + z * z)
            if m < 1e-6:
                return 1.0, 0.0, 1.0
            return x / m, z / m, m

        TRAIL_RINGS = max(1, int(TRAIL_RINGS))
        TRAIL_POINTS = max(1, int(TRAIL_POINTS))
        BURST_NODES = max(1, int(BURST_NODES))
        FINISH_TRAILS = max(1, int(FINISH_TRAILS))

        # ==========================
        # 1) 花束骨架：少量 3D 光轨（nothing）
        # ==========================
        phase = 0.0
        for ring in range(TRAIL_RINGS):
            phase += 0.55
            z_layer = (ring - (TRAIL_RINGS - 1) / 2.0) * (DEEP * 0.9)

            for i in range(TRAIL_POINTS):
                theta = (2.0 * math.pi) * (i / TRAIL_POINTS) + phase
                cx = math.cos(theta)
                sz = math.sin(theta)

                px = R * cx
                pz = R * sz + z_layer

                ox, oz, _ = norm2(px, pz)
                tx, tz = -oz, ox

                vx = OUT * ox + SWIRL * tx
                vz = OUT * oz + SWIRL * tz + (z_layer / max(1.0, DEEP)) * 6.0

                vy = BASE_UP + 6.0 + UP_GAIN * (abs(vx) + abs(vz))
                vy = clamp_vy(vy)

                self.firework_generator.generate_firework_thread(
                    (float(px), 0.0, float(pz)),
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.nothing
                )

            time.sleep(TRAIL_SLEEP)

        time.sleep(0.25)

        # ==========================
        # 2) 点亮：少量爆炸（不中心贯穿，打在“花束边缘/顶部”）
        # ==========================
        if sparkle:
            # 选择若干“边缘节点”做点亮
            phase += 0.6
            for j in range(BURST_NODES):
                theta = (2.0 * math.pi) * (j / BURST_NODES) + phase
                cx = math.cos(theta)
                sz = math.sin(theta)

                # 爆炸位置：略高半径，且分不同深度层（3D）
                px = (R + 6.0) * cx
                pz = (R + 6.0) * sz + (DEEP * 0.6) * math.sin(theta * 0.7)

                # 速度：温柔上扬 + 轻微绕圈漂移（不要贯穿感）
                vx = 8.0 * (-sz) + 4.0 * cx
                vz = 8.0 * ( cx) + 4.0 * sz
                vy = clamp_vy(30.0 + 0.08 * (abs(vx) + abs(vz)))

                self.firework_generator.generate_firework_thread(
                    (float(px), 0.0, float(pz)),
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )

                time.sleep(BURST_SLEEP)

        time.sleep(0.25)

        # ==========================
        # 3) 收尾：少量短光轨（nothing），像余辉
        # ==========================
        phase += 0.7
        for k in range(FINISH_TRAILS):
            a = phase + k * 0.55

            px = 10.0 * math.sin(a * 0.9)
            pz = 14.0 * math.cos(a * 0.7)

            vx = 10.0 * math.sin(a)
            vz = 10.0 * math.cos(a * 0.9)
            vy = clamp_vy(22.0 + 0.06 * (abs(vx) + abs(vz)))

            self.firework_generator.generate_firework_thread(
                (float(px), 0.0, float(pz)),
                (float(vx), float(vy), float(vz)),
                self.type_firework.nothing
            )

            time.sleep(FINISH_SLEEP)



    def one_wave_prismatic_gate(self, sparkle=True):
        MIN_VY = 12.0

        # ========= 性能预算（想更省就降这些）=========
        BEAMS_PER_ANCHOR = 30     # 每个锚点光束数量（1~3）
        EDGE_SWEEPS = 20         # 门框边缘扫描次数（1~3）
        FLASH_BURSTS = 30        # 闪断爆点数量（8~14）
        FINISH_TRAILS = 100      # 收尾光轨数量（8~14）

        # ========= 造型参数（3D “门”）=========
        A = 22.0                 # 门框半宽（x）
        B = 16.0                 # 门框半深（z）
        Z_DEPTH = 18.0           # 前后两层门框距离

        # ========= 速度参数（酷炫但不乱）=========
        BASE_UP = 18.0
        UP_GAIN = 0.10

        OUT = 18.0               # 径向撑开
        SWIRL = 26.0             # 切向旋流（炫的关键）
        DEPTH_PUSH = 14.0        # 纵深推送（3D 关键）
        SNAP = 22.0              # 闪断“向内扣”的强度

        # ========= 节奏 =========
        SLEEP_BEAM = 0.06
        SLEEP_EDGE = 0.06
        SLEEP_FLASH = 0.05
        SLEEP_FIN = 0.05

        BEAMS_PER_ANCHOR = max(1, int(BEAMS_PER_ANCHOR))
        EDGE_SWEEPS = max(1, int(EDGE_SWEEPS))
        FLASH_BURSTS = max(1, int(FLASH_BURSTS))
        FINISH_TRAILS = max(1, int(FINISH_TRAILS))

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def norm2(x, z):
            m = math.sqrt(x * x + z * z)
            if m < 1e-6:
                return 1.0, 0.0, 1.0
            return x / m, z / m, m

        # =========================================================
        # 1) 3D 门框锚点：前后两层“八角锚点”（强 3D 立体感）
        # =========================================================
        anchors_front = [
            (-A, -B), (-A,  B), ( A, -B), ( A,  B),  # 四角
            ( 0.0, -B), ( 0.0,  B), (-A, 0.0), (A, 0.0)  # 边中点
        ]
        anchors_back = [(x, z) for (x, z) in anchors_front]

        # =========================================================
        # 2) 第一段：能量之门“点亮骨架”（nothing，少量但极酷）
        #    每个锚点发 1~3 条光束： outward + swirl + depth push
        # =========================================================
        phase = 0.0
        for k in range(BEAMS_PER_ANCHOR):
            phase += 0.65

            # 前层
            for (x0, z0) in anchors_front:
                px, pz = x0, z0 - Z_DEPTH * 0.5
                ox, oz, _ = norm2(px, pz)
                tx, tz = -oz, ox

                vx = OUT * ox + SWIRL * tx + 5.0 * math.sin(phase + x0 * 0.03)
                vz = OUT * oz + SWIRL * tz + 5.0 * math.cos(phase * 0.9 + z0 * 0.03)
                vz += -DEPTH_PUSH * 0.6

                vy = BASE_UP + 8.0 + UP_GAIN * (abs(vx) + abs(vz))
                vy = clamp_vy(vy)

                self.firework_generator.generate_firework_thread(
                    (float(px), 0.0, float(pz)),
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.nothing
                )

            # 后层（反旋向，形成“折射”观感）
            for (x0, z0) in anchors_back:
                px, pz = x0, z0 + Z_DEPTH * 0.5
                ox, oz, _ = norm2(px, pz)
                tx, tz = -oz, ox

                vx = OUT * ox - SWIRL * tx + 5.0 * math.sin(phase + z0 * 0.03 + 1.7)
                vz = OUT * oz - SWIRL * tz + 5.0 * math.cos(phase * 0.9 + x0 * 0.03 + 1.2)
                vz += DEPTH_PUSH * 0.6

                vy = BASE_UP + 8.0 + UP_GAIN * (abs(vx) + abs(vz))
                vy = clamp_vy(vy)

                self.firework_generator.generate_firework_thread(
                    (float(px), 0.0, float(pz)),
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.nothing
                )

            time.sleep(SLEEP_BEAM)

        time.sleep(0.25)

        # =========================================================
        # 3) 第二段：门框边缘“扫描描线”（nothing）
        #    用少量扫线让门框轮廓更“完整更壮观”，但数量仍受控
        # =========================================================
        edge_points = [
            (-A, -B), (-A, 0.0), (-A,  B),
            ( 0.0, B), ( A,  B), ( A, 0.0), ( A, -B),
            ( 0.0, -B),
        ]

        for s in range(EDGE_SWEEPS):
            phase += 0.55
            for depth_sign in (-1.0, 1.0):  # 前后各扫一次
                z_layer = depth_sign * (Z_DEPTH * 0.5)
                for i, (x0, z0) in enumerate(edge_points):
                    px = x0
                    pz = z0 + z_layer

                    # 沿门框“切向滑行”的速度（描线感）
                    # 简化：用相位让描线方向随时间变换，避免机械感
                    vx = 10.0 * math.cos(phase + i * 0.6) + 6.0 * (x0 / max(1.0, A))
                    vz = 10.0 * math.sin(phase * 0.9 + i * 0.55) + 6.0 * (z0 / max(1.0, B))
                    vz += depth_sign * 6.0

                    vy = BASE_UP + 6.0 + 0.08 * (abs(vx) + abs(vz))
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(px), 0.0, float(pz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )
                time.sleep(SLEEP_EDGE)

        time.sleep(0.22)

        # =========================================================
        # 4) 第三段（高潮）：棱镜“闪断爆点”（爆炸）
        #    不是中心贯穿，而是“前后门框 + 边缘节点”同步闪断，超酷
        # =========================================================
        if sparkle:
            phase += 0.8
            # 选取爆点位置：从锚点与边缘点混合采样（数量受控）
            nodes = []
            for (x0, z0) in anchors_front[:4] + anchors_front[4:8]:
                nodes.append((x0, z0 - Z_DEPTH * 0.5))
                nodes.append((x0, z0 + Z_DEPTH * 0.5))
            # 加几处“对角折射点”
            nodes += [(-A, 0.0), (A, 0.0), (0.0, -B), (0.0, B)]
            # 映射到前后两层（形成 3D 爆闪）
            nodes = [(x, z - Z_DEPTH * 0.5) for (x, z) in nodes[:len(nodes)//2]] + [(x, z + Z_DEPTH * 0.5) for (x, z) in nodes[len(nodes)//2:]]

            # 控量：只取 FLASH_BURSTS 个
            total = len(nodes)
            step = max(1, total // FLASH_BURSTS)

            count = 0
            for idx in range(0, total, step):
                if count >= FLASH_BURSTS:
                    break
                count += 1

                px, pz = nodes[idx]

                # “闪断”速度：轻向内扣 + 轻旋，制造折射爆闪感（不做贯穿）
                ox, oz, _ = norm2(px, pz)
                tx, tz = -oz, ox

                vx = -SNAP * ox + 14.0 * tx + 4.0 * math.sin(phase + idx * 0.4)
                vz = -SNAP * oz + 14.0 * tz + 4.0 * math.cos(phase * 0.9 + idx * 0.35)

                vy = BASE_UP + 18.0 + 0.10 * (abs(vx) + abs(vz))
                vy = clamp_vy(vy)

                self.firework_generator.generate_firework_thread(
                    (float(px), 0.0, float(pz)),
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )

                time.sleep(SLEEP_FLASH)

        time.sleep(0.25)

        # =========================================================
        # 5) 第四段：余辉回卷（nothing，少量但很“高级”）
        # =========================================================
        phase += 0.7
        for k in range(FINISH_TRAILS):
            a = phase + k * 0.55
            # 在门框附近回卷，不回到中心，保持“空间门”主题
            px = (A * 0.6) * math.cos(a) + (6.0 if k % 2 == 0 else -6.0)
            pz = (B * 0.9) * math.sin(a * 0.9) + (Z_DEPTH * 0.5 if k % 3 == 0 else -Z_DEPTH * 0.5)

            vx = 12.0 * math.sin(a * 0.95)
            vz = 12.0 * math.cos(a * 0.85)
            vy = BASE_UP + 8.0 + 0.08 * (abs(vx) + abs(vz))
            vy = clamp_vy(vy)

            self.firework_generator.generate_firework_thread(
                (float(px), 0.0, float(pz)),
                (float(vx), float(vy), float(vz)),
                self.type_firework.nothing
            )

            time.sleep(SLEEP_FIN)


    def one_wave_nebula_lattice_overdrive(self):
        MIN_VY = 12.0

        # =========================
        # 规模参数（数量主要由这里决定）
        # =========================
        Z_LAYERS = 6               # 深度层数（5~8）
        GRID_N = 7                 # 每层网格边长（6~9）  -> 单层点数 = GRID_N^2
        SWEEPS = 4                 # 光轨织网轮数（3~6）

        EXPLOSION_WAVES = 3        # 爆闪波次数（2~4）
        EXPLOSIONS_PER_LAYER = 8   # 每层爆点数量（6~14）

        FINISH_TRAILS = 24         # 收尾光轨数量（16~36）

        # =========================
        # 节奏（更壮观可略减 sleep，但更吃性能）
        # =========================
        SLEEP_WEAVE = 0.05
        SLEEP_BLINK = 0.04
        SLEEP_FINISH = 0.03

        # =========================
        # 空间尺度（强 3D）
        # =========================
        SPAN_X = 58.0              # 网格总宽
        SPAN_Z = 44.0              # 深度跨度
        Z_GAP = SPAN_Z / max(1, (Z_LAYERS - 1))

        # =========================
        # 速度尺度（酷炫但可控）
        # =========================
        BASE_UP = 18.0
        UP_GAIN = 0.10

        FLOW_X = 18.0              # 网格流动
        FLOW_Z = 16.0
        RIPPLE = 9.0               # 波纹扰动（更炫）

        SNAP_IN = 16.0             # 爆闪时“向内扣”的感觉（不做中心贯穿）
        SWIRL = 18.0               # 爆闪时轻旋

        # ---------- 防御性 ----------
        Z_LAYERS = max(1, int(Z_LAYERS))
        GRID_N = max(1, int(GRID_N))
        SWEEPS = max(1, int(SWEEPS))
        EXPLOSION_WAVES = max(1, int(EXPLOSION_WAVES))
        EXPLOSIONS_PER_LAYER = max(1, int(EXPLOSIONS_PER_LAYER))
        FINISH_TRAILS = max(1, int(FINISH_TRAILS))

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def norm2(x, z):
            m = math.sqrt(x * x + z * z)
            if m < 1e-6:
                return 1.0, 0.0, 1.0
            return x / m, z / m, m

        # 生成每层网格点（x 方向均匀铺开；z 用层）
        # y 坐标始终 0，3D 体感靠 z 分层 + vz 推送
        xs = []
        if GRID_N == 1:
            xs = [0.0]
        else:
            for i in range(GRID_N):
                u = (i / (GRID_N - 1)) * 2.0 - 1.0
                xs.append(u * (SPAN_X * 0.5))

        # 网格“第二维”用 z 内部偏移（同层内再做小纵深，让体积更厚）
        zs_inner = []
        if GRID_N == 1:
            zs_inner = [0.0]
        else:
            for j in range(GRID_N):
                v = (j / (GRID_N - 1)) * 2.0 - 1.0
                zs_inner.append(v * (Z_GAP * 0.35))

        # =========================================================
        # 1) 织网：多层晶格光轨（nothing）
        # =========================================================
        phase = 0.0
        for s in range(SWEEPS):
            phase += 0.55

            for layer in range(Z_LAYERS):
                z_base = (layer - (Z_LAYERS - 1) / 2.0) * Z_GAP

                # 每层一个偏置，让层与层之间“错相流动”，避免重复
                layer_phase = phase + layer * 0.45
                layer_bias = (layer - (Z_LAYERS - 1) / 2.0) / max(1.0, (Z_LAYERS - 1) / 2.0)

                for i, x0 in enumerate(xs):
                    for j, z_in in enumerate(zs_inner):
                        px = x0
                        pz = z_base + z_in

                        # 网格流动：在局部(x,z)上叠加波动
                        vx = FLOW_X * (0.55 * math.sin(layer_phase + i * 0.55) + 0.25 * math.sin(layer_phase * 0.8 + j))
                        vz = FLOW_Z * (0.55 * math.cos(layer_phase * 0.9 + j * 0.55) + 0.25 * math.cos(layer_phase + i))

                        # 3D 推送：随层深度给一点偏移
                        vz += layer_bias * (FLOW_Z * 0.65)

                        # 加一点“晶格脉冲”扰动（更炫）
                        vx += RIPPLE * 0.22 * math.sin(layer_phase + (i - j) * 0.35)
                        vz += RIPPLE * 0.22 * math.cos(layer_phase * 0.9 + (i + j) * 0.28)

                        vy = BASE_UP + 7.0 + UP_GAIN * (abs(vx) + abs(vz))
                        vy = clamp_vy(vy)

                        self.firework_generator.generate_firework_thread(
                            (float(px), 0.0, float(pz)),
                            (float(vx), float(vy), float(vz)),
                            self.type_firework.nothing
                        )

            time.sleep(SLEEP_WEAVE)

        time.sleep(0.35)

        # =========================================================
        # 2) 爆闪：在晶格节点分层点亮（choose_random_type）
        #    不是中心贯穿，而是“多点同步闪断”
        # =========================================================
        for w in range(EXPLOSION_WAVES):
            phase += 0.75

            for layer in range(Z_LAYERS):
                z_base = (layer - (Z_LAYERS - 1) / 2.0) * Z_GAP
                layer_bias = (layer - (Z_LAYERS - 1) / 2.0) / max(1.0, (Z_LAYERS - 1) / 2.0)

                # 这一层挑若干个“节点”做爆点：用步进采样避免随机引入不稳定
                total_nodes = GRID_N * GRID_N
                step = max(1, total_nodes // EXPLOSIONS_PER_LAYER)

                idx = 0
                count = 0
                while count < EXPLOSIONS_PER_LAYER and idx < total_nodes:
                    i = idx // GRID_N
                    j = idx % GRID_N

                    px = xs[i]
                    pz = z_base + zs_inner[j]

                    # 爆闪速度：轻向内扣 + 轻旋 + 分层纵深
                    ox, oz, _ = norm2(px, pz)
                    tx, tz = -oz, ox

                    vx = (-SNAP_IN * ox) + (SWIRL * tx) + 4.0 * math.sin(phase + i * 0.7)
                    vz = (-SNAP_IN * oz) + (SWIRL * tz) + 4.0 * math.cos(phase * 0.9 + j * 0.7)
                    vz += layer_bias * 10.0

                    vy = BASE_UP + 20.0 + 0.10 * (abs(vx) + abs(vz))
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(px), 0.0, float(pz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.choose_random_type() if random.random() < 0.35 else self.type_firework.nothing
                    )

                    count += 1
                    idx += step

            time.sleep(SLEEP_BLINK)

        time.sleep(0.35)

        # =========================================================
        # 3) 收尾：余辉扫光（nothing）——长一点但不靠中心柱
        # =========================================================
        phase += 0.9
        for k in range(FINISH_TRAILS):
            a = phase + k * 0.33

            # 在空间中做“扫光曲线”：不回中心，沿外圈与纵深游走
            px = (SPAN_X * 0.42) * math.sin(a * 0.85) + 10.0 * math.sin(a * 0.22)
            pz = (SPAN_Z * 0.42) * math.cos(a * 0.75) + 8.0 * math.cos(a * 0.27)

            # 速度：轻旋与漂移
            vx = 14.0 * math.cos(a * 0.95)
            vz = 14.0 * math.sin(a * 0.88)

            vy = BASE_UP + 10.0 + 0.08 * (abs(vx) + abs(vz))
            vy = clamp_vy(vy)

            self.firework_generator.generate_firework_thread(
                (float(px), 0.0, float(pz)),
                (float(vx), float(vy), float(vz)),
                self.type_firework.nothing
            )

            time.sleep(SLEEP_FINISH)


    def one_wave_living_nebula_collapse(self):
        MIN_VY = 12.0

        # =========================
        # 规模（这一波真的多）
        # =========================
        VOLUME_LAYERS = 7          # z 轴体积层
        RINGS_PER_LAYER = 6        # 每层几个“星云环”
        POINTS_PER_RING = 12       # 每个环的点数

        BREATH_CYCLES = 3          # 星云“呼吸”轮数
        COLLAPSE_WAVES = 3         # 最终塌缩爆炸波数

        # =========================
        # 空间尺度
        # =========================
        BASE_RADIUS = 10.0
        RADIUS_STEP = 5.0
        Z_SPAN = 42.0

        # =========================
        # 速度尺度
        # =========================
        BASE_UP = 18.0
        UP_GAIN = 0.10

        FLOW = 14.0                # 星云流动
        SWIRL = 18.0               # 内部旋转
        NOISE = 6.0                # “活着”的扰动

        COLLAPSE_IN = 22.0         # 塌缩强度
        COLLAPSE_SWIRL = 24.0      # 塌缩旋转

        SLEEP_BUILD = 0.045
        SLEEP_BREATH = 0.06
        SLEEP_COLLAPSE = 0.04

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def norm2(x, z):
            m = math.sqrt(x * x + z * z)
            if m < 1e-6:
                return 1.0, 0.0, 1.0
            return x / m, z / m, m

        # ======================================================
        # 1) 星云生成：体积在空间中“生长”（nothing）
        # ======================================================
        phase = 0.0
        for layer in range(VOLUME_LAYERS):
            z_bias = (layer - (VOLUME_LAYERS - 1) / 2.0) / max(1.0, (VOLUME_LAYERS - 1) / 2.0)
            z0 = z_bias * (Z_SPAN * 0.5)

            for r in range(RINGS_PER_LAYER):
                radius = BASE_RADIUS + r * RADIUS_STEP
                phase += 0.25

                for i in range(POINTS_PER_RING):
                    theta = (2.0 * math.pi) * (i / POINTS_PER_RING) + phase

                    cx = math.cos(theta)
                    sz = math.sin(theta)

                    px = radius * cx
                    pz = radius * sz + z0

                    ox, oz, _ = norm2(px, pz)
                    tx, tz = -oz, ox

                    vx = FLOW * ox + SWIRL * tx + NOISE * math.sin(phase + i)
                    vz = FLOW * oz + SWIRL * tz + NOISE * math.cos(phase * 0.9 + i)
                    vz += z_bias * FLOW * 0.6

                    vy = BASE_UP + 6.0 + UP_GAIN * (abs(vx) + abs(vz))
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(px), 0.0, float(pz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

            time.sleep(SLEEP_BUILD)

        time.sleep(0.4)

        # ======================================================
        # 2) 星云呼吸：整个体积开始“抖动”（nothing）
        # ======================================================
        for b in range(BREATH_CYCLES):
            phase += 0.8

            for layer in range(VOLUME_LAYERS):
                z_bias = (layer - (VOLUME_LAYERS - 1) / 2.0) / max(1.0, (VOLUME_LAYERS - 1) / 2.0)
                z0 = z_bias * (Z_SPAN * 0.5)

                for r in range(RINGS_PER_LAYER):
                    radius = BASE_RADIUS + r * RADIUS_STEP

                    for i in range(POINTS_PER_RING):
                        theta = (2.0 * math.pi) * (i / POINTS_PER_RING) + phase

                        cx = math.cos(theta)
                        sz = math.sin(theta)

                        px = radius * cx
                        pz = radius * sz + z0

                        vx = 10.0 * math.sin(phase + r + i)
                        vz = 10.0 * math.cos(phase * 0.9 + r - i)
                        vy = clamp_vy(BASE_UP + 10.0)

                        self.firework_generator.generate_firework_thread(
                            (float(px), 0.0, float(pz)),
                            (float(vx), float(vy), float(vz)),
                            self.type_firework.nothing
                        )

            time.sleep(SLEEP_BREATH)

        time.sleep(0.35)

        # ======================================================
        # 3) 星云塌缩：整个体积同步爆炸（高潮）
        # ======================================================
        for wave in range(COLLAPSE_WAVES):
            phase += 1.0

            for layer in range(VOLUME_LAYERS):
                z_bias = (layer - (VOLUME_LAYERS - 1) / 2.0) / max(1.0, (VOLUME_LAYERS - 1) / 2.0)
                z0 = z_bias * (Z_SPAN * 0.5)

                for r in range(RINGS_PER_LAYER):
                    radius = BASE_RADIUS + r * RADIUS_STEP

                    for i in range(POINTS_PER_RING):
                        theta = (2.0 * math.pi) * (i / POINTS_PER_RING) + phase

                        cx = math.cos(theta)
                        sz = math.sin(theta)

                        px = radius * cx
                        pz = radius * sz + z0

                        ox, oz, _ = norm2(px, pz)
                        tx, tz = -oz, ox

                        vx = -COLLAPSE_IN * ox + COLLAPSE_SWIRL * tx
                        vz = -COLLAPSE_IN * oz + COLLAPSE_SWIRL * tz
                        vz += z_bias * COLLAPSE_IN * 0.8

                        vy = BASE_UP + 22.0 + 0.12 * (abs(vx) + abs(vz))
                        vy = clamp_vy(vy)

                        self.firework_generator.generate_firework_thread(
                            (float(px), 0.0, float(pz)),
                            (float(vx), float(vy), float(vz)),
                            self.type_firework.choose_random_type() if random.random() < 0.05 else self.type_firework.nothing
                        )

            time.sleep(SLEEP_COLLAPSE)

    def one_wave_skyfall_constellation_ruin(self):
        MIN_VY = 12.0

        # =========================
        # 规模参数
        # =========================
        CONSTELLATIONS = 5         # 星座数量
        STARS_PER_CONST = 12       # 每个星座的“星点”
        Z_LAYERS = 6               # 深度层
        DRAW_PASSES = 2            # 星座描绘轮数

        DISORDER_PASSES = 3        # 解体轮数
        COLLAPSE_WAVES = 3         # 天幕坠落爆炸波

        # =========================
        # 空间尺度
        # =========================
        SKY_RADIUS = 34.0
        CONST_RADIUS = 10.0
        Z_SPAN = 48.0

        # =========================
        # 速度尺度
        # =========================
        BASE_UP = 16.0
        UP_GAIN = 0.10

        DRAW_FLOW = 12.0           # 星座描绘流动
        ROTATE = 14.0              # 解体旋转
        DRIFT = 8.0                # 错位漂移

        FALL_PULL = 26.0           # 天幕塌缩强度
        FALL_SWIRL = 20.0          # 塌缩旋转

        SLEEP_DRAW = 0.06
        SLEEP_DISORDER = 0.07
        SLEEP_FALL = 0.045

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def norm2(x, z):
            m = math.sqrt(x * x + z * z)
            if m < 1e-6:
                return 1.0, 0.0, 1.0
            return x / m, z / m, m

        # ======================================================
        # 1) 星座描绘（nothing）——规则、优雅
        # ======================================================
        phase = 0.0
        for _ in range(DRAW_PASSES):
            phase += 0.5

            for c in range(CONSTELLATIONS):
                # 星座在天空圆周上均匀分布
                base_angle = (2.0 * math.pi) * (c / CONSTELLATIONS) + phase
                cx = SKY_RADIUS * math.cos(base_angle)
                cz = SKY_RADIUS * math.sin(base_angle)

                for layer in range(Z_LAYERS):
                    z_bias = (layer - (Z_LAYERS - 1) / 2.0) / max(1.0, (Z_LAYERS - 1) / 2.0)
                    z0 = z_bias * (Z_SPAN * 0.5)

                    for i in range(STARS_PER_CONST):
                        # 星座内部小圆弧
                        theta = (2.0 * math.pi) * (i / STARS_PER_CONST) + phase * 0.6

                        px = cx + CONST_RADIUS * math.cos(theta)
                        pz = cz + CONST_RADIUS * math.sin(theta) + z0

                        ox, oz, _ = norm2(px, pz)
                        vx = DRAW_FLOW * ox
                        vz = DRAW_FLOW * oz + z_bias * DRAW_FLOW * 0.6

                        vy = BASE_UP + 6.0 + UP_GAIN * (abs(vx) + abs(vz))
                        vy = clamp_vy(vy)

                        self.firework_generator.generate_firework_thread(
                            (float(px), 0.0, float(pz)),
                            (float(vx), float(vy), float(vz)),
                            self.type_firework.nothing
                        )

            time.sleep(SLEEP_DRAW)

        time.sleep(0.4)

        # ======================================================
        # 2) 星座失序（nothing）——旋转、错位、撕裂
        # ======================================================
        for d in range(DISORDER_PASSES):
            phase += 0.8

            for c in range(CONSTELLATIONS):
                base_angle = (2.0 * math.pi) * (c / CONSTELLATIONS) + phase

                cx = SKY_RADIUS * math.cos(base_angle)
                cz = SKY_RADIUS * math.sin(base_angle)

                for layer in range(Z_LAYERS):
                    z_bias = (layer - (Z_LAYERS - 1) / 2.0)
                    z0 = z_bias * (Z_SPAN * 0.5)

                    for i in range(STARS_PER_CONST):
                        theta = (2.0 * math.pi) * (i / STARS_PER_CONST)

                        px = cx + CONST_RADIUS * math.cos(theta)
                        pz = cz + CONST_RADIUS * math.sin(theta) + z0

                        ox, oz, _ = norm2(px, pz)
                        tx, tz = -oz, ox

                        vx = ROTATE * tx + DRIFT * math.sin(phase + i)
                        vz = ROTATE * tz + DRIFT * math.cos(phase + i)
                        vz += z_bias * DRIFT * 0.6

                        vy = BASE_UP + 10.0
                        vy = clamp_vy(vy)

                        self.firework_generator.generate_firework_thread(
                            (float(px), 0.0, float(pz)),
                            (float(vx), float(vy), float(vz)),
                            self.type_firework.nothing
                        )

            time.sleep(SLEEP_DISORDER)

        time.sleep(0.35)

        # ======================================================
        # 3) 天幕坠落（爆炸）——整片天空塌下来
        # ======================================================
        for wave in range(COLLAPSE_WAVES):
            phase += 1.0

            for c in range(CONSTELLATIONS):
                base_angle = (2.0 * math.pi) * (c / CONSTELLATIONS)

                cx = SKY_RADIUS * math.cos(base_angle)
                cz = SKY_RADIUS * math.sin(base_angle)

                for layer in range(Z_LAYERS):
                    z_bias = (layer - (Z_LAYERS - 1) / 2.0)
                    z0 = z_bias * (Z_SPAN * 0.5)

                    for i in range(STARS_PER_CONST):
                        theta = (2.0 * math.pi) * (i / STARS_PER_CONST)

                        px = cx + CONST_RADIUS * math.cos(theta)
                        pz = cz + CONST_RADIUS * math.sin(theta) + z0

                        ox, oz, _ = norm2(px, pz)
                        tx, tz = -oz, ox

                        # 向“天空中心面”塌缩 + 旋转
                        vx = -FALL_PULL * ox + FALL_SWIRL * tx
                        vz = -FALL_PULL * oz + FALL_SWIRL * tz
                        vz += z_bias * FALL_PULL * 0.8

                        vy = BASE_UP + 24.0 + 0.12 * (abs(vx) + abs(vz))
                        vy = clamp_vy(vy)

                        self.firework_generator.generate_firework_thread(
                            (float(px), 0.0, float(pz)),
                            (float(vx), float(vy), float(vz)),
                            self.type_firework.choose_random_type() if random.random() < 0.07 else self.type_firework.nothing
                        )

            time.sleep(SLEEP_FALL)


    def one_wave_temporal_shockwave_cascade(self):
        MIN_VY = 12.0

        # =========================
        # 时间参数（核心）
        # =========================
        TIME_SLICES = 14          # 时间切片数量
        PASSES = 4                # 每个切片重复扫描次数

        RADIUS = 42.0
        Z_SPAN = 36.0

        # =========================
        # 速度尺度
        # =========================
        BASE_UP = 18.0
        UP_GAIN = 0.10

        WAVE_SPEED = 22.0         # 时间波推进
        PHASE_SWIRL = 18.0        # 相位旋转
        JITTER = 6.0              # 时间抖动

        COLLAPSE_PULL = 26.0
        COLLAPSE_SWIRL = 22.0

        SLEEP_SCAN = 0.05
        SLEEP_RIFT = 0.06
        SLEEP_COLLAPSE = 0.045

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        # ======================================================
        # 1) 时间扫描：同一“时间波”反复扫过空间（nothing）
        # ======================================================
        phase = 0.0
        for _ in range(PASSES):
            for t in range(TIME_SLICES):
                phase += 0.35

                # 时间切片在 z 轴上的“位置”
                z_bias = (t / (TIME_SLICES - 1)) * 2.0 - 1.0
                z0 = z_bias * (Z_SPAN * 0.5)

                # 这一整个切片共享“时间方向”
                dir_angle = phase
                dx = math.cos(dir_angle)
                dz = math.sin(dir_angle)

                for i in range(10):  # 单个切片的空间采样（控量）
                    u = (i / 9.0) * 2.0 - 1.0

                    px = u * RADIUS
                    pz = z0

                    vx = WAVE_SPEED * dx + PHASE_SWIRL * (-dz)
                    vz = WAVE_SPEED * dz + PHASE_SWIRL * dx
                    vz += JITTER * math.sin(phase + u)

                    vy = BASE_UP + 6.0 + UP_GAIN * (abs(vx) + abs(vz))
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(px), 0.0, float(pz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

                time.sleep(SLEEP_SCAN)

        time.sleep(0.35)

        # ======================================================
        # 2) 时间撕裂：多个时间相位同时存在（nothing）
        # ======================================================
        for t in range(TIME_SLICES):
            phase += 0.6

            z_bias = (t / (TIME_SLICES - 1)) * 2.0 - 1.0
            z0 = z_bias * (Z_SPAN * 0.5)

            for k in range(3):  # 同一时间点的不同相位
                angle = phase + k * 2.1
                dx = math.cos(angle)
                dz = math.sin(angle)

                for i in range(8):
                    u = (i / 7.0) * 2.0 - 1.0

                    px = u * RADIUS * 0.8
                    pz = z0

                    vx = (WAVE_SPEED * 0.8) * dx + PHASE_SWIRL * (-dz)
                    vz = (WAVE_SPEED * 0.8) * dz + PHASE_SWIRL * dx
                    vz += z_bias * 8.0

                    vy = BASE_UP + 10.0
                    vy = clamp_vy(vy)

                    self.firework_generator.generate_firework_thread(
                        (float(px), 0.0, float(pz)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

            time.sleep(SLEEP_RIFT)

        time.sleep(0.3)

        # ======================================================
        # 3) 时间坍缩：多个“时间点”同时爆炸
        # ======================================================
        for t in range(TIME_SLICES):
            phase += 0.8

            z_bias = (t / (TIME_SLICES - 1)) * 2.0 - 1.0
            z0 = z_bias * (Z_SPAN * 0.5)

            for i in range(10):
                angle = (2.0 * math.pi) * (i / 10.0) + phase
                cx = math.cos(angle)
                sz = math.sin(angle)

                px = cx * (RADIUS * 0.6)
                pz = z0 + sz * 6.0

                vx = -COLLAPSE_PULL * cx + COLLAPSE_SWIRL * (-sz)
                vz = -COLLAPSE_PULL * sz + COLLAPSE_SWIRL * cx
                vz += z_bias * COLLAPSE_PULL * 0.6

                vy = BASE_UP + 26.0 + 0.12 * (abs(vx) + abs(vz))
                vy = clamp_vy(vy)

                self.firework_generator.generate_firework_thread(
                    (float(px), 0.0, float(pz)),
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type() if random.random() < 0.85 else self.type_firework.nothing
                )

            time.sleep(SLEEP_COLLAPSE)


    def one_wave_big8_thick_build(self):
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        # =========================
        # 1) 铺垫：3D 光轨“天幕” (nothing) —— 数量多但便宜
        #    目标：让天空先“满起来”，但不爆炸、不抢主线程
        # =========================
        # 总量约：4 层 * 18 点 = 72 发 nothing
        layers = 4
        pts = 18
        R = 26.0
        Z_SPAN = 28.0

        phase = 0.0
        for layer in range(layers):
            z_bias = (layer - (layers - 1) / 2.0) / max(1.0, (layers - 1) / 2.0)
            z0 = z_bias * (Z_SPAN * 0.5)
            phase += 0.55

            for i in range(pts):
                theta = (2.0 * math.pi) * (i / pts) + phase
                cx = math.cos(theta)
                sz = math.sin(theta)

                # 环形发射位置 + 深度分层（强 3D）
                px = R * cx
                pz = R * sz + z0

                # 温柔旋流光轨：不追求爆裂，只做“铺天幕”
                vx = 14.0 * (-sz) + 5.0 * cx
                vz = 14.0 * ( cx) + 5.0 * sz + z_bias * 8.0
                vy = clamp_vy(18.0 + 0.08 * (abs(vx) + abs(vz)))

                self.firework_generator.generate_firework_thread(
                    (float(px), 0.0, float(pz)),
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.nothing
                )

                time.sleep(0.04)  # 让它“连续铺开”，但不过载

            time.sleep(0.18)

        # 给观众“吸气”，也给系统回收一点
        time.sleep(0.7)

        # =========================
        # 2) 引爆：两段式“外圈爆闪” (爆炸) —— 数量明显增多但分段释放
        #    目标：把注意力抬上去、把气氛推到高潮门口
        # =========================
        # 第一段：外圈 12 发
        burst_pts_1 = 12
        burst_R1 = 30.0
        for i in range(burst_pts_1):
            theta = (2.0 * math.pi) * (i / burst_pts_1) + 0.3
            cx = math.cos(theta)
            sz = math.sin(theta)

            px = burst_R1 * cx
            pz = burst_R1 * sz

            # 轻微向外 + 上扬（别太快，避免粒子叠太猛）
            vx = 8.0 * cx
            vz = 8.0 * sz
            vy = clamp_vy(30.0)

            self.firework_generator.generate_firework_thread(
                (float(px), 0.0, float(pz)),
                (float(vx), float(vy), float(vz)),
                self.type_firework.choose_random_type()
            )

            time.sleep(0.10)

        time.sleep(0.35)

        # 第二段：错相外圈 16 发（更密一点，形成“爆闪环”）
        burst_pts_2 = 16
        burst_R2 = 24.0
        for i in range(burst_pts_2):
            theta = (2.0 * math.pi) * (i / burst_pts_2) + 0.3 + (math.pi / burst_pts_2)
            cx = math.cos(theta)
            sz = math.sin(theta)

            px = burst_R2 * cx
            pz = burst_R2 * sz + 8.0 * math.sin(theta * 0.7)  # 深度起伏，更 3D

            vx = 10.0 * (-sz)  # 让它稍微“绕一下”
            vz = 10.0 * ( cx)
            vy = clamp_vy(32.0)

            self.firework_generator.generate_firework_thread(
                (float(px), 0.0, float(pz)),
                (float(vx), float(vy), float(vz)),
                self.type_firework.choose_random_type()
            )

            time.sleep(0.08)

        # =========================
        # 3) 八尺玉前：强制清场缓冲（关键！）
        #    给线程/粒子/资源足够时间释放，否则你说的“放两个会卡死”会被放大
        # =========================
        time.sleep(1.6)

        # =========================
        # 4) 八尺玉：只放一个（王炸）
        # =========================
        self.firework_generator.generate_firework_thread(
            (0.0, 0.0, 0.0),
            (0.0, 44.0, 0.0),
            self.type_firework.extrimely_big_fire_3
        )

        # 八尺玉生命周期期间绝对不放别的
        time.sleep(3.2)

        # =========================
        # 5) 余韵：少量 nothing（不爆炸，避免压垮系统）
        # =========================
        for i in range(16):
            theta = (2.0 * math.pi) * (i / 16.0)
            px = 14.0 * math.cos(theta)
            pz = 14.0 * math.sin(theta)

            vx = 5.0 * math.cos(theta)
            vz = 5.0 * math.sin(theta)
            vy = clamp_vy(18.0)

            self.firework_generator.generate_firework_thread(
                (float(px), 0.0, float(pz)),
                (float(vx), float(vy), float(vz)),
                self.type_firework.nothing
            )
            time.sleep(0.06)

    def one_wave_searchlight_lightning_big2(self):
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        # =========================
        # 1) 三维交叉探照灯（nothing）
        # 风格：像两组探照灯在空中交错扫描（强 3D、很“舞台”）
        # 数量：中等偏多，但都是 nothing，比较省
        # =========================
        sweeps = 6
        beams_per_sweep = 10

        left_emitters = [(-26.0, -18.0), (-26.0, 0.0), (-26.0, 18.0)]   # (x, z)
        right_emitters = [(26.0, -18.0), (26.0, 0.0), (26.0, 18.0)]

        phase = 0.0
        for s in range(sweeps):
            phase += 0.55

            # 扫描角（在 x-z 平面扇动），并让左右方向相反形成交叉
            scan = math.sin(phase)  # [-1, 1]
            scan2 = math.cos(phase * 0.9)

            for i in range(beams_per_sweep):
                t = (i / max(1, beams_per_sweep - 1)) * 2.0 - 1.0  # [-1, 1]

                # 左侧探照灯：向右上方扫，z 随时间漂移
                for (ex, ez) in left_emitters:
                    vx = 18.0 + 10.0 * scan + 6.0 * t
                    vz = 12.0 * scan2 + 8.0 * t + (ez * 0.08)
                    vy = clamp_vy(18.0 + 0.10 * (abs(vx) + abs(vz)))

                    self.firework_generator.generate_firework_thread(
                        (float(ex), 0.0, float(ez)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

                # 右侧探照灯：向左上方扫，方向相反，形成 X 形交叉
                for (ex, ez) in right_emitters:
                    vx = -18.0 - 10.0 * scan - 6.0 * t
                    vz = -12.0 * scan2 - 8.0 * t + (ez * 0.08)
                    vy = clamp_vy(18.0 + 0.10 * (abs(vx) + abs(vz)))

                    self.firework_generator.generate_firework_thread(
                        (float(ex), 0.0, float(ez)),
                        (float(vx), float(vy), float(vz)),
                        self.type_firework.nothing
                    )

                time.sleep(0.04)

            time.sleep(0.18)

        # 给观众和系统一个“收紧”的空拍
        time.sleep(0.9)

        # =========================
        # 2) 闪电断奏（爆炸）
        # 风格：不是环、不是中心柱，而是“斜向闪电切割线”
        # 数量：不算少，但分拍释放，观感强且不容易同帧爆炸过多
        # =========================
        cuts = 3
        points_per_cut = 10

        for c in range(cuts):
            # 每次闪电线换一个空间方向，体现 3D
            # 斜线从左前 → 右后，再从右前 → 左后
            dir_sign = -1.0 if (c % 2 == 0) else 1.0

            for i in range(points_per_cut):
                u = (i / max(1, points_per_cut - 1)) * 2.0 - 1.0  # [-1,1]

                px = u * 28.0
                pz = dir_sign * (u * 20.0)  # 斜向穿透空间（z 轴很明显）

                # 爆炸速度：轻微“切向”横掠 + 上扬，不做贯穿
                vx = 10.0 * dir_sign + 6.0 * math.sin(0.9 * i + c)
                vz = -10.0 * dir_sign + 6.0 * math.cos(0.8 * i + c)
                vy = clamp_vy(30.0 + 0.08 * (abs(vx) + abs(vz)))

                self.firework_generator.generate_firework_thread(
                    (float(px), 0.0, float(pz)),
                    (float(vx), float(vy), float(vz)),
                    self.type_firework.choose_random_type()
                )

                time.sleep(0.06)

            # 每条闪电线之间留空拍，让爆炸“断奏”更帅，也给性能缓冲
            time.sleep(0.45)

        # =========================
        # 3) 八尺玉前清场缓冲（非常关键）
        # =========================
        time.sleep(1.8)

        # =========================
        # 4) 八尺玉压轴：extremely_big_fire_2（严格只放一个）
        # 按你指定格式写
        # =========================
        self.firework_generator.generate_firework_thread(
            (0.0, 0.0, 0.0),
            (0.0, 44.0, 0.0),
            self.type_firework.extrimely_big_fire_4
        )

        # 八尺玉生命周期期间不要放别的
        time.sleep(3.4)

        # =========================
        # 5) 余辉（nothing）：少量，避免压垮系统
        # 风格：从两侧“回光”收束，不是中心柱
        # =========================
        for i in range(18):
            u = (i / 17.0) * 2.0 - 1.0
            px = u * 18.0
            pz = 14.0 * math.sin(i * 0.35)

            vx = -4.0 * u
            vz = -6.0 * math.cos(i * 0.3)
            vy = clamp_vy(18.0)

            self.firework_generator.generate_firework_thread(
                (float(px), 0.0, float(pz)),
                (float(vx), float(vy), float(vz)),
                self.type_firework.nothing
            )

            time.sleep(0.06)

    def climax_30s_continuous(self):
        # ========= 总强度开关（担心卡就降到 0.7 / 0.5）=========
        INTENSITY = 0.5

        MIN_VY = 12.0

        def clamp_vy(vy: float) -> float:
            return float(vy if vy > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype):
            # pos: (x,y,z)  vel: (vx,vy,vz)
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype
            )

        # ========= 时间轴控制（30 秒，严格按节拍跑，保证连贯）=========
        DURATION = 30.0
        dt = 0.08  # 节拍间隔：越小越密越壮观，也更吃性能
        start = time.time()
        beat = 0

        # ========= 常用类型（你给的列表）=========
        T = self.type_firework
        burst_A = [T.circle, T.random_color, T.planet_random_color, T.ball, T.double_ball]
        burst_B = [T.planet_ball, T.mixed_color_ball, T.half_half_color_ball, T.double_ball, T.ball_up]
        burst_C = [T.flower,  T.mixed_color_ball, T.random_color, T.circle]

        # ========= 主循环：一直高潮 =========
        while True:
            now = time.time()
            t = now - start
            if t >= DURATION:
                break

            # ---- 选择阶段：0-10 / 10-20 / 20-30 ----
            if t < 10.0:
                phase = 0
            elif t < 20.0:
                phase = 1
            else:
                phase = 2

            # ---- 基础“能量光轨流”（nothing）：全程不断，负责连贯和舞台感 ----
            # 4 组环形喷口 + 多深度层，让整个空间一直“活着”
            base_R = (22.0 + 4.0 * math.sin(t * 0.9)) * (0.9 + 0.2 * INTENSITY)
            swirl = (18.0 + 6.0 * math.sin(t * 1.2)) * INTENSITY
            out = (10.0 + 4.0 * math.cos(t * 1.1)) * INTENSITY

            for k in range(4):
                ang = (t * 1.6) + k * (math.pi / 2.0)
                cx = math.cos(ang)
                sz = math.sin(ang)

                # 分层深度：让 3D 明显
                z_layer = (8.0 if (k % 2 == 0) else -8.0) + 6.0 * math.sin(t * 0.7 + k)

                px = base_R * cx
                pz = base_R * sz + z_layer

                # outward + tangential（绕 y 轴）形成“能量流”
                vx = out * cx + (-swirl * sz)
                vz = out * sz + ( swirl * cx)

                # 向上：温柔但持续，确保 vy>0
                vy = clamp_vy((18.0 + 0.10 * (abs(vx) + abs(vz))) * (0.9 + 0.2 * INTENSITY))

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing)

            # ---- “重拍爆炸”：每隔若干拍打一组结构化爆炸（保证壮观但有秩序）----
            # 让高潮“有音乐性”，不是乱刷
            if beat % int(max(1, round(10 / max(0.5, INTENSITY)))) == 0:
                # 爆炸环：8 个点，分两层深度
                N = 8
                Rb = 30.0 + 6.0 * math.sin(t * 0.8)
                zA = 14.0
                zB = -14.0

                if phase == 0:
                    ftype = burst_A[(beat // 10) % len(burst_A)]
                    vy0 = 30.0
                elif phase == 1:
                    ftype = burst_B[(beat // 10) % len(burst_B)]
                    vy0 = 32.0
                else:
                    ftype = burst_C[(beat // 10) % len(burst_C)]
                    vy0 = 34.0

                for i in range(N):
                    th = (2.0 * math.pi) * (i / N) + t * 0.6
                    cx = math.cos(th)
                    sz = math.sin(th)

                    # 两层深度交替
                    z_layer = (zA if (i % 2 == 0) else zB)

                    px = Rb * cx
                    pz = Rb * sz + z_layer

                    # 速度做成“轻外扩 + 轻旋”，不走中心贯穿
                    vx = 10.0 * cx + 8.0 * (-sz)
                    vz = 10.0 * sz + 8.0 * ( cx)
                    vy = clamp_vy(vy0 + 0.08 * (abs(vx) + abs(vz)))

                    fire((px, 0.0, pz), (vx, vy, vz), ftype)

            # ---- “持续补火”：保证一直高潮（每拍少量补爆炸）----
            # 数量控制：每拍 2 个补爆，最后 3 秒加密
            extra = 2
            if t > 27.0:
                extra = 5  # 压轴风暴更密更壮观
            extra = int(round(extra * INTENSITY))

            for j in range(extra):
                a = t * 1.9 + j * 1.3
                px = (14.0 + 10.0 * math.sin(t * 0.6)) * math.cos(a)
                pz = (14.0 + 10.0 * math.sin(t * 0.6)) * math.sin(a) + 10.0 * math.sin(a * 0.7)

                # 阶段风格切换（连贯但明显递进）
                if phase == 0:
                    ftype = T.random_color if (j % 2 == 0) else T.circle
                    vy0 = 28.0
                elif phase == 1:
                    ftype = T.planet_ball if (j % 2 == 0) else T.mixed_color_ball
                    vy0 = 30.0
                else:
                    # 最后 10 秒：花/爱心穿插，让“漂亮 + 爆”
                    if (beat // 8) % 3 == 0:
                        ftype = T.random_color
                    elif (beat // 8) % 3 == 1:
                        ftype = T.circle
                    else:
                        ftype = T.half_half_color_ball
                    vy0 = 32.0

                vx = 8.0 * math.sin(a) + 6.0 * math.cos(t * 0.9)
                vz = 8.0 * math.cos(a) + 6.0 * math.sin(t * 0.8)
                vy = clamp_vy(vy0 + 0.08 * (abs(vx) + abs(vz)))

                fire((px, 0.0, pz), (vx, vy, vz), ftype)

            # ---- 压轴 3 秒：纯风暴（仍不走中心贯穿），爆炸类型更“炸” ----
            if t > 27.0:
                stormN = int(round(4 * INTENSITY))
                for i in range(stormN):
                    th = t * 2.4 + i * (2.0 * math.pi / max(1, stormN))
                    px = 34.0 * math.cos(th)
                    pz = 34.0 * math.sin(th) + 18.0 * math.sin(th * 0.6)

                    # 压轴尽量用视觉冲击强的球/颜色
                    ftype = [T.double_ball, T.mixed_color_ball, T.planet_random_color, T.random_color][i % 4]

                    vx = 14.0 * (-math.sin(th))
                    vz = 14.0 * ( math.cos(th))
                    vy = clamp_vy(36.0 + 0.10 * (abs(vx) + abs(vz)))

                    fire((px, 0.0, pz), (vx, vy, vz), ftype)

            # ---- 节拍 sleep：保证总时长接近 30 秒且连贯 ----
            beat += 1
            next_time = start + beat * dt
            sleep_t = next_time - time.time()
            if sleep_t > 0:
                time.sleep(sleep_t)

    def climax_60s_with_nye_text(self):
        # ===== 总强度：担心卡就降到 0.7 / 0.5；想更猛可到 1.2 =====
        NYE=generate_func_type(self.type_firework.happy_birthday,self.type_firework.new_year)
        This_year=generate_func_type(self.type_firework.happy_birthday,self.type_firework.this_year)
        INTENSITY = 0.2

        MIN_VY = 12.0

        def clamp_vy(vy):
            return float(vy if vy > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype
            )

        T = self.type_firework

        # ===== 你给的可用类型池（按阶段取用，保证连贯但不断升级）=====
        POOL_WARM = [T.circle, T.random_color, T.ball, T.planet_random_color]
        POOL_THICK = [T.double_ball, T.planet_ball, T.mixed_color_ball, T.half_half_color_ball, T.ball_up]
        POOL_PRETTY = [T.flower, T.love_3D, T.double_love_2D, T.love_2D, T.love_2D_odd]
        POOL_HARD = [T.double_ball, T.mixed_color_ball, T.planet_random_color, T.random_color]

        # ===== 60 秒时间轴 =====
        DURATION = 60.0
        dt = 0.07  # 越小越密越壮观，也越吃性能
        start = time.time()
        beat = 0

        # ===== NYE 只放一次：放在 30s（中段最明显）=====
        NYE_TIME = 30.0
        This_year_TIME = 32.0
        nye_fired = False
        this_year_fired = False

        # ========= 主循环：全程高潮 =========
        while True:
            now = time.time()
            t = now - start
            if t >= DURATION:
                break

            # ----------- 分段（持续升级，但不换风格突兀）-----------
            # 0-20: 厚铺能量 + 彩球
            # 20-28: 更密更炸，为 NYE 做“冲门”
            # 28-33: NYE 舞台框架 + NYE 一次（爆炸让位但不断）
            # 33-55: 最漂亮最壮观段（花/爱心/行星混合）
            # 55-60: 终局风暴（硬核球类冲顶）
            if t < 20.0:
                stage = 0
            elif t < 28.0:
                stage = 1
            elif t < 33.0:
                stage = 2
            elif t < 55.0:
                stage = 3
            else:
                stage = 4

            # ----------- 全程“能量光轨地毯”（nothing）：连贯的关键 -----------
            # 8 个喷口（分前后层），持续输出，形成舞台能量流
            base_R = 22.0 + 6.0 * math.sin(t * 0.8)
            swirl = (20.0 + 10.0 * math.sin(t * 1.1)) * INTENSITY
            out = (10.0 + 5.0 * math.cos(t * 1.0)) * INTENSITY

            emitters = 8
            for k in range(emitters):
                ang = t * 1.7 + k * (2.0 * math.pi / emitters)
                cx = math.cos(ang)
                sz = math.sin(ang)

                z_layer = (10.0 if (k % 2 == 0) else -10.0) + 5.0 * math.sin(t * 0.65 + k)

                px = base_R * cx
                pz = base_R * sz + z_layer

                vx = out * cx + (-swirl * sz)
                vz = out * sz + ( swirl * cx)

                vy = clamp_vy(18.0 + 0.10 * (abs(vx) + abs(vz)))
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing)

            # ----------- “重拍环爆”：保证壮观但有秩序 -----------
            # stage 2（NYE舞台）会降低爆炸密度，避免遮住文字
            if stage == 2:
                heavy_every = int(max(10, round(18 / max(0.5, INTENSITY))))
            else:
                heavy_every = int(max(6, round(10 / max(0.5, INTENSITY))))

            if beat % heavy_every == 0:
                N = 10 if stage in (1, 3, 4) else 8
                Rb = 30.0 + 8.0 * math.sin(t * 0.7)
                zA, zB = 16.0, -16.0

                if stage == 0:
                    ftype = POOL_WARM[(beat // heavy_every) % len(POOL_WARM)]
                    vy0 = 30.0
                elif stage == 1:
                    ftype = POOL_THICK[(beat // heavy_every) % len(POOL_THICK)]
                    vy0 = 32.0
                elif stage == 2:
                    # NYE 附近尽量用“干净好辨识”的类型
                    ftype = T.circle if (beat // heavy_every) % 2 == 0 else T.random_color
                    vy0 = 30.0
                elif stage == 3:
                    # 漂亮高潮：花 + 爱心 + 行星混合
                    ftype = POOL_PRETTY[(beat // heavy_every) % len(POOL_PRETTY)]
                    vy0 = 33.0
                else:
                    ftype = POOL_HARD[(beat // heavy_every) % len(POOL_HARD)]
                    vy0 = 35.0

                for i in range(N):
                    th = (2.0 * math.pi) * (i / N) + t * 0.55
                    cx = math.cos(th)
                    sz = math.sin(th)
                    z_layer = (zA if (i % 2 == 0) else zB)

                    px = Rb * cx
                    pz = Rb * sz + z_layer

                    vx = 10.0 * cx + 8.0 * (-sz)
                    vz = 10.0 * sz + 8.0 * ( cx)
                    vy = clamp_vy(vy0 + 0.08 * (abs(vx) + abs(vz)))

                    fire((px, 0.0, pz), (vx, vy, vz), ftype)

            # ----------- 持续补火：全程高潮不断 -----------
            # NYE舞台阶段减少补火，其他时间非常密
            if stage == 2:
                extra = int(round(2 * INTENSITY))
            elif stage in (0, 1):
                extra = int(round(4 * INTENSITY))
            elif stage == 3:
                extra = int(round(5 * INTENSITY))
            else:
                extra = int(round(6 * INTENSITY))

            extra = max(1, extra)

            for j in range(extra):
                a = t * 2.0 + j * 1.25
                px = (16.0 + 12.0 * math.sin(t * 0.5)) * math.cos(a)
                pz = (16.0 + 12.0 * math.sin(t * 0.5)) * math.sin(a) + 12.0 * math.sin(a * 0.65)

                if stage == 0:
                    ftype = T.random_color if (j % 2 == 0) else T.ball
                    vy0 = 28.0
                elif stage == 1:
                    ftype = T.planet_random_color if (j % 2 == 0) else T.double_ball
                    vy0 = 30.0
                elif stage == 2:
                    ftype = T.circle
                    vy0 = 28.0
                elif stage == 3:
                    # 漂亮高潮：花/爱心穿插 + 球类撑场
                    pick = (beat // 7 + j) % 6
                    if pick == 0:
                        ftype = T.flower
                    elif pick == 1:
                        ftype = T.love_3D
                    elif pick == 2:
                        ftype = T.double_love_2D
                    elif pick == 3:
                        ftype = T.planet_ball
                    elif pick == 4:
                        ftype = T.mixed_color_ball
                    else:
                        ftype = T.half_half_color_ball
                    vy0 = 32.0
                else:
                    ftype = POOL_HARD[(j + beat) % len(POOL_HARD)]
                    vy0 = 34.0

                vx = 9.0 * math.sin(a) + 6.0 * math.cos(t * 0.8)
                vz = 9.0 * math.cos(a) + 6.0 * math.sin(t * 0.85)
                vy = clamp_vy(vy0 + 0.08 * (abs(vx) + abs(vz)))

                fire((px, 0.0, pz), (vx, vy, vz),  T.random_color)

            # ----------- NYE 舞台框架：让文字更好看（用 nothing 做“聚光框”）-----------
            # 在 28~33 秒期间，给一个“框架/底座光轨”，让 NYE 更像被舞台托起
            if 28.0 <= t <= 33.0:
                frameN = int(round(8 * INTENSITY))
                frameN = max(6, frameN)
                Rf = 26.0
                for i in range(frameN):
                    th = (2.0 * math.pi) * (i / frameN) + t * 0.9
                    px = Rf * math.cos(th)
                    pz = Rf * math.sin(th) + (10.0 if i % 2 == 0 else -10.0)

                    vx = 12.0 * (-math.sin(th))
                    vz = 12.0 * ( math.cos(th))
                    vy = clamp_vy(20.0)

                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing)

            # ----------- NYE 字体烟花：只放一次（你指定格式）-----------
            if (not nye_fired) and (t >= NYE_TIME):
                # 给它一个很干净的发射：正中、纯向上、让观众看清楚
                self.firework_generator.generate_firework_thread(
                    (0, 0, 0),
                    (0, 30, 0),
                    NYE
                )
                nye_fired = True
            if (not this_year_fired) and (t >= This_year_TIME):
                self.firework_generator.generate_firework_thread(
                    (0, 0, 0),
                    (0, 30, 0),
                    This_year
                )
                this_year_fired = True

            # ----------- 终局 55~60：风暴加压（仍不做中心贯穿）-----------
            if stage == 4:
                stormN = int(round(8 * INTENSITY))
                stormN = max(10, stormN)
                for i in range(stormN):
                    th = t * 2.6 + i * (2.0 * math.pi / stormN)
                    px = 36.0 * math.cos(th)
                    pz = 36.0 * math.sin(th) + 16.0 * math.sin(th * 0.55)

                    ftype = POOL_HARD[i % len(POOL_HARD)]

                    vx = 16.0 * (-math.sin(th))
                    vz = 16.0 * ( math.cos(th))
                    vy = clamp_vy(36.0 + 0.10 * (abs(vx) + abs(vz)))

                    fire((px, 0.0, pz), (vx, vy, vz), T.random_color if random.random()<0.1 else T.nothing)

            # ----------- 精准节拍 sleep：保证总时长接近 60 秒且连贯 -----------
            beat += 1
            next_time = start + beat * dt
            sleep_t = next_time - time.time()
            if sleep_t > 0:
                time.sleep(sleep_t)

    def transition_cushion(self, seconds=4.0, intensity=0.5, hint=True):
        """
        seconds: 过渡时长（建议 2.5~6）
        intensity: 强度（0.4~1.2），想更省就降
        hint: 是否在尾部加少量提示爆炸（不想炸就 False）
        """
        MIN_VY = 12.0
        T = self.type_firework

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype
            )

        # 过渡节拍（越大越省）
        dt = 0.08
        start = time.time()
        beat = 0

        # 两条“极光丝带”：左右对称 + 前后分层（强 3D）
        # 关键：随进度逐步“降密度 + 降速度”，让系统回收、观众也感到缓冲
        while True:
            t = time.time() - start
            if t >= seconds:
                break

            p = t / max(0.001, seconds)  # 0..1
            beat += 1

            # 密度：前半更密，后半逐渐稀疏（性能缓冲的核心）
            # 每个 tick 发射条数（控制在一个可预测范围）
            base_emit = int(round((6 - 3 * p) * intensity))
            base_emit = 2 if base_emit < 2 else base_emit

            # 速度随进度变“柔”，减少粒子与碰撞压力
            swirl = (18.0 - 6.0 * p) * intensity
            out = (10.0 - 4.0 * p) * intensity
            up_base = 18.0 - 3.0 * p

            # 半径也轻微收束，形成“舞台收光”感
            R = 22.0 - 6.0 * p

            # 两条丝带（左右），并带前后景 z 分层
            for k in range(base_emit):
                a = (t * 1.8) + k * (2.0 * math.pi / base_emit)

                # 左带
                cx = math.cos(a)
                sz = math.sin(a)
                px = -6.0 + R * cx
                pz = (R * sz) + (10.0 if (k % 2 == 0) else -10.0) + 3.0 * math.sin(t * 0.7)

                vx = out * cx + (-swirl * sz)
                vz = out * sz + ( swirl * cx)
                vy = clamp_vy(up_base + 0.08 * (abs(vx) + abs(vz)))

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing)

                # 右带（反相，制造“交织”而不是重复）
                px2 = 6.0 - R * cx
                pz2 = (-R * sz) + (-10.0 if (k % 2 == 0) else 10.0) + 3.0 * math.cos(t * 0.65)

                vx2 = -out * cx + (swirl * sz)
                vz2 = -out * sz + (-swirl * cx)
                vy2 = clamp_vy(up_base + 0.08 * (abs(vx2) + abs(vz2)))

                fire((px2, 0.0, pz2), (vx2, vy2, vz2), T.nothing)

            # 让过渡“有呼吸”：每隔几拍加一圈轻微“扫光”
            if beat % int(max(6, round(10 / max(0.4, intensity)))) == 0:
                N = 8
                R2 = 26.0 - 8.0 * p
                for i in range(N):
                    th = (2.0 * math.pi) * (i / N) + t * 0.9
                    px = R2 * math.cos(th)
                    pz = R2 * math.sin(th) + (8.0 if i % 2 == 0 else -8.0)

                    vx = 10.0 * (-math.sin(th))
                    vz = 10.0 * ( math.cos(th))
                    vy = clamp_vy(18.0)

                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing)

            # 精准 sleep
            next_time = start + beat * dt
            sleep_t = next_time - time.time()
            if sleep_t > 0:
                time.sleep(sleep_t)

        # 尾部提示：给下一波一个“起拍点”（极少量爆炸，避免抢戏）
        if hint:
            hint_types = [T.circle, T.random_color]
            for i in range(int(round(2 * max(0.6, intensity)))):
                ang = i * math.pi
                px = 18.0 * math.cos(ang)
                pz = 18.0 * math.sin(ang)

                vx = 6.0 * math.cos(ang)
                vz = 6.0 * math.sin(ang)
                vy = clamp_vy(26.0)

                fire((px, 0.0, pz), (vx, vy, vz), hint_types[i % len(hint_types)])
                time.sleep(0.12)
    def transition_sky_calligraphy(self, seconds=5.0, intensity=0.5, stamp=True):
        """
        独一无二过渡：天幕书法笔触（nothing）+ 落款印章（可选，小爆）
        seconds: 过渡时长（建议 4~7）
        intensity: 0.4~1.2  强度/密度
        stamp: 是否最后落款（建议 True）
        """
        MIN_VY = 12.0
        T = self.type_firework

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype
            )

        # 节拍：越大越省性能
        dt = 0.075
        start = time.time()
        beat = 0

        # 笔触尺度（空间形态是“书法一笔”，不是几何图案）
        # u 从 0 -> 1，画出一条“符箓式”的三维笔画轨迹（x,z 随 u 变）
        def stroke_pos(u):
            # 一个“书法笔画”路径：先提笔、再按下、再收锋（通过幅度变化体现）
            # 这里的形状刻意非对称、非周期化，看起来不像在绕圈
            # scale 做“笔锋粗细”变化：前中段更强，尾部收束
            scale = (0.35 + 0.85 * math.sin(math.pi * u))  # 0.35~1.2

            x = 34.0 * scale * math.sin(1.15 * math.pi * u + 0.25) + 6.0 * math.sin(4.2 * math.pi * u)
            z = 22.0 * scale * math.sin(2.05 * math.pi * u + 1.10) - 7.0 * math.sin(3.1 * math.pi * u + 0.4)

            # 轻微前后“压纸感”：让 z 有一点不规则起伏
            z += 3.0 * math.cos(1.7 * math.pi * u)

            return x, z

        # 用数值微分求切线方向（书法笔触的“走向”）
        eps = 1e-3
        def stroke_tangent(u):
            u1 = max(0.0, min(1.0, u + eps))
            u0 = max(0.0, min(1.0, u - eps))
            x1, z1 = stroke_pos(u1)
            x0, z0 = stroke_pos(u0)
            dx = x1 - x0
            dz = z1 - z0
            m = math.sqrt(dx*dx + dz*dz) + 1e-6
            return dx / m, dz / m

        # 主循环：沿笔触路径移动“发射点”，发射 nothing，形成“写字”的连续光轨
        while True:
            t = time.time() - start
            if t >= seconds:
                break

            beat += 1
            u = t / max(0.001, seconds)  # 0..1

            # 密度随 u 逐步降低：越到后面越“收锋”，同时给系统回收缓冲
            # 这能显著降低“重复感”和性能压力
            base_emit = int(round((7.0 - 4.0 * u) * intensity))
            base_emit = max(2, base_emit)

            # 每隔一些拍故意“断墨”（不发射），形成书法特有的呼吸感，也更像转场
            if (beat % int(max(6, round(10 / max(0.4, intensity))))) == 0 and u > 0.35:
                time.sleep(dt)
                continue

            x, z = stroke_pos(u)
            tx, tz = stroke_tangent(u)

            # 笔势：沿切线方向 + 轻微旋转偏移，让笔触有“飞白”质感
            # 并且随 u 收束（尾部更轻更柔）
            speed = (20.0 + 10.0 * math.sin(math.pi * u)) * intensity
            swirl = (8.0 * (1.0 - u)) * intensity

            for k in range(base_emit):
                # 在笔触附近加一点“抖动”，像毛笔纤维散开的光
                jitter = (k - (base_emit - 1) / 2.0) / max(1.0, (base_emit - 1) / 2.0)
                px = x + 2.2 * jitter * (-tz)
                pz = z + 2.2 * jitter * ( tx)

                vx = speed * tx + swirl * (-tz) + 2.0 * math.sin(6.0 * u + k)
                vz = speed * tz + swirl * ( tx) + 2.0 * math.cos(5.5 * u + k)

                vy = clamp_vy(18.0 + 6.0 * (1.0 - u) + 0.07 * (abs(vx) + abs(vz)))

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing)

            # 精准节拍 sleep（保持稳定连贯）
            next_time = start + beat * dt
            sleep_t = next_time - time.time()
            if sleep_t > 0:
                time.sleep(sleep_t)

        # 落款印章：只来一次，小而“定格”，提示下一波开始（可关掉 stamp）
        if stamp:
            # 印章位置不在中心，避免“中心贯穿”既视感；用一个漂亮类型即可
            px, pz = (22.0, -18.0)
            vx, vz = (0.0, 0.0)
            vy = clamp_vy(28.0)

            # 印章建议用 circle 或 random_color（干净、辨识度强）
            stamp_type = T.circle if int(time.time() * 10) % 2 == 0 else T.random_color

            fire((px, 0.0, pz), (vx, vy, vz), stamp_type)


    def transition_teleport_afterimage(self, seconds=4.5, intensity=0.5, stamp=True):
        """
        独一无二过渡：瞬移残影
        seconds: 过渡时长（建议 3~6）
        intensity: 0.4~1.2（密度/速度）
        stamp: 是否末尾定场提示（建议 True）
        """
        MIN_VY = 12.0
        T = self.type_firework

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype
            )

        # --------- 跳点集合：固定“舞台编排”，每次过渡都一样但不显得重复 ----------
        # 这些点故意不对称、分前后景（z），看起来像“瞬移舞步”
        nodes = [
            (-28.0, -18.0), (-10.0,  22.0), ( 16.0, -6.0), ( 30.0,  14.0),
            (-22.0,  10.0), (  6.0, -24.0), ( 24.0, -16.0), (-4.0,   6.0),
            (-30.0,  20.0), ( 12.0,  26.0), ( 28.0,   2.0), (-14.0, -12.0),
        ]

        # 深度层（真正 3D）：每次瞬移会落到不同 z 层
        z_layers = [-22.0, -10.0, 0.0, 10.0, 22.0]

        # 跳跃节奏：离散“咔哒咔哒”的感觉
        hop_dt = 0.16 / max(0.6, intensity)   # 瞬移间隔
        after_dt = 0.04                       # 残影喷射间隔（短）

        start = time.time()
        hop = 0

        # 当前“角色位置”
        x, z = nodes[0]
        depth = z_layers[2]

        while True:
            t = time.time() - start
            if t >= seconds:
                break

            # --------- 选择下一个瞬移目标 ----------
            hop += 1
            nx, nz = nodes[hop % len(nodes)]
            nd = z_layers[hop % len(z_layers)]

            # --------- 瞬移动作：从当前点到目标点，喷一小段“残影” ----------
            # 残影数量随时间逐步减少：自然缓冲性能
            p = t / max(0.001, seconds)  # 0..1
            trails = int(round((6.0 - 3.0 * p) * intensity))
            trails = max(2, trails)

            dx = nx - x
            dz = nz - z
            dd = nd - depth

            # 归一化方向
            m = math.sqrt(dx*dx + dz*dz + dd*dd) + 1e-6
            ux, uz, ud = dx / m, dz / m, dd / m

            # 速度：沿“瞬移方向”快速掠过，同时给一点侧向偏移，形成残影扇面
            base_speed = (34.0 + 10.0 * math.sin(hop * 0.7)) * intensity
            side = (10.0 * (1.0 - p)) * intensity

            # 在旧位置喷残影（像“留下了上一帧”）
            for k in range(trails):
                s = (k - (trails - 1) / 2.0) / max(1.0, (trails - 1) / 2.0)

                # 侧向基向量（只在 x-z 平面内）
                sx, sz = -uz, ux

                px = x + 1.8 * s * sx
                pz = z + 1.8 * s * sz + depth

                vx = base_speed * ux + side * s * sx
                vz = base_speed * uz + side * s * sz + 6.0 * ud  # 把深度变化折进 vz，更 3D
                vy = clamp_vy(18.0 + 6.0 * (1.0 - p) + 0.06 * (abs(vx) + abs(vz)))

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing)
                time.sleep(after_dt)

            # 更新到新位置（“瞬移完成”）
            x, z, depth = nx, nz, nd

            # 在新位置补一个短“到达闪影”（仍然 nothing）
            vx = 10.0 * math.sin(hop * 0.9) * intensity
            vz = 10.0 * math.cos(hop * 0.9) * intensity
            vy = clamp_vy(20.0)
            fire((x, 0.0, z + depth), (vx, vy, vz), T.nothing)

            time.sleep(hop_dt)

        # --------- 末尾定场：提示下一波开始（极少量爆炸，可关 stamp） ----------
        if stamp:
            # 定场点：最后瞬移点附近，干净不抢戏
            stamp_types = [T.circle, T.random_color]
            for i in range(max(1, int(round(2 * intensity)))):
                px = x + (i * 3.0 - 1.5)
                pz = (z + depth) + (i * 2.0 - 1.0)

                vx, vz = 0.0, 0.0
                vy = clamp_vy(28.0 + i * 1.5)

                fire((px, 0.0, pz), (vx, vy, vz), stamp_types[i % len(stamp_types)])
                time.sleep(0.12)


    def transition_shutter_flip(self, seconds=4.8, intensity=0.5, seal=True):
        """
        独一无二过渡：快门翻帧（2D 光栅 + 3D 深度翻页）
        seconds: 3~7
        intensity: 0.4~1.2
        seal: 是否封帧提示下一波（建议 True）
        """
        MIN_VY = 12.0
        T = self.type_firework

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype
            )

        # 帧参数：一帧是一组“光栅线”
        # 你会看到像摄影快门一样，一帧帧翻过去
        frame_dt = 0.22 / max(0.6, intensity)    # 每帧持续
        line_points = int(round(12 * intensity))  # 每条线的点数
        lines = int(round(6 * intensity))         # 每帧几条线
        line_points = max(6, line_points)
        lines = max(3, lines)

        # 屏幕尺度（2D 感来自“整齐光栅”）
        X_SPAN = 56.0
        Z_DEPTHS = [-22.0, -10.0, 0.0, 10.0, 22.0]  # 3D 来自不同帧落在不同深度

        # 速度：让光栅“刷过去”，而不是旋转/环绕
        sweep_vx = 26.0 * intensity
        base_up = 18.0

        start = time.time()
        frame = 0

        while True:
            t = time.time() - start
            if t >= seconds:
                break

            frame += 1
            p = t / max(0.001, seconds)   # 0..1

            # 每帧选择一个深度层（翻页感）
            depth = Z_DEPTHS[frame % len(Z_DEPTHS)]

            # 帧的“倾斜角”随时间变化（让它像翻页，不像固定栅格）
            tilt = math.sin(t * 1.8)  # [-1,1]

            # 随进度逐渐“收光”：越到后面越少/越慢（缓冲性能）
            cur_lines = max(2, int(round(lines * (1.0 - 0.35 * p))))
            cur_points = max(5, int(round(line_points * (1.0 - 0.25 * p))))

            # 帧中心在 x 上来回移动，形成“快门滑动”
            center_x = (X_SPAN * 0.28) * math.sin(t * 1.4)

            # 一帧生成 cur_lines 条线；每条线用 nothing 画出短残影
            for li in range(cur_lines):
                # 线在 z 上的偏移（同一帧内部仍是 2D 光栅）
                z_off = (li - (cur_lines - 1) / 2.0) * (4.5 + 2.0 * tilt)

                # 线的“起点”从左向右刷（快门）
                # u in [-1,1]
                for pi in range(cur_points):
                    u = (pi / max(1, cur_points - 1)) * 2.0 - 1.0

                    # 2D 栅格点位置：主要铺在 x 方向
                    px = center_x + u * (X_SPAN * 0.5)
                    pz = depth + z_off + 3.0 * math.sin(t * 0.9 + li)

                    # 速度：整体向右刷，带一点“翻页”倾斜（vz 轻微变化）
                    vx = sweep_vx + 6.0 * tilt
                    vz = (10.0 * tilt) + 3.0 * math.sin(t * 1.2 + u * 2.0)
                    vy = clamp_vy(base_up + 6.0 * (1.0 - p) + 0.06 * (abs(vx) + abs(vz)))

                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing)

                # 每条线之间稍微空一下，能看出“线”的存在（也更省）
                time.sleep(0.01)

            # 帧间隔
            time.sleep(frame_dt)

        # 封帧：最后给一个“定格”的提示（极少量爆炸）
        if seal:
            # 选择一个不居中的位置（避免中心柱既视感）
            px, pz = (18.0, -14.0)
            for i in range(max(1, int(round(2 * intensity)))):
                ftype = T.circle if (i % 2 == 0) else T.random_color
                fire((px + i * 3.0, 0.0, pz + i * 2.0), (0.0, clamp_vy(28.0 + i * 2.0), 0.0), ftype)
                time.sleep(0.12)


    def transition_origami_fold(self, seconds=5.0, intensity=0.1, seal=True):
        """
        独一无二过渡：折纸折叠（先2D面，再3D折叠）
        seconds: 3~7
        intensity: 0.4~1.2
        seal: 是否末尾封口提示（建议 True）
        """
        MIN_VY = 12.0
        T = self.type_firework

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype
            )

        # 折纸的“顶点”（一个不规则四边形，避免重复几何感）
        # 先在近景 z=0 画出面，再逐段折叠到不同深度
        quad = [(-26.0, -10.0), (-6.0, 22.0), (24.0, 8.0), (6.0, -24.0)]  # (x,z_plane)

        # 折痕（在面内的三条折线，用参数 s 表示折叠进度）
        # 每条折痕都有不同的“折向”（往前/往后），形成 3D 折纸感
        creases = [
            {"p0": (-18.0, -2.0), "p1": (18.0, 10.0), "dir":  1.0},
            {"p0": (-10.0, 18.0), "p1": (12.0, -20.0), "dir": -1.0},
            {"p0": (-24.0, -14.0), "p1": (10.0, 24.0), "dir":  1.0},
        ]

        # 采样密度（面和折痕的点）
        edge_pts = max(10, int(round(14 * intensity)))
        fill_pts = max(10, int(round(18 * intensity)))

        dt = 0.09  # 过渡节拍（稳且省）
        start = time.time()
        beat = 0

        # 小工具：线性插值
        def lerp(a, b, t):
            return a + (b - a) * t

        # 小工具：点到折线的“侧”判断（用于决定折叠方向）
        def side_of_line(px, pz, ax, az, bx, bz):
            return (bx - ax) * (pz - az) - (bz - az) * (px - ax)

        # 折叠深度最大值（3D 强度）
        max_depth = 26.0

        while True:
            t = time.time() - start
            if t >= seconds:
                break
            beat += 1

            p = t / max(0.001, seconds)  # 0..1
            # 前 35%：主要“展开面”（2D）
            # 后 65%：逐步折叠（3D）
            unfold = 1.0 if p < 0.35 else max(0.0, 1.0 - (p - 0.35) / 0.65)

            # 折叠强度（0->1）
            fold = 0.0 if p < 0.35 else min(1.0, (p - 0.35) / 0.65)

            # 1) 画四边形边框（像纸边）
            for e in range(4):
                x0, z0 = quad[e]
                x1, z1 = quad[(e + 1) % 4]
                for i in range(edge_pts):
                    u = i / max(1, edge_pts - 1)
                    px = lerp(x0, x1, u)
                    pz = lerp(z0, z1, u)

                    # 折叠：根据折痕把点推入不同深度
                    depth = 0.0
                    if fold > 0.0:
                        for cr in creases:
                            ax, az = cr["p0"]
                            bx, bz = cr["p1"]
                            s = side_of_line(px, pz, ax, az, bx, bz)
                            # 在折线两侧产生相反深度（像折纸翻面）
                            depth += cr["dir"] * (1.0 if s > 0 else -1.0) * (max_depth * 0.22) * fold

                    # 展开阶段深度收回（保持 2D 面）
                    depth *= (1.0 - 0.65 * unfold)

                    # 速度：沿边“轻扫”，但不绕圈、不成幕帘
                    vx = (10.0 + 8.0 * (1.0 - fold)) * (1.0 if e % 2 == 0 else -1.0)
                    vz = 6.0 * math.sin(t * 1.3 + e)
                    vy = clamp_vy(18.0 + 6.0 * (1.0 - fold) + 0.06 * (abs(vx) + abs(vz)))

                    fire((px, 0.0, pz + depth), (vx, vy, vz), T.nothing)

            # 2) 画“纸面填充纹理”（少量点，像纸的发光纤维）
            # 这里用一个不规则插值，让它看起来像“纸面纹理”而不是网格
            if beat % 2 == 0:
                for i in range(fill_pts):
                    u = (i / max(1, fill_pts - 1))
                    # 在四边形里做一个近似的“扭曲插值”
                    # 取两条对角边插值，再插值其间
                    xa, za = quad[0]
                    xb, zb = quad[1]
                    xc, zc = quad[2]
                    xd, zd = quad[3]

                    # 两条“边”
                    xL = lerp(xa, xd, u)
                    zL = lerp(za, zd, u)
                    xR = lerp(xb, xc, u)
                    zR = lerp(zb, zc, u)

                    v = (0.35 + 0.65 * math.sin(t * 0.9 + i * 0.3)) * 0.5 + 0.5  # [0,1] 扭曲
                    px = lerp(xL, xR, v)
                    pz = lerp(zL, zR, v)

                    depth = 0.0
                    if fold > 0.0:
                        for cr in creases:
                            ax, az = cr["p0"]
                            bx, bz = cr["p1"]
                            s = side_of_line(px, pz, ax, az, bx, bz)
                            depth += cr["dir"] * (1.0 if s > 0 else -1.0) * (max_depth * 0.16) * fold
                    depth *= (1.0 - 0.65 * unfold)

                    vx = 6.0 * math.cos(t * 1.1 + i * 0.2)
                    vz = 6.0 * math.sin(t * 1.0 + i * 0.18)
                    vy = clamp_vy(18.0 + 4.0 * (1.0 - fold) + 0.05 * (abs(vx) + abs(vz)))

                    fire((px, 0.0, pz + depth), (vx, vy, vz), T.nothing)

            # 3) 折痕强调（折叠后更明显）：像折纸的折线发光
            if fold > 0.15:
                for cr in creases:
                    ax, az = cr["p0"]
                    bx, bz = cr["p1"]
                    for i in range(max(8, int(round(10 * intensity)))):
                        u = i / max(1, (max(8, int(round(10 * intensity))) - 1))
                        px = lerp(ax, bx, u)
                        pz = lerp(az, bz, u)

                        depth = cr["dir"] * (max_depth * 0.6) * fold
                        vx = 8.0 * (-cr["dir"]) * fold
                        vz = 4.0 * math.cos(t * 1.4 + u * 3.0)
                        vy = clamp_vy(20.0 + 8.0 * fold)

                        fire((px, 0.0, pz + depth), (vx, vy, vz), T.nothing)

            time.sleep(dt)

        # 封口：折完后给一个“折痕封印”小爆点（提示下一波）
        if seal:
            # 在一条折痕的末端落款，位置不居中
            sx, sz = creases[1]["p1"]  # 选第二条折痕末端
            px = sx + 6.0
            pz = sz - 6.0 + (max_depth * 0.45)

            ftype = T.circle if int(time.time() * 10) % 2 == 0 else T.random_color
            fire((px, 0.0, pz), (0.0, clamp_vy(28.0), 0.0), ftype)
            time.sleep(0.12)


    def wave_halton_galaxy_spray(self, duration=8.0, intensity=1.0, explode_ratio=0.22):
        """
        完全不同发射方式：Halton 低差异序列驱动的均匀伪随机喷射（银河星尘）
        duration: 持续时间（秒）
        intensity: 强度（0.5~1.5），越大越密越快
        explode_ratio: 爆炸比例（0~1），建议 0.15~0.30
        """
        MIN_VY = 12.0
        T = self.type_firework

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype
            )

        # -------- Halton 低差异序列（均匀覆盖，不像 random 那样扎堆）--------
        def halton(index, base):
            f = 1.0
            r = 0.0
            i = index
            while i > 0:
                f /= base
                r += f * (i % base)
                i //= base
            return r

        # -------- 发射密度/节拍 --------
        dt = 0.05 / max(0.6, intensity)  # 强度越大越密
        start = time.time()
        k = 1  # Halton index 从 1 开始更好

        # -------- 空间尺度（圆盘 + 深度漂移）--------
        R = 36.0           # 发射圆盘半径（越大越铺开）
        Z_DEPTH = 26.0     # 深度层次
        Y0 = 0.0

        # -------- 速度尺度（均匀覆盖半球，且保证 vy>0）--------
        SPEED_MIN = 24.0
        SPEED_MAX = 46.0

        # 爆炸类型池（你给的好看的）
        burst_pool = [
            T.circle, T.random_color, T.ball, T.double_ball,
            T.planet_random_color, T.planet_ball,
            T.half_half_color_ball, T.mixed_color_ball, T.ball_up,
            T.flower, T.love_3D
        ]

        while True:
            t = time.time() - start
            if t >= duration:
                break

            # 1) 位置：用 Halton(2,3) 把点均匀铺在圆盘内
            u = halton(k, 2)             # [0,1)
            v = halton(k, 3)             # [0,1)
            rr = R * math.sqrt(max(1e-9, u))
            ang = 2.0 * math.pi * v

            px = rr * math.cos(ang)
            pz = rr * math.sin(ang)

            # 叠加“深度漂移”（不是分层环、而是缓慢飘动的体积感）
            w = halton(k, 5)             # [0,1)
            pz += (w - 0.5) * Z_DEPTH + 6.0 * math.sin(t * 0.9 + ang)

            # 2) 方向：均匀覆盖“上半球”（Halton 7,11）
            # elev ∈ (0, π/2)，确保 vy > 0
            a = halton(k, 7)
            b = halton(k, 11)
            yaw = 2.0 * math.pi * a
            elev = (0.18 * math.pi) + (0.72 * (math.pi / 2.0)) * b  # 约 32°~97°间的上抛（但我们只取上半球的正 sin）

            # 3) 速度大小：也用 Halton 控制（避免重复速度）
            s = halton(k, 13)
            speed = SPEED_MIN + (SPEED_MAX - SPEED_MIN) * s

            # 分解速度（vy 永远 > 0）
            vx = speed * math.cos(elev) * math.cos(yaw)
            vz = speed * math.cos(elev) * math.sin(yaw)
            vy = speed * math.sin(elev)
            vy = clamp_vy(vy)

            # 4) 类型：多数是 nothing 星尘光轨，少数爆炸点亮
            # 使用 Halton(17) 决定是否爆炸（均匀分布，而不是一坨一坨爆）
            rsel = halton(k, 17)
            if rsel < explode_ratio:
                ftype = burst_pool[k % len(burst_pool)]
            else:
                ftype = T.nothing

            fire((px, Y0, pz), (vx, vy, vz), ftype)

            k += 1
            time.sleep(dt)

    def narration_fireworks_loop(self, stop_event, intensity=0.8):
        """
        旁白烟花（更好看版）：
        - 每隔一小段时间发射一小组 T.nothing
        - 队形清晰：左右梳子 / 底部波浪 / 侧边括号 / 角落斜线 / 双侧同步条
        - 每次规律都不一样：参数随时间与节拍变化（但仍然规整）
        - 始终放在两侧或底部，不抢中心
        """
        MIN_VY = 12.0
        T = self.type_firework

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                T.nothing
            )

        # 便于随时停
        def wait_s(seconds):
            # 分段 wait，保证 stop_event 反应快
            step = 0.05
            left = seconds
            while left > 0 and not stop_event.is_set():
                stop_event.wait(min(step, left))
                left -= step

        # ===== 舞台边界（旁白永远在边缘/底部）=====
        LEFT_X = -36.0
        RIGHT_X = 36.0
        BOTTOM_Z = -34.0

        # 深度层（让背景也有 3D，但仍不抢中心）
        DEPTHS = [-18.0, -10.0, 0.0, 10.0, 18.0]

        # ===== 伪随机（不依赖 random；但每次规律都不同且可复现）=====
        seed = int(time.time() * 1000) & 0x7fffffff

        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff  # [0,1)

        # 基础节奏：旁白不密集，主秀更突出
        base_dt = 0.48 / max(0.55, float(intensity))

        start = time.time()
        beat = 0

        while not stop_event.is_set():
            t = time.time() - start
            beat += 1

            # 偶尔给“空拍”（更像旁白，不会一直刷屏）
            if (beat % 9 == 0) and (rnd() < 0.45):
                wait_s(base_dt * (1.6 + 1.2 * rnd()))
                continue

            # 每次选择一个“队形”模式（0~5），并让参数变化
            mode = int(rnd() * 6)  # 0..5
            depth = DEPTHS[int(rnd() * len(DEPTHS))]
            tilt = (rnd() * 2.0 - 1.0)  # [-1,1]
            inward = 1.0 if rnd() > 0.5 else -1.0

            # 点数：不多，但要“成队形”
            n = int(round((6 + 6 * rnd()) * max(0.6, intensity)))
            n = max(5, min(n, 16))

            # 上升速度：旁白不需要太猛，但要稳定看得见
            vy0 = clamp_vy(16.0 + 6.0 * rnd())

            # 轻微横向速度（让光轨有生命，但不乱）
            drift = 3.0 + 4.0 * rnd()

            # ----------------------------
            # 模式 0：左侧“梳子”竖列（清晰、规整）
            # ----------------------------
            if mode == 0:
                z0 = -18.0 + 8.0 * math.sin(t * 0.5 + rnd() * 3.0)
                dz = 4.0 + 2.0 * rnd()
                for i in range(n):
                    px = LEFT_X
                    pz = z0 + (i - (n - 1) / 2.0) * dz + depth
                    vx = drift * 0.6  # 微向内
                    vz = drift * 0.2 * tilt
                    vy = clamp_vy(vy0 + 0.10 * (abs(vx) + abs(vz)))
                    fire((px, 0.0, pz), (vx, vy, vz))
                wait_s(base_dt)

            # ----------------------------
            # 模式 1：右侧“梳子”竖列（与左不同参数）
            # ----------------------------
            elif mode == 1:
                z0 = 16.0 * math.cos(t * 0.42 + rnd() * 2.0)
                dz = 3.5 + 2.5 * rnd()
                for i in range(n):
                    px = RIGHT_X
                    pz = z0 + (i - (n - 1) / 2.0) * dz + depth
                    vx = -drift * 0.6  # 微向内
                    vz = -drift * 0.2 * tilt
                    vy = clamp_vy(vy0 + 0.10 * (abs(vx) + abs(vz)))
                    fire((px, 0.0, pz), (vx, vy, vz))
                wait_s(base_dt)

            # ----------------------------
            # 模式 2：底部“波浪横排”（一条清楚的底边字幕感）
            # ----------------------------
            elif mode == 2:
                x_span = 42.0 + 10.0 * rnd()
                z_base = BOTTOM_Z + depth * 0.35
                for i in range(n):
                    u = (i / max(1, n - 1)) * 2.0 - 1.0
                    px = u * (x_span * 0.5)
                    pz = z_base + 4.0 * math.sin(t * 0.9 + u * (2.0 + 2.0 * rnd()))  # 波纹
                    vx = drift * 0.25 * math.sin(u * 3.0 + t)
                    vz = drift * 0.15 * math.cos(u * 2.0 + t * 0.7)
                    vy = clamp_vy(vy0 + 2.0 + 0.08 * (abs(vx) + abs(vz)))
                    fire((px, 0.0, pz), (vx, vy, vz))
                wait_s(base_dt * 1.05)

            # ----------------------------
            # 模式 3：双侧“括号” (  ) —— 很像舞台框架，清晰又高级
            # ----------------------------
            elif mode == 3:
                height = 22.0 + 10.0 * rnd()
                z_mid = depth
                # 左括号
                for i in range(n):
                    u = i / max(1, n - 1)
                    px = LEFT_X + 2.5 * math.sin(u * math.pi)
                    pz = z_mid + (u * 2.0 - 1.0) * (height * 0.5)
                    vx = drift * 0.55
                    vz = drift * 0.15 * tilt
                    vy = clamp_vy(vy0 + 0.10 * (abs(vx) + abs(vz)))
                    fire((px, 0.0, pz), (vx, vy, vz))
                # 右括号
                for i in range(n):
                    u = i / max(1, n - 1)
                    px = RIGHT_X - 2.5 * math.sin(u * math.pi)
                    pz = z_mid + (u * 2.0 - 1.0) * (height * 0.5)
                    vx = -drift * 0.55
                    vz = -drift * 0.15 * tilt
                    vy = clamp_vy(vy0 + 0.10 * (abs(vx) + abs(vz)))
                    fire((px, 0.0, pz), (vx, vy, vz))
                wait_s(base_dt * 1.10)

            # ----------------------------
            # 模式 4：角落“斜向短线” —— 像舞台角落扫光，很不重复
            # ----------------------------
            elif mode == 4:
                corner_left = True if rnd() > 0.5 else False
                px0 = LEFT_X if corner_left else RIGHT_X
                pz0 = (18.0 if rnd() > 0.5 else -18.0) + depth
                dx = (6.0 + 6.0 * rnd()) * (1.0 if corner_left else -1.0)
                dz = (10.0 + 8.0 * rnd()) * (1.0 if rnd() > 0.5 else -1.0)

                for i in range(n):
                    u = i / max(1, n - 1)
                    px = px0 + u * dx
                    pz = pz0 + u * dz
                    vx = drift * (0.35 + 0.25 * rnd()) * inward
                    vz = drift * (0.30 + 0.25 * rnd()) * tilt
                    vy = clamp_vy(vy0 + 3.0 + 0.08 * (abs(vx) + abs(vz)))
                    fire((px, 0.0, pz), (vx, vy, vz))
                wait_s(base_dt * 0.95)

            # ----------------------------
            # 模式 5：双侧“同步短条” —— 左右同时出现两段短线，节奏感很强
            # ----------------------------
            else:
                # 两侧各一段短条，位置每次变化
                z_center = (-10.0 + 20.0 * rnd()) + depth
                x_inset = 6.0 + 8.0 * rnd()
                for side in (-1.0, 1.0):
                    x_base = LEFT_X + x_inset if side < 0 else RIGHT_X - x_inset
                    for i in range(n):
                        u = (i / max(1, n - 1)) * 2.0 - 1.0
                        px = x_base + u * (4.0 + 4.0 * rnd()) * side
                        pz = z_center + u * (6.0 + 4.0 * rnd()) * tilt
                        vx = drift * 0.45 * (-side)  # 向舞台内侧一点
                        vz = drift * 0.10 * math.sin(t + u * 2.0)
                        vy = clamp_vy(vy0 + 0.10 * (abs(vx) + abs(vz)))
                        fire((px, 0.0, pz), (vx, vy, vz))
                wait_s(base_dt * 1.05)

    def start_narration_fireworks(self):
        if hasattr(self, "_narration_stop") and self._narration_stop and not self._narration_stop.is_set():
            return
        self._narration_stop = threading.Event()
        self._narration_thread = threading.Thread(
            target=self.narration_fireworks_loop,
            args=(self._narration_stop, 0.8),
            daemon=True
        )
        self._narration_thread.start()

    def stop_narration_fireworks(self):
        if hasattr(self, "_narration_stop") and self._narration_stop:
            self._narration_stop.set()


    def climax_hypernova_symphony(self):
        T = self.type_firework
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype
            )

        # =========================
        # Phase 1: 三重推进（能量柱不是贯穿，而是三点起势 + 旋流光轨）
        # =========================
        launchers = [(-26.0, -10.0), (0.0, 0.0), (26.0, 10.0)]  # (x, z)
        helix_turns = 26
        for k in range(helix_turns):
            a = k * 0.35
            for idx, (lx, lz) in enumerate(launchers):
                spin = 1.0 if idx % 2 == 0 else -1.0
                # 位置做轻微环绕，让“起势”更立体
                px = lx + 4.0 * math.cos(a + idx)
                pz = lz + 4.0 * math.sin(a * 0.9 + idx)

                # 速度：上升 + 绕圈 + 纵深漂移
                vx = 12.0 * math.cos(a * 1.2 + idx) * spin
                vz = 12.0 * math.sin(a * 1.1 + idx) * spin + (6.0 if idx == 0 else (-6.0 if idx == 2 else 0.0))
                vy = clamp_vy(22.0 + 0.08 * (abs(vx) + abs(vz)))

                # 主体用 nothing，偶尔 ball_up 增加“喷泉上扬”视觉
                ftype = T.ball_up if (k % 5 == 0 and idx != 1) else T.nothing
                fire((px, 0.0, pz), (vx, vy, vz), ftype)

            time.sleep(0.055)

        time.sleep(0.25)

        # =========================
        # Phase 2: 立体棱镜环（多层深度爆闪，像水晶冠）
        # =========================
        ring_layers = [-18.0, -6.0, 6.0, 18.0]
        ring_pts = 14
        for wave in range(4):
            R = 26.0 + 5.0 * math.sin(wave * 0.9)
            for i in range(ring_pts):
                th = (2.0 * math.pi) * (i / ring_pts) + wave * 0.45
                cx = math.cos(th)
                sz = math.sin(th)

                depth = ring_layers[(i + wave) % len(ring_layers)]
                px = R * cx
                pz = R * sz + depth

                # 速度：轻旋 + 外扩，上扬明显但不做中心贯穿
                vx = 10.0 * cx + 10.0 * (-sz)
                vz = 10.0 * sz + 10.0 * ( cx) + depth * 0.20
                vy = clamp_vy(32.0 + 0.10 * (abs(vx) + abs(vz)))

                # 这一段用“行星/球系”会特别炫
                fpool = [T.planet_random_color, T.planet_ball, T.double_ball, T.mixed_color_ball, T.half_half_color_ball]
                fire((px, 0.0, pz), (vx, vy, vz), fpool[(i + 2 * wave) % len(fpool)])

            time.sleep(0.11)

        time.sleep(0.25)

        # =========================
        # Phase 3: 花雨+心焰（美 + 炫 同时上强度）
        # =========================
        # 外圈“花雨”扫过，内圈“爱心焰”穿插（3D 纵深交错）
        for step in range(18):
            ph = step * 0.42
            # 花雨：外圈 10 点
            Nf = 4
            Rf = 30.0
            for i in range(Nf):
                th = (2.0 * math.pi) * (i / Nf) + ph
                px = Rf * math.cos(th)
                pz = Rf * math.sin(th) + (14.0 * math.sin(ph * 0.7 + i * 0.6))

                vx = 12.0 * (-math.sin(th))
                vz = 12.0 * ( math.cos(th))
                vy = clamp_vy(34.0)

                fire((px, 0.0, pz), (vx, vy, vz), T.flower)

            # 心焰：内圈 6 点（少量但很点睛）
            Nh = 6
            Rh = 16.0
            for j in range(Nh):
                th = (2.0 * math.pi) * (j / Nh) - ph * 0.9
                px = Rh * math.cos(th)
                pz = Rh * math.sin(th) + (10.0 if j % 2 == 0 else -10.0)

                vx = 8.0 * math.cos(th + 1.2)
                vz = 8.0 * math.sin(th + 1.2)
                vy = clamp_vy(30.0)

                # 3D 爱心为主，偶尔 2D 双心做“闪一下”
                ftype = T.random_color
                fire((px, 0.0, pz), (vx, vy, vz), ftype)

            time.sleep(0.095)

        time.sleep(0.30)

        # =========================
        # Phase 4: 超新星终爆（全场最炫：多源连发 + 中心爆闪风暴）
        # =========================
        # 先做一圈“星核点火”（速度更快，密度更高）
        ignition_sources = 12
        for burst in range(3):
            R0 = 34.0 - burst * 3.0
            for i in range(ignition_sources):
                th = (2.0 * math.pi) * (i / ignition_sources) + burst * 0.35
                px = R0 * math.cos(th)
                pz = R0 * math.sin(th) + 16.0 * math.sin(th * 0.6)

                vx = 16.0 * (-math.sin(th))
                vz = 16.0 * ( math.cos(th))
                vy = clamp_vy(38.0)

                hard = [T.double_ball, T.mixed_color_ball, T.random_color, T.planet_random_color]
                fire((px, 0.0, pz), (vx, vy, vz), hard[(i + burst) % len(hard)])

            time.sleep(0.09)

        # 最后：中心“超新星风暴”——高速连续爆闪（就是爽）
        for tick in range(26):
            a = tick * 0.55
            # 中心附近做一个“旋转喷发环”，但半径小，形成“核爆涌出”
            coreN = 8
            r = 6.0 + 2.0 * math.sin(a)
            for i in range(coreN):
                th = (2.0 * math.pi) * (i / coreN) + a
                px = r * math.cos(th)
                pz = r * math.sin(th) + 10.0 * math.sin(a * 0.7 + i)

                # 速度：强上扬 + 强旋转（炫的核心）
                vx = 18.0 * math.cos(th + 0.9)
                vz = 18.0 * math.sin(th + 0.9)
                vy = clamp_vy(42.0 + 0.08 * (abs(vx) + abs(vz)))

                # 终爆类型池：最炫的都上
                final_pool = [T.double_ball, T.mixed_color_ball, T.half_half_color_ball, T.planet_random_color, T.random_color]
                fire((px, 0.0, pz), (vx, vy, vz), final_pool[(tick + i) % len(final_pool)])

            # 同时给两侧补两发“侧翼爆闪”，形成舞台包围感
            if tick % 2 == 0:
                for side in (-1.0, 1.0):
                    px = side * 26.0
                    pz = 12.0 * math.sin(a)
                    vx = -side * 8.0
                    vz = 6.0 * math.cos(a * 0.8)
                    vy = clamp_vy(36.0)
                    fire((px, 0.0, pz), (vx, vy, vz), T.circle)

            time.sleep(0.06)


    def climax_tree_shape(self):
        T = self.type_firework
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # =========================
        # 配色（RGB 0~255）
        # =========================
        TRUNK = (120, 72, 35)          # 树干棕
        TRUNK_DARK = (90, 52, 26)      # 深棕阴影
        LEAF_1 = (40, 180, 70)         # 叶绿
        LEAF_2 = (20, 140, 55)         # 深绿
        LEAF_3 = (90, 220, 120)        # 亮绿高光
        BLOOM = (255, 120, 170)        # 粉花点缀
        FRUIT = (255, 70, 60)          # 红果点缀
        GOLD = (255, 220, 90)          # 金色闪点

        # =========================
        # 0) 地面根系（低矮扩散，不抢主戏，建立“树扎根”）
        # =========================
        root_n = 10
        for i in range(root_n):
            u = (i / (root_n - 1)) * 2.0 - 1.0  # [-1,1]
            px = u * 8.0
            pz = (u * 6.0)
            vx = u * 10.0
            vz = (u * 6.0)
            vy = clamp_vy(14.0)  # 低矮但必须 >0
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, TRUNK_DARK)
            time.sleep(0.03)

        time.sleep(0.15)

        # =========================
        # 1) 树干生长（竖直线条，厚实）
        # =========================
        # 用多股 very-small vx/vz 的 nothing 叠出粗树干
        trunk_cols = [(-1.6, -0.8), (-0.8, 0.6), (0.0, 0.0), (0.9, -0.6), (1.6, 0.8)]
        trunk_steps = 18
        for s in range(trunk_steps):
            # 越往后越高，像“长出来”
            vy = clamp_vy(22.0 + s * 1.2)

            for (ox, oz) in trunk_cols:
                # 树干几乎竖直：vx/vz 很小，只做轻微纹理
                vx = ox * 0.8
                vz = oz * 0.8
                col = TRUNK if (s % 3 != 0) else TRUNK_DARK
                fire((ox, 0.0, oz), (vx, vy, vz), T.nothing, col)

            time.sleep(0.06)

        time.sleep(0.20)

        # =========================
        # 2) 树枝分叉（清晰的“Y型/分叉”轮廓）
        # =========================
        # 这些“枝条”不做旋涡，只做斜向上+外扩，左右对称并带一点3D深度
        branch_levels = [
            # (spread_x, spread_z, up, count, color)
            (10.0,  4.0, 26.0, 7, TRUNK),
            (14.0, -6.0, 28.0, 8, TRUNK_DARK),
            (18.0,  8.0, 30.0, 9, TRUNK),
        ]
        for (sx, sz, up, cnt, bcol) in branch_levels:
            for i in range(cnt):
                u = (i / (cnt - 1)) * 2.0 - 1.0  # [-1,1] 左右展开
                # 主枝：向左右外扩；z 方向也分出前后景
                vx = u * sx
                vz = (u * sz)
                vy = clamp_vy(up + 2.0 * (1.0 - abs(u)))  # 中间略高，枝叉更“提”
                # 起点从地面略偏中间，让枝条看起来从树干“长出”
                px = u * 1.0
                pz = u * 0.8
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, bcol)
                time.sleep(0.02)
            time.sleep(0.10)

        time.sleep(0.25)

        # =========================
        # 3) 树冠叶团（主视觉：巨大树冠，分层、很满、很漂亮）
        # =========================
        # 叶团用会“好看地爆开”的类型（球/行星/混色/花）
        canopy_types = [
            T.planet_random_color,
            T.planet_ball,
            T.mixed_color_ball,
            T.half_half_color_ball,
            T.double_ball,
            T.flower,
        ]

        # 树冠做三层：下冠、中冠、上冠（越高越集中）
        canopy_layers = [
            # (radius, up, depth_amp, bursts, base_colorA, base_colorB)
            (26.0, 34.0, 14.0, 18, LEAF_1, LEAF_2),
            (22.0, 36.0, 10.0, 16, LEAF_2, LEAF_3),
            (18.0, 38.0,  8.0, 14, LEAF_1, LEAF_3),
        ]

        # 为了“树形”而不是“球形”：让下冠更宽，上冠更窄
        phase = 0.0
        for layer_idx, (R, up, depth_amp, bursts, cA, cB) in enumerate(canopy_layers):
            phase += 0.45
            for i in range(bursts):
                th = (2.0 * math.pi) * (i / bursts) + phase

                # 树冠发射点：围绕树干底部，但不画圈——只是起点分散
                px0 = 2.0 * math.cos(th)
                pz0 = 2.0 * math.sin(th)

                # 速度：外扩到树冠半径（无旋涡，只径向扩散）
                vx = (R * 0.45) * math.cos(th)
                vz = (R * 0.45) * math.sin(th) + depth_amp * math.sin(th * 0.6)

                # 向上：层越高越往上
                vy = clamp_vy(up + 0.08 * (abs(vx) + abs(vz)))

                # 颜色交替，让叶团有层次
                col = cA if (i % 2 == 0) else cB

                ftype = canopy_types[(i + layer_idx * 2) % len(canopy_types)]
                fire((px0, 0.0, pz0), (vx, vy, vz), ftype, col)

                time.sleep(0.02)

            time.sleep(0.18)

        time.sleep(0.25)

        # =========================
        # 4) 点缀：花与果（让“树”更像树，而不是单纯一团绿）
        # =========================
        # 少量粉花（flower / love_3D）+ 少量红果（ball / circle）
        accents = 14
        for i in range(accents):
            th = (2.0 * math.pi) * (i / accents)
            # 点缀更靠近树冠中上部
            vx = 10.0 * math.cos(th)
            vz = 10.0 * math.sin(th) + 6.0 * math.sin(th * 0.7)
            vy = clamp_vy(34.0)

            if i % 4 == 0:
                ftype, col = T.flower, BLOOM
            elif i % 4 == 1:
                ftype, col = T.circle, FRUIT
            elif i % 4 == 2:
                ftype, col = T.love_3D, BLOOM
            else:
                ftype, col = T.random_color, GOLD

            fire((0.0, 0.0, 0.0), (vx, vy, vz), ftype, col)
            time.sleep(0.05)

        # 结束：给观众一点余韵
        time.sleep(0.30)


    def climax_van_gogh_starry_night(self, intensity=1.0):
        T = self.type_firework
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # -------------------------
        # 调色板（梵高星空风）
        # -------------------------
        NIGHT_1 = (10, 20, 55)      # 深夜蓝
        NIGHT_2 = (20, 45, 105)     # 群青
        NIGHT_3 = (35, 80, 160)     # 亮蓝
        NIGHT_4 = (70, 130, 200)    # 青蓝高光（油画笔触亮边）

        STAR_1  = (255, 220, 90)    # 星黄
        STAR_2  = (255, 245, 200)   # 星白金
        MOON_1  = (255, 235, 140)   # 月亮黄
        MOON_2  = (255, 250, 220)   # 月晕亮白

        CYPRESS_1 = (8, 15, 10)     # 柏树近黑绿
        CYPRESS_2 = (15, 35, 20)    # 柏树暗绿边

        TOWN_1 = (255, 190, 90)     # 村庄灯火
        TOWN_2 = (255, 120, 70)     # 暖橙窗光

        # 强度安全处理
        intensity = max(0.4, float(intensity))

        # -------------------------
        # Phase 0：铺底“夜空油画底色”（大面积 but 轻）
        # -------------------------
        # 在上半天幕铺一层深蓝“雾化笔刷”，主要用 nothing
        haze_rows = int(round(7 * intensity))
        haze_cols = int(round(18 * intensity))
        haze_rows = max(5, haze_rows)
        haze_cols = max(14, haze_cols)

        for r in range(haze_rows):
            z_base = 10.0 + r * 7.0
            for c in range(haze_cols):
                u = (c / max(1, haze_cols - 1)) * 2.0 - 1.0
                px = u * 42.0
                pz = z_base + 8.0 * math.sin(u * 2.0 + r)

                # 非旋涡：轻微横向刷动 + 稳定上扬
                vx = 6.0 * math.sin(0.8 * r + u * 2.3)
                vz = 3.0 * math.cos(0.7 * r + u * 1.7)
                vy = clamp_vy(16.0 + 2.0 * intensity)

                col = [NIGHT_1, NIGHT_2, NIGHT_3][(r + c) % 3]
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                if c % 4 == 0:
                    time.sleep(0.004)

            time.sleep(0.02)

        time.sleep(0.18)

        # -------------------------
        # Phase 1：梵高式“旋云笔触”（真正像画出来的风）
        # -------------------------
        # 用多条“弧形笔刷带”叠出星空的流动感（像油画刷子扫过）
        bands = int(round(7 * intensity))
        strokes_per_band = int(round(30 * intensity))
        bands = max(5, bands)
        strokes_per_band = max(22, strokes_per_band)

        # 画面中心偏左（梵高星空常见的旋云核心）
        cx, cz = (-10.0, 26.0)

        for b in range(bands):
            # 每条带不同半径与倾斜，避免重复
            R0 = 10.0 + b * 5.0
            tilt = 0.6 + 0.15 * b
            zlift = (b - (bands - 1) / 2.0) * 2.0

            for i in range(strokes_per_band):
                t = i / max(1, strokes_per_band - 1)

                # 弧形轨迹（不是规则圆）：半径随 t 波动，像手刷出来
                ang = (1.2 * math.pi) * t + 0.35 * math.sin(5.0 * t + b)
                R = R0 * (0.85 + 0.25 * math.sin(2.0 * math.pi * t + b))

                px = cx + R * math.cos(ang)
                pz = cz + (R * tilt) * math.sin(ang) + zlift

                # 速度沿“笔触切线方向”，再加一点上扬（像刷子掠过天空）
                tx = -math.sin(ang)
                tz =  math.cos(ang) * tilt

                speed = (22.0 + 10.0 * math.sin(2.0 * math.pi * t + b)) * intensity
                vx = speed * tx + 3.0 * math.cos(ang * 2.0 + b)
                vz = speed * tz + 3.0 * math.sin(ang * 2.0 + b)
                vy = clamp_vy(18.0 + 6.0 * intensity)

                # 笔触高光：偶尔用更亮的蓝
                col = NIGHT_2
                if (i + b) % 6 == 0:
                    col = NIGHT_4
                elif (i + b) % 3 == 0:
                    col = NIGHT_3

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                if i % 6 == 0:
                    time.sleep(0.005)

            time.sleep(0.03)

        time.sleep(0.18)

        # -------------------------
        # Phase 2：星点爆闪（星黄 + 星白金）
        # -------------------------
        # 固定一些“星星中心”，每颗星做一圈爆闪 + 少量拖尾
        star_centers = [
            (-28.0, 34.0), (-16.0, 38.0), (-2.0, 42.0), (12.0, 40.0), (26.0, 36.0),
            (-22.0, 24.0), (-6.0, 30.0), (10.0, 28.0), (24.0, 26.0),
            (-14.0, 18.0), (2.0, 20.0), (18.0, 18.0),
        ]

        star_types = [T.circle, T.ball, T.double_ball, T.planet_ball, T.planet_random_color]
        for s, (sx, sz) in enumerate(star_centers):
            bursts = int(round((10 + (s % 5) * 2) * intensity))
            bursts = max(10, bursts)
            for i in range(bursts):
                th = (2.0 * math.pi) * (i / bursts)

                # 从星心向外“放射”，形成梵高星的放射感
                vx = (10.0 + 6.0 * math.sin(i)) * math.cos(th)
                vz = (10.0 + 6.0 * math.cos(i)) * math.sin(th)
                vy = clamp_vy(30.0 + 4.0 * intensity)

                col = STAR_1 if (i % 2 == 0) else STAR_2
                ftype = star_types[(s + i) % len(star_types)]
                fire((sx, 0.0, sz), (vx, vy, vz), ftype, col)

                if i % 4 == 0:
                    time.sleep(0.01)

            # 星星“光晕拖尾”（nothing）——更像油画晕染
            halo = int(round(10 * intensity))
            for j in range(halo):
                th = (2.0 * math.pi) * (j / halo)
                vx = 8.0 * math.cos(th)
                vz = 8.0 * math.sin(th)
                vy = clamp_vy(20.0 + 3.0 * intensity)
                fire((sx, 0.0, sz), (vx, vy, vz), T.nothing, STAR_2)
            time.sleep(0.08)

        time.sleep(0.25)

        # -------------------------
        # Phase 3：右上角大月亮（超级亮、超级大）
        # -------------------------
        moon_center = (30.0, 44.0)
        moon_rings = int(round(4 * intensity))
        moon_rings = max(3, moon_rings)

        for ring in range(moon_rings):
            R = 4.0 + ring * 4.0
            N = int(round((18 + ring * 8) * intensity))
            N = max(18, N)
            for i in range(N):
                th = (2.0 * math.pi) * (i / N)
                px = moon_center[0] + 0.8 * math.cos(th)  # 起点集中一点，像“月团”
                pz = moon_center[1] + 0.8 * math.sin(th)

                vx = (12.0 + 4.0 * ring) * math.cos(th)
                vz = (12.0 + 4.0 * ring) * math.sin(th)
                vy = clamp_vy(34.0 + 3.0 * ring)

                col = MOON_2 if ring % 2 == 0 else MOON_1
                ftype = T.double_ball if ring >= 2 else T.ball
                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 6 == 0:
                    time.sleep(0.008)

            # 月晕刷痕（nothing，高光边）
            for j in range(int(round(14 * intensity))):
                th = (2.0 * math.pi) * (j / max(1, int(round(14 * intensity))))
                vx = 10.0 * math.cos(th)
                vz = 10.0 * math.sin(th)
                vy = clamp_vy(22.0)
                fire((moon_center[0], 0.0, moon_center[1]), (vx, vy, vz), T.nothing, MOON_2)

            time.sleep(0.10)

        time.sleep(0.22)

        # -------------------------
        # Phase 4：左下角柏树剪影（黑绿“火焰形”竖刷）
        # -------------------------
        # 柏树像黑色火焰：用很多短竖笔触（nothing）堆形
        cypress_base = (-30.0, -18.0)
        trunk_lines = int(round(26 * intensity))
        trunk_lines = max(20, trunk_lines)

        for i in range(trunk_lines):
            u = (i / max(1, trunk_lines - 1))  # 0..1
            # 柏树宽度随高度变化（中上更宽）
            width = 5.0 + 8.0 * math.sin(math.pi * u)
            px = cypress_base[0] + (width * (2.0 * (u - 0.5))) * 0.12 + 2.0 * math.sin(i * 0.4)
            pz = cypress_base[1] + 4.0 * math.sin(i * 0.3)

            vx = 2.0 * math.sin(i * 0.7)
            vz = 1.5 * math.cos(i * 0.6)
            vy = clamp_vy(18.0 + 18.0 * u + 4.0 * intensity)

            col = CYPRESS_1 if i % 3 != 0 else CYPRESS_2
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            time.sleep(0.02)

        time.sleep(0.18)

        # -------------------------
        # Phase 5：底部村庄灯火（暖色小爆点，衬托画面）
        # -------------------------
        houses = int(round(18 * intensity))
        houses = max(12, houses)
        for i in range(houses):
            u = (i / max(1, houses - 1)) * 2.0 - 1.0
            px = u * 38.0
            pz = -38.0 + 3.0 * math.sin(i * 0.7)

            vx = 0.5 * math.sin(i)
            vz = 0.5 * math.cos(i)
            vy = clamp_vy(20.0)

            col = TOWN_1 if i % 2 == 0 else TOWN_2
            ftype = T.circle if i % 3 == 0 else T.random_color
            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            time.sleep(0.02)

        time.sleep(0.22)

        # -------------------------
        # Phase 6：终章“整幅画点亮”（蓝笔触 + 金闪同拍连发）
        # -------------------------
        finale_ticks = int(round(22 * intensity))
        finale_ticks = max(18, finale_ticks)

        for k in range(finale_ticks):
            a = k * 0.35

            # 蓝色高光刷：横向大笔触（像油画扫亮）
            N = int(round(16 * intensity))
            N = max(12, N)
            z_row = 14.0 + 26.0 * math.sin(0.2 * k)  # 行在上半区游走
            for i in range(N):
                u = (i / max(1, N - 1)) * 2.0 - 1.0
                px = u * 48.0
                pz = z_row + 6.0 * math.sin(u * 2.0 + a)

                vx = 10.0 + 6.0 * math.sin(a + u)
                vz = 3.0 * math.cos(a * 0.8 + u * 2.0)
                vy = clamp_vy(18.0 + 5.0 * intensity)

                col = NIGHT_4 if (i + k) % 3 == 0 else NIGHT_3
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            # 金闪：在星云核心附近打几发高亮星爆（非常爽）
            gold_bursts = int(round(6 * intensity))
            gold_bursts = max(4, gold_bursts)
            for j in range(gold_bursts):
                th = a + j * (2.0 * math.pi / gold_bursts)
                sx = cx + 10.0 * math.cos(th)
                sz = cz + 10.0 * math.sin(th)

                vx = 14.0 * math.cos(th)
                vz = 14.0 * math.sin(th)
                vy = clamp_vy(36.0)

                ftype = [T.double_ball, T.planet_random_color, T.mixed_color_ball][(k + j) % 3]
                fire((sx, 0.0, sz), (vx, vy, vz), ftype, STAR_1)

            time.sleep(0.07)


    def climax_aurora_gate_10(self, intensity=1.0):
        T = self.type_firework
        MIN_VY = 12.0

        intensity = max(0.4, float(intensity))

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # =========================
        # 梵高不需要，这里是“极光舞台门”的调色板（RGB 0~255）
        # =========================
        # 极光绿 -> 青 -> 蓝 -> 紫（高光）
        AURORA = [
            (40, 255, 160),
            (20, 210, 180),
            (40, 170, 255),
            (120, 120, 255),
            (200, 120, 255),
        ]
        # 门节点金白（像舞台灯珠）
        GOLD = (255, 220, 110)
        WHITEGOLD = (255, 245, 220)

        # =========================
        # 舞台尺度（很大）
        # =========================
        X_LEFT = -48.0
        X_RIGHT = 48.0
        Z_SPAN = 34.0

        # 发射密度（越大越壮观）
        curtains = int(round(10 * intensity))     # 每侧极光帘条数
        curtains = max(8, curtains)

        pulses = int(round(20 * intensity))       # 极光推进“脉冲次数”（时间长度）
        pulses = max(16, pulses)

        # 每个脉冲每侧发几条“帘丝”（同一帘里做多丝更像帘布）
        strands = int(round(4 * intensity))
        strands = max(3, strands)

        # =========================
        # Phase 1：左右极光拱门生成（主体：T.nothing）
        # - 不做漩涡：不绕圈，只做“向上+向内”的拱形弹道
        # - 通过不同 curtain 的角度/高度形成“门”的轮廓
        # =========================
        for p in range(pulses):
            # 进度 0..1
            u = p / max(1, pulses - 1)

            # 门的“开合感”：中段最强，前后略弱（像舞台灯慢慢开到最亮）
            power = 0.70 + 0.55 * math.sin(math.pi * u)

            # 随时间轻微变换：让每次规律不一样但仍然像“帘”
            wob = math.sin(0.9 * p) * 0.8

            # 这次脉冲选择主色（渐变滚动）
            c_main = AURORA[p % len(AURORA)]
            c_hi = AURORA[(p + 2) % len(AURORA)]

            for c in range(curtains):
                # curtain 的位置分布：覆盖整条门，前后景都有（强 3D）
                z_base = (c / max(1, curtains - 1)) * 2.0 - 1.0  # [-1,1]
                z = z_base * (Z_SPAN * 0.5)

                # 每条帘的“向内角度”：靠上/靠中更往中心收
                inward = 26.0 + 18.0 * (1.0 - abs(z_base))  # 中间更收
                upward = 34.0 + 16.0 * (1.0 - abs(z_base))  # 中间更高

                # 轻微深度扰动（不是旋涡，只是极光的抖动）
                z_jit = 3.0 * math.sin(p * 0.55 + c * 0.9) + wob

                # ---- 左门帘：从左往中心拱 ----
                for s in range(strands):
                    # 多丝：让帘布更厚、更“帘”
                    off = (s - (strands - 1) / 2.0) * (1.6 + 0.6 * power)
                    posL = (X_LEFT, 0.0, z + z_jit + off)

                    vxL = inward * power
                    vzL = (6.0 * z_base + 4.0 * math.sin(p * 0.45 + s)) * power
                    vyL = clamp_vy((upward * power) + 8.0)

                    # 颜色：丝与丝之间做高光交替
                    colL = c_main if (s % 2 == 0) else c_hi
                    fire(posL, (vxL, vyL, vzL), T.nothing, colL)

                # ---- 右门帘：从右往中心拱 ----
                for s in range(strands):
                    off = (s - (strands - 1) / 2.0) * (1.6 + 0.6 * power)
                    posR = (X_RIGHT, 0.0, z - z_jit - off)

                    vxR = -inward * power
                    vzR = (-6.0 * z_base + 4.0 * math.cos(p * 0.42 + s)) * power
                    vyR = clamp_vy((upward * power) + 8.0)

                    colR = c_main if (s % 2 == 0) else c_hi
                    fire(posR, (vxR, vyR, vzR), T.nothing, colR)

            # 节奏：持续推进但不“断层”
            time.sleep(0.06)

        time.sleep(0.25)

        # =========================
        # Phase 2：拱门“节点点亮”（球系/行星爆炸）
        # - 让观众明确看到“门的骨架”被点亮
        # =========================
        node_types = [T.planet_ball, T.planet_random_color, T.double_ball, T.mixed_color_ball, T.half_half_color_ball]
        node_rings = int(round(5 * intensity))
        node_rings = max(4, node_rings)

        for ring in range(node_rings):
            # 节点分布在左右两侧与上方区域（大门的“铆钉灯”）
            N = 10 + ring * 2
            N = int(round(N * intensity))
            N = max(10, N)

            # 节点“更大更高”：后几圈更猛烈
            up = 34.0 + ring * 3.5
            inw = 22.0 + ring * 2.0

            for i in range(N):
                th = (2.0 * math.pi) * (i / N)

                # 位置：靠两侧，但略向中心（像门边灯带）
                side = -1.0 if (i % 2 == 0) else 1.0
                px = side * (44.0 - ring * 4.0)
                pz = (Z_SPAN * 0.55) * math.sin(th) + 8.0 * math.sin(th * 0.5)

                # 速度：向内 + 向上（不旋转）
                vx = -side * inw
                vz = 8.0 * math.sin(th)  # 轻微沿深度铺开
                vy = clamp_vy(up)

                ftype = node_types[(i + ring) % len(node_types)]
                col = GOLD if (i % 3 != 0) else WHITEGOLD
                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 5 == 0:
                    time.sleep(0.01)

            time.sleep(0.10)

        time.sleep(0.22)

        # =========================
        # Phase 3：门内辉光（中心金白“光瀑”）
        # - 让整个门“亮起来”，把高潮推到最满
        # =========================
        glow_ticks = int(round(28 * intensity))
        glow_ticks = max(22, glow_ticks)

        for k in range(glow_ticks):
            a = k * 0.35
            # 每 tick 生成两层：一层是金色粒点（爆），一层是白金光丝（nothing）
            # 让门内像舞台烟雾被灯打亮
            innerN = int(round(10 * intensity))
            innerN = max(8, innerN)

            # 白金光丝（更连贯）
            for i in range(innerN):
                u = (i / max(1, innerN - 1)) * 2.0 - 1.0
                px = u * 16.0
                pz = 10.0 * math.sin(a * 0.7 + u * 2.0)  # 门内轻微起伏

                vx = 3.0 * math.sin(a + u)
                vz = 3.0 * math.cos(a * 0.8 + u * 1.7)
                vy = clamp_vy(22.0 + 6.0 * intensity)

                col = WHITEGOLD if (i + k) % 3 == 0 else GOLD
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            # 金色闪点（更炸、更华丽）
            if k % 2 == 0:
                sparks = int(round(6 * intensity))
                sparks = max(4, sparks)
                for j in range(sparks):
                    th = a + j * (2.0 * math.pi / sparks)
                    px = 10.0 * math.cos(th)
                    pz = 12.0 * math.sin(th)

                    vx = 10.0 * math.cos(th)
                    vz = 10.0 * math.sin(th)
                    vy = clamp_vy(36.0)

                    ftype = [T.circle, T.random_color, T.double_ball][(k + j) % 3]
                    fire((px, 0.0, pz), (vx, vy, vz), ftype, GOLD)

            time.sleep(0.07)

        time.sleep(0.30)

    def climax_bloom_superfield_low_flower_love(self, intensity=1.0):
        T = self.type_firework
        intensity = 0.2
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # -------------------------
        # 伪随机（不依赖 random）
        # -------------------------
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # -------------------------
        # 配色：花海的三套色域（你也可以按主题改）
        # -------------------------
        # A：粉紫梦幻
        A1, A2, A3 = (255, 120, 190), (190, 110, 255), (255, 180, 230)
        # B：青绿霓彩
        B1, B2, B3 = (60, 220, 200), (40, 170, 255), (120, 255, 170)
        # C：金橙华丽
        C1, C2, C3 = (255, 220, 110), (255, 150, 80), (255, 245, 220)

        palettes = [
            (A1, A2, A3),
            (B1, B2, B3),
            (C1, C2, C3),
        ]

        # 主体爆炸类型池（花/爱心少用）
        main_types = [
            T.planet_random_color, T.planet_ball,
            T.double_ball, T.mixed_color_ball, T.half_half_color_ball,
            T.random_color, T.circle, T.ball, T.ball_up
        ]

        # 花与爱心：只做极少点缀
        accent_types = [T.flower, T.love_3D]

        # -------------------------
        # 花海结构：3 高度层 * 2 纵深层
        # -------------------------
        layers = [
            # (radius, vy_base, depth_shift, count_per_pulse)
            (26.0, 30.0, -14.0, int(round(18 * intensity))),  # 低层（更宽）
            (22.0, 33.0,  14.0, int(round(16 * intensity))),  # 中层
            (18.0, 36.0,   0.0, int(round(14 * intensity))),  # 高层（更集中）
        ]

        # 脉冲次数（越多越“花海铺满”）
        pulses = int(round(16 * intensity))
        pulses = max(12, pulses)

        # -------------------------
        # Phase 1：快速铺“花海底”（密集但有秩序的环状分布 + 深度错层）
        # -------------------------
        for p in range(pulses):
            ph = p * (0.35 + 0.08 * rnd())  # 每次相位变化不同，避免重复感
            pal = palettes[p % len(palettes)]
            # 每次脉冲：三层同时打，形成“整片开花”
            for li, (R, vy0, dshift, cnt) in enumerate(layers):
                cnt2 = max(10, cnt + int(round((rnd() - 0.5) * 6)))  # 每次数量微变
                for i in range(cnt2):
                    th = (2.0 * math.pi) * (i / cnt2) + ph + (li * 0.18)

                    # 起点：轻微散开（像花朵从空气里冒出来）
                    px0 = 2.5 * math.cos(th * 1.7)
                    pz0 = 2.5 * math.sin(th * 1.4) + dshift * 0.15

                    # 速度：径向扩张 + 少量纵深起伏（不旋涡）
                    vx = (R * 0.42) * math.cos(th) + (rnd() * 2.0 - 1.0) * 2.0
                    vz = (R * 0.42) * math.sin(th) + dshift + 6.0 * math.sin(th * 0.6)

                    vy = clamp_vy(vy0 + 0.08 * (abs(vx) + abs(vz)))

                    # 类型：绝大部分用 main_types
                    ftype = main_types[(p + i + li) % len(main_types)] if rnd() < 0.4 else T.random_color

                    # 颜色：同一脉冲内做三色轮换，形成“花海花色分区”
                    col = pal[i % 3]
                    fire((px0, 0.0, pz0), (vx, vy, vz), ftype, col)

                    if i % 6 == 0:
                        time.sleep(0.004)

            # 极少“花/爱心”点缀：每 4 个脉冲只给 1~2 发
            if p % 4 == 0:
                accents = 1 if rnd() < 0.6 else 2
                for a in range(accents):
                    th = ph + a * 2.2
                    vx = 12.0 * math.cos(th)
                    vz = 12.0 * math.sin(th)
                    vy = clamp_vy(34.0)

                    ftype = accent_types[(p + a) % len(accent_types)]
                    col = (255, 200, 230) if ftype == T.flower else (255, 245, 220)
                    fire((0.0, 0.0, 0.0), (vx, vy, vz), ftype, col)

            time.sleep(0.08)

        time.sleep(0.25)

        # -------------------------
        # Phase 2：超级扩张终章（把“花海”推到最大画幅）
        # - 大半径、更多点、金白高光穿插
        # -------------------------
        finale_ticks = int(round(22 * intensity))
        finale_ticks = max(18, finale_ticks)

        for k in range(finale_ticks):
            a = k * 0.42 + 0.6 * math.sin(k * 0.3)

            # 每 tick 两圈：外圈更大更炸，内圈更密更亮
            for ring in range(2):
                R = (34.0 if ring == 0 else 22.0) + 4.0 * math.sin(a + ring)
                N = int(round((22 if ring == 0 else 18) * intensity))
                N = max(14, N)

                for i in range(N):
                    th = (2.0 * math.pi) * (i / N) + a

                    px0 = 0.0
                    pz0 = 0.0

                    vx = (R * 0.46) * math.cos(th) + (rnd() * 2.0 - 1.0) * 3.0
                    vz = (R * 0.46) * math.sin(th) + (rnd() * 2.0 - 1.0) * 6.0
                    vy = clamp_vy((38.0 if ring == 0 else 34.0) + 0.08 * (abs(vx) + abs(vz)))

                    ftype = [T.double_ball, T.mixed_color_ball, T.planet_random_color, T.half_half_color_ball][(k + i + ring) % 4] if rnd() < 0.3 else T.random_color

                    # 颜色：金白高光为主，少量彩色点亮
                    if (i + k) % 5 == 0:
                        col = (255, 245, 220)
                    elif (i + k) % 3 == 0:
                        col = (255, 220, 110)
                    else:
                        pal = palettes[(k + ring) % len(palettes)]
                        col = pal[i % 3]

                    fire((px0, 0.0, pz0), (vx, vy, vz), ftype, col)

                    if i % 7 == 0:
                        time.sleep(0.004)

            # 最后只给一次 flower 作为“花海签名”（非常少）
            if k == finale_ticks - 2:
                fire((0.0, 0.0, 0.0), (0.0, clamp_vy(40.0), 0.0), T.flower, (255, 200, 230))

            time.sleep(0.07)

        time.sleep(0.25)


    def climax_rainbow_waterfall(self, intensity=1.0):
        T = self.type_firework
        intensity = 0.5
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # -------------------------
        # 彩虹色带（RGB 0~255）
        # -------------------------
        R = (255, 70, 70)
        O = (255, 140, 60)
        Y = (255, 230, 80)
        G = (60, 230, 120)
        C = (60, 210, 255)
        B = (60, 120, 255)
        P = (190, 90, 255)
        RAINBOW = [R, O, Y, G, C, B, P]

        # -------------------------
        # 瀑布尺寸（很大）
        # -------------------------
        WIDTH = 52.0          # 瀑布宽度（越大越震撼）
        TOP_Z = 34.0          # 瀑布从偏前景开始
        DEPTH_SWAY = 18.0     # 水幕在 z 上的“前后起伏”（更 3D）
        Y_SHIFT = 0.0

        # -------------------------
        # 密度控制
        # -------------------------
        # 帘线数量：越多越像“水幕”
        curtains = int(round(28 * intensity))
        curtains = max(20, curtains)

        # 每条帘线每个节拍喷几滴（点越多越“连成水流”）
        drops = int(round(3 + 3 * intensity))
        drops = max(3, drops)

        # 总节拍数：这一波持续时间（更长更壮观）
        ticks = int(round(120 * intensity))  # intensity=1 大约 120 * 0.05 ~ 6秒左右
        ticks = max(90, ticks)

        # 节拍间隔：越小越密
        dt = 0.05 / max(0.7, intensity)

        # -------------------------
        # 倾斜方向：让瀑布“往舞台中心/前方倾泻”
        # 由于 vy 不能为负，我们用 vx/vz 来做“下落错觉”，vy 稳定上扬保证合法
        # -------------------------
        tilt_x = -18.0   # 整体向左倾斜（你可以改成 +18 向右）
        tilt_z = -10.0   # 整体向观众方向倾斜（或反过来）

        # -------------------------
        # Phase 1：建立水幕（清晰彩虹帘）
        # -------------------------
        for k in range(ticks):
            t = k * dt

            # 水幕“呼吸”：中段最强，前后稍弱（更像瀑布浪头）
            swell = 0.75 + 0.45 * math.sin(min(1.0, t / (ticks * dt)) * math.pi)

            # z 方向起伏：让水幕有体积（不是平板）
            z_wave = TOP_Z + (DEPTH_SWAY * 0.5) * math.sin(t * 0.9)

            for i in range(curtains):
                u = (i / max(1, curtains - 1)) * 2.0 - 1.0  # [-1,1]
                x_line = u * (WIDTH * 0.5)

                # 每条帘线固定一种彩虹色（排列清晰）
                col = RAINBOW[i % len(RAINBOW)]

                # 帘线自身也有轻微摆动（让瀑布活起来，但仍规整）
                x_jit = 2.2 * math.sin(t * 1.6 + u * 2.0)
                z_line = z_wave + (DEPTH_SWAY * 0.35) * math.sin(u * 1.6 + t * 1.1)

                # 每条帘线每 tick 多滴“水”
                for d in range(drops):
                    # 滴的位置：沿同一帘线略错开
                    off = (d - (drops - 1) / 2.0) * 1.3
                    px = x_line + x_jit
                    pz = z_line + off

                    # 速度：向“倾斜方向”推进，vy 稳定上扬（合法），营造倾泻动势
                    vx = (tilt_x + 8.0 * math.sin(t * 1.2 + u * 1.5)) * swell
                    vz = (tilt_z + 6.0 * math.cos(t * 1.0 + u * 1.1)) * swell

                    # 上扬：足够高，且随水幕浪头略变化
                    vy = clamp_vy((20.0 + 8.0 * swell) + 0.06 * (abs(vx) + abs(vz)))

                    fire((px, Y_SHIFT, pz), (vx, vy, vz), T.nothing, col)

                # 偶尔加入“水花闪点”（很少，不会盖住彩虹帘）
                if (k % 7 == 0) and (i % 5 == 0):
                    vx = (tilt_x * 0.6) + 10.0 * math.sin(t + i)
                    vz = (tilt_z * 0.6) + 10.0 * math.cos(t + i * 0.7)
                    vy = clamp_vy(30.0 + 4.0 * swell)

                    splash_type = [T.circle, T.ball, T.random_color][(k + i) % 3]
                    # 水花用偏白的彩色高光（更像折射）
                    splash_col = (min(255, col[0] + 60), min(255, col[1] + 60), min(255, col[2] + 60))
                    fire((px, Y_SHIFT, pz), (vx, vy, vz), splash_type, splash_col)

            time.sleep(dt)

        time.sleep(0.25)

        # -------------------------
        # Phase 2：瀑布“顶冠”爆闪（把画面推到最大）
        # 在瀑布顶部打一圈彩虹爆闪，让观众觉得“瀑布是从天穹倾泻”
        # -------------------------
        crown = int(round(70 * intensity))
        crown = max(50, crown)

        for i in range(crown):
            u = (i / max(1, crown - 1)) * 2.0 - 1.0
            px = u * (WIDTH * 0.52)
            pz = TOP_Z + 18.0 + 8.0 * math.sin(u * 3.0)

            # 爆闪向外扩散但不旋涡
            vx = 14.0 * u
            vz = 10.0 * math.sin(u * 2.5)
            vy = clamp_vy(36.0)

            col = RAINBOW[i % len(RAINBOW)]
            ftype = [T.double_ball, T.mixed_color_ball, T.planet_random_color, T.half_half_color_ball][i % 4]
            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 8 == 0:
                time.sleep(0.01)

        time.sleep(0.30)


    def climax_kaleidoscope_rift(self, intensity=1.0):
        T = self.type_firework
        intensity = 0.5
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # -------------------------
        # 伪随机（不依赖 random），每次运行都不同
        # -------------------------
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # -------------------------
        # HSV->RGB（0..1）再转 0..255，方便做霓虹渐变
        # -------------------------
        def hsv_to_rgb255(h, s, v):
            h = h % 1.0
            i = int(h * 6.0)
            f = h * 6.0 - i
            p = v * (1.0 - s)
            q = v * (1.0 - f * s)
            t = v * (1.0 - (1.0 - f) * s)
            i = i % 6
            if i == 0:
                r, g, b = v, t, p
            elif i == 1:
                r, g, b = q, v, p
            elif i == 2:
                r, g, b = p, v, t
            elif i == 3:
                r, g, b = p, q, v
            elif i == 4:
                r, g, b = t, p, v
            else:
                r, g, b = v, p, q
            return (int(r * 255), int(g * 255), int(b * 255))

        # -------------------------
        # 类型池：万花筒节点爆闪（尽量炫）
        # -------------------------
        burst_pool = [
            T.double_ball,
            T.mixed_color_ball,
            T.half_half_color_ball,
            T.planet_random_color,
            T.planet_ball,
            T.random_color,
            T.circle,
        ]

        # -------------------------
        # 画面尺度（很大）
        # -------------------------
        R_OUT = 48.0   # 外圈碎片尖端半径
        R_IN = 18.0    # 内圈裂隙附近半径
        DEPTH = 26.0   # 前后景深度层

        # 每帧间隔
        dt = 0.07 / max(0.7, intensity)

        # 总帧数（这一波时长）
        frames = int(round(20 * intensity))
        frames = max(20, frames)

        # -------------------------
        # Phase 0：先点亮“裂隙骨架”（中心裂纹，不旋涡）
        # -------------------------
        crack_segs = int(round(6 * intensity))
        crack_segs = max(8, crack_segs)
        for i in range(crack_segs):
            u = i / max(1, crack_segs - 1)
            # 折线裂纹：不规则、像破碎玻璃
            px = (-18.0 + 36.0 * u) + 6.0 * math.sin(u * 7.0 + rnd() * 2.0)
            pz = (8.0 * math.sin(u * 4.0 + 0.7) + 10.0 * math.cos(u * 3.0 + 0.2)) + (rnd() * 2.0 - 1.0) * 2.0
            vx = (rnd() * 2.0 - 1.0) * 6.0
            vz = (rnd() * 2.0 - 1.0) * 6.0
            vy = clamp_vy(20.0 + 6.0 * intensity)
            # 冷白裂光
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, (245, 250, 255))
            if i % 5 == 0:
                time.sleep(0.01)

        time.sleep(0.18)

        # -------------------------
        # Phase 1：万花筒碎片“翻动”
        # 关键：每帧改变扇区数量、边界抖动、色相偏移、深度层策略 -> 不重复
        # -------------------------
        for f in range(frames):
            t = f * dt

            # 扇区数量：每帧变化（8~16）
            shards = 4 + int(rnd() * 9)  # 8..16
            shards = max(4, min(shards, 16))
            dth = (2.0 * math.pi) / max(1, shards)

            # 本帧的整体色相偏移（霓虹变奏）
            hue0 = rnd()
            sat = 0.85 + 0.12 * rnd()
            val = 0.85 + 0.12 * rnd()

            # “碎片边界”抖动（让碎片像在裂隙中翻动）
            jitter = 0.18 + 0.22 * rnd()

            # 每帧控制“纹理密度”：像万花筒内部的玻璃纹
            ribs = 2 + int(rnd() * 3)  # 2..4
            rib_pts = int(round((6 + 4 * intensity) * (0.9 + 0.4 * rnd())))
            rib_pts = max(6, rib_pts)

            # 末端爆闪密度（不要每帧都炸，避免视觉疲劳）
            flash_this_frame = (f % 3 == 0) or (rnd() < 0.25)

            # 这一帧的前后景策略：交替深度，让画面立体
            depth_mode = f % 3

            # --- 遍历每个扇区，生成碎片边 + 内部纹理 ---
            for s in range(shards):
                th0 = s * dth
                th1 = (s + 1) * dth

                # 碎片角度轻微“开合”
                wob0 = (rnd() * 2.0 - 1.0) * jitter
                wob1 = (rnd() * 2.0 - 1.0) * jitter
                a0 = th0 + wob0
                a1 = th1 + wob1
                amid = 0.5 * (a0 + a1)

                # 深度层：让碎片在前后景错开（3D）
                if depth_mode == 0:
                    z_shift = (DEPTH * 0.65) * math.sin(amid * 1.7)
                elif depth_mode == 1:
                    z_shift = (DEPTH * 0.65) * math.cos(amid * 1.3)
                else:
                    z_shift = (DEPTH * 0.35) * (1.0 if (s % 2 == 0) else -1.0)

                # 本扇区主色（霓虹渐变）
                col_main = hsv_to_rgb255(hue0 + (s / shards) * 0.55, sat, val)
                col_edge = hsv_to_rgb255(hue0 + (s / shards) * 0.55 + 0.08, min(1.0, sat + 0.10), min(1.0, val + 0.12))

                # 1) 碎片边（两条边 + 外圈边）
                edge_pts = int(round((3 + 4 * intensity) * (0.9 + 0.3 * rnd())))
                edge_pts = max(3, edge_pts)

                # 两条辐射边：从内圈到外圈
                for i in range(edge_pts):
                    u = i / max(1, edge_pts - 1)
                    r = R_IN + (R_OUT - R_IN) * u

                    # 边 A
                    px = r * math.cos(a0)
                    pz = r * math.sin(a0) + z_shift
                    vx = 10.0 * math.cos(a0) + 4.0 * (rnd() * 2.0 - 1.0)
                    vz = 10.0 * math.sin(a0) + 4.0 * (rnd() * 2.0 - 1.0)
                    vy = clamp_vy(18.0 + 10.0 * intensity)
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col_edge)

                    # 边 B
                    px = r * math.cos(a1)
                    pz = r * math.sin(a1) - z_shift * 0.7
                    vx = 10.0 * math.cos(a1) + 4.0 * (rnd() * 2.0 - 1.0)
                    vz = 10.0 * math.sin(a1) + 4.0 * (rnd() * 2.0 - 1.0)
                    vy = clamp_vy(18.0 + 10.0 * intensity)
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col_edge)

                # 外圈边：在 r=R_OUT 一段短弧（让碎片尖端轮廓更清晰）
                arc_pts = max(3, int(round(4 * intensity)))
                for i in range(arc_pts):
                    u = i / max(1, arc_pts - 1)
                    a = a0 + (a1 - a0) * u
                    px = R_OUT * math.cos(a)
                    pz = R_OUT * math.sin(a) + z_shift * 0.35
                    vx = 6.0 * math.cos(a) + 2.0 * (rnd() * 2.0 - 1.0)
                    vz = 6.0 * math.sin(a) + 2.0 * (rnd() * 2.0 - 1.0)
                    vy = clamp_vy(16.0 + 8.0 * intensity)
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col_main)

                # 2) 碎片内部“光栅纹理”（像玻璃折射纹）
                for rib in range(ribs):
                    # rib 在扇区内不同半径处
                    rr = R_IN + (R_OUT - R_IN) * (0.25 + 0.55 * rnd())
                    # rib 倾斜：让每帧都不一样
                    skew = (rnd() * 2.0 - 1.0) * 0.45

                    for p_i in range(rib_pts):
                        u = p_i / max(1, rib_pts - 1)
                        # 在扇区内插值取角度（稍带 skew）
                        a = (a0 + (a1 - a0) * u) + skew * (u - 0.5)
                        px = rr * math.cos(a)
                        pz = rr * math.sin(a) + z_shift * (0.2 + 0.6 * rnd())

                        # 纹理速度：轻微向外推开（不绕圈）
                        vx = 8.0 * math.cos(a) + 3.0 * (rnd() * 2.0 - 1.0)
                        vz = 8.0 * math.sin(a) + 3.0 * (rnd() * 2.0 - 1.0)
                        vy = clamp_vy(16.0 + 8.0 * intensity)

                        # 内纹比边略暗一点
                        col_in = hsv_to_rgb255(hue0 + (s / shards) * 0.55 + 0.03 * rib, sat * 0.92, val * 0.85)
                        fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col_in)

                # 3) “节点爆闪”：碎片尖端/中段偶尔炸一下，形成万花筒的“宝石”感
                if flash_this_frame and ((s + f) % 2 == 0):
                    # 尖端节点
                    px = R_OUT * math.cos(amid)
                    pz = R_OUT * math.sin(amid) + z_shift * 0.35

                    # 放射爆闪（不旋涡）
                    rad = 14.0 + 10.0 * rnd()
                    vx = rad * math.cos(amid) + (rnd() * 2.0 - 1.0) * 4.0
                    vz = rad * math.sin(amid) + (rnd() * 2.0 - 1.0) * 6.0
                    vy = clamp_vy(34.0 + 6.0 * intensity)

                    ftype = burst_pool[(s + f) % len(burst_pool)]
                    # 节点更亮更宝石
                    col_b = hsv_to_rgb255(hue0 + (s / shards) * 0.55, min(1.0, sat + 0.08), 1.0)
                    fire((px, 0.0, pz), (vx, vy, vz), ftype, col_b)

            # 中心裂隙“闪白一下”：每隔几帧给观众一个“裂缝在呼吸”的感觉
            if f % 4 == 0:
                flashes = int(round(10 * intensity))
                flashes = max(8, flashes)
                for i in range(flashes):
                    a = (2.0 * math.pi) * (i / flashes) + (rnd() - 0.5) * 0.6
                    vx = 12.0 * math.cos(a)
                    vz = 12.0 * math.sin(a)
                    vy = clamp_vy(30.0)
                    fire((0.0, 0.0, 0.0), (vx, vy, vz), T.circle, (255, 250, 245))

            time.sleep(dt)

        # -------------------------
        # Phase 2：终章 “Rift Bloom” —— 裂隙爆开彩虹晶体雨（超大收束）
        # -------------------------
        finale = int(round(120 * intensity))
        finale = max(70, finale)
        for i in range(finale):
            u = (i / max(1, finale - 1)) * 2.0 - 1.0
            # 以裂隙为中心向两侧扩张
            px = u * 54.0 + 6.0 * math.sin(i * 0.15)
            pz = 10.0 * math.sin(u * 3.0) + (rnd() * 2.0 - 1.0) * 10.0

            # 速度：像晶体雨“喷射扩散”
            vx = 16.0 * u + (rnd() * 2.0 - 1.0) * 6.0
            vz = 10.0 * math.sin(u * 2.2) + (rnd() * 2.0 - 1.0) * 10.0
            vy = clamp_vy(38.0 + 8.0 * rnd() + 4.0 * intensity)

            ftype = burst_pool[i % len(burst_pool)]
            col = hsv_to_rgb255((i / finale) + 0.15, 0.95, 1.0)
            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 8 == 0:
                time.sleep(0.01)

        time.sleep(0.25)


    def climax_phoenix_rise(self, intensity=1.0):
        T = self.type_firework
        intensity = 1
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # -------------------------
        # 伪随机（不依赖 random）
        # -------------------------
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # -------------------------
        # 凤凰火焰调色板（橙红金白）
        # -------------------------
        EMBER = (255, 80, 40)          # 炽红
        ORANGE = (255, 140, 60)        # 橙
        GOLD = (255, 220, 110)         # 金
        WHITEGOLD = (255, 245, 220)    # 白金高光
        MAGENTA = (255, 80, 170)       # 霞色点缀（少量）
        SMOKE = (60, 40, 30)           # 暗烟（用于轮廓阴影）

        # 主体爆炸类型池（不依赖 flower/love）
        burst_pool = [
            T.double_ball,
            T.mixed_color_ball,
            T.half_half_color_ball,
            T.planet_random_color,
            T.planet_ball,
            T.random_color,
            T.circle,
            T.ball,
            T.ball_up
        ]

        # -------------------------
        # 舞台尺度（大）
        # -------------------------
        WING_SPAN = 62.0     # 翼展
        HEIGHT_BIAS = 26.0   # 轮廓上扬高度基准
        DEPTH = 26.0         # 前后景层次

        # -------------------------
        # 辅助：凤凰翼轮廓曲线（半边），返回 (x,z) 的形状点
        # 说明：这是“具象轮廓”，不是旋涡。
        # u: 0..1 从身体到翼尖
        # side: -1 左翼, +1 右翼
        # -------------------------
        def wing_shape(u, side):
            # x：先缓慢展开，后段迅速拉长到翼尖
            x = side * ( (u ** 0.85) * (WING_SPAN * 0.5) )
            # z：翼是“上拱 + 羽尖下探”的形状（像鸟翼）
            z = (18.0 * math.sin(math.pi * u)) - (10.0 * (u ** 1.8))
            # 加少量“羽片参差”
            z += 2.6 * math.sin(8.0 * math.pi * u + (0.6 if side > 0 else -0.6))
            return x, z

        # -------------------------
        # 辅助：凤凰身体/尾羽曲线
        # u: 0..1，从下到上
        # -------------------------
        def body_shape(u):
            # 身体中心线在 x=0 附近，稍微有摆动
            x = 1.6 * math.sin(2.0 * math.pi * u)
            # 尾部更低，上半更高
            z = -24.0 + 54.0 * u - 6.0 * (u ** 2)
            return x, z

        # =========================
        # Phase 1：火羽散落（铺场：大量 ember 羽毛从两侧与下方飞起）
        # =========================
        feather_ticks = int(round(30 * intensity))
        feather_ticks = max(24, feather_ticks)

        for k in range(feather_ticks):
            t = k / max(1, feather_ticks - 1)
            # 每拍发射数量（很壮观）
            n = int(round((10 + 10 * intensity) * (0.7 + 0.6 * rnd())))
            n = max(10, n)

            for i in range(n):
                # 起点：两侧与底部的“火堆”区域
                pick = i % 3
                if pick == 0:
                    px = -30.0 + (rnd() * 2.0 - 1.0) * 8.0
                    pz = -34.0 + (rnd() * 2.0 - 1.0) * 6.0
                elif pick == 1:
                    px = 30.0 + (rnd() * 2.0 - 1.0) * 8.0
                    pz = -34.0 + (rnd() * 2.0 - 1.0) * 6.0
                else:
                    px = (rnd() * 2.0 - 1.0) * 18.0
                    pz = -40.0 + (rnd() * 2.0 - 1.0) * 4.0

                # 速度：向上为主，带一点向中心收拢（像火羽被吸起）
                pull = (1.0 - t)
                vx = (-px * 0.18) + (rnd() * 2.0 - 1.0) * 6.0
                vz = (-pz * 0.08) + (rnd() * 2.0 - 1.0) * 5.0
                vy = clamp_vy(18.0 + 10.0 * intensity + 10.0 * pull)

                # 色彩：橙红为主，少量金白/粉霞
                rsel = rnd()
                if rsel < 0.60:
                    col = EMBER
                elif rsel < 0.85:
                    col = ORANGE
                elif rsel < 0.95:
                    col = GOLD
                else:
                    col = MAGENTA

                # 主体用 nothing 做“羽毛光轨”，偶尔用 ball_up 做火舌
                ftype = T.ball_up if (i % 11 == 0 and k > feather_ticks * 0.3) else T.nothing
                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 8 == 0:
                    time.sleep(0.003)

            time.sleep(0.06)

        time.sleep(0.20)

        # =========================
        # Phase 2：凤凰轮廓显形（身体 + 双翼分层展开）
        # - 用 T.nothing 画出轮廓线
        # - 关键羽尖节点用少量爆闪点亮（非常华丽）
        # =========================
        outline_steps = int(round(44 * intensity))
        outline_steps = max(36, outline_steps)

        # 2A) 身体与尾羽（中心竖向骨架）
        for s in range(outline_steps):
            u = s / max(1, outline_steps - 1)
            x, z = body_shape(u)

            # 深度错层：让身体也有“立体骨架”
            depth = (DEPTH * 0.25) * math.sin(u * math.pi)

            # 身体几乎竖直，上扬明显
            vx = 0.6 * math.sin(u * 8.0)
            vz = 0.6 * math.cos(u * 7.0)
            vy = clamp_vy(24.0 + 18.0 * u + 6.0 * intensity)

            # 颜色：下部偏暗烟，向上逐渐金白
            if u < 0.25:
                col = SMOKE
            elif u < 0.70:
                col = ORANGE
            else:
                col = GOLD if (s % 3 != 0) else WHITEGOLD

            fire((x, 0.0, z + depth), (vx, vy, vz), T.nothing, col)

            # 尾部加一点“尾羽丝”
            if u < 0.35 and (s % 2 == 0):
                for tail in range(3):
                    side = -1.0 if tail % 2 == 0 else 1.0
                    px = x + side * (2.0 + 1.2 * tail)
                    pz = z - 6.0 - 4.0 * tail
                    vx2 = side * (6.0 + 2.0 * tail)
                    vz2 = 2.0 * math.sin(s * 0.4 + tail)
                    vy2 = clamp_vy(20.0 + 3.0 * tail)
                    fire((px, 0.0, pz), (vx2, vy2, vz2), T.nothing, EMBER)

            time.sleep(0.02)

        time.sleep(0.18)

        # 2B) 双翼展开（多层羽片：外轮廓 + 内羽脉）
        wing_layers = 3  # 层数越多越华丽
        wing_pts = int(round(42 * intensity))
        wing_pts = max(34, wing_pts)

        for layer in range(wing_layers):
            layer_scale = 1.0 - 0.13 * layer
            layer_depth = (layer - (wing_layers - 1) / 2.0) * (DEPTH * 0.28)

            for s in range(wing_pts):
                u = s / max(1, wing_pts - 1)

                for side in (-1.0, 1.0):
                    wx, wz = wing_shape(u, side)
                    wx *= layer_scale
                    wz *= (0.95 + 0.08 * layer)

                    # 翼的起点与身体连接：整体上移一些
                    px = wx
                    pz = wz + HEIGHT_BIAS + layer_depth + 2.0 * math.sin(u * 2.2 + layer)

                    # 速度：让线条“显形”——沿翼方向外推，且上扬
                    # 不用旋转，直接用几何切线
                    # 近似切线：用相邻差分
                    u2 = min(1.0, u + 0.01)
                    wx2, wz2 = wing_shape(u2, side)
                    tx = (wx2 - wx) * 80.0
                    tz = (wz2 - wz) * 80.0

                    vx = tx * 0.35 + side * (3.0 + 2.0 * layer)
                    vz = tz * 0.20 + 2.0 * math.sin(u * 6.0 + layer)
                    vy = clamp_vy(26.0 + 10.0 * intensity + 10.0 * (1.0 - u))

                    # 颜色：内层偏橙，外轮廓偏金白高光
                    if layer == 0 and (s % 5 == 0):
                        col = WHITEGOLD
                    elif (s + layer) % 4 == 0:
                        col = GOLD
                    else:
                        col = ORANGE

                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    # 羽尖节点爆闪：只在外层、翼尖区域，少量但非常点睛
                    if layer == 0 and u > 0.72 and (s % 6 == 0):
                        bx = px
                        bz = pz
                        # 爆闪向外扩散（不旋涡）
                        rad = 18.0 + 10.0 * rnd()
                        bvx = side * rad * (0.75 + 0.2 * rnd())
                        bvz = (rnd() * 2.0 - 1.0) * 10.0
                        bvy = clamp_vy(36.0 + 6.0 * intensity)

                        ftype = burst_pool[(s + layer) % len(burst_pool)]
                        bcol = GOLD if (s % 12 != 0) else WHITEGOLD
                        fire((bx, 0.0, bz), (bvx, bvy, bvz), ftype, bcol)

                if s % 7 == 0:
                    time.sleep(0.005)

            time.sleep(0.10)

        time.sleep(0.25)

        # =========================
        # Phase 3：涅槃金核（胸口一次“金核爆” + 全翼二次点亮）
        # =========================
        # 3A) 胸口金核：位置在身体上部偏中
        core_x, core_z = (0.0, HEIGHT_BIAS + 16.0)

        core_bursts = int(round(90 * intensity))  # 很大很炸
        core_bursts = max(70, core_bursts)
        for i in range(core_bursts):
            th = (2.0 * math.pi) * (i / core_bursts)
            rad = 16.0 + 18.0 * rnd()

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 4.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 8.0
            vy = clamp_vy(42.0 + 8.0 * rnd() + 6.0 * intensity)

            ftype = burst_pool[i % len(burst_pool)]
            col = WHITEGOLD if i % 3 == 0 else GOLD
            fire((core_x, 0.0, core_z), (vx, vy, vz), ftype, col)

            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.15)

        # 3B) 全翼二次点亮：沿翼面撒一层“金粉”
        glow_sweeps = int(round(16 * intensity))
        glow_sweeps = max(12, glow_sweeps)

        for k in range(glow_sweeps):
            u = k / max(1, glow_sweeps - 1)
            # 从内到外扫一遍
            for side in (-1.0, 1.0):
                wx, wz = wing_shape(0.20 + 0.75 * u, side)
                px = wx
                pz = wz + HEIGHT_BIAS + 6.0 * math.sin(k * 0.4)

                vx = side * (10.0 + 12.0 * u)
                vz = 6.0 * math.cos(k * 0.6)
                vy = clamp_vy(34.0 + 6.0 * intensity)

                # 这层用 circle/random_color 少量点亮即可
                ftype = T.circle if (k % 2 == 0) else T.random_color
                col = GOLD if (k % 3 != 0) else WHITEGOLD
                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            time.sleep(0.06)

        time.sleep(0.25)



    def climax_rose_window(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.5, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # -------------------------
        # 伪随机（不依赖 random）
        # -------------------------
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # -------------------------
        # 彩窗调色板（典型彩绘玻璃：宝石色 + 金白高光 + 铅条暗色）
        # -------------------------
        LEAD = (25, 25, 35)          # 铅条暗色
        LEAD_HI = (60, 60, 80)       # 铅条高光（少量）
        GOLD = (255, 220, 120)       # 金边
        WHITE = (255, 245, 230)      # 圣光

        RUBY = (255, 60, 90)
        AMBER = (255, 140, 60)
        TOPAZ = (255, 210, 90)
        EMERALD = (60, 220, 130)
        CYAN = (60, 200, 255)
        SAPPHIRE = (80, 120, 255)
        AMETHYST = (190, 90, 255)
        WHITEGOLD = (255, 245, 220)

        GLASS = [RUBY, AMBER, TOPAZ, EMERALD, CYAN, SAPPHIRE, AMETHYST]

        # -------------------------
        # 类型池：彩窗宝石节点爆闪（少量）
        # -------------------------
        gem_pool = [
            T.mixed_color_ball,
            T.half_half_color_ball,
            T.double_ball,
            T.planet_ball,
            T.planet_random_color,
            T.circle
        ]

        # -------------------------
        # 玫瑰窗尺度（很大）
        # -------------------------
        R_OUT = 58.0
        R_MID = 38.0
        R_IN = 18.0
        DEPTH = 22.0   # 前后景层次（让彩窗更立体）

        # 花瓣数量（典型玫瑰窗 12~16）
        petals = int(round(12 + 4 * (rnd())))  # 12..16
        petals = max(12, min(petals, 16))

        # 肋骨数量（放射铅条）
        ribs = petals * 2

        # 密度
        ring_pts = int(round(60 * intensity))
        ring_pts = max(44, ring_pts)

        # -------------------------
        # 工具：在角度 a、半径 r 上取点并附加深度起伏
        # -------------------------
        def point_on_ring(r, a, depth_mode):
            # depth_mode: 0/1/2 让不同结构在不同前后景
            if depth_mode == 0:
                dz = (DEPTH * 0.55) * math.sin(a * 1.7)
            elif depth_mode == 1:
                dz = (DEPTH * 0.55) * math.cos(a * 1.3)
            else:
                dz = (DEPTH * 0.25) * (1.0 if int(a * 10) % 2 == 0 else -1.0)
            return (r * math.cos(a), r * math.sin(a) + dz)

        # ==========================================================
        # Phase 0：先出“铅条骨架”（三圈 + 肋骨），让形状一眼看懂
        # ==========================================================
        rings = [R_IN, R_MID, R_OUT]
        for ri, r in enumerate(rings):
            for i in range(ring_pts):
                a = (2.0 * math.pi) * (i / ring_pts)
                px, pz = point_on_ring(r, a, ri % 3)

                # 铅条：几乎径向轻推 + 上扬
                vx = 6.0 * math.cos(a) + (rnd() * 2.0 - 1.0) * 1.5
                vz = 6.0 * math.sin(a) + (rnd() * 2.0 - 1.0) * 1.5
                vy = clamp_vy(18.0 + 6.0 * intensity)

                col = LEAD_HI if (i % 11 == 0) else LEAD
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                if i % 10 == 0:
                    time.sleep(0.004)
            time.sleep(0.03)

        # 放射肋骨（从内到外的铅条）
        rib_steps = int(round(18 * intensity))
        rib_steps = max(14, rib_steps)

        for r_i in range(ribs):
            a = (2.0 * math.pi) * (r_i / ribs)
            for s in range(rib_steps):
                u = s / max(1, rib_steps - 1)
                r = R_IN + (R_OUT - R_IN) * u
                px, pz = point_on_ring(r, a, 2)

                vx = 7.0 * math.cos(a)
                vz = 7.0 * math.sin(a)
                vy = clamp_vy(18.0 + 6.0 * intensity)

                col = LEAD_HI if (s % 5 == 0 and r_i % 3 == 0) else LEAD
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            if r_i % 3 == 0:
                time.sleep(0.01)

        time.sleep(0.18)

        # ==========================================================
        # Phase 1：花瓣彩玻填充（扇区彩片 + 金边高光）
        # ==========================================================
        # 每个花瓣是一个扇区：在 R_MID~R_OUT 区域填“彩玻碎片纹”
        sector_pts = int(round(22 * intensity))
        sector_pts = max(18, sector_pts)

        sector_ribs = int(round(6 * intensity))
        sector_ribs = max(5, sector_ribs)

        dth = (2.0 * math.pi) / petals

        for p in range(petals):
            a0 = p * dth
            a1 = (p + 1) * dth
            amid = 0.5 * (a0 + a1)

            # 本花瓣主色：宝石色轮换
            base = GLASS[p % len(GLASS)]
            alt = GLASS[(p + 3) % len(GLASS)]

            # 1) 花瓣边（金边高光）
            edgeN = int(round(16 * intensity))
            edgeN = max(12, edgeN)
            for i in range(edgeN):
                u = i / max(1, edgeN - 1)
                a = a0 + (a1 - a0) * u
                px, pz = point_on_ring(R_OUT, a, 0)

                vx = 8.0 * math.cos(a)
                vz = 8.0 * math.sin(a)
                vy = clamp_vy(20.0 + 8.0 * intensity)

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, GOLD)

                if i % 6 == 0:
                    time.sleep(0.003)

            # 2) 花瓣内部“彩玻碎片纹理”（多条短弧 + 短径向线）
            for rib in range(sector_ribs):
                rr = R_MID + (R_OUT - R_MID) * (0.18 + 0.70 * rnd())
                skew = (rnd() * 2.0 - 1.0) * 0.25

                for i in range(sector_pts):
                    u = i / max(1, sector_pts - 1)
                    a = a0 + (a1 - a0) * u + skew * (u - 0.5)

                    px, pz = point_on_ring(rr, a, 1)

                    # 彩玻的“光泽”：轻推 + 上扬
                    vx = 7.0 * math.cos(a) + (rnd() * 2.0 - 1.0) * 2.0
                    vz = 7.0 * math.sin(a) + (rnd() * 2.0 - 1.0) * 2.0
                    vy = clamp_vy(18.0 + 8.0 * intensity)

                    # 同花瓣内两色交织，像彩窗拼片
                    col = base if ((i + rib) % 2 == 0) else alt
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    if i % 7 == 0:
                        time.sleep(0.003)

            # 3) 花瓣“宝石节点”爆闪（很少但非常华丽）
            if p % 2 == 0:
                node_r = R_MID + (R_OUT - R_MID) * 0.78
                px, pz = point_on_ring(node_r, amid, 0)
                rad = 16.0 + 10.0 * rnd()
                vx = rad * math.cos(amid)
                vz = rad * math.sin(amid)
                vy = clamp_vy(36.0 + 6.0 * intensity)
                ftype = gem_pool[p % len(gem_pool)]
                fire((px, 0.0, pz), (vx, vy, vz), ftype, WHITE)
                time.sleep(0.02)

            time.sleep(0.03)

        time.sleep(0.20)

        # ==========================================================
        # Phase 2：中心玫瑰芯（内圈花瓣 + 十字光）
        # ==========================================================
        core_petals = int(round(8 + 2 * rnd()))  # 8~10
        core_petals = max(8, min(core_petals, 10))
        core_dth = (2.0 * math.pi) / core_petals

        core_pts = int(round(20 * intensity))
        core_pts = max(16, core_pts)

        for p in range(core_petals):
            a0 = p * core_dth
            a1 = (p + 1) * core_dth
            amid = 0.5 * (a0 + a1)

            col = GLASS[(p + 1) % len(GLASS)]
            for i in range(core_pts):
                u = i / max(1, core_pts - 1)
                # 内芯像花朵：半径在 R_IN 附近起伏
                r = R_IN * (0.55 + 0.35 * math.sin(u * math.pi))
                a = a0 + (a1 - a0) * u
                px, pz = point_on_ring(r, a, 2)

                vx = 6.0 * math.cos(a)
                vz = 6.0 * math.sin(a)
                vy = clamp_vy(18.0 + 8.0 * intensity)

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            # 内芯节点爆闪（更集中）
            if p % 3 == 0:
                rad = 14.0 + 8.0 * rnd()
                vx = rad * math.cos(amid)
                vz = rad * math.sin(amid)
                vy = clamp_vy(34.0 + 6.0 * intensity)
                ftype = gem_pool[(p + 2) % len(gem_pool)]
                fire((0.0, 0.0, 0.0), (vx, vy, vz), ftype, WHITEGOLD)

            time.sleep(0.03)

        # 十字光（教堂感）：水平/竖直两道“圣光”
        cross_len = 26.0
        cross_pts = int(round(18 * intensity))
        cross_pts = max(14, cross_pts)
        for i in range(cross_pts):
            u = (i / max(1, cross_pts - 1)) * 2.0 - 1.0
            # 横
            fire((u * cross_len, 0.0, 0.0), (6.0 * u, clamp_vy(28.0), 0.0), T.nothing, WHITE)
            # 竖（用 z 当“竖向”在你的平面里）
            fire((0.0, 0.0, u * cross_len), (0.0, clamp_vy(28.0), 6.0 * u), T.nothing, WHITE)
            time.sleep(0.01)

        time.sleep(0.20)

        # ==========================================================
        # Phase 3：终章“整窗通电”（外圈宝石雨 + 金白圣辉）
        # ==========================================================
        finale = int(round(120 * intensity))
        finale = max(90, finale)

        for i in range(finale):
            a = (2.0 * math.pi) * (i / finale)
            # 从外圈一圈打出“宝石雨”
            px, pz = point_on_ring(R_OUT, a, 0)

            rad = 18.0 + 14.0 * rnd()
            vx = rad * math.cos(a) + (rnd() * 2.0 - 1.0) * 4.0
            vz = rad * math.sin(a) + (rnd() * 2.0 - 1.0) * 6.0
            vy = clamp_vy(40.0 + 8.0 * rnd() + 6.0 * intensity)

            ftype = gem_pool[i % len(gem_pool)]
            # 颜色：宝石色 + 金白高光交替
            if i % 5 == 0:
                col = WHITEGOLD
            elif i % 3 == 0:
                col = GOLD
            else:
                col = GLASS[i % len(GLASS)]

            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.25)


    def climax_confetti_hurricane(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.5, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # -------------------------
        # 伪随机（不依赖 random）
        # -------------------------
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # -------------------------
        # 彩纸调色板（霓虹派对感）
        # 每个彩纸有“正面色”和“背面色”（翻面用）
        # -------------------------
        PAIRS = [
            ((255, 60, 120), (120, 30, 70)),     # 霓虹粉 <-> 暗粉
            ((60, 220, 255), (20, 90, 120)),     # 青蓝 <-> 深青
            ((255, 220, 80), (130, 90, 20)),     # 金黄 <-> 暗金
            ((120, 255, 120), (40, 120, 60)),    # 荧光绿 <-> 深绿
            ((190, 90, 255), (90, 40, 120)),     # 紫 <-> 深紫
            ((255, 140, 60), (120, 60, 20)),     # 橙 <-> 暗橙
            ((255, 245, 230), (120, 120, 120)),  # 白亮片 <-> 灰背面
        ]

        # 终章亮片爆闪类型（少量即可很华丽）
        glitter_pool = [
            T.mixed_color_ball, T.double_ball, T.planet_random_color, T.half_half_color_ball, T.circle
        ]

        # -------------------------
        # 场景尺度（满屏）
        # -------------------------
        WIDTH = 86.0     # x 覆盖范围
        DEPTH = 54.0     # z 覆盖范围
        SIDE_X = 52.0    # 侧面入口
        FAR_Z = 38.0     # 远处入口（给纵深）

        # 密度/节奏
        dt = 0.055 / max(0.7, intensity)
        ticks = int(round(150 * intensity))   # 约 150*0.055 = 8.25s（intensity=1）
        ticks = max(110, ticks)

        # 每拍彩纸数量（很壮观，但仍可控）
        per_tick = int(round(14 + 18 * intensity))
        per_tick = max(16, per_tick)

        # “翻面频率”：越小越频繁翻面
        flip_period = max(4, int(round(7 / max(0.7, intensity))))

        # -------------------------
        # 风场：不是固定旋转，而是“阵风脉冲 + 剪切 + 上升热流”
        # -------------------------
        def wind_field(t, u):
            # u 是空间采样参数（-1..1），让不同位置风略不同
            gust = 0.65 + 0.55 * math.sin(t * 0.9) + 0.25 * math.sin(t * 2.1)
            shear = 0.35 * math.sin(t * 0.6 + u * 2.5)

            wx = (22.0 * gust) + (14.0 * shear)
            wz = (10.0 * math.cos(t * 0.7) - 8.0 * math.sin(t * 1.1 + u))

            # 上升热流（一直>0）
            up = 20.0 + 8.0 * gust + 6.0 * math.sin(t * 1.3 + u)
            return wx, wz, up

        # -------------------------
        # “纸片片段”生成：用 2~3 条 very short 的 T.nothing 形成“片状闪烁”
        # -------------------------
        def emit_confetti_sheet(px, pz, vx, vy, vz, pair_idx, flip):
            front, back = PAIRS[pair_idx % len(PAIRS)]
            col = front if flip else back

            # 用小偏移的多条轨迹模拟“纸片边缘”
            # 偏移方向随机一点，但幅度小 -> 像一片在翻
            ox = (rnd() * 2.0 - 1.0) * 0.9
            oz = (rnd() * 2.0 - 1.0) * 0.9

            # 纸片“翻面抖动”：让速度在很小范围内抖一下
            jx = (rnd() * 2.0 - 1.0) * 3.0
            jz = (rnd() * 2.0 - 1.0) * 3.0

            # 2~3 条线段，视觉更像片状，不是单点
            fire((px, 0.0, pz), (vx + jx, clamp_vy(vy), vz + jz), T.nothing, col)
            fire((px + ox, 0.0, pz + oz), (vx - jx * 0.6, clamp_vy(vy + 1.2), vz - jz * 0.6), T.nothing, col)

            if (pair_idx + int(px) + int(pz)) % 3 == 0:
                fire((px - ox * 0.7, 0.0, pz - oz * 0.7),
                    (vx + jx * 0.3, clamp_vy(vy + 0.6), vz + jz * 0.3),
                    T.nothing, col)

        # ==========================================================
        # Phase 1：风暴建立（从两侧 + 远处大量卷入）
        # ==========================================================
        for k in range(ticks):
            t = k * dt

            # 每拍翻面状态（整片风暴同步有节奏地“闪一下”）
            flip = (k // flip_period) % 2 == 0

            # 阵风方向轻微改变（左右交替“拍打”）
            sway = math.sin(t * 0.8)  # -1..1

            for i in range(per_tick):
                # 入口选择：左/右/远处底边（让风暴更立体）
                sel = i % 3
                u = (i / max(1, per_tick - 1)) * 2.0 - 1.0  # -1..1

                if sel == 0:
                    # 左侧卷入
                    px = -SIDE_X + (rnd() * 2.0 - 1.0) * 4.0
                    pz = (rnd() * 2.0 - 1.0) * (DEPTH * 0.5)
                elif sel == 1:
                    # 右侧卷入
                    px = SIDE_X + (rnd() * 2.0 - 1.0) * 4.0
                    pz = (rnd() * 2.0 - 1.0) * (DEPTH * 0.5)
                else:
                    # 远处卷入（制造纵深）
                    px = (rnd() * 2.0 - 1.0) * (WIDTH * 0.5)
                    pz = FAR_Z + (rnd() * 2.0 - 1.0) * 6.0

                wx, wz, up = wind_field(t, u)

                # 基础速度：风场 + 一点向中心的“拉回”（形成风暴聚集）
                vx = (wx * (1.0 if sel != 1 else -1.0)) * 0.55 + (-px * 0.10) + 10.0 * sway
                vz = (wz * 0.70) + (-pz * 0.06) + 6.0 * math.cos(t * 0.9 + u)

                vy = clamp_vy(up + 6.0 * intensity + 0.05 * (abs(vx) + abs(vz)))

                # 纸片配色索引：随空间与时间变化，避免重复块
                pair_idx = int((k * 3 + i * 7 + (px + 1000)) * 0.37) % len(PAIRS)

                emit_confetti_sheet(px, pz, vx, vy, vz, pair_idx, flip)

                if i % 10 == 0:
                    time.sleep(0.002)

            # 偶尔来一发“彩纸爆散点”让观众更嗨（很少）
            if k % int(max(6, round(9 / max(0.7, intensity)))) == 0:
                # 在中心上方区域打一小团亮片感
                col = PAIRS[k % len(PAIRS)][0]
                vx = (rnd() * 2.0 - 1.0) * 18.0
                vz = (rnd() * 2.0 - 1.0) * 18.0
                vy = clamp_vy(34.0 + 6.0 * intensity)
                fire((0.0, 0.0, 10.0 * math.sin(t)), (vx, vy, vz), T.circle, col)

            time.sleep(dt)

        time.sleep(0.25)

        # ==========================================================
        # Phase 2：终章——全部变“亮片”爆闪（短而炸）
        # ==========================================================
        finale = int(round(90 * intensity))
        finale = max(70, finale)

        for i in range(finale):
            a = (2.0 * math.pi) * (i / finale)

            # 在全场分布几个爆点，让“亮片雨”铺满
            px = (WIDTH * 0.5) * math.cos(a) + (rnd() * 2.0 - 1.0) * 12.0
            pz = (DEPTH * 0.5) * math.sin(a) + (rnd() * 2.0 - 1.0) * 12.0

            rad = 18.0 + 16.0 * rnd()
            vx = rad * math.cos(a) + (rnd() * 2.0 - 1.0) * 6.0
            vz = rad * math.sin(a) + (rnd() * 2.0 - 1.0) * 8.0
            vy = clamp_vy(42.0 + 8.0 * rnd() + 6.0 * intensity)

            ftype = glitter_pool[i % len(glitter_pool)]
            # 终章颜色：大量白金 + 少量霓虹
            if i % 4 == 0:
                col = (255, 245, 230)
            elif i % 4 == 1:
                col = (255, 220, 120)
            else:
                col = PAIRS[i % len(PAIRS)][0]

            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.25)



    def climax_fountain_throne(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.5, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # -------------------------
        # 伪随机（不依赖 random）
        # -------------------------
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # -------------------------
        # 配色：王座喷泉（金白为主，青蓝为阴影与水光）
        # -------------------------
        GOLD = (255, 220, 120)
        WHITEGOLD = (255, 245, 230)
        AQUA = (70, 210, 255)
        DEEP_AQUA = (40, 140, 210)
        ROSE = (255, 120, 200)   # 少量点缀（宝石感）

        # 华丽节点类型池（少量）
        jewel_pool = [
            T.planet_ball, T.planet_random_color,
            T.mixed_color_ball, T.half_half_color_ball,
            T.double_ball, T.circle, T.random_color
        ]

        # -------------------------
        # 舞台尺寸（很大）
        # -------------------------
        W = 78.0      # 王座宽度
        D = 36.0      # 纵深
        X0 = 0.0
        Z0 = -6.0     # 王座中心稍偏后，显得像“坐在舞台里”
        ARM_Z = Z0 - 8.0
        BACK_Z = Z0 + 14.0

        # 柱阵与节奏
        dt = 0.06 / max(0.7, intensity)

        # 每根柱子喷几根“丝”（越多越像喷泉柱）
        strands = int(round(3 + 2 * intensity))
        strands = max(3, strands)

        # ==========================================================
        # Phase 1：底座喷泉柱阵（地基 + 扶手柱）
        # ==========================================================
        base_cols = int(round(14 * intensity))
        base_cols = max(12, base_cols)

        # 底座：一排宽阔喷泉柱
        for step in range(int(round(18 * intensity))):
            swell = 0.75 + 0.45 * math.sin(step * 0.35)  # 呼吸感
            for i in range(base_cols):
                u = (i / max(1, base_cols - 1)) * 2.0 - 1.0
                px = X0 + u * (W * 0.5)
                pz = Z0 + 0.25 * D * math.sin(u * math.pi)  # 中间略靠前形成“坐垫弧”

                # 速度：几乎竖直上喷 + 少量左右摇摆（水柱质感）
                vx_base = 4.0 * math.sin(step * 0.25 + u * 2.3)
                vz_base = 2.5 * math.cos(step * 0.22 + u * 1.8)
                vy_base = clamp_vy((22.0 + 12.0 * swell) + 6.0 * intensity)

                for s in range(strands):
                    off = (s - (strands - 1) / 2.0) * 1.6
                    col = GOLD if (i + s + step) % 3 != 0 else AQUA
                    fire((px + off, 0.0, pz - off * 0.6),
                        (vx_base + off * 0.8, vy_base, vz_base - off * 0.5),
                        T.nothing, col)

                # 柱顶偶尔亮一下（像灯杯）
                if step % 6 == 0 and i % 4 == 0:
                    fire((px, 0.0, pz),
                        (vx_base * 0.6, clamp_vy(34.0), vz_base * 0.6),
                        T.circle, WHITEGOLD)

            time.sleep(dt)

        time.sleep(0.20)

        # 扶手：左右两条“扶手喷泉轨”，更高更亮
        arm_pts = int(round(10 * intensity))
        arm_pts = max(8, arm_pts)

        for step in range(int(round(16 * intensity))):
            swell = 0.75 + 0.45 * math.sin(0.6 + step * 0.32)
            for side in (-1.0, 1.0):
                for i in range(arm_pts):
                    u = i / max(1, arm_pts - 1)
                    # 扶手从前到后延伸
                    px = X0 + side * (W * 0.45 + 2.0 * math.sin(u * math.pi))
                    pz = ARM_Z + u * (BACK_Z - ARM_Z) + 2.0 * math.sin(u * 2.0 + step * 0.2)

                    vx = (-side * 2.5) + 3.0 * math.sin(step * 0.25 + u * 3.0)
                    vz = 2.5 * math.cos(step * 0.20 + u * 2.2)
                    vy = clamp_vy((28.0 + 14.0 * swell) + 6.0 * intensity)

                    for s in range(strands):
                        off = (s - (strands - 1) / 2.0) * 1.4
                        col = WHITEGOLD if (step + i + s) % 5 == 0 else DEEP_AQUA
                        fire((px + off * 0.6, 0.0, pz + off),
                            (vx + off * 0.5, vy, vz - off * 0.4),
                            T.nothing, col)

                    if step % 5 == 0 and i % 3 == 0:
                        fire((px, 0.0, pz),
                            (vx * 0.6, clamp_vy(38.0), vz * 0.6),
                            T.ball, GOLD)

            time.sleep(dt)

        time.sleep(0.25)

        # ==========================================================
        # Phase 2：靠背与拱（王座轮廓最关键：大、对称、像“建筑”）
        # ==========================================================
        # 靠背立柱：左右 + 中间几根
        back_cols = [
            (-W * 0.38, BACK_Z),
            (-W * 0.20, BACK_Z + 2.0),
            (0.0, BACK_Z + 4.0),
            (W * 0.20, BACK_Z + 2.0),
            (W * 0.38, BACK_Z),
        ]

        for step in range(int(round(18 * intensity))):
            swell = 0.80 + 0.50 * math.sin(step * 0.30)
            for j, (px, pz) in enumerate(back_cols):
                # 中心更高，形成“王座背”
                height_bias = 1.0 + 0.55 * (1.0 - abs(j - (len(back_cols)-1)/2.0) / ((len(back_cols)-1)/2.0))
                vx = 2.0 * math.sin(step * 0.22 + j)
                vz = 2.0 * math.cos(step * 0.20 + j)
                vy = clamp_vy((34.0 + 18.0 * swell) * height_bias + 6.0 * intensity)

                for s in range(strands + 1):
                    off = (s - (strands) / 2.0) * 1.2
                    col = GOLD if (j + s + step) % 4 != 0 else WHITEGOLD
                    fire((px + off, 0.0, pz - off * 0.4),
                        (vx + off * 0.6, vy, vz - off * 0.3),
                        T.nothing, col)

                # 柱顶宝石灯
                if step % 6 == 0:
                    ftype = jewel_pool[(j + step) % len(jewel_pool)]
                    col = WHITEGOLD if j == 2 else GOLD
                    fire((px, 0.0, pz),
                        (0.0, clamp_vy(44.0), 0.0),
                        ftype, col)

            time.sleep(dt)

        time.sleep(0.22)

        # 拱：把靠背上沿连起来（像王座的“拱冠”）
        arch_pts = int(round(42 * intensity))
        arch_pts = max(34, arch_pts)

        for step in range(int(round(14 * intensity))):
            for i in range(arch_pts):
                u = (i / max(1, arch_pts - 1)) * 2.0 - 1.0
                # 拱形曲线：中间最高
                px = X0 + u * (W * 0.40)
                pz = BACK_Z + 8.0 + 8.0 * math.sin((1.0 - abs(u)) * math.pi * 0.5)

                # 上扬速度：构成拱的“光梁”
                vx = 6.0 * u
                vz = 3.0 * math.sin(u * 3.0 + step * 0.3)
                vy = clamp_vy(28.0 + 10.0 * intensity + 6.0 * (1.0 - abs(u)))

                col = WHITEGOLD if (i + step) % 7 == 0 else GOLD
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                # 拱梁节点少量炸一下（像彩灯）
                if step % 4 == 0 and i % 9 == 0:
                    ftype = jewel_pool[(i + step) % len(jewel_pool)]
                    jcol = ROSE if (i % 18 == 0) else WHITEGOLD
                    fire((px, 0.0, pz),
                        (vx * 0.4, clamp_vy(40.0), vz * 0.4),
                        ftype, jcol)

                if i % 10 == 0:
                    time.sleep(0.003)

            time.sleep(0.04)

        time.sleep(0.25)

        # ==========================================================
        # Phase 3：王冠终爆（中央冠冕 + 两侧翼尖同步）
        # ==========================================================
        crown_center = (0.0, BACK_Z + 18.0)

        # 3A) 中央冠冕：多尖角放射（不旋涡，纯放射）
        crown_spikes = int(round(64 * intensity))
        crown_spikes = max(50, crown_spikes)

        for i in range(crown_spikes):
            th = (2.0 * math.pi) * (i / crown_spikes)
            # 做“尖角感”：让半径有周期性起伏
            rad = 18.0 + 10.0 * (0.5 + 0.5 * math.sin(6.0 * th)) + 8.0 * rnd()

            vx = math.cos(th) * rad
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
            vy = clamp_vy(46.0 + 8.0 * rnd() + 6.0 * intensity)

            ftype = jewel_pool[i % len(jewel_pool)]
            col = WHITEGOLD if i % 3 == 0 else GOLD
            fire((crown_center[0], 0.0, crown_center[1]), (vx, vy, vz), ftype, col)

            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.15)

        # 3B) 两侧“王座翼尖”同步爆闪（让画面更宽、更大）
        wing_bursts = int(round(36 * intensity))
        wing_bursts = max(28, wing_bursts)

        for i in range(wing_bursts):
            side = -1.0 if i % 2 == 0 else 1.0
            px = side * (W * 0.48)
            pz = BACK_Z + 10.0 + 4.0 * math.sin(i * 0.4)

            th = (2.0 * math.pi) * (i / wing_bursts)
            rad = 16.0 + 10.0 * rnd()

            vx = -side * (10.0 + 8.0 * rnd())  # 向内喷
            vz = math.sin(th) * rad
            vy = clamp_vy(42.0 + 6.0 * intensity)

            ftype = [T.double_ball, T.mixed_color_ball, T.planet_random_color, T.circle][i % 4]
            col = AQUA if i % 3 == 0 else GOLD
            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 8 == 0:
                time.sleep(0.01)

        time.sleep(0.25)


    def climax_cloud_sea_gate(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.5, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            return float(v if v > MIN_VY else MIN_VY)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # --- 伪随机（不依赖 random）---
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # --- 配色：云（乳白/冷白/淡紫/银灰）+ 星海（金白/群青/青蓝）---
        CLOUD_A = (245, 248, 255)
        CLOUD_B = (220, 235, 255)
        CLOUD_C = (235, 220, 255)
        CLOUD_D = (170, 185, 210)
        EDGE_GOLD = (255, 230, 150)
        EDGE_WHITE = (255, 250, 240)

        STAR_GOLD = (255, 220, 120)
        STAR_WHITE = (255, 245, 230)
        STAR_BLUE1 = (30, 70, 170)
        STAR_BLUE2 = (70, 150, 255)
        DEEP_SPACE = (10, 18, 60)

        # --- 场面尺度（很大）---
        WIDTH = 96.0
        DEPTH = 64.0
        Z_CENTER = 6.0     # “门”中心稍偏前
        CLOUD_ZFAR = 18.0  # 云幕的主要纵深
        CLOUD_ZNEAR = -14.0

        # --- 节奏/密度（intensity 会线性放大）---
        dt = 0.06 / max(0.7, intensity)

        # 开门时长（云幕从合到开）
        open_ticks = int(round(64 * intensity))
        open_ticks = max(48, open_ticks)

        # 星海推进时长
        star_ticks = int(round(44 * intensity))
        star_ticks = max(34, star_ticks)

        # 终章推满时长
        finale_ticks = int(round(24 * intensity))
        finale_ticks = max(18, finale_ticks)

        # 每拍云的“丝”数量（越多越像云）
        cloud_strands = int(round(12 + 10 * intensity))
        cloud_strands = max(14, cloud_strands)

        # 每拍星点数量
        stars_per_tick = int(round(10 + 14 * intensity))
        stars_per_tick = max(12, stars_per_tick)

        # 星海爆闪类型池（华丽但不过度依赖 flower/love）
        star_types = [
            T.planet_random_color, T.planet_ball,
            T.mixed_color_ball, T.half_half_color_ball,
            T.double_ball, T.circle, T.random_color
        ]

        # ==========================================================
        # Phase 0：深空底（很淡，但让“开门后”更有层次）
        # ==========================================================
        bg = int(round(50 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (WIDTH * 0.52)
            pz = (rnd() * 2.0 - 1.0) * (DEPTH * 0.45)
            vx = (rnd() * 2.0 - 1.0) * 4.0
            vz = (rnd() * 2.0 - 1.0) * 4.0
            vy = clamp_vy(14.0 + 4.0 * rnd())
            col = DEEP_SPACE if i % 3 else STAR_BLUE1
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)
            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.18)

        # ==========================================================
        # Phase 1：云海开门（两侧云幕向外拉开，中间形成“门缝”）
        # ==========================================================
        for k in range(open_ticks):
            u = k / max(1, open_ticks - 1)  # 0..1
            # 门缝宽度从小到大
            gap = (8.0 + 34.0 * (u ** 1.15))  # 半宽
            # 云幕厚度呼吸
            puff = 0.75 + 0.45 * math.sin(u * math.pi)

            for s in range(cloud_strands):
                # 在纵深上分布云丝，形成云海体积
                z = Z_CENTER + (rnd() * 2.0 - 1.0) * (0.55 * DEPTH)
                z += 10.0 * math.sin(0.6 * u + s * 0.2)

                # 左云幕：起点靠近门缝边缘，速度向左外推
                xL = -(gap + 4.0 + 10.0 * rnd())
                # 右云幕：对称
                xR = +(gap + 4.0 + 10.0 * rnd())

                # 云丝速度：横向为主（拉幕），vy 稳定上扬，z 有轻微漂移
                wx = (16.0 + 18.0 * u) * puff
                driftz = 6.0 * math.sin(u * 3.0 + s) + (rnd() * 2.0 - 1.0) * 3.0
                vy = clamp_vy(18.0 + 10.0 * puff + 6.0 * intensity)

                # 颜色：云体冷白+淡紫交织，偶尔银灰增加层次
                pick = (s + k) % 9
                if pick < 4:
                    col = CLOUD_A
                elif pick < 7:
                    col = CLOUD_B
                elif pick == 7:
                    col = CLOUD_C
                else:
                    col = CLOUD_D

                # 多丝分层：让云像“帘”一样厚
                off = (s % 3 - 1) * 1.2
                fire((xL + off, 0.0, z), (-wx, vy, driftz), T.nothing, col)
                fire((xR - off, 0.0, z), (+wx, vy, -driftz), T.nothing, col)

                # 门缝边缘描一条“亮边”（开门越大越明显）
                if (s % 6 == 0) and (k % 3 == 0):
                    edge_y = clamp_vy(22.0 + 8.0 * u + 6.0 * intensity)
                    # 左边缘
                    fire((-(gap + 1.2), 0.0, z),
                        (-6.0 - 4.0 * u, edge_y, 2.0 * math.cos(u * 5.0 + s)),
                        T.nothing, EDGE_WHITE if (s % 12 == 0) else EDGE_GOLD)
                    # 右边缘
                    fire(((gap + 1.2), 0.0, z),
                        (6.0 + 4.0 * u, edge_y, 2.0 * math.sin(u * 5.0 + s)),
                        T.nothing, EDGE_WHITE if (s % 12 == 0) else EDGE_GOLD)

            time.sleep(dt)

        time.sleep(0.22)

        # ==========================================================
        # Phase 2：门内星海显现（从门缝里“涌出”星点与星团）
        # ==========================================================
        for k in range(star_ticks):
            u = k / max(1, star_ticks - 1)  # 0..1
            # 门缝进一步“通透”，星海更宽
            gap = 30.0 + 18.0 * u
            # 星海脉冲：有推进感
            surge = 0.85 + 0.55 * math.sin(u * math.pi)

            for i in range(stars_per_tick):
                # 星点从门内区域产生：|x| < gap
                px = (rnd() * 2.0 - 1.0) * gap
                # 纵深分两层：前景更亮、后景更蓝
                if i % 2 == 0:
                    pz = Z_CENTER + 8.0 + (rnd() * 2.0 - 1.0) * 10.0
                    base_col = STAR_GOLD if (i % 6 == 0) else STAR_WHITE
                else:
                    pz = Z_CENTER + 22.0 + (rnd() * 2.0 - 1.0) * 18.0
                    base_col = STAR_BLUE2 if (i % 5) else STAR_BLUE1

                # 速度：像星海从门内“涌出”，向上+向外扩散一点
                vx = (px * 0.10) + (rnd() * 2.0 - 1.0) * (10.0 + 6.0 * u) * surge
                vz = (rnd() * 2.0 - 1.0) * (10.0 + 10.0 * u)
                vy = clamp_vy(28.0 + 12.0 * surge + 6.0 * intensity)

                ftype = star_types[(k + i) % len(star_types)] if rnd() < 0.2 else T.nothing
                fire((px, 0.0, pz), (vx, vy, vz), ftype, base_col)

                if i % 10 == 0:
                    time.sleep(0.003)

            # 星海“流光”——少量 nothing 拉出丝状星尘（更梦幻）
            if k % 3 == 0:
                trails = int(round(6 + 6 * intensity))
                for j in range(trails):
                    px = (rnd() * 2.0 - 1.0) * (gap * 0.95)
                    pz = Z_CENTER + (rnd() * 2.0 - 1.0) * 22.0 + 10.0
                    vx = (rnd() * 2.0 - 1.0) * 10.0
                    vz = (rnd() * 2.0 - 1.0) * 10.0
                    vy = clamp_vy(20.0 + 8.0 * intensity)
                    col = STAR_WHITE if j % 2 == 0 else STAR_BLUE2
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            time.sleep(dt)

        time.sleep(0.25)

        # ==========================================================
        # Phase 3：终章——云边圣光 + 星海推满（大、亮、收束）
        # ==========================================================
        for k in range(finale_ticks):
            u = k / max(1, finale_ticks - 1)
            gap = 46.0  # 最终门完全打开
            flash = 0.85 + 0.55 * math.sin(u * math.pi)

            # 1) 云边“圣光描边”强化（像门框发光）
            edge_count = int(round(18 * intensity))
            for i in range(edge_count):
                z = Z_CENTER + (rnd() * 2.0 - 1.0) * (DEPTH * 0.55)
                # 左右门框
                for side in (-1.0, 1.0):
                    px = side * (gap + 1.5 + 2.0 * rnd())
                    vx = side * (8.0 + 8.0 * flash)
                    vz = (rnd() * 2.0 - 1.0) * 6.0
                    vy = clamp_vy(32.0 + 10.0 * flash + 6.0 * intensity)
                    col = EDGE_WHITE if i % 4 == 0 else EDGE_GOLD
                    fire((px, 0.0, z), (vx, vy, vz), T.nothing, col)

            # 2) 门内一次“星海洪流”（更大更炸）
            big = int(round(34 * intensity))
            for i in range(big):
                th = (2.0 * math.pi) * (i / max(1, big))
                rad = 16.0 + 18.0 * rnd()
                px = (rnd() * 2.0 - 1.0) * gap * 0.92
                pz = Z_CENTER + 10.0 + (rnd() * 2.0 - 1.0) * 16.0

                vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
                vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 8.0
                vy = clamp_vy(44.0 + 10.0 * rnd() + 6.0 * intensity)

                ftype = [T.double_ball, T.planet_random_color, T.mixed_color_ball, T.circle][i % 4] if rnd() < 0.3 else T.nothing
                col = STAR_WHITE if i % 3 == 0 else STAR_GOLD
                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 10 == 0:
                    time.sleep(0.004)

            time.sleep(0.07)

        time.sleep(0.25)

    def climax_prism_burst_corridor(self, intensity=1.0, corridor_frames=12, refraction_spread=28.0):
        T = self.type_firework
        intensity = 0.5
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 颜色（RGB 0-255）
        GLASS_1 = (220, 235, 255)
        GLASS_2 = (170, 215, 255)
        GLASS_3 = (200, 200, 230)
        WHITEGOLD = (255, 245, 230)
        GOLD = (255, 220, 120)

        RAINBOW = [
            (255, 70, 70),    # R
            (255, 140, 60),   # O
            (255, 230, 80),   # Y
            (60, 230, 120),   # G
            (60, 210, 255),   # C
            (60, 120, 255),   # B
            (190, 90, 255),   # P
        ]

        # 华丽节点（少量，贵气）
        gem_pool = [T.circle, T.double_ball, T.mixed_color_ball, T.planet_ball, T.planet_random_color, T.half_half_color_ball]

        # 长廊尺度（z 方向是纵深）
        corridor_frames = int(max(8, corridor_frames))
        far_z = 62.0
        near_z = -10.0
        z_span = far_z - near_z

        # 透视尺寸：远小近大
        far_w, far_h = 16.0, 10.0
        near_w, near_h = 64.0, 40.0

        # “棱镜点”在中段
        prism_z = near_z + 0.55 * z_span

        # 线条厚度（玻璃边）
        edge_strands = int(round(2 + 2 * intensity))
        edge_strands = max(2, edge_strands)

        dt = 0.06 / max(0.7, intensity)

        # -----------------------------
        # 工具：画一个“水晶门框”（带倒角，像棱镜框）
        # -----------------------------
        def draw_frame(z, w, h, color_main, color_hi, depth_wobble=0.0, brighten=0.0):
            # 倒角比例
            cham = 0.22
            cx = w * cham
            cz = h * cham

            # 8边形轮廓点（x,z平面）
            pts = [
                (-w/2 + cx, -h/2), ( w/2 - cx, -h/2),
                ( w/2, -h/2 + cz), ( w/2,  h/2 - cz),
                ( w/2 - cx,  h/2), (-w/2 + cx,  h/2),
                (-w/2,  h/2 - cz), (-w/2, -h/2 + cz),
            ]

            # 画边：pts[i] -> pts[i+1]
            for i in range(len(pts)):
                x0, z0 = pts[i]
                x1, z1 = pts[(i + 1) % len(pts)]

                # 分段数：越大越细腻
                segs = int(round(6 + 6 * intensity))
                segs = max(6, segs)

                for s in range(segs):
                    u = s / max(1, segs - 1)
                    px = x0 + (x1 - x0) * u
                    pz = z0 + (z1 - z0) * u

                    # 加一点深度起伏，让框“像玻璃在折光”
                    pz2 = z + pz + depth_wobble * math.sin(u * 6.0 + i)

                    # 速度：轻微沿边推开 + 上扬（线条会更“立”）
                    # 边的切向
                    tx = (x1 - x0)
                    tz = (z1 - z0)
                    m = (tx * tx + tz * tz) ** 0.5 + 1e-6
                    tx, tz = tx / m, tz / m

                    vx = 6.0 * tx + (rnd() * 2.0 - 1.0) * 1.8
                    vz = 6.0 * tz + (rnd() * 2.0 - 1.0) * 1.8
                    vy = clamp_vy(18.0 + 6.0 * intensity + brighten)

                    # 多股并排增加“玻璃厚度”
                    for k in range(edge_strands):
                        off = (k - (edge_strands - 1) / 2.0) * 0.9
                        col = color_hi if ((s + i + k) % 9 == 0) else color_main
                        fire((px + off, 0.0, pz2 - off * 0.6), (vx, vy, vz), T.nothing, col)

                # 少量停顿，避免一次性喷太猛
                if i % 2 == 0:
                    time.sleep(0.004)

        # ==========================================================
        # Phase A：水晶长廊骨架（透视门框一层层立起来）
        # ==========================================================
        for f in range(corridor_frames):
            a = f / max(1, corridor_frames - 1)          # 0(远) -> 1(近)
            z = far_z - a * z_span

            w = far_w + (near_w - far_w) * (a ** 1.25)
            h = far_h + (near_h - far_h) * (a ** 1.25)

            # 远处偏冷、近处偏亮
            col_main = GLASS_3 if a < 0.35 else (GLASS_2 if a < 0.7 else GLASS_1)
            col_hi = WHITEGOLD if a > 0.75 else GLASS_1

            wob = (2.0 + 5.0 * a) * math.sin(0.9 * f) * 0.35
            draw_frame(z, w, h, col_main, col_hi, depth_wobble=wob, brighten=0.0)

            time.sleep(0.03)

        time.sleep(0.20)

        # ==========================================================
        # Phase B：白光穿梭（从远端沿长廊推进到棱镜点）
        # ==========================================================
        beam_ticks = int(round(46 * intensity))
        beam_ticks = max(34, beam_ticks)

        for k in range(beam_ticks):
            u = k / max(1, beam_ticks - 1)
            # 白光所在深度：远 -> prism_z
            z = far_z - u * (far_z - prism_z)

            # 光束宽度逐渐收拢（像聚焦穿过走廊）
            spread = (24.0 * (1.0 - u) + 10.0) * (0.9 + 0.2 * rnd())

            shots = int(round(16 + 14 * intensity))
            for i in range(shots):
                px = (rnd() * 2.0 - 1.0) * spread
                pz = z + (rnd() * 2.0 - 1.0) * 3.0

                # 速度主要沿“向近处推进”的方向：这里用 vz 偏向 near_z
                vx = (rnd() * 2.0 - 1.0) * 6.0
                vz = -(18.0 + 16.0 * u) + (rnd() * 2.0 - 1.0) * 4.0
                vy = clamp_vy(14.0 + 6.0 * intensity)  # 注意 vy 仍 > 0

                # 白光主体用 nothing，偶尔 circle 做“光斑”
                if (i % 11 == 0) and (k % 3 == 0):
                    fire((px, 0.0, pz), (vx, clamp_vy(28.0), vz * 0.35), T.circle, WHITEGOLD)
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, WHITEGOLD)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase C：棱镜折射（白光在 prism_z 分裂成七色光束）
        # ==========================================================
        # 折射角度（度）
        spread_deg = float(refraction_spread)
        spread_rad = spread_deg * math.pi / 180.0

        # 7束：从左到右均匀分布
        beams = 7
        refract_ticks = int(round(26 * intensity))
        refract_ticks = max(18, refract_ticks)

        for k in range(refract_ticks):
            u = k / max(1, refract_ticks - 1)
            # 折射越往后越“张开”
            open_factor = 0.65 + 0.55 * math.sin(u * math.pi)

            # 每束每拍发射多少“光丝”
            per_beam = int(round(10 + 10 * intensity))
            for b in range(beams):
                # beam index -> [-1, 1]
                t = (b / (beams - 1)) * 2.0 - 1.0
                # 目标偏转方向（不靠旋涡，只是折射扇开）
                ang = t * spread_rad * open_factor

                # 折射后的方向：主要向“近处”推进（vz负），并在 x 上分裂
                dir_x = math.sin(ang)
                dir_z = -math.cos(ang)

                col = RAINBOW[b]

                for i in range(per_beam):
                    # 棱镜点附近略随机抖动，让光束更“活”
                    px = (rnd() * 2.0 - 1.0) * 2.0
                    pz = prism_z + (rnd() * 2.0 - 1.0) * 2.0

                    speed = (26.0 + 18.0 * u) * (0.85 + 0.25 * rnd())
                    vx = dir_x * speed + (rnd() * 2.0 - 1.0) * 4.0
                    vz = dir_z * speed + (rnd() * 2.0 - 1.0) * 6.0
                    vy = clamp_vy(18.0 + 8.0 * intensity + 4.0 * u)

                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    # 轻微“折射高光”（少量，不会太炸）
                    if (k % 5 == 0) and (i % 9 == 0):
                        fire((px, 0.0, pz),
                            (vx * 0.35, clamp_vy(30.0 + 6.0 * intensity), vz * 0.35),
                            T.circle, WHITEGOLD)

            time.sleep(dt)

        time.sleep(0.20)

        # ==========================================================
        # Phase D：水晶共振（门框从远到近依次点亮，最后全亮收束）
        # ==========================================================
        # 依次点亮：每帧挑一个门框，角点打宝石爆闪
        for f in range(corridor_frames):
            a = f / max(1, corridor_frames - 1)
            z = far_z - a * z_span

            w = far_w + (near_w - far_w) * (a ** 1.25)
            h = far_h + (near_h - far_h) * (a ** 1.25)

            # 先把这一框加亮描边一遍
            draw_frame(z, w, h, GLASS_1, WHITEGOLD, depth_wobble=2.0 * math.sin(f), brighten=10.0)

            # 再在“角点/倒角点”打宝石节点（非常“贵”）
            cham = 0.22
            cx = w * cham
            cz = h * cham
            nodes = [
                (-w/2 + cx, -h/2),
                ( w/2 - cx, -h/2),
                ( w/2, -h/2 + cz),
                ( w/2,  h/2 - cz),
                ( w/2 - cx,  h/2),
                (-w/2 + cx,  h/2),
                (-w/2,  h/2 - cz),
                (-w/2, -h/2 + cz),
            ]

            # 每个框只炸一半节点，避免卡，但足够华丽
            pick_n = 4
            base_idx = int(rnd() * 8)
            for j in range(pick_n):
                x, dz = nodes[(base_idx + j * 2) % 8]
                pz = z + dz + (rnd() * 2.0 - 1.0) * 1.2

                th = (2.0 * math.pi) * (j / pick_n)
                rad = 16.0 + 10.0 * rnd()
                vx = math.cos(th) * rad
                vz = math.sin(th) * rad
                vy = clamp_vy(38.0 + 6.0 * intensity)

                ftype = gem_pool[(f + j) % len(gem_pool)]
                col = GOLD if (j % 2 == 0) else WHITEGOLD
                fire((x, 0.0, pz), (vx, vy, vz), ftype, col)

                time.sleep(0.01)

            time.sleep(0.06)

        # 终章：全走廊“通电”一次（从中心向外的金白共振）
        finale = int(round(90 * intensity))
        finale = max(70, finale)

        for i in range(finale):
            th = (2.0 * math.pi) * (i / finale)
            rad = 18.0 + 16.0 * rnd()

            # 从棱镜点附近喷出“金白共振波”
            px = (rnd() * 2.0 - 1.0) * 6.0
            pz = prism_z + (rnd() * 2.0 - 1.0) * 4.0

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vy = clamp_vy(44.0 + 10.0 * rnd() + 6.0 * intensity)

            ftype = gem_pool[i % len(gem_pool)]
            col = WHITEGOLD if i % 3 == 0 else GOLD
            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.25)


    def climax_hyper_torus_bloom(self, intensity=1.0, major_R=44.0, minor_r=14.0):
        T = self.type_firework
        intensity = max(0.5, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 配色：青蓝/紫辉 + 金白能量
        DEEP = (10, 18, 60)
        CYAN = (70, 150, 255)
        AQUA = (60, 210, 255)
        PURPLE = (190, 90, 255)
        WHITEGOLD = (255, 245, 230)
        GOLD = (255, 220, 120)

        burst_pool = [T.double_ball, T.mixed_color_ball, T.half_half_color_ball, T.planet_ball, T.planet_random_color, T.circle]

        dt = 0.06 / max(0.7, intensity)

        # -------------------------
        # 环面参数化（主半径 R，管半径 r）
        # 我们把“竖向”用 y 方向的速度表达（位置只用 x,z）
        # 通过 depth_shift（z）制造前后景层次
        # -------------------------
        R = float(major_R)
        r = float(minor_r)

        # 采样密度（越大越细腻，但更吃性能）
        U_STEPS = int(round(22 * intensity))  # 主环角
        V_STEPS = int(round(14 * intensity))  # 管截面角
        U_STEPS = max(16, U_STEPS)
        V_STEPS = max(10, V_STEPS)

        # 每个点的“厚度”用多发 few strands 增强体积感
        strands = int(round(2 + 2 * intensity))
        strands = max(2, strands)

        # ==========================================================
        # Phase 0：深空底（淡，增强对比）
        # ==========================================================
        bg = int(round(45 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (R * 0.9)
            pz = (rnd() * 2.0 - 1.0) * (R * 0.7)
            vx = (rnd() * 2.0 - 1.0) * 4.0
            vz = (rnd() * 2.0 - 1.0) * 4.0
            vy = clamp_vy(14.0 + 4.0 * rnd())
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, DEEP if i % 3 else CYAN)
            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.18)

        # ==========================================================
        # Phase 1：织出环面体积（点云/线云，不是圆环）
        # 关键：V 是管截面角，导致环面“厚”而立体
        # ==========================================================
        for uu in range(U_STEPS):
            u = (2.0 * math.pi) * (uu / U_STEPS)

            # 每条主环“经线”往前后景摆动一点，形成体积
            u_wob = 0.55 * math.sin(u * 1.7)

            for vv in range(V_STEPS):
                v = (2.0 * math.pi) * (vv / V_STEPS)

                # 环面点（x,z平面），并给 z 加深度偏移
                # 标准：x=(R+r cos v) cos u, z=(R+r cos v) sin u, y=r sin v
                # 这里 y 不做位置，只转为 vy 的变化：sin v 决定“上扬强度”
                tube = r * math.cos(v)
                px = (R + tube) * math.cos(u)
                pz = (R + tube) * math.sin(u) + (r * 0.65) * math.sin(v + u_wob)

                # 速度：轻微向外推开（像“织出来”），并根据 sin(v) 提升上扬形成厚度错觉
                outward = 7.0 + 5.0 * rnd()
                vx0 = outward * math.cos(u) + (rnd() * 2.0 - 1.0) * 2.0
                vz0 = outward * math.sin(u) + (rnd() * 2.0 - 1.0) * 2.0
                vy0 = clamp_vy(18.0 + 10.0 * intensity + 8.0 * max(0.0, math.sin(v)))

                # 颜色：外表面偏青蓝，内侧偏紫辉（用 cos(v) 区分）
                if math.cos(v) > 0.2:
                    base_col = AQUA
                elif math.cos(v) < -0.2:
                    base_col = PURPLE
                else:
                    base_col = CYAN

                # 多股增强“体积”
                for s in range(strands):
                    off = (s - (strands - 1) / 2.0) * 0.9
                    col = WHITEGOLD if ((uu + vv + s) % 17 == 0) else base_col
                    fire((px + off * (-math.sin(u)), 0.0, pz + off * (math.cos(u))),
                        (vx0, vy0, vz0),
                        T.nothing, col)

                if vv % 4 == 0:
                    time.sleep(0.003)

            time.sleep(0.012)

        time.sleep(0.22)

        # ==========================================================
        # Phase 2：能量通道（沿内圈切线脉冲，不旋涡，像“环面内部在流动”）
        # ==========================================================
        pulses = int(round(34 * intensity))
        pulses = max(24, pulses)

        for k in range(pulses):
            t = k / max(1, pulses - 1)
            surge = 0.85 + 0.55 * math.sin(t * math.pi)

            # 每次脉冲抽取若干 u 点，沿切线方向喷出金白能量
            shots = int(round(18 + 14 * intensity))
            for i in range(shots):
                u = (2.0 * math.pi) * rnd()

                # 选“内圈”点：tube 取负（cos v ~ -1），让点更靠内侧
                tube = -r * (0.75 + 0.20 * rnd())
                px = (R + tube) * math.cos(u)
                pz = (R + tube) * math.sin(u)

                # 切线方向（-sin u, cos u），能量沿环面流动
                tx, tz = -math.sin(u), math.cos(u)

                speed = (26.0 + 16.0 * surge) * (0.85 + 0.25 * rnd())
                vx = tx * speed + (rnd() * 2.0 - 1.0) * 3.5
                vz = tz * speed + (rnd() * 2.0 - 1.0) * 5.0
                vy = clamp_vy(22.0 + 10.0 * intensity + 6.0 * surge)

                # 主通道用金白
                col = WHITEGOLD if i % 3 == 0 else GOLD
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                # 少量“能量节点”闪一下（贵气，但不过度炸）
                if (k % 5 == 0) and (i % 9 == 0):
                    ftype = burst_pool[(k + i) % len(burst_pool)]
                    fire((px, 0.0, pz),
                        (vx * 0.25, clamp_vy(36.0 + 6.0 * intensity), vz * 0.25),
                        ftype, WHITEGOLD)

                if i % 10 == 0:
                    time.sleep(0.002)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 3：崩解成星尘雨 + 少量彩爆（收束）
        # ==========================================================
        collapse = int(round(110 * intensity))
        collapse = max(80, collapse)

        for i in range(collapse):
            u = (2.0 * math.pi) * rnd()
            v = (2.0 * math.pi) * rnd()

            tube = r * math.cos(v)
            px = (R + tube) * math.cos(u)
            pz = (R + tube) * math.sin(u) + (r * 0.55) * math.sin(v)

            # 崩解：向外散 + 向上抬（合法），并带一点“下坠错觉”的横向拉扯
            vx = (18.0 + 10.0 * rnd()) * math.cos(u) + (rnd() * 2.0 - 1.0) * 6.0
            vz = (18.0 + 10.0 * rnd()) * math.sin(u) + (rnd() * 2.0 - 1.0) * 10.0
            vy = clamp_vy(34.0 + 10.0 * rnd() + 6.0 * intensity)

            # 颜色：外散时混入青蓝/紫辉，偶尔金白高光
            if i % 9 == 0:
                col = WHITEGOLD
            elif i % 4 == 0:
                col = PURPLE
            else:
                col = AQUA if i % 2 == 0 else CYAN

            # 大部分用星尘（nothing），少量爆闪点做收束
            if i % 14 == 0:
                ftype = burst_pool[i % len(burst_pool)]
                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)
            else:
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            if i % 12 == 0:
                time.sleep(0.006)

        time.sleep(0.25)


    def climax_milkyway_bridgefall(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.5, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 配色：银河（深蓝底 + 白金星沙 + 青蓝辉光）
        DEEP = (10, 18, 60)
        BLUE = (30, 70, 170)
        CYAN = (70, 150, 255)
        WHITEGOLD = (255, 245, 230)
        GOLD = (255, 220, 120)

        # 华丽节点（少量）
        cap_pool = [
            T.double_ball, T.mixed_color_ball, T.half_half_color_ball,
            T.planet_ball, T.planet_random_color, T.circle
        ]

        # 桥的尺寸（x-z 平面是一座拱桥）
        SPAN = 96.0         # 桥宽（左右跨度）
        ARCH_H = 34.0       # 拱高（体现在 z 的曲线高度，不是 y）
        Z0 = 10.0           # 桥大致位置（z）
        Z_DEPTH = 18.0      # 让桥有“前后厚度”一点点

        # 节奏
        dt = 0.055 / max(0.7, intensity)

        # 工具：拱桥曲线（u in [-1, 1]）
        # 用抛物线：中心最高，两端回到低处
        def arch_point(u):
            x = u * (SPAN * 0.5)
            z = Z0 + ARCH_H * (1.0 - u * u)
            return x, z

        # 工具：拱桥切线方向（用于“沿桥流动”）
        def arch_tangent(u):
            # x = a*u, z = Z0 + H*(1-u^2) => dz/du = -2H*u, dx/du = a
            dx = (SPAN * 0.5)
            dz = -2.0 * ARCH_H * u
            m = (dx * dx + dz * dz) ** 0.5 + 1e-6
            return dx / m, dz / m

        # ==========================================================
        # Phase 0：深空底（很淡，增强对比）
        # ==========================================================
        bg = int(round(45 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (SPAN * 0.55)
            pz = (rnd() * 2.0 - 1.0) * (ARCH_H * 1.1) + Z0
            vx = (rnd() * 2.0 - 1.0) * 4.0
            vz = (rnd() * 2.0 - 1.0) * 4.0
            vy = clamp_vy(14.0 + 4.0 * rnd())
            col = DEEP if i % 3 else BLUE
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)
            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.15)

        # ==========================================================
        # Phase 1：搭桥（清晰轮廓：两条拱 + 桥面横梁）
        # ==========================================================
        arch_pts = int(round(70 * intensity))
        arch_pts = max(54, arch_pts)

        # 1A) 双拱（前后两条，形成厚度）
        for layer in range(2):
            z_shift = (Z_DEPTH * 0.5) * (1.0 if layer == 0 else -1.0)
            for i in range(arch_pts):
                u = (i / max(1, arch_pts - 1)) * 2.0 - 1.0
                x, z = arch_point(u)
                z += z_shift + 1.2 * math.sin(u * 3.0)  # 微起伏更“星河”

                tx, tz = arch_tangent(u)
                # 速度：轻推沿切线 + 上扬（让线条立起来）
                vx = 6.0 * tx + (rnd() * 2.0 - 1.0) * 1.8
                vz = 6.0 * tz + (rnd() * 2.0 - 1.0) * 1.8
                vy = clamp_vy(18.0 + 8.0 * intensity)

                # 颜色：白金描边为主，夹少量青蓝辉光
                col = WHITEGOLD if (i % 8 == 0) else (CYAN if (i % 5 == 0) else BLUE)
                fire((x, 0.0, z), (vx, vy, vz), T.nothing, col)

                if i % 10 == 0:
                    time.sleep(0.004)
            time.sleep(0.03)

        # 1B) 桥面横梁（在较低处连成“桥板”）
        beams = int(round(10 * intensity))
        beams = max(8, beams)
        for b in range(beams):
            u = (b / max(1, beams - 1)) * 2.0 - 1.0
            x, z = arch_point(u)
            z = Z0 + (ARCH_H * 0.35) + 2.5 * math.sin(u * math.pi)  # 桥板更平

            # 一条短横梁：左右各喷一点线
            span_local = 10.0 + 10.0 * (1.0 - abs(u))
            segs = int(round(10 * intensity))
            segs = max(8, segs)

            for i in range(segs):
                t = (i / max(1, segs - 1)) * 2.0 - 1.0
                px = x + t * (span_local * 0.5)
                pz = z + (rnd() * 2.0 - 1.0) * 1.4
                vx = 5.0 * t + (rnd() * 2.0 - 1.0) * 1.0
                vz = (rnd() * 2.0 - 1.0) * 2.0
                vy = clamp_vy(18.0 + 6.0 * intensity)

                col = GOLD if (i % 7 == 0) else WHITEGOLD
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            time.sleep(0.02)

        time.sleep(0.20)

        # ==========================================================
        # Phase 2：桥面星沙流动（沿拱切线“跑光”）
        # ==========================================================
        flow_ticks = int(round(46 * intensity))
        flow_ticks = max(34, flow_ticks)

        for k in range(flow_ticks):
            t = k / max(1, flow_ticks - 1)
            surge = 0.85 + 0.55 * math.sin(t * math.pi)

            shots = int(round(18 + 18 * intensity))
            for i in range(shots):
                # 取拱上一点，偏向桥面上半部
                u = (rnd() * 2.0 - 1.0)
                x, z = arch_point(u)
                z += (rnd() * 2.0 - 1.0) * 3.0

                # 流动方向：沿切线向两端“奔流”
                tx, tz = arch_tangent(u)
                dir_sign = -1.0 if (i % 2 == 0) else 1.0  # 左右交替奔流
                speed = (22.0 + 18.0 * surge) * (0.85 + 0.25 * rnd())

                vx = dir_sign * tx * speed + (rnd() * 2.0 - 1.0) * 3.0
                vz = dir_sign * tz * speed + (rnd() * 2.0 - 1.0) * 4.5
                vy = clamp_vy(20.0 + 8.0 * intensity + 6.0 * surge)

                # 星沙颜色：白金为主，夹青蓝
                col = WHITEGOLD if (i % 3 == 0) else (CYAN if i % 5 == 0 else GOLD)
                fire((x, 0.0, z), (vx, vy, vz), T.nothing, col)

                # 少量“星团闪点”
                if (k % 6 == 0) and (i % 11 == 0):
                    fire((x, 0.0, z), (vx * 0.25, clamp_vy(34.0 + 6.0 * intensity), vz * 0.25),
                        T.circle, WHITEGOLD)

                if i % 10 == 0:
                    time.sleep(0.002)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 3：泄落成瀑（从拱下沿多点“滴落”，形成银河瀑布）
        # 说明：vy 设得很低（但 > MIN_VY），配合引擎重力会更像下坠。
        # ==========================================================
        fall_ticks = int(round(54 * intensity))
        fall_ticks = max(40, fall_ticks)

        for k in range(fall_ticks):
            t = k / max(1, fall_ticks - 1)
            # 越到后面越密，像瀑布加大流量
            density = 0.65 + 0.55 * t

            drops = int(round((18 + 22 * intensity) * density))
            for i in range(drops):
                # 从拱下沿取点：让它看起来从桥下“漏”下来
                u = (rnd() * 2.0 - 1.0) * (0.95 - 0.25 * rnd())
                x, z_top = arch_point(u)

                # 下沿位置：比拱低一截，且带前后层次
                z = (Z0 + ARCH_H * (1.0 - u * u)) - (10.0 + 8.0 * rnd())
                z += (rnd() * 2.0 - 1.0) * (Z_DEPTH * 0.6)

                # 速度：vy 很小（合法），横向/纵向拉开，形成“坠落轨迹”
                # 让瀑布略向舞台中心聚拢
                vx = (-x * 0.14) + (rnd() * 2.0 - 1.0) * 8.0
                vz = (-6.0 - 14.0 * rnd()) + (rnd() * 2.0 - 1.0) * 6.0
                vy = clamp_vy(12.5 + 2.5 * rnd() + 2.0 * intensity)  # 接近最小值，制造“落感”

                # 颜色：瀑布更偏冷白/青蓝，偶尔金白闪一下
                if i % 9 == 0:
                    col = WHITEGOLD
                elif i % 3 == 0:
                    col = CYAN
                else:
                    col = BLUE

                fire((x, 0.0, z), (vx, vy, vz), T.nothing, col)

                if i % 14 == 0:
                    time.sleep(0.002)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 4：桥端封顶（两端同时爆闪，收束“桥”这个主题）
        # ==========================================================
        end_bursts = int(round(24 * intensity))
        end_bursts = max(18, end_bursts)

        for i in range(end_bursts):
            side = -1.0 if (i % 2 == 0) else 1.0
            u = side * 1.0
            x, z = arch_point(u)
            # 两端略抬高一点
            z = Z0 + 6.0 + (rnd() * 2.0 - 1.0) * 2.0

            th = (2.0 * math.pi) * (i / end_bursts)
            rad = 18.0 + 14.0 * rnd()

            vx = -side * (10.0 + 8.0 * rnd()) + math.cos(th) * 6.0
            vz = math.sin(th) * rad
            vy = clamp_vy(40.0 + 6.0 * intensity)

            ftype = cap_pool[i % len(cap_pool)]
            col = GOLD if i % 3 else WHITEGOLD
            fire((x, 0.0, z), (vx, vy, vz), ftype, col)

            if i % 6 == 0:
                time.sleep(0.01)

        time.sleep(0.25)


    def climax_day_night_flip(self, intensity=1.0):
        T = self.type_firework
        intensity = 0.5
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # -------------------------
        # 颜色（RGB 0~255）
        # 左：极昼（金白/暖光/淡橙）
        # 右：极夜（深蓝/群青/冷白星点）
        # 中：分界线（白金+少量青蓝电辉）
        # -------------------------
        DAY_WHITE = (255, 250, 240)
        DAY_GOLD  = (255, 220, 120)
        DAY_AMBER = (255, 160, 80)

        NIGHT_DEEP = (10, 16, 55)
        NIGHT_BLUE = (30, 70, 170)
        NIGHT_CYAN = (70, 150, 255)
        STAR_WHITE = (255, 245, 230)

        LINE_WHITE = (255, 250, 245)
        LINE_GOLD  = (255, 230, 150)
        LINE_CYAN  = (120, 220, 255)

        # 少量高光类型（不要太炸）
        sparkle_pool = [T.circle, T.double_ball, T.planet_ball, T.planet_random_color, T.mixed_color_ball]

        # -------------------------
        # 舞台尺度（很大）
        # -------------------------
        XMAX = 92.0
        ZMAX = 64.0
        ZCENTER = 8.0

        # 时间控制
        dt = 0.055 / max(0.7, intensity)

        # 密度（可控，默认已经很壮观）
        base_pts = int(round(18 + 18 * intensity))     # 每帧铺底点数
        base_pts = max(18, base_pts)

        stars_pts = int(round(14 + 14 * intensity))    # 夜侧星点
        stars_pts = max(14, stars_pts)

        line_pts = int(round(22 + 22 * intensity))     # 分界线密度
        line_pts = max(22, line_pts)

        # 各阶段帧数
        warmup_ticks = int(round(40 * intensity))      # 先分别铺“昼/夜”
        warmup_ticks = max(30, warmup_ticks)

        blend_ticks  = int(round(36 * intensity))      # 两侧互相“侵染”，强化概念
        blend_ticks  = max(28, blend_ticks)

        sweep_ticks  = int(round(64 * intensity))      # 分界线大扫描
        sweep_ticks  = max(48, sweep_ticks)

        finale_ticks = int(round(24 * intensity))      # 终章闪白收束
        finale_ticks = max(18, finale_ticks)

        # ==========================================================
        # Phase 0：建立“昼/夜底场”（左暖右冷，规模先铺开）
        # ==========================================================
        for k in range(warmup_ticks):
            t = k / max(1, warmup_ticks - 1)
            swell = 0.75 + 0.45 * math.sin(t * math.pi)

            # 左侧（极昼云光）
            for i in range(base_pts):
                px = -abs((rnd() * XMAX)) * (0.85 + 0.15 * rnd())
                pz = ZCENTER + (rnd() * 2.0 - 1.0) * (ZMAX * 0.55)

                vx = (rnd() * 2.0 - 1.0) * 6.0 + 6.0 * (1.0 - t)   # 略向外扩散
                vz = (rnd() * 2.0 - 1.0) * 5.0
                vy = clamp_vy(18.0 + 10.0 * swell + 6.0 * intensity)

                # 暖光渐变：越靠近中线越白金
                near_mid = 1.0 - min(1.0, abs(px) / (XMAX * 0.65))
                rsel = rnd()
                if rsel < 0.45:
                    col = DAY_GOLD
                elif rsel < 0.75:
                    col = DAY_AMBER
                else:
                    col = DAY_WHITE if near_mid > 0.35 else DAY_GOLD

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                if i % 12 == 0:
                    time.sleep(0.0015)

            # 右侧（极夜星海）
            for i in range(stars_pts):
                px = abs((rnd() * XMAX)) * (0.85 + 0.15 * rnd())
                pz = ZCENTER + (rnd() * 2.0 - 1.0) * (ZMAX * 0.60)

                vx = (rnd() * 2.0 - 1.0) * 5.0 - 5.0 * (1.0 - t)   # 略向外扩散
                vz = (rnd() * 2.0 - 1.0) * 6.0
                vy = clamp_vy(16.0 + 8.0 * swell + 6.0 * intensity)

                # 夜色：深空底 + 星点冷白/青蓝
                rsel = rnd()
                if rsel < 0.45:
                    col = NIGHT_DEEP
                elif rsel < 0.75:
                    col = NIGHT_BLUE
                elif rsel < 0.90:
                    col = NIGHT_CYAN
                else:
                    col = STAR_WHITE

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                # 少量星点闪烁（很少）
                if (k % 6 == 0) and (i % 9 == 0):
                    fire((px, 0.0, pz), (vx * 0.25, clamp_vy(28.0), vz * 0.25), T.circle, STAR_WHITE)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 1：互相“侵染”的过渡（昼向右渗、夜向左渗，增强“切换”）
        # ==========================================================
        for k in range(blend_ticks):
            t = k / max(1, blend_ticks - 1)
            pulse = 0.85 + 0.55 * math.sin(t * math.pi)

            # 渗透宽度逐渐扩大
            band = 10.0 + 28.0 * t

            # 昼向右渗：在 x>0 的窄带打暖光
            for i in range(int(round(base_pts * 0.65))):
                px = (rnd() * band)  # 0..band
                pz = ZCENTER + (rnd() * 2.0 - 1.0) * (ZMAX * 0.50)

                vx = (rnd() * 2.0 - 1.0) * 6.0 + 8.0 * pulse
                vz = (rnd() * 2.0 - 1.0) * 5.0
                vy = clamp_vy(20.0 + 10.0 * pulse + 6.0 * intensity)

                col = DAY_WHITE if i % 3 == 0 else DAY_GOLD
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            # 夜向左渗：在 x<0 的窄带打冷蓝星雾
            for i in range(int(round(stars_pts * 0.90))):
                px = -(rnd() * band)
                pz = ZCENTER + (rnd() * 2.0 - 1.0) * (ZMAX * 0.55)

                vx = (rnd() * 2.0 - 1.0) * 6.0 - 8.0 * pulse
                vz = (rnd() * 2.0 - 1.0) * 6.0
                vy = clamp_vy(18.0 + 10.0 * pulse + 6.0 * intensity)

                col = NIGHT_CYAN if i % 4 == 0 else NIGHT_BLUE
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            time.sleep(dt)

        time.sleep(0.20)

        # ==========================================================
        # Phase 2：分界线巨型扫描（来回两次，极其壮观）
        # 扫描线本身是“高亮墙”，扫过位置两侧颜色会“翻转增强”
        # ==========================================================
        sweeps = 2  # 来回两次
        for s in range(sweeps):
            for k in range(sweep_ticks):
                t = k / max(1, sweep_ticks - 1)

                # 线位置：第1次从左到右，第2次从右到左
                if s % 2 == 0:
                    x_line = -XMAX * 0.72 + (XMAX * 1.44) * t
                else:
                    x_line = +XMAX * 0.72 - (XMAX * 1.44) * t

                # 线宽（视觉上是一堵光墙）
                thickness = 6.0 + 10.0 * (0.5 + 0.5 * math.sin(t * math.pi))
                pulse = 0.85 + 0.55 * math.sin((t + 0.1) * math.pi)

                # 2A) 分界线本体（高亮密集）
                for i in range(line_pts):
                    # 沿 z 分布，形成纵向很长的墙
                    pz = ZCENTER + (rnd() * 2.0 - 1.0) * (ZMAX * 0.62)
                    px = x_line + (rnd() * 2.0 - 1.0) * thickness

                    vx = (rnd() * 2.0 - 1.0) * 6.0
                    vz = (rnd() * 2.0 - 1.0) * 8.0
                    vy = clamp_vy(28.0 + 12.0 * pulse + 6.0 * intensity)

                    # 线色：白金为主，夹一点青蓝电辉
                    col = LINE_WHITE if i % 4 != 0 else (LINE_GOLD if i % 8 != 0 else LINE_CYAN)
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    # 少量节点闪一下（非常“电”）
                    if (k % 6 == 0) and (i % 11 == 0):
                        ftype = sparkle_pool[(k + i) % len(sparkle_pool)]
                        fire((px, 0.0, pz), (vx * 0.25, clamp_vy(38.0 + 6.0 * intensity), vz * 0.25), ftype, LINE_WHITE)

                # 2B) 扫描线“激活”两侧：左侧更昼、右侧更夜（增强对比）
                side_hits = int(round(14 + 10 * intensity))
                for i in range(side_hits):
                    pz = ZCENTER + (rnd() * 2.0 - 1.0) * (ZMAX * 0.55)

                    # 左侧（极昼增强带）
                    pxL = x_line - (8.0 + 10.0 * rnd())
                    vxL = -10.0 - 10.0 * rnd()
                    vzL = (rnd() * 2.0 - 1.0) * 6.0
                    vyL = clamp_vy(20.0 + 8.0 * intensity + 6.0 * pulse)
                    colL = DAY_WHITE if i % 3 == 0 else DAY_GOLD
                    fire((pxL, 0.0, pz), (vxL, vyL, vzL), T.nothing, colL)

                    # 右侧（极夜增强带）
                    pxR = x_line + (8.0 + 10.0 * rnd())
                    vxR = +10.0 + 10.0 * rnd()
                    vzR = (rnd() * 2.0 - 1.0) * 6.0
                    vyR = clamp_vy(18.0 + 8.0 * intensity + 6.0 * pulse)
                    colR = STAR_WHITE if i % 5 == 0 else (NIGHT_CYAN if i % 2 == 0 else NIGHT_BLUE)
                    fire((pxR, 0.0, pz), (vxR, vyR, vzR), T.nothing, colR)

                time.sleep(dt)

            time.sleep(0.12)

        time.sleep(0.22)

        # ==========================================================
        # Phase 3：终章——分界线“归一化”大闪（全场金白收束）
        # ==========================================================
        for k in range(finale_ticks):
            t = k / max(1, finale_ticks - 1)
            flash = 0.85 + 0.55 * math.sin(t * math.pi)

            # 把整条中线附近炸亮（但仍控制爆炸数量）
            big = int(round((36 + 24 * intensity) * flash))
            for i in range(big):
                px = (rnd() * 2.0 - 1.0) * 10.0
                pz = ZCENTER + (rnd() * 2.0 - 1.0) * (ZMAX * 0.62)

                th = (2.0 * math.pi) * (i / max(1, big))
                rad = 18.0 + 18.0 * rnd()

                vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
                vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
                vy = clamp_vy(44.0 + 10.0 * rnd() + 6.0 * intensity)

                ftype = sparkle_pool[i % len(sparkle_pool)] if (i % 5 == 0) else T.nothing
                col = LINE_WHITE if i % 3 == 0 else LINE_GOLD
                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 12 == 0:
                    time.sleep(0.004)

            time.sleep(0.07)

        time.sleep(0.25)


    def climax_stargate_array_overload(self, intensity=1.0, gate_count=9):
        T = self.type_firework
        intensity = 0.3
        gate_count = int(max(7, min(13, gate_count)))  # 7~13 之间比较稳

        MIN_VY = 12.0
        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 颜色（RGB 0~255）
        FRAME_COLD = (210, 235, 255)
        FRAME_DEEP = (90, 140, 210)
        FRAME_WHITE = (255, 250, 240)
        GOLD = (255, 220, 120)

        FLOW_A = (70, 210, 255)
        FLOW_B = (190, 90, 255)
        FLOW_C = (255, 140, 60)
        FLOW_D = (120, 255, 160)

        # 节点/过载用的烟花类型（少量用，点睛）
        node_pool = [T.circle, T.double_ball, T.planet_ball, T.planet_random_color, T.mixed_color_ball, T.half_half_color_ball]

        # 舞台尺度（z 方向做纵深：远处门更小）
        far_z = 72.0
        near_z = -8.0
        z_span = far_z - near_z

        far_w, far_h = 18.0, 12.0
        near_w, near_h = 76.0, 50.0

        # 门框厚度（用多股 T.nothing 叠）
        strands = int(round(2 + 2 * intensity))
        strands = max(2, min(5, strands))

        # 节奏
        dt = 0.055 / max(0.7, intensity)

        # -----------------------------
        # 工具：圆角矩形轮廓点（8边形近似）
        # -----------------------------
        def gate_points(w, h):
            cham = 0.22
            cx = w * cham
            cy = h * cham
            return [
                (-w/2 + cx, -h/2), ( w/2 - cx, -h/2),
                ( w/2, -h/2 + cy), ( w/2,  h/2 - cy),
                ( w/2 - cx,  h/2), (-w/2 + cx,  h/2),
                (-w/2,  h/2 - cy), (-w/2, -h/2 + cy),
            ]

        # -----------------------------
        # 工具：画一个门框（T.nothing），带轻微“电流抖动”
        # -----------------------------
        def draw_gate_frame(z, w, h, brightness=0.0, depth_wobble=0.0):
            pts = gate_points(w, h)
            segs = int(round(7 + 7 * intensity))
            segs = max(7, segs)

            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                # 边切向
                tx = x1 - x0
                ty = y1 - y0
                m = (tx * tx + ty * ty) ** 0.5 + 1e-6
                tx, ty = tx / m, ty / m

                for s in range(segs):
                    u = s / max(1, segs - 1)
                    px = x0 + (x1 - x0) * u
                    py = y0 + (y1 - y0) * u

                    # 用 py 影响 z 深度，形成“门面有体积”的错觉
                    pz = z + depth_wobble * math.sin(u * 6.0 + i) + 0.18 * py

                    # 速度：沿边轻推 + 上扬 + 电流噪声
                    vx = 7.0 * tx + (rnd() * 2.0 - 1.0) * 2.2
                    vz = 7.0 * ty + (rnd() * 2.0 - 1.0) * 2.2
                    vy = clamp_vy(18.0 + 8.0 * intensity + brightness)

                    for k in range(strands):
                        off = (k - (strands - 1) / 2.0) * 0.9
                        # 冷白为主，夹深蓝阴影
                        col = FRAME_WHITE if ((i + s + k) % 11 == 0) else (FRAME_COLD if (s % 3 != 0) else FRAME_DEEP)
                        fire((px + off * (-ty), 0.0, pz + off * (tx)), (vx, vy, vz), T.nothing, col)

                if i % 2 == 0:
                    time.sleep(0.003)

        # -----------------------------
        # 工具：门角/节点共振（少量爆闪）
        # -----------------------------
        def pulse_gate_nodes(z, w, h, step_idx, strong=False):
            pts = gate_points(w, h)

            # 只取 4 个“主角点”更稳：0,2,4,6
            corners = [0, 2, 4, 6]
            for j, ci in enumerate(corners):
                x, y = pts[ci]
                pz = z + 0.18 * y

                # 节点向外发一点
                th = (2.0 * math.pi) * (j / len(corners))
                rad = (18.0 if not strong else 26.0) + 10.0 * rnd()

                vx = math.cos(th) * rad
                vz = math.sin(th) * rad
                vy = clamp_vy((32.0 if not strong else 44.0) + 6.0 * intensity)

                ftype = node_pool[(step_idx + j) % len(node_pool)]
                col = GOLD if (j % 2 == 0) else FRAME_WHITE
                fire((x, 0.0, pz), (vx, vy, vz), ftype, col)

                time.sleep(0.008 if strong else 0.004)

        # ==========================================================
        # Phase A：星门阵列“搭建”（远到近依次出现，纵深极强）
        # ==========================================================
        for g in range(gate_count):
            a = g / max(1, gate_count - 1)  # 0远->1近
            z = far_z - a * z_span

            # 透视：近处更大
            w = far_w + (near_w - far_w) * (a ** 1.25)
            h = far_h + (near_h - far_h) * (a ** 1.25)

            wob = (2.0 + 6.0 * a) * math.sin(g * 0.9) * 0.35
            draw_gate_frame(z, w, h, brightness=0.0, depth_wobble=wob)

            # 每出现一个门，给它轻点一下“角灯”
            if g % 2 == 0:
                pulse_gate_nodes(z, w, h, g, strong=False)

            time.sleep(0.03)

        time.sleep(0.20)

        # ==========================================================
        # Phase B：门间共振传递（像电流从远处一路传到近处）
        # ==========================================================
        relay_rounds = int(round(2 + 1 * intensity))
        relay_rounds = max(2, relay_rounds)

        for r in range(relay_rounds):
            for g in range(gate_count):
                a = g / max(1, gate_count - 1)
                z = far_z - a * z_span
                w = far_w + (near_w - far_w) * (a ** 1.25)
                h = far_h + (near_h - far_h) * (a ** 1.25)

                # 共振：只点节点 + 轻描一圈高光边
                draw_gate_frame(z, w, h, brightness=6.0 + 4.0 * r, depth_wobble=2.0 * math.sin(g + r))
                pulse_gate_nodes(z, w, h, g + r * 7, strong=False)

                time.sleep(0.04)

            time.sleep(0.10)

        time.sleep(0.18)

        # ==========================================================
        # Phase C：中央门“打开”喷出彩色洪流（壮观的主戏）
        # ==========================================================
        mid = gate_count // 2
        a = mid / max(1, gate_count - 1)
        z_mid = far_z - a * z_span
        w_mid = far_w + (near_w - far_w) * (a ** 1.25)
        h_mid = far_h + (near_h - far_h) * (a ** 1.25)

        # 先让中央门加亮一次（像锁扣解除）
        draw_gate_frame(z_mid, w_mid, h_mid, brightness=14.0, depth_wobble=3.0)
        pulse_gate_nodes(z_mid, w_mid, h_mid, 999, strong=True)
        time.sleep(0.12)

        flood_ticks = int(round(52 * intensity))
        flood_ticks = max(36, flood_ticks)

        for k in range(flood_ticks):
            t = k / max(1, flood_ticks - 1)
            surge = 0.85 + 0.55 * math.sin(t * math.pi)

            # 洪流密度（可控，强但不至于卡死）
            shots = int(round((18 + 18 * intensity) * (0.75 + 0.45 * surge)))
            shots = max(18, shots)

            for i in range(shots):
                # 从中央门内部区域发出：|x| < w_mid*0.25, |y| < h_mid*0.18
                px = (rnd() * 2.0 - 1.0) * (w_mid * 0.25)
                py = (rnd() * 2.0 - 1.0) * (h_mid * 0.18)
                pz = z_mid + 0.18 * py + (rnd() * 2.0 - 1.0) * 2.0

                # 速度：向观众方向“喷出”并扩散（这里用 vz 向 near_z 方向更负）
                vx = (rnd() * 2.0 - 1.0) * (18.0 + 10.0 * surge)
                vz = -(24.0 + 22.0 * surge) + (rnd() * 2.0 - 1.0) * 8.0
                vy = clamp_vy(22.0 + 10.0 * intensity + 10.0 * surge)

                # 彩色洪流：四种色域交织
                pick = (k * 7 + i * 11) % 16
                if pick < 4:
                    col = FLOW_A
                elif pick < 8:
                    col = FLOW_B
                elif pick < 12:
                    col = FLOW_C
                else:
                    col = FLOW_D

                # 主体用 nothing（更像“能量流”），少量用 circle 做光斑
                if (i % 13 == 0) and (k % 3 == 0):
                    fire((px, 0.0, pz), (vx * 0.25, clamp_vy(34.0 + 6.0 * intensity), vz * 0.25), T.circle, FRAME_WHITE)
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                if i % 12 == 0:
                    time.sleep(0.002)

            # 偶尔在门框角点加一圈“电弧节点”
            if k % int(max(6, round(10 / max(0.7, intensity)))) == 0:
                pulse_gate_nodes(z_mid, w_mid, h_mid, k, strong=False)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase D：全阵列过载同闪（所有门同时“通电”，但严格限量避免卡）
        # ==========================================================
        # 过载：每个门只炸一次（4角点），并且只给一半门做强闪，其余弱闪
        for g in range(gate_count):
            a = g / max(1, gate_count - 1)
            z = far_z - a * z_span
            w = far_w + (near_w - far_w) * (a ** 1.25)
            h = far_h + (near_h - far_h) * (a ** 1.25)

            strong = (g % 2 == 0)  # 只让一半门强闪
            pulse_gate_nodes(z, w, h, 2000 + g, strong=strong)

            # 最后再补一圈高光边（让“过载”像真的通电）
            draw_gate_frame(z, w, h, brightness=(18.0 if strong else 8.0), depth_wobble=2.0)

            time.sleep(0.03)

        # 终极收束：中央一次金白合唱（少量爆闪，不是铺天盖地乱炸）
        finale = int(round(70 * intensity))
        finale = max(50, finale)

        for i in range(finale):
            th = (2.0 * math.pi) * (i / finale)
            rad = 18.0 + 16.0 * rnd()

            px = (rnd() * 2.0 - 1.0) * 6.0
            pz = z_mid + (rnd() * 2.0 - 1.0) * 4.0

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vy = clamp_vy(44.0 + 10.0 * rnd() + 6.0 * intensity)

            ftype = node_pool[i % len(node_pool)]
            col = FRAME_WHITE if i % 3 == 0 else GOLD
            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.25)


    def climax_rift_canyon_panorama(self, intensity=1.0):
        T = self.type_firework
        intensity = 0.6
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # -------------------------
        # 配色（两套气质混合：深空紫蓝 + 熔流橙金）
        # -------------------------
        DEEP = (10, 16, 55)
        INDIGO = (30, 70, 170)
        CYAN = (70, 150, 255)
        PURPLE = (190, 90, 255)

        MAGMA = (255, 90, 40)
        AMBER = (255, 160, 80)
        GOLD = (255, 220, 120)
        WHITEGOLD = (255, 245, 230)

        EDGE_WHITE = (255, 250, 245)
        EDGE_GOLD = (255, 230, 150)

        burst_pool = [T.circle, T.double_ball, T.mixed_color_ball, T.planet_ball, T.planet_random_color, T.half_half_color_ball]

        # -------------------------
        # 舞台尺度（裂谷横向贯穿）
        # -------------------------
        XMAX = 110.0
        Z0 = 6.0
        ZSPAN = 56.0  # 内部翻涌的纵深范围

        # 节奏
        dt = 0.055 / max(0.7, intensity)

        # 采样密度（可控）
        edge_pts = int(round(60 * intensity))
        edge_pts = max(46, edge_pts)

        inner_pts = int(round(28 * intensity))
        inner_pts = max(20, inner_pts)

        # -------------------------
        # 裂谷“中心线”形状：多频叠加，形成自然断层
        # u in [-1,1] -> z offset
        # -------------------------
        def centerline_z(u, t):
            # 大尺度弯曲 + 中尺度扭曲 + 小尺度锯齿
            a1 = 10.0 * math.sin(1.15 * u * math.pi + 0.7 * t)
            a2 = 6.0 * math.sin(3.2 * u * math.pi - 1.3 * t)
            a3 = 2.6 * math.sin(10.0 * u * math.pi + 2.1 * t)
            return Z0 + a1 + a2 + a3

        # ==========================================================
        # Phase 0：背景深空（淡铺，增强对比）
        # ==========================================================
        bg = int(round(50 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (XMAX * 0.55)
            pz = Z0 + (rnd() * 2.0 - 1.0) * (ZSPAN * 0.55)
            vx = (rnd() * 2.0 - 1.0) * 4.0
            vz = (rnd() * 2.0 - 1.0) * 4.0
            vy = clamp_vy(14.0 + 4.0 * rnd())
            col = DEEP if i % 3 else INDIGO
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)
            if i % 12 == 0:
                time.sleep(0.01)

        time.sleep(0.15)

        # ==========================================================
        # Phase 1：裂谷张开 + 边缘描边（白金断层线非常清晰）
        # ==========================================================
        open_ticks = int(round(46 * intensity))
        open_ticks = max(34, open_ticks)

        for k in range(open_ticks):
            t = k / max(1, open_ticks - 1)
            # 裂谷宽度：先迅速打开，再缓慢稳定
            gap = 8.0 + 26.0 * (t ** 0.95)  # 总宽度
            glow = 0.75 + 0.55 * math.sin(t * math.pi)

            for i in range(edge_pts):
                u = (i / max(1, edge_pts - 1)) * 2.0 - 1.0
                x = u * XMAX
                cz = centerline_z(u, t * 3.0)

                # 两条边缘
                zL = cz + gap * 0.5
                zR = cz - gap * 0.5

                # 边缘速度：轻微“撕裂外推” + 上扬（像断层冒光）
                vx = (rnd() * 2.0 - 1.0) * 3.0
                vz = (rnd() * 2.0 - 1.0) * 4.0
                vy = clamp_vy(22.0 + 10.0 * glow + 6.0 * intensity)

                col = EDGE_WHITE if (i % 7 == 0) else EDGE_GOLD
                fire((x, 0.0, zL), (vx, vy, vz), T.nothing, col)
                fire((x, 0.0, zR), (vx, vy, -vz), T.nothing, col)

                # 少量“边缘火花”
                if (k % 6 == 0) and (i % 13 == 0):
                    ftype = T.circle
                    fire((x, 0.0, cz), (vx * 0.3, clamp_vy(34.0 + 6.0 * intensity), vz * 0.3), ftype, WHITEGOLD)

                if i % 12 == 0:
                    time.sleep(0.0025)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 2：裂谷内部翻涌（星云/熔流湍动，不靠旋涡）
        # ==========================================================
        churn_ticks = int(round(64 * intensity))
        churn_ticks = max(46, churn_ticks)

        for k in range(churn_ticks):
            t = k / max(1, churn_ticks - 1)
            # 裂谷宽度维持，但会“呼吸”让内部更活
            gap = 26.0 + 6.0 * math.sin(t * 2.0 * math.pi)
            pulse = 0.85 + 0.55 * math.sin(t * math.pi)

            for i in range(inner_pts):
                u = (rnd() * 2.0 - 1.0)
                x = u * XMAX * (0.92 + 0.08 * rnd())
                cz = centerline_z(u, 1.2 + t * 5.0)

                # 在裂谷内部均匀取点：cz ± gap/2
                z = cz + (rnd() * 2.0 - 1.0) * (gap * 0.48)

                # 速度：向上为主，横向/纵向形成“湍流卷吸”的错觉
                # 向中心线略聚拢（像被裂谷吸走）
                pull = -(z - cz) * 0.22
                vx = (rnd() * 2.0 - 1.0) * (10.0 + 6.0 * pulse)
                vz = pull + (rnd() * 2.0 - 1.0) * (12.0 + 6.0 * pulse)
                vy = clamp_vy(18.0 + 12.0 * pulse + 6.0 * intensity)

                # 颜色策略：靠近中心线更亮/更热，外缘更冷/更深
                dist = abs(z - cz) / max(1e-6, gap * 0.5)
                rsel = rnd()
                if dist < 0.35:
                    col = WHITEGOLD if rsel < 0.12 else (GOLD if rsel < 0.45 else (AMBER if rsel < 0.75 else MAGMA))
                else:
                    col = PURPLE if rsel < 0.35 else (INDIGO if rsel < 0.70 else CYAN)

                fire((x, 0.0, z), (vx, vy, vz), T.nothing, col)

                # 少量“翻涌节点”爆闪点睛（不多，不会卡）
                if (k % 9 == 0) and (i % 11 == 0):
                    ftype = burst_pool[(k + i) % len(burst_pool)]
                    fire((x, 0.0, z), (vx * 0.25, clamp_vy(34.0 + 6.0 * intensity), vz * 0.25), ftype, WHITEGOLD)

                if i % 12 == 0:
                    time.sleep(0.002)

            time.sleep(dt)

        time.sleep(0.20)

        # ==========================================================
        # Phase 3：裂谷闭合（一道超亮“缝线”扫过，全屏都能看懂）
        # ==========================================================
        close_ticks = int(round(54 * intensity))
        close_ticks = max(40, close_ticks)

        for k in range(close_ticks):
            t = k / max(1, close_ticks - 1)
            # gap 从大到近似 0
            gap = 26.0 * (1.0 - t) + 2.0
            seam_glow = 0.90 + 0.65 * math.sin(t * math.pi)

            # “闭合线”像扫描一样在 x 方向推进
            x_scan = -XMAX * 0.95 + (XMAX * 1.90) * t

            # 3A) 全局边缘随 gap 收拢
            for i in range(int(round(edge_pts * 0.75))):
                uu = (i / max(1, int(round(edge_pts * 0.75)) - 1)) * 2.0 - 1.0
                x = uu * XMAX
                cz = centerline_z(uu, 2.0 + t * 4.0)

                zL = cz + gap * 0.5
                zR = cz - gap * 0.5

                vx = (rnd() * 2.0 - 1.0) * 3.0
                vz = (rnd() * 2.0 - 1.0) * 4.0
                vy = clamp_vy(24.0 + 10.0 * seam_glow + 6.0 * intensity)

                col = EDGE_WHITE if i % 6 == 0 else EDGE_GOLD
                fire((x, 0.0, zL), (vx, vy, vz), T.nothing, col)
                fire((x, 0.0, zR), (vx, vy, -vz), T.nothing, col)

            # 3B) 扫描缝线本体：在 x_scan 附近打一堵超亮线墙
            seam_pts = int(round(26 + 18 * intensity))
            for i in range(seam_pts):
                pz = Z0 + (rnd() * 2.0 - 1.0) * (ZSPAN * 0.62)
                px = x_scan + (rnd() * 2.0 - 1.0) * (5.0 + 6.0 * (1.0 - t))
                vx = (rnd() * 2.0 - 1.0) * 6.0
                vz = (rnd() * 2.0 - 1.0) * 8.0
                vy = clamp_vy(30.0 + 12.0 * seam_glow + 6.0 * intensity)

                col = WHITEGOLD if i % 4 != 0 else EDGE_WHITE
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                if (k % 8 == 0) and (i % 13 == 0):
                    fire((px, 0.0, pz), (vx * 0.2, clamp_vy(40.0 + 6.0 * intensity), vz * 0.2), T.circle, WHITEGOLD)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 4：冲击波（闭合线爆出一圈波纹，壮观收束）
        # ==========================================================
        shock = int(round(96 * intensity))
        shock = max(70, shock)

        for i in range(shock):
            th = (2.0 * math.pi) * (i / shock)
            rad = 22.0 + 22.0 * rnd()

            # 位置：沿中心线附近随机一点，让冲击波更“活”
            u = (rnd() * 2.0 - 1.0) * 0.25
            px0 = u * XMAX * 0.35
            pz0 = centerline_z(u, 9.0) + (rnd() * 2.0 - 1.0) * 3.0

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vy = clamp_vy(46.0 + 10.0 * rnd() + 6.0 * intensity)

            # 绝大多数用 nothing 形成“波纹线”，少量用爆闪做“波峰”
            if i % 9 == 0:
                ftype = burst_pool[i % len(burst_pool)]
                col = WHITEGOLD if i % 18 != 0 else GOLD
                fire((px0, 0.0, pz0), (vx, vy, vz), ftype, col)
            else:
                col = EDGE_WHITE if i % 4 == 0 else EDGE_GOLD
                fire((px0, 0.0, pz0), (vx, vy, vz), T.nothing, col)

            if i % 12 == 0:
                time.sleep(0.008)

        time.sleep(0.25)


    def climax_aurora_cathedral(self, intensity=1.0):
        T = self.type_firework
        intensity = 0.05
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 极光调色板（青绿 -> 青蓝 -> 紫辉，少量金白电光）
        AUR_GREEN = (70, 255, 170)
        AUR_MINT  = (90, 240, 210)
        AUR_CYAN  = (70, 210, 255)
        AUR_BLUE  = (60, 120, 255)
        AUR_PURP  = (190, 90, 255)
        AUR_WHITE = (255, 245, 230)
        AUR_GOLD  = (255, 220, 120)

        # 舞台尺度（很大）
        XMAX = 40.0
        Z0 = 10.0
        ZSPAN = 62.0

        # 节奏/密度（intensity 越大越密）
        dt = 0.055 / max(0.7, intensity)
        ticks = int(round(150 * intensity))   # 约 8~12 秒级（随 intensity）
        ticks = max(60, ticks)

        ribbons = int(round(9 + 5 * intensity))   # 极光帘“主带”数量
        ribbons = max(5, ribbons)

        strands_per_ribbon = int(round(10 + 10 * intensity))  # 每条主带的竖向丝数
        strands_per_ribbon = max(6, strands_per_ribbon)

        particles_per_tick = int(round(10 + 10 * intensity))  # 帘面“雾化颗粒”
        particles_per_tick = max(5, particles_per_tick)

        # ---------------------------------------------------------
        # 工具：给定 x 与时间，生成极光帘的“中心线 z”
        # （多频叠加，形成自然飘动的带状波）
        # ---------------------------------------------------------
        def aurora_center_z(xn, t, layer_phase):
            # xn: x / XMAX in [-1,1]
            a1 = 14.0 * math.sin(0.9 * xn * math.pi + 0.8 * t + layer_phase)
            a2 = 7.0  * math.sin(2.6 * xn * math.pi - 1.1 * t + 0.7 * layer_phase)
            a3 = 2.0  * math.sin(9.0 * xn * math.pi + 2.0 * t)
            return Z0 + a1 + a2 + a3

        # ---------------------------------------------------------
        # 工具：极光颜色（随高度/相位渐变）
        # ---------------------------------------------------------
        def aurora_color(phase, depth, sparkle=False):
            # depth: 0 近景更亮，1 远景更冷
            p = (phase % 1.0)
            if p < 0.20:
                col = AUR_GREEN
            elif p < 0.40:
                col = AUR_MINT
            elif p < 0.60:
                col = AUR_CYAN
            elif p < 0.80:
                col = AUR_BLUE
            else:
                col = AUR_PURP

            if depth > 0.6:  # 远景稍暗冷
                if col == AUR_GREEN: col = AUR_MINT
                if col == AUR_MINT:  col = AUR_CYAN

            if sparkle:
                return AUR_WHITE if (rnd() < 0.7) else AUR_GOLD
            return col

        # =========================================================
        # Phase 0：先铺一层“冷色天空薄雾”（让极光更立体）
        # =========================================================
        bg = int(round(40 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (XMAX * 0.55)
            pz = Z0 + (rnd() * 2.0 - 1.0) * (ZSPAN * 0.55)
            vx = (rnd() * 2.0 - 1.0) * 4.0
            vz = (rnd() * 2.0 - 1.0) * 4.0
            vy = clamp_vy(14.0 + 4.0 * rnd())
            col = (20, 40, 90) if i % 3 else (40, 90, 170)
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)
            if i % 12 == 0:
                time.sleep(0.01)

        time.sleep(0.18)

        # =========================================================
        # Phase 1：极光帘幕主戏（两层：近景厚、远景薄；整体左右漂移）
        # =========================================================
        for k in range(ticks):
            t = k * dt
            breath = 0.75 + 0.55 * math.sin(t * 0.85)   # 呼吸亮度
            drift = 14.0 * math.sin(t * 0.25)           # 整体左右漂移（很慢）

            # 两层：depth=0 近景，depth=1 远景
            for depth in (0, 1):
                layer_phase = 1.7 if depth == 0 else -0.8
                layer_scale = 1.0 if depth == 0 else 0.78
                z_depth_shift = (-10.0 if depth == 0 else +14.0)  # 前后景分离

                # 每层的主带中心 x 坐标（均匀分布，但每条带有独立摆动）
                for r in range(ribbons):
                    u = (r / max(1, ribbons - 1)) * 2.0 - 1.0
                    x_center = u * (XMAX * 0.75) + drift * (0.35 if depth == 0 else 0.20)
                    # 每条主带有独立轻微游走
                    x_center += 10.0 * math.sin(t * (0.35 + 0.05 * r) + r * 0.9) * (0.65 if depth == 0 else 0.45)

                    # “帘”宽度：近景更宽更厚
                    width = (10.0 + 8.0 * (1.0 - abs(u))) * (1.15 if depth == 0 else 0.85)

                    # 帘面竖向丝：在 x_center 附近取多条线
                    for s in range(strands_per_ribbon):
                        sx = x_center + (rnd() * 2.0 - 1.0) * width
                        xn = max(-1.0, min(1.0, sx / XMAX))
                        cz = aurora_center_z(xn, t, layer_phase) + z_depth_shift

                        # 竖向丝的局部“摆幅”（形成清晰丝带纹）
                        ripple = 6.0 * math.sin(t * 1.6 + sx * 0.03 + r * 0.7)
                        pz = cz + ripple * (0.75 if depth == 0 else 0.55)

                        # 速度：上升为主，横向轻微摆动（像帘在风里飘）
                        vx = (rnd() * 2.0 - 1.0) * 6.0 + 8.0 * math.sin(t * 0.55 + r) * layer_scale
                        vz = (rnd() * 2.0 - 1.0) * 7.0 + 6.0 * math.cos(t * 0.60 + s * 0.2) * layer_scale
                        vy = clamp_vy((22.0 + 10.0 * breath) * layer_scale + 6.0 * intensity + 4.0 * max(0.0, math.sin(t + s * 0.08)))

                        # 颜色：沿时间相位流动，近景更亮
                        phase = (0.12 * r + 0.03 * s + 0.18 * t) % 1.0
                        col = aurora_color(phase, depth * 0.8, sparkle=False)

                        # 偶尔做“电光闪烁丝”（很少，但极光会更灵）
                        if (k % 8 == 0) and (s % 11 == 0) and (rnd() < 0.35):
                            col2 = aurora_color(phase, depth * 0.8, sparkle=True)
                            fire((sx, 0.0, pz), (vx * 0.6, clamp_vy(34.0 + 6.0 * intensity), vz * 0.6), T.circle, col2)

                        fire((sx, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    # 每条主带偶尔补一些“雾化粒子”，让帘面更丰满
                    if (r % 2 == 0) and (k % 2 == 0):
                        for i in range(max(2, particles_per_tick // (3 if depth == 0 else 4))):
                            sx = x_center + (rnd() * 2.0 - 1.0) * (width * 1.3)
                            xn = max(-1.0, min(1.0, sx / XMAX))
                            cz = aurora_center_z(xn, t, layer_phase) + z_depth_shift
                            pz = cz + (rnd() * 2.0 - 1.0) * 10.0

                            vx = (rnd() * 2.0 - 1.0) * 8.0
                            vz = (rnd() * 2.0 - 1.0) * 10.0
                            vy = clamp_vy(18.0 + 8.0 * breath + 6.0 * intensity)

                            phase = (0.2 * t + rnd()) % 1.0
                            col = aurora_color(phase, depth * 0.8, sparkle=False)
                            fire((sx, 0.0, pz), (vx, vy, vz), T.nothing, col)

            time.sleep(dt)

        time.sleep(0.22)

        # =========================================================
        # Phase 2：极光冠冕收束（顶部一圈“冠状高亮”，壮观但不狂炸）
        # =========================================================
        crown = int(round(120 * intensity))
        crown = max(60, crown)

        for i in range(crown):
            th = (2.0 * math.pi) * (i / crown)
            # 冠冕不是标准圆：做“尖瓣”起伏
            rad = 34.0 + 18.0 * (0.5 + 0.5 * math.sin(7.0 * th)) + 10.0 * rnd()

            px = math.cos(th) * rad
            pz = Z0 + 22.0 + math.sin(th) * (rad * 0.55)

            vx = math.cos(th) * (18.0 + 14.0 * rnd())
            vz = math.sin(th) * (22.0 + 16.0 * rnd())
            vy = clamp_vy(44.0 + 10.0 * rnd() + 6.0 * intensity)

            # 颜色：金白为主，夹青蓝/紫辉
            if i % 5 == 0:
                col = AUR_WHITE
                ftype = T.circle
            elif i % 5 == 1:
                col = AUR_GOLD
                ftype = T.circle
            else:
                col = [AUR_CYAN, AUR_BLUE, AUR_PURP, AUR_MINT][i % 4]
                ftype = T.nothing

            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 12 == 0:
                time.sleep(0.008)

        time.sleep(0.25)


    def climax_romantic_binary_constellation(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.6, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 浪漫调色板（香槟金/暖粉/玫瑰紫/象牙白）
        IVORY = (255, 245, 230)
        CHAMPAGNE = (255, 230, 170)
        GOLD = (255, 220, 120)
        ROSE = (255, 120, 200)
        LILAC = (210, 140, 255)
        DEEP_ROSE = (170, 70, 160)

        # 点睛类型（少量）
        jewel_pool = [T.circle, T.double_ball, T.mixed_color_ball, T.half_half_color_ball, T.planet_ball]

        # 舞台尺度（温柔但大）
        XW = 90.0
        ZW = 60.0
        Z0 = 8.0

        dt = 0.06 / max(0.7, intensity)

        # ==========================================================
        # Phase 0：柔和星尘底（暖色薄雾，营造氛围）
        # ==========================================================
        bg = int(round(55 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (XW * 0.55)
            pz = Z0 + (rnd() * 2.0 - 1.0) * (ZW * 0.45)
            vx = (rnd() * 2.0 - 1.0) * 4.0
            vz = (rnd() * 2.0 - 1.0) * 4.0
            vy = clamp_vy(14.0 + 4.0 * rnd())
            col = CHAMPAGNE if i % 3 else IVORY
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)
            if i % 12 == 0:
                time.sleep(0.01)

        time.sleep(0.18)

        # ==========================================================
        # Phase 1：双星登场（左右各一颗“恋人星”拉出柔光轨迹）
        # ==========================================================
        trail_ticks = int(round(72 * intensity))
        trail_ticks = max(54, trail_ticks)

        for k in range(trail_ticks):
            t = k / max(1, trail_ticks - 1)
            breathe = 0.75 + 0.55 * math.sin(t * math.pi)

            # 左星与右星的“轨迹中心”缓慢向中间靠拢，同时在 z 上轻微错位（立体感）
            left_x  = -XW * 0.75 + (XW * 0.50) * (t ** 1.05)
            right_x =  XW * 0.75 - (XW * 0.50) * (t ** 1.05)
            left_z  = Z0 - 10.0 + 8.0 * math.sin(t * 2.2)
            right_z = Z0 + 10.0 - 8.0 * math.sin(t * 2.2 + 0.7)

            # 每帧每颗星拉一束“丝带光轨”（多条 T.nothing 形成柔和体积）
            strands = int(round(10 + 10 * intensity))
            strands = max(10, strands)

            for s in range(strands):
                # 左侧丝带
                px = left_x + (rnd() * 2.0 - 1.0) * (7.0 + 4.0 * (1.0 - t))
                pz = left_z + (rnd() * 2.0 - 1.0) * (6.0 + 4.0 * (1.0 - t))

                # 速度：向上为主 + 向中间的温柔牵引
                vx = (0.0 - px) * 0.12 + (rnd() * 2.0 - 1.0) * 6.0
                vz = (Z0 - pz) * 0.06 + (rnd() * 2.0 - 1.0) * 5.0
                vy = clamp_vy(20.0 + 10.0 * breathe + 6.0 * intensity)

                col = ROSE if s % 4 == 0 else (CHAMPAGNE if s % 2 == 0 else IVORY)
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                # 右侧丝带
                px = right_x + (rnd() * 2.0 - 1.0) * (7.0 + 4.0 * (1.0 - t))
                pz = right_z + (rnd() * 2.0 - 1.0) * (6.0 + 4.0 * (1.0 - t))

                vx = (0.0 - px) * 0.12 + (rnd() * 2.0 - 1.0) * 6.0
                vz = (Z0 - pz) * 0.06 + (rnd() * 2.0 - 1.0) * 5.0
                vy = clamp_vy(20.0 + 10.0 * breathe + 6.0 * intensity)

                col = LILAC if s % 4 == 1 else (CHAMPAGNE if s % 2 == 0 else IVORY)
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                if s % 10 == 0:
                    time.sleep(0.002)

            # 每隔一小段给左右星各一个“柔光星点”
            if k % int(max(6, round(10 / max(0.7, intensity)))) == 0:
                fire((left_x, 0.0, left_z), (0.0, clamp_vy(34.0), 0.0), T.circle, IVORY)
                fire((right_x, 0.0, right_z), (0.0, clamp_vy(34.0), 0.0), T.circle, IVORY)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 2：中央交汇“心跳脉冲”（短、克制、但很抓人）
        # ==========================================================
        heartbeats = 3
        for hb in range(heartbeats):
            # 每次心跳：先柔光聚拢，再一次亮点爆闪
            burst = int(round(36 * intensity))
            for i in range(burst):
                th = (2.0 * math.pi) * (i / burst)
                rad = 18.0 + 14.0 * rnd()

                px = (rnd() * 2.0 - 1.0) * 4.0
                pz = Z0 + (rnd() * 2.0 - 1.0) * 4.0

                vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 4.0
                vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
                vy = clamp_vy(42.0 + 8.0 * rnd() + 6.0 * intensity)

                # 心跳色：香槟金与玫瑰粉交替
                col = GOLD if (i % 3 == 0) else (ROSE if (i % 3 == 1) else IVORY)

                # 大部分用 nothing 做光浪，少量用 jewel 做脉冲点
                if i % 8 == 0:
                    ftype = jewel_pool[i % len(jewel_pool)]
                else:
                    ftype = T.nothing

                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 12 == 0:
                    time.sleep(0.004)

            # 只用一次小爱心（避免俗套与重复）
            if hb == 1:
                fire((0.0, 0.0, Z0), (0.0, clamp_vy(36.0), 0.0), T.love_3D, ROSE)

            time.sleep(0.25)

        time.sleep(0.15)

        # ==========================================================
        # Phase 3：香槟玫瑰星尘雨（很大、很温柔、很壮观的收束）
        # ==========================================================
        rain = int(round(160 * intensity))
        rain = max(120, rain)

        for i in range(rain):
            # 从一个很大的“玫瑰云团”散开：中心在上方略靠后
            px = (rnd() * 2.0 - 1.0) * (XW * 0.55)
            pz = Z0 + 18.0 + (rnd() * 2.0 - 1.0) * (ZW * 0.35)

            th = (2.0 * math.pi) * rnd()
            rad = 12.0 + 22.0 * rnd()

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vy = clamp_vy(34.0 + 10.0 * rnd() + 6.0 * intensity)

            # 颜色：玫瑰/丁香/香槟/象牙交织，偶尔深玫瑰做层次
            mod = i % 10
            if mod == 0:
                col = IVORY
            elif mod in (1, 2, 3):
                col = CHAMPAGNE
            elif mod in (4, 5, 6):
                col = ROSE
            elif mod in (7, 8):
                col = LILAC
            else:
                col = DEEP_ROSE

            # 爆炸类型少量点睛，其余全部是光轨
            if i % 14 == 0:
                ftype = jewel_pool[i % len(jewel_pool)]
            else:
                ftype = T.nothing

            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 14 == 0:
                time.sleep(0.008)

        time.sleep(0.25)


    def climax_romantic_moonlit_vows(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.6, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 配色：月光银白 + 香槟金高光 + 玫瑰粉/淡紫点缀
        MOON_WHITE = (245, 250, 255)
        SILVER = (210, 225, 245)
        CHAMPAGNE = (255, 230, 170)
        GOLD = (255, 220, 120)
        ROSE = (255, 120, 200)
        LILAC = (210, 140, 255)
        DEEP_BLUE = (10, 16, 55)

        jewel_pool = [T.circle, T.double_ball, T.mixed_color_ball, T.half_half_color_ball, T.planet_ball]

        # 舞台尺度
        XMAX = 95.0
        Z0 = 10.0
        ZSPAN = 62.0

        dt = 0.055 / max(0.7, intensity)

        # ==========================================================
        # Phase 0：静谧夜空薄雾（很淡）
        # ==========================================================
        bg = int(round(45 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (XMAX * 0.55)
            pz = Z0 + (rnd() * 2.0 - 1.0) * (ZSPAN * 0.45)
            vx = (rnd() * 2.0 - 1.0) * 3.5
            vz = (rnd() * 2.0 - 1.0) * 3.5
            vy = clamp_vy(14.0 + 4.0 * rnd())
            col = DEEP_BLUE if i % 3 else SILVER
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)
            if i % 12 == 0:
                time.sleep(0.01)

        time.sleep(0.18)

        # ==========================================================
        # Phase 1：月光拱廊（左右两侧一排排拱门点亮，像仪式感场景）
        # ==========================================================
        arcade = int(round(8 + 4 * intensity))   # 拱门数量
        arcade = max(8, arcade)

        arch_pts = int(round(18 * intensity))
        arch_pts = max(14, arch_pts)

        for a in range(arcade):
            t = a / max(1, arcade - 1)
            # 拱门越靠后越小（纵深）
            scale = 0.55 + 0.75 * (1.0 - t)
            z_gate = Z0 + 18.0 + t * 28.0

            # 左右各一个拱门中心
            centers = [(-XMAX * (0.62 + 0.05 * math.sin(a)), z_gate),
                    ( XMAX * (0.62 + 0.05 * math.cos(a)), z_gate)]

            for (cx, cz) in centers:
                # 画半拱：参数 theta 从 0..pi
                for i in range(arch_pts):
                    th = math.pi * (i / max(1, arch_pts - 1))
                    rad = (18.0 + 10.0 * t) * scale

                    px = cx + math.cos(th) * rad
                    pz = cz + math.sin(th) * (rad * 0.85)

                    # 速度：轻柔向上 + 微微向内（像月光拱门在“亮起来”）
                    vx = (-cx) * 0.02 + (rnd() * 2.0 - 1.0) * 2.2
                    vz = (Z0 - pz) * 0.01 + (rnd() * 2.0 - 1.0) * 2.2
                    vy = clamp_vy(18.0 + 8.0 * intensity + 4.0 * (1.0 - abs(math.cos(th))))

                    # 银白为主，偶尔香槟金高光
                    col = CHAMPAGNE if ((a + i) % 7 == 0) else (MOON_WHITE if i % 3 else SILVER)
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                # 拱门“灯点”少量点睛
                if a % 2 == 0:
                    fire((cx, 0.0, cz), (0.0, clamp_vy(30.0), 0.0), T.circle, MOON_WHITE)

            time.sleep(0.09)

        time.sleep(0.20)

        # ==========================================================
        # Phase 2：誓言光线（中央一条优雅的弧形光轨被“写”出来）
        # ==========================================================
        vow_ticks = int(round(54 * intensity))
        vow_ticks = max(40, vow_ticks)

        for k in range(vow_ticks):
            t = k / max(1, vow_ticks - 1)
            # 弧线：从左下到右上（像一笔写出的誓言）
            x = -XMAX * 0.35 + (XMAX * 0.70) * t
            z = Z0 - 6.0 + 32.0 * math.sin(t * math.pi)  # 中间抬高

            # 光线厚度：多条丝并排
            strands = int(round(10 + 8 * intensity))
            for s in range(strands):
                px = x + (rnd() * 2.0 - 1.0) * 2.4
                pz = z + (rnd() * 2.0 - 1.0) * 2.6

                # 速度：沿弧线方向推进 + 上扬
                vx = (XMAX * 0.70) * 0.12 + (rnd() * 2.0 - 1.0) * 3.0
                vz = (math.cos(t * math.pi)) * 10.0 + (rnd() * 2.0 - 1.0) * 4.0
                vy = clamp_vy(22.0 + 10.0 * intensity + 8.0 * (0.5 + 0.5 * math.sin(t * math.pi)))

                # 颜色：银白->香槟金->玫瑰点缀
                if s % 9 == 0:
                    col = ROSE
                elif s % 4 == 0:
                    col = CHAMPAGNE
                else:
                    col = MOON_WHITE

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            # 弧线端点轻闪一下（像笔尖的光）
            if k % 10 == 0:
                fire((x, 0.0, z), (0.0, clamp_vy(34.0), 0.0), T.circle, MOON_WHITE)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 3：月冠轻闪 + 花瓣星尘雨（温柔的大收束）
        # ==========================================================
        # 3A 月冠（很克制的高光，不炸满）
        crown = int(round(48 * intensity))
        crown = max(36, crown)
        for i in range(crown):
            th = (2.0 * math.pi) * (i / crown)
            rad = 26.0 + 14.0 * (0.5 + 0.5 * math.sin(5.0 * th)) + 6.0 * rnd()

            px = math.cos(th) * rad
            pz = Z0 + 36.0 + math.sin(th) * (rad * 0.55)

            vx = math.cos(th) * (14.0 + 10.0 * rnd())
            vz = math.sin(th) * (16.0 + 12.0 * rnd())
            vy = clamp_vy(40.0 + 8.0 * rnd() + 6.0 * intensity)

            col = MOON_WHITE if i % 3 else GOLD
            ftype = T.circle if i % 4 == 0 else T.nothing
            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.20)

        # 3B 花瓣星尘雨（多是光轨，少量宝石点）
        rain = int(round(140 * intensity))
        rain = max(110, rain)

        for i in range(rain):
            # 从上方较大的云团散落
            px = (rnd() * 2.0 - 1.0) * (XMAX * 0.55)
            pz = Z0 + 22.0 + (rnd() * 2.0 - 1.0) * (ZSPAN * 0.35)

            th = (2.0 * math.pi) * rnd()
            rad = 10.0 + 18.0 * rnd()

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 5.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 9.0
            vy = clamp_vy(30.0 + 10.0 * rnd() + 6.0 * intensity)

            mod = i % 12
            if mod in (0, 1, 2):
                col = MOON_WHITE
            elif mod in (3, 4, 5):
                col = CHAMPAGNE
            elif mod in (6, 7):
                col = ROSE
            elif mod in (8, 9):
                col = LILAC
            else:
                col = SILVER

            ftype = jewel_pool[i % len(jewel_pool)] if (i % 16 == 0) else T.nothing
            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 14 == 0:
                time.sleep(0.008)

        time.sleep(0.25)


    def climax_dream_bubble_nebula(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.6, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 梦幻粉彩调色板（偏柔、偏雾）
        MIST = (235, 245, 255)
        MOON = (255, 245, 235)
        PEARL = (255, 250, 245)

        PINK = (255, 160, 210)
        LILAC = (210, 160, 255)
        SKY = (150, 210, 255)
        MINT = (160, 255, 220)
        SOFT_GOLD = (255, 230, 170)

        # 少量点睛类型（克制）
        sparkle_pool = [T.circle, T.planet_ball, T.planet_random_color, T.mixed_color_ball]

        # 舞台尺度（大而飘）
        XMAX = 105.0
        Z0 = 10.0
        ZSPAN = 70.0

        dt = 0.055 / max(0.7, intensity)

        # ==========================================================
        # Phase 0：梦雾底（柔和薄雾星尘，建立“梦境空气感”）
        # ==========================================================
        bg = int(round(70 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (XMAX * 0.60)
            pz = Z0 + (rnd() * 2.0 - 1.0) * (ZSPAN * 0.55)

            vx = (rnd() * 2.0 - 1.0) * 3.5
            vz = (rnd() * 2.0 - 1.0) * 3.5
            vy = clamp_vy(14.0 + 4.0 * rnd())

            col = MIST if i % 3 else MOON
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            if i % 14 == 0:
                time.sleep(0.008)

        time.sleep(0.18)

        # ==========================================================
        # Phase 1：梦泡上升（“泡群”从多个源点升起，每个泡都有外圈光晕）
        # ==========================================================
        bubble_sources = int(round(7 + 3 * intensity))
        bubble_sources = max(7, bubble_sources)

        # 固定几个梦泡源点（左右+前后），避免重复感
        sources = []
        for i in range(bubble_sources):
            x = ( (i / max(1, bubble_sources - 1)) * 2.0 - 1.0 ) * (XMAX * 0.65)
            # 源点在纵深上交错
            z = Z0 - 18.0 + (i % 3) * 10.0 + (rnd() * 2.0 - 1.0) * 6.0
            sources.append((x, z))

        rise_ticks = int(round(78 * intensity))
        rise_ticks = max(58, rise_ticks)

        for k in range(rise_ticks):
            t = k / max(1, rise_ticks - 1)
            breathe = 0.75 + 0.55 * math.sin(t * math.pi)

            # 每帧挑几个源点发泡（控制性能）
            launches = int(round(3 + 2 * intensity))
            for li in range(launches):
                sx, sz = sources[(k + li * 2) % len(sources)]

                # 泡的“大小”与颜色
                bubble_r = 10.0 + 16.0 * rnd()
                palette = [PINK, LILAC, SKY, MINT, SOFT_GOLD]
                base_col = palette[(k + li) % len(palette)]

                # 泡的外圈：用若干条 T.nothing 向四周轻轻散开 + 上升，形成“泡”的错觉
                ring_pts = int(round(12 + 8 * intensity))
                for i in range(ring_pts):
                    th = (2.0 * math.pi) * (i / ring_pts)
                    # 发射位置在源点附近（泡的起点）
                    px = sx + (rnd() * 2.0 - 1.0) * 2.5
                    pz = sz + (rnd() * 2.0 - 1.0) * 2.5

                    # 速度：环向扩散 + 上升（泡越大扩散越大）
                    vx = math.cos(th) * (0.55 * bubble_r) + (rnd() * 2.0 - 1.0) * 3.0
                    vz = math.sin(th) * (0.55 * bubble_r) + (rnd() * 2.0 - 1.0) * 4.0
                    vy = clamp_vy(20.0 + 10.0 * breathe + 6.0 * intensity + 4.0 * rnd())

                    # 外圈颜色：同色系，但偶尔用珍珠白高光
                    col = PEARL if (i % 5 == 0 and rnd() < 0.5) else base_col
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    # 少量“泡面闪点”（很克制）
                    if (k % 10 == 0) and (i % 6 == 0) and (rnd() < 0.25):
                        fire((px, 0.0, pz),
                            (vx * 0.25, clamp_vy(34.0 + 6.0 * intensity), vz * 0.25),
                            T.circle, PEARL)

                time.sleep(0.01)

            # 轻雾补充：让泡群之间不空
            fog = int(round(6 + 6 * intensity))
            for i in range(fog):
                px = (rnd() * 2.0 - 1.0) * (XMAX * 0.55)
                pz = Z0 + (rnd() * 2.0 - 1.0) * (ZSPAN * 0.45)
                vx = (rnd() * 2.0 - 1.0) * 5.0
                vz = (rnd() * 2.0 - 1.0) * 5.0
                vy = clamp_vy(16.0 + 8.0 * breathe + 6.0 * intensity)
                col = MIST if i % 2 == 0 else MOON
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 2：缎带彗光穿过泡群（两三条“丝带”横跨天空，非常梦幻）
        # ==========================================================
        ribbon_ticks = int(round(48 * intensity))
        ribbon_ticks = max(34, ribbon_ticks)

        for k in range(ribbon_ticks):
            t = k / max(1, ribbon_ticks - 1)
            pulse = 0.85 + 0.55 * math.sin(t * math.pi)

            # 两条丝带：一条偏上、一条偏下，z 深度不同（3D层次）
            for band in (0, 1):
                z_band = Z0 + (22.0 if band == 0 else -2.0) + (8.0 * math.sin(2.2 * t + band))
                z_band += (18.0 if band == 0 else -16.0)  # 前后层分离

                # 丝带沿 x 方向推进
                x_head = -XMAX * 0.95 + (XMAX * 1.90) * t
                width = 12.0 + 10.0 * (0.5 + 0.5 * math.sin(t * math.pi))

                ribbons = int(round(18 + 12 * intensity))
                for i in range(ribbons):
                    px = x_head + (rnd() * 2.0 - 1.0) * width
                    pz = z_band + (rnd() * 2.0 - 1.0) * 10.0

                    # 速度：强烈横向 + 上升，形成长飘带
                    vx = (22.0 + 16.0 * pulse) + (rnd() * 2.0 - 1.0) * 6.0
                    vz = (rnd() * 2.0 - 1.0) * (12.0 + 6.0 * pulse)
                    vy = clamp_vy(22.0 + 10.0 * intensity + 8.0 * pulse)

                    # 丝带颜色：偏冷（梦幻）+ 少量金粉
                    col = [SKY, LILAC, MINT, PEARL, SOFT_GOLD][(i + band) % 5]
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    # 丝带上偶尔出现“彗光结点”
                    if (k % 9 == 0) and (i % 11 == 0):
                        ftype = sparkle_pool[(k + i) % len(sparkle_pool)]
                        fire((px, 0.0, pz),
                            (vx * 0.25, clamp_vy(36.0 + 6.0 * intensity), vz * 0.25),
                            ftype, PEARL)

                    if i % 12 == 0:
                        time.sleep(0.002)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 3：梦泡“无声破裂”成柔光环 + 星尘雨（温柔高潮）
        # ==========================================================
        pop = int(round(160 * intensity))
        pop = max(120, pop)

        for i in range(pop):
            # 破裂点分布在上方较大区域
            px0 = (rnd() * 2.0 - 1.0) * (XMAX * 0.60)
            pz0 = Z0 + 22.0 + (rnd() * 2.0 - 1.0) * (ZSPAN * 0.45)

            th = (2.0 * math.pi) * rnd()
            rad = 14.0 + 22.0 * rnd()

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vy = clamp_vy(34.0 + 10.0 * rnd() + 6.0 * intensity)

            # 色彩：粉彩交织，珍珠白高光更梦幻
            mod = i % 11
            if mod in (0, 1):
                col = PEARL
            elif mod in (2, 3):
                col = SKY
            elif mod in (4, 5):
                col = LILAC
            elif mod in (6, 7):
                col = MINT
            elif mod == 8:
                col = SOFT_GOLD
            else:
                col = PINK

            # 大多数用 nothing 做“破裂波纹”，少量用 circle 做“轻响”点睛
            if i % 15 == 0:
                ftype = sparkle_pool[i % len(sparkle_pool)]
                fire((px0, 0.0, pz0), (vx, vy, vz), ftype, col)
            else:
                fire((px0, 0.0, pz0), (vx, vy, vz), T.nothing, col)

            if i % 14 == 0:
                time.sleep(0.008)

        time.sleep(0.25)

    def climax_whirlwind_tornado(self, intensity=1.0):
        T = self.type_firework
        intensity = 0.5
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else MIN_VY

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 风暴配色：冷青电光 + 风尘灰蓝 + 少量金白碎片
        STORM_CYAN = (120, 220, 255)
        STORM_BLUE = (60, 120, 255)
        DUST_1 = (180, 195, 220)
        DUST_2 = (130, 150, 190)
        DEEP = (10, 16, 55)
        WHITE = (255, 245, 230)
        GOLD = (255, 220, 120)

        sparkle_pool = [T.circle, T.planet_ball, T.planet_random_color, T.double_ball, T.mixed_color_ball]

        # 舞台尺度
        XMAX = 90.0
        ZMAX = 70.0
        Z0 = 10.0

        dt = 0.055 / max(0.7, intensity)

        # 旋风参数（底部半径大、顶部半径小）
        R0 = 46.0           # 底部半径
        R1 = 10.0           # 顶部半径（形成漏斗）
        HEIGHT = 88.0       # 用 vy 表达的“上升高度感”
        TWIST = 7.2         # 扭转强度（越大越“卷”）

        # 密度
        warm_ticks = int(round(30 * intensity))
        warm_ticks = max(24, warm_ticks)

        funnel_ticks = int(round(120 * intensity))   # 主体时长（约 7~12 秒）
        funnel_ticks = max(90, funnel_ticks)

        climax_ticks = int(round(34 * intensity))
        climax_ticks = max(26, climax_ticks)

        strands = int(round(26 + 22 * intensity))    # 每帧发射的风丝数量
        strands = max(28, strands)

        debris = int(round(6 + 6 * intensity))       # 每帧碎片点睛数量
        debris = max(6, debris)

        # ==========================================================
        # Phase 0：暗场风尘底（让旋风更立体）
        # ==========================================================
        bg = int(round(60 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (XMAX * 0.55)
            pz = Z0 + (rnd() * 2.0 - 1.0) * (ZMAX * 0.55)
            vx = (rnd() * 2.0 - 1.0) * 4.0
            vz = (rnd() * 2.0 - 1.0) * 4.0
            vy = clamp_vy(14.0 + 4.0 * rnd())
            col = DEEP if i % 3 else DUST_2
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)
            if i % 14 == 0:
                time.sleep(0.008)

        time.sleep(0.18)

        # ==========================================================
        # Phase 1：集风（地面气流从四周向中心汇聚，旋风将起）
        # ==========================================================
        for k in range(warm_ticks):
            t = k / max(1, warm_ticks - 1)
            pull = 0.25 + 0.35 * t

            shots = int(round(18 + 14 * intensity))
            for i in range(shots):
                # 从外围来
                ang = 2.0 * math.pi * rnd()
                rad = (R0 * 1.05) + 18.0 * rnd()
                px = math.cos(ang) * rad
                pz = Z0 + math.sin(ang) * rad

                # 向中心吸 + 微旋转偏置
                vx = (-px) * pull + (-math.sin(ang)) * (10.0 + 10.0 * t) + (rnd() * 2.0 - 1.0) * 3.0
                vz = (-(pz - Z0)) * pull + ( math.cos(ang)) * (10.0 + 10.0 * t) + (rnd() * 2.0 - 1.0) * 3.0
                vy = clamp_vy(18.0 + 8.0 * intensity + 6.0 * t)

                col = DUST_1 if i % 3 else STORM_CYAN
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                if i % 14 == 0:
                    time.sleep(0.002)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 2：漏斗成形（真正 3D：不同“高度层”半径不同，形成锥体）
        # 思路：每帧取多条“风丝”，给它一个高度参数 h（0..1），
        # 半径从 R0 -> R1 收缩，角度随时间+高度扭转（TWIST），
        # 再用切向速度制造旋转，用径向速度制造吸入，用 vy 抬升。
        # ==========================================================
        for k in range(funnel_ticks):
            t = k / max(1, funnel_ticks - 1)
            # 呼吸：让漏斗像活的一样
            breathe = 0.78 + 0.55 * math.sin(t * math.pi)

            # 漏斗整体轻微漂移（避免太“死板”）
            drift_x = 8.0 * math.sin(t * 1.2)
            drift_z = 6.0 * math.cos(t * 1.05)

            for i in range(strands):
                # 高度层 h：0(底) -> 1(顶)
                h = (rnd() ** 0.65)  # 偏向底部更密（更像龙卷风）
                # 半径随高度收缩
                r = (R0 + (R1 - R0) * (h ** 1.15)) * (0.92 + 0.18 * rnd())

                # 角度：随时间推进 + 高度扭转（形成“螺旋上卷”的视觉）
                ang = (2.0 * math.pi) * (rnd() + 0.35 * t) + TWIST * h + 1.7 * math.sin(t * 2.0 + h * 3.0)

                px = drift_x + math.cos(ang) * r
                pz = Z0 + drift_z + math.sin(ang) * r

                # 切向方向（旋转）
                tx = -math.sin(ang)
                tz =  math.cos(ang)

                # 径向方向（吸入）
                rx = -math.cos(ang)
                rz = -math.sin(ang)

                # 速度分解：旋转 + 吸入 + 少量抖动
                spin = (26.0 + 28.0 * breathe) * (0.55 + 0.75 * (1.0 - h))  # 底部更猛
                suck = (10.0 + 18.0 * breathe) * (0.35 + 0.65 * h)          # 越高越吸紧

                vx = tx * spin + rx * suck + (rnd() * 2.0 - 1.0) * 4.0
                vz = tz * spin + rz * suck + (rnd() * 2.0 - 1.0) * 6.0

                # vy：高度越高越“轻”，但永远 > 0
                vy = clamp_vy(18.0 + 18.0 * intensity + (26.0 * h) + 10.0 * breathe)

                # 颜色：底部更尘、顶部更电光
                if h < 0.25:
                    col = DUST_2 if (i % 4) else DUST_1
                elif h < 0.60:
                    col = DUST_1 if (i % 3) else STORM_BLUE
                else:
                    col = STORM_CYAN if (i % 3) else WHITE

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                if i % 18 == 0:
                    time.sleep(0.0015)

            # 碎片/电光点睛：沿漏斗“中上段”卷起（很少，但会非常像风暴）
            if k % int(max(5, round(9 / max(0.7, intensity)))) == 0:
                for j in range(debris):
                    h = 0.45 + 0.50 * rnd()
                    r = (R0 + (R1 - R0) * (h ** 1.15)) * (0.75 + 0.25 * rnd())
                    ang = (2.0 * math.pi) * rnd() + TWIST * h + 0.6 * t * 2.0 * math.pi

                    px = drift_x + math.cos(ang) * r
                    pz = Z0 + drift_z + math.sin(ang) * r

                    # 碎片速度：更“被甩出去”
                    tx = -math.sin(ang)
                    tz =  math.cos(ang)

                    vx = tx * (42.0 + 10.0 * rnd()) + (rnd() * 2.0 - 1.0) * 6.0
                    vz = tz * (46.0 + 14.0 * rnd()) + (rnd() * 2.0 - 1.0) * 10.0
                    vy = clamp_vy(38.0 + 10.0 * rnd() + 6.0 * intensity)

                    ftype = sparkle_pool[(k + j) % len(sparkle_pool)]
                    col = WHITE if j % 2 == 0 else (GOLD if j % 3 == 0 else STORM_CYAN)
                    fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            # 风眼：中心少量上升细雾（让“空心”更明显）
            if k % 6 == 0:
                eye = int(round(4 + 4 * intensity))
                for e in range(eye):
                    px = drift_x + (rnd() * 2.0 - 1.0) * 3.2
                    pz = Z0 + drift_z + (rnd() * 2.0 - 1.0) * 3.2
                    vx = (rnd() * 2.0 - 1.0) * 2.0
                    vz = (rnd() * 2.0 - 1.0) * 2.0
                    vy = clamp_vy(20.0 + 10.0 * intensity)
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, DEEP)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 3：风暴爆发收束（顶部“电闪环”+ 甩出一圈碎片）
        # ==========================================================
        for k in range(climax_ticks):
            t = k / max(1, climax_ticks - 1)
            flash = 0.85 + 0.65 * math.sin(t * math.pi)

            # 顶部电闪环（不是漩涡发射：是一次性环形爆发）
            ring = int(round((64 + 40 * intensity) * flash))
            ring = max(56, ring)

            for i in range(ring):
                th = 2.0 * math.pi * (i / ring)
                # 顶部半径小一点，更像漏斗顶端“抽紧后爆发”
                rad = (R1 + 14.0) * (0.8 + 0.4 * rnd())

                px = math.cos(th) * rad
                pz = Z0 + 6.0 + math.sin(th) * rad

                vx = math.cos(th) * (26.0 + 18.0 * rnd())
                vz = math.sin(th) * (30.0 + 22.0 * rnd())
                vy = clamp_vy(46.0 + 10.0 * rnd() + 6.0 * intensity)

                ftype = sparkle_pool[i % len(sparkle_pool)] if (i % 7 == 0) else T.nothing
                col = WHITE if i % 3 == 0 else (STORM_CYAN if i % 3 == 1 else GOLD)
                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 14 == 0:
                    time.sleep(0.004)

            time.sleep(0.07)

        time.sleep(0.25)


    def climax_rotating_world_tree(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.6, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else (MIN_VY + 0.5)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 配色：树干（木色）+ 树冠（青绿）+ 金色高光
        BARK_1 = (120, 72, 38)
        BARK_2 = (80, 48, 26)
        SAP_GLOW = (255, 220, 120)

        LEAF_1 = (90, 240, 170)
        LEAF_2 = (70, 210, 255)
        LEAF_3 = (210, 160, 255)
        LEAF_HI = (255, 245, 230)

        jewel_pool = [T.circle, T.planet_ball, T.planet_random_color, T.mixed_color_ball, T.half_half_color_ball]

        # 尺度（你可以按场景再放大）
        trunk_steps = int(round(16 + 8 * intensity))          # 树干分段
        trunk_steps = max(18, trunk_steps)

        rings_per_step = int(round(8 + 6 * intensity))        # 每段木纹“环”
        rings_per_step = max(8, rings_per_step)

        branches_levels = [0.28, 0.45, 0.62, 0.78]             # 4层开枝高度（相对）
        branch_each = int(round(8 + 4 * intensity))            # 每层枝数
        branch_each = max(8, branch_each)

        canopy_layers = int(round(5 + 3 * intensity))          # 树冠层数
        canopy_layers = max(5, canopy_layers)

        canopy_rays = int(round(26 + 16 * intensity))          # 每层叶幕射线数
        canopy_rays = max(28, canopy_rays)

        dt = 0.055 / max(0.7, intensity)

        # =========================
        # Phase 0：根基柔光（地面气息）
        # =========================
        base = int(round(36 * intensity))
        for i in range(base):
            th = 2.0 * math.pi * rnd()
            rad = 10.0 + 18.0 * rnd()
            px = math.cos(th) * (rad * 0.35)
            pz = math.sin(th) * (rad * 0.35)

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 4.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
            vy = clamp_vy(18.0 + 6.0 * intensity)

            col = SAP_GLOW if i % 7 == 0 else BARK_1
            fire((px, 0.0, pz), (vx * 0.35, vy, vz * 0.35), T.nothing, col)
            if i % 10 == 0:
                time.sleep(0.008)

        time.sleep(0.15)

        # =========================
        # Phase 1：树干螺旋生长（核心：用 Rz 旋转“木纹环”）
        # =========================
        # 木纹环的基向量：先给一个小的横向，再叠加向上速度
        base_ring_vec = np.array([[14.0], [0.0], [0.0]])  # 只负责横向“木纹环”的半径速度分量

        trunk_twist = 26.0 + 18.0 * intensity            # 每段的旋转增量（度）——扭生感
        trunk_up = 26.0 + 10.0 * intensity               # 树干整体向上速度基准

        for s in range(trunk_steps):
            t = s / max(1, trunk_steps - 1)

            # 树干逐段变细（越往上环越小）
            shrink = 1.0 - 0.55 * (t ** 1.15)
            ring_speed = (10.0 + 10.0 * intensity) * shrink

            # 这一段的扭转角度（度）
            twist_deg = s * trunk_twist + 18.0 * math.sin(t * 3.2)

            # 每段喷几个“木纹环”，像树皮绕着长
            for r in range(rings_per_step):
                # 在这一段内部再做一点微旋转，让木纹更细腻
                deg = twist_deg + (360.0 / rings_per_step) * r

                vxy = Rz(deg) @ (base_ring_vec * (ring_speed * (0.85 + 0.25 * rnd())))
                vx = float(vxy[0, 0]) + (rnd() * 2.0 - 1.0) * 1.6
                vz = float(vxy[1, 0]) + (rnd() * 2.0 - 1.0) * 2.2  # 注意：这里把矩阵的“y”当作 z 平面横向分量用
                vy = clamp_vy(trunk_up + 10.0 * intensity + 10.0 * (1.0 - abs(2.0 * t - 1.0)))

                # 树干颜色：下深上浅 + 偶尔“树脂金光”
                if (s % 5 == 0) and (r % 7 == 0) and (rnd() < 0.6):
                    col = SAP_GLOW
                else:
                    col = BARK_2 if (r % 2 == 0) else BARK_1

                fire((0.0, 0.0, 0.0), (vx, vy, vz), T.nothing, col)

                if r % 6 == 0:
                    time.sleep(0.002)

            # 在特定高度开枝（下一段做）
            time.sleep(dt)

            # =========================
            # Phase 2：分层开枝（旋转扇出枝丫，形成 3D）
            # =========================
            for lv_idx, lv in enumerate(branches_levels):
                if abs(t - lv) < (0.5 / trunk_steps):  # 命中该层
                    # 枝丫基向量：横向大、向上中等、带 z 深度交错
                    branch_base = np.array([[28.0 + 10.0 * intensity],
                                            [0.0],
                                            [0.0]])

                    # 枝丫围绕树干一圈“旋转开花”
                    for b in range(branch_each):
                        ang = (360.0 / branch_each) * b + twist_deg * 0.55 + 22.0 * lv_idx

                        vxy = Rz(ang) @ branch_base
                        vx = float(vxy[0, 0]) + (rnd() * 2.0 - 1.0) * 3.0
                        vz = float(vxy[1, 0]) + (rnd() * 2.0 - 1.0) * 4.5

                        # 让枝丫在 3D 上“前后交错”（不是只有平面）
                        depth = (1.0 if (b % 2 == 0) else -1.0) * (10.0 + 10.0 * rnd())
                        vz += depth

                        vy = clamp_vy(22.0 + 10.0 * intensity + 6.0 * (1.0 - lv) + 6.0 * rnd())

                        # 枝：主要是树皮光轨，枝尖给一点叶色“发芽感”
                        tip_col = LEAF_1 if (b % 3 == 0) else LEAF_2
                        col = SAP_GLOW if (b % 7 == 0) else (BARK_1 if rnd() < 0.6 else BARK_2)
                        fire((0.0, 0.0, 0.0), (vx, vy, vz), T.nothing, col)

                        # 枝尖“叶芽闪点”（很少，但会让枝丫更像活的）
                        if b % 4 == 0:
                            fire((0.0, 0.0, 0.0),
                                (vx * 0.25, clamp_vy(34.0 + 6.0 * intensity), vz * 0.25),
                                T.circle, tip_col)

                        time.sleep(0.01)

                    time.sleep(0.12)

        time.sleep(0.18)

        # =========================
        # Phase 3：巨型树冠（分层叶幕：大、柔、梦幻）
        # =========================
        # 树冠“基向量”——射线向外扩散，靠 Rz 做环向铺开
        canopy_base = np.array([[32.0 + 18.0 * intensity],
                                [0.0],
                                [0.0]])

        for layer in range(canopy_layers):
            u = layer / max(1, canopy_layers - 1)
            # 每层半径更大、向上更轻柔
            radial = (0.85 + 0.55 * u)
            lift = 26.0 + 10.0 * intensity + 8.0 * (1.0 - u)

            # 轻微“风”让树冠像在呼吸摆动
            wind_deg = 18.0 * math.sin(layer * 1.7)

            for i in range(canopy_rays):
                ang = (360.0 / canopy_rays) * i + wind_deg

                vxy = Rz(ang) @ (canopy_base * radial)
                vx = float(vxy[0, 0]) + (rnd() * 2.0 - 1.0) * 6.0
                vz = float(vxy[1, 0]) + (rnd() * 2.0 - 1.0) * 9.0

                # 让树冠有“球形体积”：前后层次更明显
                vz += (rnd() * 2.0 - 1.0) * (16.0 + 10.0 * u)

                vy = clamp_vy(lift + 10.0 * rnd())

                # 叶色渐变：青绿 -> 青蓝 -> 淡紫 -> 珍珠白高光
                mod = (i + layer * 3) % 12
                if mod < 4:
                    col = LEAF_1
                elif mod < 7:
                    col = LEAF_2
                elif mod < 10:
                    col = LEAF_3
                else:
                    col = LEAF_HI

                # 大多数用光轨（温柔又壮观），少量宝石点睛
                if i % 13 == 0:
                    ftype = jewel_pool[(i + layer) % len(jewel_pool)]
                    fire((0.0, 0.0, 0.0), (vx, vy, vz), ftype, col)
                else:
                    fire((0.0, 0.0, 0.0), (vx, vy, vz), T.nothing, col)

                if i % 14 == 0:
                    time.sleep(0.003)

            time.sleep(0.12)

        # =========================
        # Phase 4：树冠“星辉加冕”（一次很大的顶端收束）
        # =========================
        crown = int(round(90 * intensity))
        crown = max(70, crown)

        for i in range(crown):
            th = 2.0 * math.pi * (i / crown)
            rad = 22.0 + 18.0 * rnd()

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 6.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vy = clamp_vy(44.0 + 10.0 * rnd() + 6.0 * intensity)

            col = LEAF_HI if i % 3 == 0 else SAP_GLOW
            ftype = T.circle if i % 4 == 0 else T.nothing
            fire((0.0, 0.0, 0.0), (vx, vy, vz), ftype, col)

            if i % 12 == 0:
                time.sleep(0.008)

        time.sleep(0.25)

    def climax_christmas_tree_persistent(self, intensity=1.0, keepalive_seconds=18.0):
        T = self.type_firework
        intensity = 0.05
        keepalive_seconds = max(6.0, float(keepalive_seconds))
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else (MIN_VY + 0.5)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 颜色
        GREEN_D = (25, 110, 65)
        GREEN_M = (70, 200, 120)
        GREEN_H = (140, 255, 190)

        TRUNK_1 = (120, 72, 38)
        TRUNK_2 = (80, 48, 26)

        STAR_GOLD  = (255, 220, 120)
        STAR_WHITE = (255, 245, 230)

        LIGHTS = [
            (255, 90, 90),
            (255, 160, 80),
            (90, 210, 255),
            (210, 140, 255),
            (160, 255, 220),
        ]

        # 树形尺度（把轮廓做得更“像🌲”：宽底尖顶）
        W = 40.0  # 轮廓更明显：比你上个版本更宽
        vy_min = 18.0 + 6.0 * intensity
        vy_max = 66.0 + 10.0 * intensity

        # 3D 厚度：三层
        z_layers = [-10.0, 0.0, 10.0]

        # 刷新节奏：越小越“常亮”，但线程更多；这里取折中
        refresh_dt = 0.28 / max(0.75, intensity)

        # 树干做“粗而稳”：横向速度极小，让它像固定灯带
        trunk_w = 9.0
        trunk_d = 6.0
        trunk_cols = int(round(10 + 6 * intensity))
        trunk_rows = int(round(8 + 4 * intensity))
        # trunk_cols = max(12, trunk_cols)
        # trunk_rows = max(8, trunk_rows)

        # 轮廓点：多一些才清晰
        outline_pts = int(round(60 + 30 * intensity))
        # outline_pts = max(110, outline_pts)

        # 填充点：少量，避免盖住轮廓
        fill_pts = int(round(10 + 8 * intensity))
        # fill_pts = max(18, fill_pts)

        # 背景轻雾（非常少）
        def bg_mist(n=18):
            for i in range(n):
                px = (rnd() * 2.0 - 1.0) * (W * 0.42)
                pz = (rnd() * 2.0 - 1.0) * 24.0
                vx = (rnd() * 2.0 - 1.0) * 2.5
                vz = (rnd() * 2.0 - 1.0) * 3.0
                vy = clamp_vy(14.0 + 3.0 * rnd())
                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, (25, 45, 95))

        # “轮廓高度函数”：frac=1-|x|/(W/2)，并让顶部更尖
        def height_frac(x):
            frac = 1.0 - min(1.0, abs(x) / (W * 0.5))
            return max(0.0, frac) ** 1.22

        # 持续刷新：树干 + 轮廓 + 少量填充
        start = time.time()
        ornament_done = False
        star_done = False

        while (time.time() - start) < keepalive_seconds:
            tsec = time.time() - start
            phase = tsec / keepalive_seconds

            # 每次刷新先来一点点背景雾，增强对比（很轻）
            if int(tsec / refresh_dt) % 6 == 0:
                bg_mist(n=10)

            # -------- 树干刷新（持续可见的关键）--------
            for layer_i, z0 in enumerate(z_layers):
                for ix in range(trunk_cols):
                    for iz in range(trunk_rows):
                        x = (-trunk_w * 0.5) + trunk_w * (ix / max(1, trunk_cols - 1))
                        z = z0 + (-trunk_d * 0.5) + trunk_d * (iz / max(1, trunk_rows - 1))

                        # 极稳的“灯带式”树干
                        vx = (rnd() * 2.0 - 1.0) * 0.7
                        vz = (rnd() * 2.0 - 1.0) * 0.9
                        vy = clamp_vy(22.0 + 6.0 * intensity + 2.0 * rnd())

                        col = TRUNK_1 if (ix + iz + layer_i) % 2 == 0 else TRUNK_2
                        fire((x, 0.0, z), (vx, vy, vz), T.nothing, col)

                time.sleep(0.01)

            # -------- 轮廓刷新（确保🌲形状一直在）--------
            # 轮廓两条边 + 少量“加粗”
            for layer_i, z0 in enumerate(z_layers):
                layer_boost = 0.90 if layer_i == 0 else (1.0 if layer_i == 1 else 1.12)

                for i in range(outline_pts):
                    x = (-W * 0.5) + W * (i / max(1, outline_pts - 1))
                    frac = height_frac(x)

                    # 轮廓越靠顶越亮、速度越“直”
                    z = z0 + (rnd() * 2.0 - 1.0) * (1.2 + 1.6 * (1.0 - frac))

                    vx = (rnd() * 2.0 - 1.0) * 0.9
                    vz = (rnd() * 2.0 - 1.0) * 1.2
                    vy = clamp_vy(vy_min + (vy_max - vy_min) * frac * layer_boost)

                    if frac > 0.72:
                        col = GREEN_H
                    elif frac > 0.40:
                        col = GREEN_M
                    else:
                        col = GREEN_D

                    fire((x, 0.0, z), (vx, vy, vz), T.nothing, col)

                    # 轮廓加粗（但不加太多，避免卡）
                    if i % 4 == 0:
                        fire((x, 0.0, z + (1.6 if layer_i == 2 else -1.2)),
                            (vx * 0.85, clamp_vy(vy * 0.98), vz * 0.85),
                            T.nothing, col)

                time.sleep(0.02)

            # -------- 少量内部填充（维持“树体感”，但不遮轮廓）--------
            if int(tsec / refresh_dt) % 2 == 0:
                for layer_i, z0 in enumerate(z_layers):
                    for i in range(fill_pts):
                        h = rnd() ** 0.75
                        max_x = (W * 0.5) * (1.0 - h)
                        x = (rnd() * 2.0 - 1.0) * max_x
                        z = z0 + (rnd() * 2.0 - 1.0) * (7.0 + 10.0 * (1.0 - h))

                        vx = (rnd() * 2.0 - 1.0) * 1.2
                        vz = (rnd() * 2.0 - 1.0) * 1.8
                        vy = clamp_vy(vy_min + (vy_max - vy_min) * h * (0.90 + 0.12 * math.sin(tsec)))

                        col = GREEN_M if i % 3 == 0 else GREEN_D
                        fire((x, 0.0, z), (vx, vy, vz), T.nothing, col)

            # -------- 中段：彩灯只点缀一次（否则会重复很乱）--------
            if (not ornament_done) and (phase > 0.40):
                ornaments = int(round(26 + 8 * intensity))
                for i in range(ornaments):
                    h = 0.22 + 0.75 * rnd()
                    max_x = (W * 0.5) * (1.0 - h)
                    x = (rnd() * 2.0 - 1.0) * max_x
                    z = (rnd() * 2.0 - 1.0) * (10.0 + 12.0 * (1.0 - h))

                    vy = clamp_vy(vy_min + (vy_max - vy_min) * h * 0.90)
                    vx = (rnd() * 2.0 - 1.0) * 1.0
                    vz = (rnd() * 2.0 - 1.0) * 1.3

                    col = LIGHTS[i % len(LIGHTS)]
                    fire((x, 0.0, z), (vx, clamp_vy(vy + 10.0), vz), T.circle, col)

                    if i % 6 == 0:
                        time.sleep(0.02)

                ornament_done = True
                time.sleep(0.15)

            # -------- 末段：顶端星星只出现一次（必须非常清晰）--------
            if (not star_done) and (phase > 0.75):
                # 星核
                fire((0.0, 0.0, 0.0), (0.0, clamp_vy(vy_max + 12.0), 0.0), T.circle, STAR_GOLD)
                time.sleep(0.08)

                # 星芒（用 Rz 旋转做 5角节奏）
                rays = 10
                base = np.array([[26.0 + 10.0 * intensity], [0.0], [0.0]])
                for i in range(rays):
                    deg = (360.0 / rays) * i
                    vxy = Rz(deg) @ base
                    scale = 1.0 if (i % 2 == 0) else 0.55

                    vx = float(vxy[0, 0]) * scale + (rnd() * 2.0 - 1.0) * 2.0
                    vz = float(vxy[1, 0]) * scale + (rnd() * 2.0 - 1.0) * 3.0
                    vy = clamp_vy(vy_max + (16.0 if i % 2 == 0 else 12.0))

                    col = STAR_WHITE if (i % 3 == 0) else STAR_GOLD
                    fire((0.0, 0.0, 0.0), (vx, vy, vz), T.nothing, col)
                    time.sleep(0.015)

                star_done = True
                time.sleep(0.12)

            time.sleep(refresh_dt)

        time.sleep(0.25)



    def climax_pillar_forest_uplift(self, intensity=1.0):
        T = self.type_firework
        intensity = max(0.6, float(intensity))
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else (MIN_VY + 0.5)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 颜色：柱芯冷白 + 青蓝辉光 + 金白顶帽
        CORE = (245, 250, 255)
        ICE  = (170, 220, 255)
        CYAN = (120, 220, 255)
        DEEP = (60, 120, 255)
        GOLD = (255, 220, 120)
        PEARL = (255, 245, 230)

        # 3D 柱阵布局：x 方向一排排，z 三层（前/中/后）
        XMAX = 95.0
        z_rows = [-22.0, 0.0, 22.0]   # 明确前后层次
        cols_per_row = int(round(11 + 5 * intensity))
        cols_per_row = max(9, min(18, cols_per_row))

        xs = [(-XMAX + (2 * XMAX) * (i / max(1, cols_per_row - 1))) for i in range(cols_per_row)]

        dt = 0.055 / max(0.7, intensity)

        # 柱子高度通过 vy 模拟：越大越“高”
        vy_base = 22.0 + 10.0 * intensity
        vy_peak = 72.0 + 12.0 * intensity

        # ==========================================================
        # Phase 0：地基点火（很短，强调“从地面起”）
        # ==========================================================
        base_shots = int(round(40 * intensity))
        for i in range(base_shots):
            x = xs[i % len(xs)]
            z = z_rows[i % len(z_rows)] + (rnd() * 2.0 - 1.0) * 3.0

            vx = (rnd() * 2.0 - 1.0) * 1.0
            vz = (rnd() * 2.0 - 1.0) * 1.2
            vy = clamp_vy(18.0 + 6.0 * intensity + 4.0 * rnd())

            col = CYAN if i % 5 == 0 else ICE
            fire((x, 0.0, z), (vx, vy, vz), T.nothing, col)

            if i % 12 == 0:
                time.sleep(0.01)

        time.sleep(0.15)

        # ==========================================================
        # Phase 1：立柱成林（从左到右“竖直上拔”的波，方向非常明确）
        # ==========================================================
        build_ticks = int(round(46 * intensity))
        build_ticks = max(34, build_ticks)

        for k in range(build_ticks):
            t = k / max(1, build_ticks - 1)

            # “能量波前沿”从左扫到右：front in [-XMAX, XMAX]
            front = -XMAX + (2 * XMAX) * t

            for zi, z0 in enumerate(z_rows):
                depth_boost = 0.92 if zi == 0 else (1.0 if zi == 1 else 1.08)  # 前层更亮一点

                for xi, x0 in enumerate(xs):
                    # 离波前越近越亮越高（形成清晰的扫过效果）
                    d = abs(x0 - front)
                    influence = max(0.0, 1.0 - d / 28.0)  # 影响半径
                    if influence <= 0.0:
                        continue

                    # 一根柱子用几股竖丝加粗（但保持方向几乎纯 +Y）
                    strands = 2 + (1 if xi % 3 == 0 else 0)
                    for s in range(strands):
                        px = x0 + (rnd() * 2.0 - 1.0) * 1.3
                        pz = z0 + (rnd() * 2.0 - 1.0) * 1.7

                        vx = (rnd() * 2.0 - 1.0) * 0.8   # 横向极小，确保“竖直柱”
                        vz = (rnd() * 2.0 - 1.0) * 1.0
                        vy = clamp_vy((vy_base + (vy_peak - vy_base) * influence) * depth_boost)

                        # 颜色：波前核心更白，外缘偏蓝
                        if influence > 0.78:
                            col = CORE if (s % 2 == 0) else PEARL
                        elif influence > 0.45:
                            col = ICE
                        else:
                            col = DEEP

                        fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    if xi % 6 == 0:
                        time.sleep(0.0015)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 2：柱内“上行脉冲”（每根柱子出现沿高度上行的亮点，仍是竖直方向）
        # ==========================================================
        pulse_ticks = int(round(40 * intensity))
        pulse_ticks = max(30, pulse_ticks)

        for k in range(pulse_ticks):
            t = k / max(1, pulse_ticks - 1)

            # 脉冲位置：从低到高（通过 vy 逐步增大来模拟）
            pulse_vy = clamp_vy(vy_base + (vy_peak - vy_base) * t)

            for zi, z0 in enumerate(z_rows):
                depth_boost = 0.95 if zi == 0 else (1.0 if zi == 1 else 1.05)

                # 每次只点亮部分柱，避免太卡，同时节奏更像“呼吸”
                for xi, x0 in enumerate(xs):
                    if (xi + k) % 2 != 0:
                        continue

                    px = x0 + (rnd() * 2.0 - 1.0) * 1.0
                    pz = z0 + (rnd() * 2.0 - 1.0) * 1.3

                    vx = (rnd() * 2.0 - 1.0) * 0.7
                    vz = (rnd() * 2.0 - 1.0) * 0.9
                    vy = clamp_vy(pulse_vy * depth_boost + 6.0 * rnd())

                    col = PEARL if (xi % 6 == 0) else ICE
                    # 少量用 circle 做“脉冲亮点”
                    if xi % 7 == 0 and (k % 3 == 0):
                        fire((px, 0.0, pz), (vx, clamp_vy(vy + 10.0), vz), T.circle, col)
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                time.sleep(0.01)

            time.sleep(0.05)

        time.sleep(0.18)

        # ==========================================================
        # Phase 3：柱顶冠帽（每根柱子的“顶端”统一加冕一次，柱子主题收束很明确）
        # ==========================================================
        caps = int(round(2 + 1 * intensity))
        caps = max(2, caps)

        for c in range(caps):
            for zi, z0 in enumerate(z_rows):
                for xi, x0 in enumerate(xs):
                    if (xi + c) % 2 == 1:
                        continue

                    # 顶帽位置仍在柱底发射，但用更强 vy + 更亮颜色表达“顶端冠帽”
                    px = x0 + (rnd() * 2.0 - 1.0) * 0.9
                    pz = z0 + (rnd() * 2.0 - 1.0) * 1.2

                    vx = (rnd() * 2.0 - 1.0) * 1.2
                    vz = (rnd() * 2.0 - 1.0) * 1.6
                    vy = clamp_vy(vy_peak + 10.0 + 6.0 * rnd())

                    col = GOLD if (xi % 5 == 0) else PEARL
                    # 顶帽少量宝石点睛（不铺天盖地）
                    if xi % 6 == 0:
                        fire((px, 0.0, pz), (vx, vy, vz), T.planet_random_color, col)
                    else:
                        fire((px, 0.0, pz), (vx, vy, vz), T.circle, col)

                    if xi % 7 == 0:
                        time.sleep(0.004)

            time.sleep(0.18)

        time.sleep(0.25)

    def climax_hypercube_lattice_collapse(self, intensity=1.0):
        T = self.type_firework
        intensity = 0.3
        MIN_VY = 12.0

        def clamp_vy(v):
            v = float(v)
            return v if v > MIN_VY else (MIN_VY + 0.5)

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 科幻配色：冷白/冰蓝/深蓝 + 金白核心
        PEARL = (255, 245, 230)
        COREW = (245, 250, 255)
        ICE   = (170, 220, 255)
        DEEP  = (60, 120, 255)
        VIO   = (190, 90, 255)
        GOLD  = (255, 220, 120)

        jewel = [T.circle, T.planet_ball, T.planet_random_color, T.mixed_color_ball, T.half_half_color_ball, T.double_ball]

        # 舞台参数（cube 在 XZ 平面投影很大，靠 vy 做“高度层”形成 3D）
        S = 72.0                        # 立方体半边长（越大越震撼）
        layer_z = [-18.0, 0.0, 18.0]    # 前/中/后纵深层
        dt = 0.055 / max(0.7, intensity)

        # 通用：根据“深度层”给不同的亮度与 vy（形成真正的 3D 层次）
        def depth_style(li):
            # li: 0后,1中,2前
            if li == 0:
                return (DEEP, 0.92, 0.88)   # 颜色、vy倍率、亮度倍率
            elif li == 1:
                return (ICE, 1.00, 1.00)
            else:
                return (COREW, 1.08, 1.12)

        # ==========================================================
        # Phase 0：很轻的“空间尘埃”让全息框更显眼
        # ==========================================================
        bg = int(round(48 * intensity))
        for i in range(bg):
            px = (rnd() * 2.0 - 1.0) * (S * 0.65)
            pz = (rnd() * 2.0 - 1.0) * (S * 0.55)
            vx = (rnd() * 2.0 - 1.0) * 3.5
            vz = (rnd() * 2.0 - 1.0) * 4.0
            vy = clamp_vy(14.0 + 4.0 * rnd())
            fire((px, 0.0, pz), (vx, vy, vz), T.nothing, (15, 25, 70) if i % 3 else DEEP)
            if i % 14 == 0:
                time.sleep(0.008)

        time.sleep(0.16)

        # ==========================================================
        # Phase 1：全息立方体“框架锁定”（12条边：每条边用多股线条加粗）
        # ==========================================================
        # 立方体 8 个顶点（只用 XZ，Y 用 vy 表达层次）
        verts = [
            (-S, -S), ( S, -S), ( S,  S), (-S,  S),  # 底面 4 点
            (-S, -S), ( S, -S), ( S,  S), (-S,  S),  # 顶面投影同样 4 点（靠 vy 区分）
        ]
        # 边连接（底面4，顶面4，竖边4）——用索引表示
        edges = [
            (0,1),(1,2),(2,3),(3,0),   # 底面
            (4,5),(5,6),(6,7),(7,4),   # 顶面（用更高 vy 表示）
            (0,4),(1,5),(2,6),(3,7),   # 竖边（用 vy 变化做“抬升”错觉）
        ]

        edge_samples = int(round(18 + 10 * intensity))
        edge_samples = max(18, edge_samples)
        edge_strands = int(round(2 + 2 * intensity))
        edge_strands = max(2, min(5, edge_strands))

        # 边的“高度编码”：底面低、顶面高、竖边中间渐变
        def edge_vy_mode(ei):
            if ei < 4:      # 底面
                return 26.0 + 10.0 * intensity
            elif ei < 8:    # 顶面
                return 54.0 + 12.0 * intensity
            else:           # 竖边
                return 40.0 + 12.0 * intensity

        for li, zoff in enumerate(layer_z):
            base_col, vy_mul, lum = depth_style(li)

            for ei, (a, b) in enumerate(edges):
                (x0, z0) = verts[a]
                (x1, z1) = verts[b]

                vy_edge = clamp_vy(edge_vy_mode(ei) * vy_mul)

                for s in range(edge_samples):
                    u = s / max(1, edge_samples - 1)
                    px = x0 + (x1 - x0) * u
                    pz = zoff + (z0 + (z1 - z0) * u)

                    # 速度方向：沿边“描线”，同时向上抬升，形成框线的视觉
                    tx = (x1 - x0)
                    tz = (z1 - z0)
                    m = (tx * tx + tz * tz) ** 0.5 + 1e-6
                    tx, tz = tx / m, tz / m

                    # 沿边推进 + 轻微稳定抖动（不要太飘，不然框会糊）
                    vx0 = tx * (18.0 + 10.0 * intensity) + (rnd() * 2.0 - 1.0) * 1.6
                    vz0 = tz * (18.0 + 10.0 * intensity) + (rnd() * 2.0 - 1.0) * 2.2

                    # 线条加粗：平行偏移几股
                    for k in range(edge_strands):
                        off = (k - (edge_strands - 1) / 2.0) * 1.2
                        # 法线偏移
                        nx, nz = -tz, tx
                        col = PEARL if ((s + k + ei) % 11 == 0) else base_col
                        fire((px + nx * off, 0.0, pz + nz * off), (vx0, vy_edge, vz0), T.nothing, col)

                    if s % 7 == 0:
                        time.sleep(0.0015)

                # 每条边的端点偶尔给一点“锁定闪点”
                if ei % 3 == 0:
                    corner_col = PEARL if ei % 2 == 0 else GOLD
                    fire((x0, 0.0, zoff + z0), (0.0, clamp_vy(vy_edge + 10.0), 0.0), T.circle, corner_col)

            time.sleep(0.06)

        time.sleep(0.20)

        # ==========================================================
        # Phase 2：内部光栅晶格（像空间坐标网格被点亮）
        # 重点：规则但不死板，点阵+短线混合，形成“全息体积”
        # ==========================================================
        grid_n = 5  # 5x5x3（纵深3层）
        grid_pts_per_tick = int(round(28 + 18 * intensity))
        grid_ticks = int(round(42 * intensity))
        #grid_ticks = max(32, grid_ticks)

        for k in range(grid_ticks):
            t = k / max(1, grid_ticks - 1)
            pulse = 0.75 + 0.55 * math.sin(t * math.pi)

            for li, zoff in enumerate(layer_z):
                base_col, vy_mul, lum = depth_style(li)

                for i in range(grid_pts_per_tick):
                    gx = int(rnd() * grid_n)
                    gz = int(rnd() * grid_n)

                    # 映射到 [-S, S]
                    px = (-S) + (2 * S) * (gx / max(1, grid_n - 1))
                    pz = zoff + (-S) + (2 * S) * (gz / max(1, grid_n - 1))

                    # “网格发光”速度：几乎竖直，轻微横向让它像悬浮点
                    vx = (rnd() * 2.0 - 1.0) * (2.0 + 2.0 * pulse)
                    vz = (rnd() * 2.0 - 1.0) * (2.6 + 2.4 * pulse)
                    vy = clamp_vy((22.0 + 22.0 * pulse + 8.0 * intensity) * vy_mul)

                    # 颜色：靠中心更亮，边缘更冷
                    edge = max(abs(px) / S, abs((pz - zoff)) / S)
                    if edge < 0.35:
                        col = PEARL if (i % 7 == 0) else ICE
                    elif edge < 0.75:
                        col = base_col
                    else:
                        col = DEEP

                    # 绝大多数用 nothing（全息点），少量用 circle 作为“节点灯”
                    if (i % 13 == 0) and (k % 3 == 0):
                        fire((px, 0.0, pz), (vx * 0.25, clamp_vy(vy + 14.0), vz * 0.25), T.circle, col)
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    if i % 14 == 0:
                        time.sleep(0.0015)

            time.sleep(0.045)

        time.sleep(0.18)

        # ==========================================================
        # Phase 3：崩塌收束（所有光栅向中心“吸入”，但 vy 仍保持正值）
        # 视觉：x/z 向 0 聚拢，形成“空间塌陷”
        # ==========================================================
        collapse_ticks = int(round(40 * intensity))
        collapse_ticks = max(30, collapse_ticks)

        collapse_shots = int(round(36 + 20 * intensity))
        collapse_shots = max(36, collapse_shots)

        for k in range(collapse_ticks):
            t = k / max(1, collapse_ticks - 1)
            grip = 0.55 + 0.85 * t  # 吸入强度逐步增强

            for li, zoff in enumerate(layer_z):
                base_col, vy_mul, lum = depth_style(li)

                for i in range(collapse_shots):
                    # 从整个立方体体积采样点
                    px = (rnd() * 2.0 - 1.0) * S
                    pz = zoff + (rnd() * 2.0 - 1.0) * S

                    # 向中心吸入：vx,vz 指向 0
                    vx = (-px) * (0.55 * grip) + (rnd() * 2.0 - 1.0) * 5.0
                    vz = (-(pz - zoff)) * (0.60 * grip) + (rnd() * 2.0 - 1.0) * 6.0
                    vy = clamp_vy((28.0 + 18.0 * grip + 8.0 * intensity) * vy_mul)

                    # 吸入越强越亮
                    col = PEARL if (i % 9 == 0) else (ICE if grip < 1.0 else COREW)
                    fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                    # 崩塌边缘偶尔有“紫电”
                    if (k % 8 == 0) and (i % 17 == 0):
                        fire((px, 0.0, pz),
                            (vx * 0.25, clamp_vy(vy + 16.0), vz * 0.25),
                            T.circle, VIO)

                    if i % 18 == 0:
                        time.sleep(0.0018)

            time.sleep(0.04)

        time.sleep(0.18)

        # ==========================================================
        # Phase 4：核心超新星外爆（一次“震撼的连贯高潮”）
        # ==========================================================
        finale = int(round(170 * intensity))
        finale = max(130, finale)

        for i in range(finale):
            th = 2.0 * math.pi * (i / finale)
            rad = 18.0 + 26.0 * rnd()

            # 外爆方向（x/z 放大），vy 给很高形成“核心喷薄”
            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 14.0
            vy = clamp_vy(56.0 + 14.0 * rnd() + 10.0 * intensity)

            # 颜色：金白核心 + 冷白外层 + 少量紫蓝电晕
            if i % 11 == 0:
                ftype = jewel[i % len(jewel)]
                col = GOLD if i % 22 == 0 else PEARL
            elif i % 7 == 0:
                ftype = T.circle
                col = VIO if (i % 14 == 0) else COREW
            else:
                ftype = T.nothing
                col = ICE if i % 3 else COREW

            fire((0.0, 0.0, 0.0), (vx, vy, vz), ftype, col)

            if i % 14 == 0:
                time.sleep(0.006)

        time.sleep(0.25)

    def climax_dna_helix_ascension(self, intensity=1.0):
        T = self.type_firework
        intensity = 0.4

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 配色：两条链不同色相，梯级用冷白，终章加金白
        A1 = (90, 210, 255)     # cyan
        A2 = (190, 90, 255)     # violet
        B1 = (255, 120, 200)    # rose
        B2 = (255, 220, 120)    # gold
        WHITE = (255, 245, 230)
        ICE = (245, 250, 255)

        # 终章点睛（不要太多，避免卡）
        jewel_pool = [T.circle, T.planet_ball, T.planet_random_color, T.mixed_color_ball, T.double_ball, T.half_half_color_ball]

        # 时间步进：intensity 越大越快越紧凑
        dt = 0.055 / intensity

        # 主体参数：全依赖 intensity（无 max）
        steps = int(80 * intensity) + 55                 # 双螺旋持续时间
        strands_per_step = int(10 * intensity) + 10      # 每步每条链的“丝数”（越多越厚）
        rung_every = int(6 / intensity) + 3              # 梯级出现频率（intensity大 -> 更频繁）
        finale_steps = int(26 * intensity) + 18          # 解链终章时长

        # 螺旋半径与扭转速度（角度用“度”，适配你现成的 Rz）
        base_radius = (18.0 + 20.0 * intensity)
        twist_deg_per_step = (18.0 + 26.0 * intensity)

        # 上升速度（保证 vy>0，只用 intensity 缩放）
        vy_base = intensity * 26.0
        vy_gain = intensity * 56.0

        # 起点（地面）稍微前后分层，让 3D 更明显
        z_layers = [-10.0, 0.0, 10.0]

        # ==========================================================
        # Phase 1：双螺旋上升（两条链 180° 相位差）
        # ==========================================================
        v_base = np.array([[1.0], [0.0], [0.0]])  # 用 Rz 旋转生成 XZ 平面方向（这里把矩阵第2分量当 Z 用）

        for k in range(steps):
            h = k / (steps - 1)  # 0..1
            # 螺旋半径随高度轻微“呼吸”，更像活体
            breathe = 0.78 + 0.55 * math.sin(h * math.pi * 2.0)
            radius = base_radius * (0.85 + 0.25 * breathe)

            # 两条链的角度（B 相位差 180°）
            angA = k * twist_deg_per_step
            angB = angA + 180.0

            # 上升速度逐步增强（越往后越震撼）
            vy = vy_base + vy_gain * (0.25 + 0.75 * h)

            # 每步发多条“丝”，让链条看起来连续、粗细可控
            for li, z0 in enumerate(z_layers):
                depth_boost = 0.92 + 0.08 * li  # 前层略亮/略强

                for s in range(strands_per_step):
                    # A 链方向
                    dirA = Rz(angA + (rnd() * 2.0 - 1.0) * 6.0) @ v_base
                    vxA = float(dirA[0, 0]) * radius * (0.65 + 0.25 * rnd())
                    vzA = float(dirA[1, 0]) * radius * (0.65 + 0.25 * rnd())

                    # B 链方向
                    dirB = Rz(angB + (rnd() * 2.0 - 1.0) * 6.0) @ v_base
                    vxB = float(dirB[0, 0]) * radius * (0.65 + 0.25 * rnd())
                    vzB = float(dirB[1, 0]) * radius * (0.65 + 0.25 * rnd())

                    # 让两链更“缠绕”：加一点相反的微偏置
                    vxA += (rnd() * 2.0 - 1.0) * (3.0 + 3.0 * intensity)
                    vzA += (rnd() * 2.0 - 1.0) * (5.0 + 4.0 * intensity)
                    vxB += (rnd() * 2.0 - 1.0) * (3.0 + 3.0 * intensity)
                    vzB += (rnd() * 2.0 - 1.0) * (5.0 + 4.0 * intensity)

                    # 颜色沿高度渐变（梦幻又清晰）
                    if h < 0.5:
                        colA = A1
                        colB = B1
                    else:
                        colA = A2
                        colB = B2

                    # 发射位置：围绕中心略抖动，叠出“厚度”
                    px = (rnd() * 2.0 - 1.0) * (2.0 + 1.2 * intensity)
                    pz = z0 + (rnd() * 2.0 - 1.0) * (2.6 + 1.6 * intensity)

                    fire((px, 0.0, pz), (vxA, vy * depth_boost, vzA), T.nothing, colA)
                    fire((px, 0.0, pz), (vxB, vy * depth_boost, vzB), T.nothing, colB)

                    if s % 10 == 0:
                        time.sleep(0.0015)

            # ======================================================
            # 梯级横梁（“基因天梯”的关键视觉）：每隔一段出现一圈横向连线
            # 做法：在当前角度，用两侧相反方向的速度发一串，形成“横梁”
            # ======================================================
            if k % rung_every == 0:
                rung_rays = int(12 * intensity) + 10
                rung_radius = radius * 0.72

                for li, z0 in enumerate(z_layers):
                    # 横梁方向取当前 A 的方向，但发“正反两束”形成连线
                    dirR = Rz(angA + 90.0) @ v_base
                    rx = float(dirR[0, 0]) * rung_radius
                    rz = float(dirR[1, 0]) * rung_radius

                    for i in range(rung_rays):
                        jitter = (rnd() * 2.0 - 1.0) * (4.0 + 2.0 * intensity)
                        vx1 = rx + jitter
                        vz1 = rz + (rnd() * 2.0 - 1.0) * (6.0 + 3.0 * intensity)
                        vx2 = -rx + jitter
                        vz2 = -rz + (rnd() * 2.0 - 1.0) * (6.0 + 3.0 * intensity)

                        vy_r = intensity * (36.0 + 30.0 * (k / (steps - 1)))

                        px = 0.0 + (rnd() * 2.0 - 1.0) * 2.0
                        pz = z0 + (rnd() * 2.0 - 1.0) * 2.2

                        fire((px, 0.0, pz), (vx1, vy_r, vz1), T.nothing, ICE)
                        fire((px, 0.0, pz), (vx2, vy_r, vz2), T.nothing, ICE)

                        # 梯级端点偶尔闪一下，强化“结构感”
                        if i % 9 == 0:
                            fire((px, 0.0, pz), (vx1 * 0.25, intensity * 70.0, vz1 * 0.25), T.circle, WHITE)

                        if i % 10 == 0:
                            time.sleep(0.002)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 2：解链终章（双螺旋“外翻扩张”→ 彩色能量雨，震撼收束）
        # ==========================================================
        for k in range(finale_steps):
            t = k / (finale_steps - 1)
            # 半径迅速扩大，形成“解链外翻”的瞬间
            radius = base_radius * (1.0 + 1.2 * t) * (1.0 + 0.25 * math.sin(t * math.pi))
            vy = intensity * (64.0 + 40.0 * t)

            burst = int(34 * intensity) + 28
            for li, z0 in enumerate(z_layers):
                for i in range(burst):
                    ang = (k * twist_deg_per_step * 1.4) + (360.0 * (i / burst))
                    dirV = Rz(ang) @ v_base
                    vx = float(dirV[0, 0]) * radius + (rnd() * 2.0 - 1.0) * (10.0 + 8.0 * intensity)
                    vz = float(dirV[1, 0]) * radius + (rnd() * 2.0 - 1.0) * (16.0 + 10.0 * intensity)

                    # 颜色：彩色能量雨（白金+紫蓝+粉青交错）
                    m = (i + k) % 6
                    if m == 0:
                        col = WHITE
                    elif m == 1:
                        col = B2
                    elif m == 2:
                        col = A2
                    elif m == 3:
                        col = A1
                    elif m == 4:
                        col = B1
                    else:
                        col = ICE

                    # 少量用 jewel 点睛，其余用 nothing 保证连贯光轨
                    if i % 13 == 0:
                        ftype = jewel_pool[(i + k) % len(jewel_pool)]
                    else:
                        ftype = T.nothing

                    px = (rnd() * 2.0 - 1.0) * 3.0
                    pz = z0 + (rnd() * 2.0 - 1.0) * 3.5
                    fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                    if i % 16 == 0:
                        time.sleep(0.0025)

            time.sleep(0.05 / intensity)

        time.sleep(0.25)


    def climax_lissajous_knot_sculpture(self, intensity=1.0):
        intensity = 0.5
        T = self.type_firework

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 光谱色（更“雕塑感”，避免像普通乱炸）
        C_CYAN   = (90, 210, 255)
        C_BLUE   = (60, 120, 255)
        C_VIOLET = (190, 90, 255)
        C_ROSE   = (255, 120, 200)
        C_GOLD   = (255, 220, 120)
        C_WHITE  = (255, 245, 230)
        C_ICE    = (245, 250, 255)

        jewel_pool = [
            T.circle,
            T.planet_ball,
            T.planet_random_color,
            T.mixed_color_ball,
            T.double_ball,
            T.half_half_color_ball
        ]

        # 时间步进：intensity 越大越紧凑
        dt = 0.055 / intensity

        # 总时长（ticks * dt）：随 intensity 变化但都很长、很连贯
        ticks = int(230 * intensity) + 140

        # 每步发射数量（不要太离谱，但足够“雕塑密度”）
        per_tick = int(7 * intensity) + 7

        # “结”的频率组合（3D knot 关键：互质频率 + 相位差）
        a = 3
        b = 2
        c = 5

        # 速度尺度（决定结的“体积”）
        V = 34.0 + 26.0 * intensity
        Vz = 44.0 + 30.0 * intensity
        Vy_base = 22.0 + 18.0 * intensity  # 保证 vy > 0
        Vy_amp  = 20.0 + 22.0 * intensity  # 结的“竖向呼吸”

        # 3D 纵深层：让结不是平面的
        z_layers = [-14.0, -4.0, 4.0, 14.0]

        # 结点强调频率（越大越频繁）
        beat_every = int(10 / intensity) + 6

        # ----------------------------------------------------------
        # 工具：按参数相位选择颜色（让结看起来像“光谱雕塑”）
        # ----------------------------------------------------------
        def spectrum(p):
            # p in [0,1)
            if p < 0.18:
                return C_CYAN
            if p < 0.36:
                return C_BLUE
            if p < 0.54:
                return C_VIOLET
            if p < 0.72:
                return C_ROSE
            if p < 0.90:
                return C_GOLD
            return C_ICE

        # ==========================================================
        # Phase 1：结的“雕刻生成”（持续、连贯、3D）
        # ==========================================================
        for k in range(ticks):
            t = (2.0 * math.pi) * (k / (ticks - 1))

            # 结的“呼吸”与“紧缩”节奏（像活体雕塑）
            breathe = 0.78 + 0.55 * math.sin(0.65 * t)
            tighten = 0.70 + 0.55 * math.sin(0.35 * t + 1.2)

            for li, z0 in enumerate(z_layers):
                depth_boost = 0.90 + 0.05 * li

                for i in range(per_tick):
                    # 在 t 附近做多采样，形成“丝带厚度”
                    tt = t + (rnd() * 2.0 - 1.0) * (0.12 + 0.10 * intensity)

                    # 李萨如结速度场（核心）
                    vx = (V  * math.sin(a * tt + 0.7)) * (0.80 + 0.30 * breathe)
                    vz = (Vz * math.sin(c * tt + 1.9)) * (0.75 + 0.35 * tighten)

                    # vy 必须 > 0：用 base + amp*(0..1) 结构
                    vy_wave = 0.50 + 0.50 * math.sin(b * tt + 2.3)  # [0,1]
                    vy = Vy_base + Vy_amp * vy_wave

                    # 少量抖动避免“数学太死板”
                    vx += (rnd() * 2.0 - 1.0) * (5.0 + 5.0 * intensity)
                    vz += (rnd() * 2.0 - 1.0) * (7.0 + 7.0 * intensity)

                    # 发射位置：围绕中心很小的云团，突出“速度雕刻”
                    px = (rnd() * 2.0 - 1.0) * (2.6 + 2.2 * intensity)
                    pz = z0 + (rnd() * 2.0 - 1.0) * (3.2 + 2.8 * intensity)

                    # 颜色按相位走光谱，让形体更可读
                    phase = (0.12 * k + 0.31 * i + 0.07 * li) / (ticks)
                    col = spectrum(phase % 1.0)

                    fire((px, 0.0, pz), (vx * depth_boost, vy * depth_boost, vz), T.nothing, col)

                    # 让“结的筋络”更清晰：偶尔加一条近似同向的“并行丝”
                    if (i % 3 == 0) and (li % 2 == 0):
                        fire((px, 0.0, pz),
                            (vx * 0.78 * depth_boost, (vy + 10.0 * intensity) * depth_boost, vz * 0.78),
                            T.nothing, C_ICE)

                    if i % 10 == 0:
                        time.sleep(0.0015)

            # ======================================================
            # 结点强调：周期性在“结心”附近闪烁，让观众看懂拓扑结构
            # ======================================================
            if k % beat_every == 0:
                # 结点高光（少量，避免卡）
                flashes = int(10 * intensity) + 10
                for j in range(flashes):
                    tt = t + (j / flashes) * (0.8 + 0.6 * intensity)

                    vx = (V  * math.sin(a * tt + 0.7)) * 0.55
                    vz = (Vz * math.sin(c * tt + 1.9)) * 0.55
                    vy_wave = 0.50 + 0.50 * math.sin(b * tt + 2.3)
                    vy = (Vy_base + Vy_amp * vy_wave) + (18.0 + 12.0 * intensity)

                    # 白金闪点突出“结点”
                    col = C_WHITE if (j % 2 == 0) else C_GOLD
                    ftype = T.circle if (j % 3 != 0) else jewel_pool[(j + k) % len(jewel_pool)]

                    fire((0.0, 0.0, 0.0), (vx, vy, vz), ftype, col)

                    if j % 8 == 0:
                        time.sleep(0.002)

            time.sleep(dt)

        time.sleep(0.20)

        # ==========================================================
        # Phase 2：结心“解放”终章（从结结构外翻成光谱雨）
        # ==========================================================
        finale_ticks = int(28 * intensity) + 20
        finale_burst = int(55 * intensity) + 60

        for k in range(finale_ticks):
            u = k / (finale_ticks - 1)

            # 外翻尺度：越到后越大
            scale = 0.85 + 1.55 * u
            vy = (Vy_base + 26.0 * intensity) + (50.0 + 40.0 * intensity) * u

            for i in range(finale_burst):
                th = (2.0 * math.pi) * (i / finale_burst)

                vx = math.cos(th) * (26.0 + 44.0 * intensity) * scale + (rnd() * 2.0 - 1.0) * (10.0 + 10.0 * intensity)
                vz = math.sin(th) * (34.0 + 56.0 * intensity) * scale + (rnd() * 2.0 - 1.0) * (16.0 + 14.0 * intensity)

                # 光谱雨颜色交错
                phase = (i / finale_burst + 0.22 * u) % 1.0
                col = spectrum(phase)

                # 少量 jewel 点睛，其余保持连续光轨
                if i % 15 == 0:
                    ftype = jewel_pool[(i + k) % len(jewel_pool)]
                else:
                    ftype = T.nothing

                fire((0.0, 0.0, 0.0), (vx, vy, vz), ftype, col)

                if i % 18 == 0:
                    time.sleep(0.0028)

            time.sleep(0.05 / intensity)

        time.sleep(0.25)


    def climax_mobius_loom(self, intensity=1.0):
        T = self.type_firework

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 配色：丝带渐变（冷->暖->紫->白金）
        PAL = [
            (90, 210, 255),   # cyan
            (70, 120, 255),   # blue
            (190, 90, 255),   # violet
            (255, 120, 200),  # rose
            (255, 220, 120),  # gold
            (255, 245, 230),  # pearl
        ]

        # ---------------------------
        # 固定“舞台几何”和“时间节奏”
        # ---------------------------
        ticks = 90            # 总步数（固定）
        dt = 0.085            # 每步间隔（固定，约 7.6 秒）

        # 莫比乌斯参数（固定）
        R = 46.0              # 主半径
        W = 12.0              # 带宽（半宽）
        sXZ = 0.78            # XZ 速度缩放
        sY  = 9.5             # y 形变映射强度
        base_up = 22.0        # 保证 vy 始终为正（固定）

        # intensity 只影响“每步粒子数量”
        p_main = int(18 * intensity)      # 主织带粒子/步
        p_stitch = int(6 * intensity)     # 针脚粒子/触发
        p_crown = int(120 * intensity)    # 终章加冕粒子数

        # ---------------------------
        # 工具：莫比乌斯带嵌入（u in [0,2pi), v in [-W,W]）
        # 返回一个 3D 点 (x,y,z)，我们把它映射成“速度向量”
        # ---------------------------
        def mobius_point(u, v):
            cu = math.cos(u)
            su = math.sin(u)
            cu2 = math.cos(u * 0.5)
            su2 = math.sin(u * 0.5)

            x = (R + v * cu2) * cu
            z = (R + v * cu2) * su
            y = v * su2
            return x, y, z

        # ---------------------------
        # Phase 1：织带成环（持续“雕刻”莫比乌斯带）
        # ---------------------------
        for k in range(ticks):
            # 环绕相位（固定推进）
            u0 = (2.0 * math.pi) * (k / (ticks - 1))

            # 每步的颜色段（按 u0 映射）
            col = PAL[int((u0 / (2.0 * math.pi)) * len(PAL)) % len(PAL)]

            # 主织带：在当前 u0 附近撒一圈 “v” 分布，让带子有厚度
            for i in range(p_main):
                # u 在当前相位附近做轻微扩展，形成连续丝带
                u = u0 + (rnd() * 2.0 - 1.0) * 0.22

                # v 选在带宽上：中间多，边缘也有（避免只有一条线）
                if i % 5 == 0:
                    v = (1.0 if (i % 10 == 0) else -1.0) * W * (0.85 + 0.10 * rnd())
                else:
                    v = (rnd() * 2.0 - 1.0) * W * (0.75 + 0.20 * rnd())

                x, y, z = mobius_point(u, v)

                # 速度向量：XZ 按几何点发散，Y 用 base_up + (y+W)*sY 映射，确保 vy>0
                vx = x * sXZ + (rnd() * 2.0 - 1.0) * 4.0
                vz = z * sXZ + (rnd() * 2.0 - 1.0) * 6.0
                vy = base_up + (y + W) * sY + (rnd() * 2.0 - 1.0) * 3.0  # 永远 > 0

                # 位置围绕中心微抖动，突出“织造”的感觉
                px = (rnd() * 2.0 - 1.0) * 2.0
                pz = (rnd() * 2.0 - 1.0) * 2.5

                fire((px, 0.0, pz), (vx, vy, vz), T.nothing, col)

                # 偶尔给边缘一颗“缎光点”
                if i % 17 == 0:
                    fire((px, 0.0, pz), (vx * 0.25, vy + 16.0, vz * 0.25), T.circle, (255, 245, 230))

                if i % 18 == 0:
                    time.sleep(0.0015)

            # -----------------------
            # 针脚：每隔几步把两侧边缘“缝合”
            # 视觉：你会看到带子有“被织起来”的工艺感
            # -----------------------
            if k % 7 == 0:
                for j in range(p_stitch):
                    u = u0 + (j / (p_stitch + 1)) * 0.9
                    # 两侧边缘 v=±W
                    x1, y1, z1 = mobius_point(u, +W)
                    x2, y2, z2 = mobius_point(u, -W)

                    # 用两束相向速度制造“针脚横梁”
                    vx1 = x1 * 0.58 + (rnd() * 2.0 - 1.0) * 3.0
                    vz1 = z1 * 0.58 + (rnd() * 2.0 - 1.0) * 4.0
                    vy1 = base_up + (y1 + W) * (sY * 0.8) + 8.0

                    vx2 = x2 * 0.58 + (rnd() * 2.0 - 1.0) * 3.0
                    vz2 = z2 * 0.58 + (rnd() * 2.0 - 1.0) * 4.0
                    vy2 = base_up + (y2 + W) * (sY * 0.8) + 8.0

                    stitch_col = (245, 250, 255) if (j % 2 == 0) else (255, 220, 120)
                    fire((0.0, 0.0, 0.0), (vx1, vy1, vz1), T.nothing, stitch_col)
                    fire((0.0, 0.0, 0.0), (vx2, vy2, vz2), T.nothing, stitch_col)

                    if j % 10 == 0:
                        time.sleep(0.002)

            time.sleep(dt)

        time.sleep(0.20)

        # ---------------------------
        # Phase 2：丝带加冕（环形外扩 + 白金高光）
        # ---------------------------
        for i in range(p_crown):
            th = (2.0 * math.pi) * (i / (p_crown + 1))
            # 在莫比乌斯环附近取点，但 v 变小，像“外层光晕”
            u = th
            v = (rnd() * 2.0 - 1.0) * (W * 0.35)
            x, y, z = mobius_point(u, v)

            vx = x * 0.95 + (rnd() * 2.0 - 1.0) * 10.0
            vz = z * 0.95 + (rnd() * 2.0 - 1.0) * 14.0
            vy = base_up + (y + W) * (sY * 0.9) + 34.0

            # 白金为主，夹少量紫/青
            m = i % 9
            if m == 0:
                col = (255, 220, 120)
                ftype = T.planet_random_color
            elif m == 1:
                col = (255, 245, 230)
                ftype = T.circle
            elif m == 2:
                col = (190, 90, 255)
                ftype = T.nothing
            else:
                col = (90, 210, 255)
                ftype = T.nothing

            fire((0.0, 0.0, 0.0), (vx, vy, vz), ftype, col)

            if i % 22 == 0:
                time.sleep(0.006)

        time.sleep(0.25)



    def climax_mushroom_cloud(self, intensity=1.0):
        T = self.type_firework

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 颜色：核心火焰 / 灰烟 / 高光
        HOT1 = (255, 160, 80)     # 橙
        HOT2 = (255, 80, 60)      # 红
        HOT3 = (255, 220, 120)    # 金
        SMK1 = (70, 80, 95)       # 深灰蓝烟
        SMK2 = (110, 120, 140)    # 灰
        ASH  = (190, 200, 210)    # 灰白
        WHITE = (255, 245, 230)

        # ---------------------------
        # 固定时间节奏（不受 intensity 影响）
        # ---------------------------
        dt = 0.06

        # ---------------------------
        # intensity 只控制“数量”
        # ---------------------------
        ground_flash = int(18 * intensity)
        column_ticks = 28
        column_per_tick = int(20 * intensity)

        cap_burst = int(120 * intensity)
        roll_ticks = 20
        roll_per_tick = int(28 * intensity)

        ash_ticks = 22
        ash_per_tick = int(22 * intensity)

        # ==========================================================
        # Phase 0：地面闪燃（很短，告诉观众“爆点在这里”）
        # ==========================================================
        for i in range(ground_flash):
            th = 2.0 * math.pi * rnd()
            rad = 6.0 + 10.0 * rnd()
            x = math.cos(th) * rad * 0.45
            z = math.sin(th) * rad * 0.45

            vx = math.cos(th) * (18.0 + 18.0 * rnd())
            vz = math.sin(th) * (18.0 + 22.0 * rnd())
            vy = 26.0 + 10.0 * rnd()  # >0

            col = HOT3 if i % 5 == 0 else (HOT2 if i % 2 == 0 else HOT1)
            ftype = T.circle if i % 4 == 0 else T.nothing
            fire((x, 0.0, z), (vx, vy, vz), ftype, col)

            if i % 8 == 0:
                time.sleep(0.006)

        time.sleep(0.12)

        # ==========================================================
        # Phase 1：垂直火柱（蘑菇云“杆”）
        # 关键：vx/vz 很小，vy 很大，让方向非常明确
        # ==========================================================
        for k in range(column_ticks):
            t = k / (column_ticks - 1)

            for i in range(column_per_tick):
                # 柱体半径：下粗上稍细（但仍然是柱）
                r = (10.0 - 4.0 * t) * (0.25 + 0.75 * rnd())
                th = 2.0 * math.pi * rnd()

                px = math.cos(th) * r
                pz = math.sin(th) * r

                vx = (rnd() * 2.0 - 1.0) * 3.0
                vz = (rnd() * 2.0 - 1.0) * 4.5

                # vy 固定很高（不随 intensity），逐步增强到顶端
                vy = 54.0 + 36.0 * t + 8.0 * rnd()  # >0

                # 颜色：柱芯热，外缘烟
                if i % 7 == 0:
                    col = HOT3
                    ftype = T.circle
                elif i % 3 == 0:
                    col = HOT1
                    ftype = T.nothing
                else:
                    col = SMK1
                    ftype = T.nothing

                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 18 == 0:
                    time.sleep(0.0015)

            time.sleep(dt)

        time.sleep(0.10)

        # ==========================================================
        # Phase 2：顶部伞盖爆开（蘑菇“帽”）
        # 关键：vx/vz 强烈向外，vy 中等偏高，形成伞状扩张
        # ==========================================================
        for i in range(cap_burst):
            th = 2.0 * math.pi * (i / (cap_burst + 1))
            # 伞盖的“半径层”：中心少、边缘多（让帽子外轮廓更明显）
            layer = rnd() ** 0.45
            rad = 22.0 + 48.0 * layer

            # 伞盖初始位置稍微抬高（靠速度表达），这里 pos 仍用地面点
            px = (rnd() * 2.0 - 1.0) * 3.5
            pz = (rnd() * 2.0 - 1.0) * 4.0

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vz = math.sin(th) * (rad * 1.10) + (rnd() * 2.0 - 1.0) * 14.0
            vy = 46.0 + 12.0 * rnd()  # >0

            # 热核少量点睛，主体用烟/灰，让“蘑菇云”而不是烟花球
            if i % 17 == 0:
                col = HOT2
                ftype = T.planet_random_color
            elif i % 5 == 0:
                col = ASH
                ftype = T.circle
            else:
                col = SMK2
                ftype = T.nothing

            fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

            if i % 24 == 0:
                time.sleep(0.004)

        time.sleep(0.14)

        # ==========================================================
        # Phase 3：伞盖边缘翻滚环（“卷边”是蘑菇云灵魂）
        # 关键：做一个环带，速度切向 + 径向小扰动，形成翻滚感
        # ==========================================================
        ring_R = 70.0
        for k in range(roll_ticks):
            u = k / (roll_ticks - 1)

            # 卷边随时间“呼吸”，更像在滚动
            breathe = 0.80 + 0.55 * math.sin(u * math.pi)

            for i in range(roll_per_tick):
                th = 2.0 * math.pi * rnd()

                # 环带位置（仍用 pos 在地面附近，靠速度做形态）
                px = (rnd() * 2.0 - 1.0) * 3.0
                pz = (rnd() * 2.0 - 1.0) * 3.5

                # 环的切向方向
                tx = -math.sin(th)
                tz =  math.cos(th)

                # 径向方向
                rx = math.cos(th)
                rz = math.sin(th)

                # 切向主导：翻滚环绕；径向轻微内外摆动
                spin = 34.0 * breathe
                puff = 14.0 * math.sin(2.0 * th + 3.0 * u)

                vx = tx * spin + rx * puff + (rnd() * 2.0 - 1.0) * 6.0
                vz = tz * (spin * 1.05) + rz * puff + (rnd() * 2.0 - 1.0) * 8.0

                # vy 维持上抬，让环处在“帽子边缘高度感”
                vy = 40.0 + 10.0 * breathe + 6.0 * rnd()  # >0

                # 颜色以烟为主，偶尔给灰白高光强调卷边
                if i % 11 == 0:
                    col = ASH
                    ftype = T.circle
                else:
                    col = SMK1 if i % 3 else SMK2
                    ftype = T.nothing

                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 20 == 0:
                    time.sleep(0.0018)

            time.sleep(dt)

        time.sleep(0.12)

        # ==========================================================
        # Phase 4：灰烬烟尘持续上涌（收尾让蘑菇云“留在天上”）
        # ==========================================================
        for k in range(ash_ticks):
            for i in range(ash_per_tick):
                th = 2.0 * math.pi * rnd()
                rad = 18.0 + 34.0 * rnd()

                px = math.cos(th) * rad * 0.35
                pz = math.sin(th) * rad * 0.35

                vx = math.cos(th) * (10.0 + 12.0 * rnd()) + (rnd() * 2.0 - 1.0) * 6.0
                vz = math.sin(th) * (12.0 + 16.0 * rnd()) + (rnd() * 2.0 - 1.0) * 8.0
                vy = 26.0 + 10.0 * rnd()  # >0

                col = ASH if i % 4 == 0 else (SMK2 if i % 2 == 0 else SMK1)
                ftype = T.nothing if i % 6 else T.circle
                fire((px, 0.0, pz), (vx, vy, vz), ftype, col)

                if i % 18 == 0:
                    time.sleep(0.0016)

            time.sleep(0.05)

        time.sleep(0.25)


    def climax_prism_cathedral_overdrive(self, intensity=1.0):
        T = self.type_firework

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 颜色（棱镜+极光+白金高光）
        PEARL = (255, 245, 230)
        ICE   = (245, 250, 255)
        CYAN  = (90, 210, 255)
        BLUE  = (60, 120, 255)
        VIO   = (190, 90, 255)
        ROSE  = (255, 120, 200)
        GOLD  = (255, 220, 120)
        MINT  = (160, 255, 220)

        # intensity 只控制数量
        frame_density = int(180 * intensity) + 180      # 框架“常亮”点数
        curtain_per_tick = int(42 * intensity) + 40     # 极光帷幕每拍数量
        shell_count = int(260 * intensity) + 240        # 半球壳总粒子
        crown_count = int(220 * intensity) + 220        # 王冠收束粒子
        spark_count = int(26 * intensity) + 22          # 少量点睛闪点（避免糊）

        # 固定节奏（不随 intensity 变化）
        dt_frame = 0.055
        dt_curtain = 0.065
        dt_shell = 0.06

        # ==============================
        # Phase 1：3D 棱镜圣殿框架（关键：pos.y 直接“画”出结构）
        # ==============================
        # 做一个“高耸的棱镜盒体”：底面 y=0..8，顶部 y=56..64
        W = 90.0     # 横向尺度
        D = 60.0     # 纵深尺度
        y_bot = 2.0
        y_top = 62.0

        # 8 个角点（x,z）+ 两层 y
        corners = [
            (-W, -D), ( W, -D), ( W,  D), (-W,  D)
        ]

        # 框架边：底面、顶面、竖边
        edges = []
        # 底面环
        for i in range(4):
            a = corners[i]
            b = corners[(i + 1) % 4]
            edges.append((a, b, y_bot, y_bot))
        # 顶面环
        for i in range(4):
            a = corners[i]
            b = corners[(i + 1) % 4]
            edges.append((a, b, y_top, y_top))
        # 竖边
        for i in range(4):
            a = corners[i]
            edges.append((a, a, y_bot, y_top))

        # 再加两条“斜脊梁”（让它更像圣殿而不是普通盒子）
        edges.append((corners[0], corners[2], y_top, y_top))
        edges.append((corners[1], corners[3], y_top, y_top))

        # 框架“发射”策略：在边上采样点（pos），给近似竖直速度（vel） → 线条非常清晰
        samples_per_edge = 28
        strands = 2

        for pass_id in range(3):  # 刷新三次，保证“常亮感”
            for (a, b, ya, yb) in edges:
                x0, z0 = a
                x1, z1 = b

                for s in range(samples_per_edge):
                    u = s / (samples_per_edge - 1)
                    px = x0 + (x1 - x0) * u
                    pz = z0 + (z1 - z0) * u
                    py = ya + (yb - ya) * u

                    # 速度：几乎竖直，微抖动让它像能量线
                    for k in range(strands):
                        vx = (rnd() * 2.0 - 1.0) * 1.6
                        vz = (rnd() * 2.0 - 1.0) * 2.0
                        vy = 28.0 + 10.0 * rnd()  # >0

                        # 颜色：顶面更亮、底面偏冷，脊梁用白金
                        if abs(py - y_top) < 2.0:
                            col = PEARL if (s % 9 == 0) else ICE
                        elif abs(py - y_bot) < 2.0:
                            col = BLUE if (s % 7 == 0) else CYAN
                        else:
                            col = VIO if (pass_id % 2 == 0) else CYAN

                        # 脊梁高光
                        if (a == corners[0] and b == corners[2]) or (a == corners[1] and b == corners[3]):
                            col = GOLD if (s % 6 == 0) else PEARL

                        fire((px, py, pz), (vx, vy, vz), T.nothing, col)

                    if s % 9 == 0:
                        time.sleep(0.0015)

            # 角点锁定闪点（很少，但会让结构“立住”）
            for (cx, cz) in corners:
                fire((cx, y_bot, cz), (0.0, 46.0, 0.0), T.circle, CYAN)
                fire((cx, y_top, cz), (0.0, 56.0, 0.0), T.circle, PEARL)

            time.sleep(dt_frame)

        time.sleep(0.18)

        # ==============================
        # Phase 2：极光帷幕（在框架内部“垂挂”出 3D 光幕）
        # ==============================
        curtain_ticks = 26
        for k in range(curtain_ticks):
            t = k / (curtain_ticks - 1)

            # 帷幕从低到高逐渐“填满”
            y0 = 10.0 + 44.0 * t

            for i in range(curtain_per_tick):
                # 在框架内部随机取一条“帷幕线”位置
                px = (rnd() * 2.0 - 1.0) * (W * 0.75)
                pz = (rnd() * 2.0 - 1.0) * (D * 0.70)
                py = y0 + (rnd() * 2.0 - 1.0) * 6.0

                # 速度：向上为主 + 一点横向摆动（像帷幕抖动）
                vx = (rnd() * 2.0 - 1.0) * 6.0
                vz = (rnd() * 2.0 - 1.0) * 10.0
                vy = 34.0 + 18.0 * rnd()  # >0

                # 颜色随“帷幕相位”变化，产生极光渐变
                m = (i + k) % 6
                if m == 0:
                    col = CYAN
                elif m == 1:
                    col = MINT
                elif m == 2:
                    col = VIO
                elif m == 3:
                    col = ROSE
                elif m == 4:
                    col = ICE
                else:
                    col = BLUE

                fire((px, py, pz), (vx, vy, vz), T.nothing, col)

                # 少量“极光结点”闪一下（不要太多）
                if i % 19 == 0:
                    fire((px, py, pz), (vx * 0.25, vy + 20.0, vz * 0.25), T.circle, PEARL)

                if i % 22 == 0:
                    time.sleep(0.0018)

            time.sleep(dt_curtain)

        time.sleep(0.18)

        # ==============================
        # Phase 3：三层半球壳同爆（地面/中空/高空）——超级壮观的“体积高潮”
        # ==============================
        # 关键：从不同 y 的“发射源”同时做上半球扩张，观众会看到巨大 3D 体积
        sources = [
            (0.0, 0.0, 0.0),
            (0.0, 26.0, 0.0),
            (0.0, 52.0, 0.0),
        ]

        # 上半球采样：保证 vy>0（polar angle 0..pi/2）
        for s_idx, (sx, sy, sz) in enumerate(sources):
            # 每层给不同色相倾向
            layer_bias = s_idx % 3

            for i in range(shell_count // 3):
                th = 2.0 * math.pi * rnd()
                # 只取上半球：cos(phi) in [0,1]
                c = rnd()  # 0..1
                phi = math.acos(c)  # 0..pi/2

                # 半径强烈（让它“巨大”）
                rad = 46.0 + 70.0 * rnd()

                ux = math.cos(th) * math.sin(phi)
                uy = math.cos(phi)              # >=0
                uz = math.sin(th) * math.sin(phi)

                vx = ux * rad + (rnd() * 2.0 - 1.0) * 14.0
                vy = 44.0 + uy * 58.0 + 10.0 * rnd()  # >0 且很高
                vz = uz * (rad * 1.12) + (rnd() * 2.0 - 1.0) * 18.0

                # 颜色分层：底层更彩，中层更冷，高层更白金
                m = (i + s_idx) % 7
                if layer_bias == 0:
                    col = [CYAN, VIO, ROSE, BLUE, ICE, MINT, PEARL][m]
                elif layer_bias == 1:
                    col = [ICE, CYAN, BLUE, VIO, MINT, PEARL, GOLD][m]
                else:
                    col = [PEARL, GOLD, ICE, CYAN, VIO, PEARL, GOLD][m]

                # 点睛：少量爆炸类型，其余用 nothing 保证连续光轨体积
                if i % 17 == 0:
                    ftype = T.planet_random_color
                elif i % 29 == 0:
                    ftype = T.mixed_color_ball
                else:
                    ftype = T.nothing

                fire((sx, sy, sz), (vx, vy, vz), ftype, col)

                if i % 24 == 0:
                    time.sleep(0.0035)

            time.sleep(0.06)

        time.sleep(0.18)

        # ==============================
        # Phase 4：高空“王冠加冕”（在 y=72 左右爆出一圈巨型冠冕）
        # ==============================
        crown_y = 72.0
        for i in range(crown_count):
            th = 2.0 * math.pi * (i / (crown_count + 1))
            rad = 28.0 + 44.0 * rnd()

            px = math.cos(th) * 6.0
            pz = math.sin(th) * 6.0
            py = crown_y + (rnd() * 2.0 - 1.0) * 3.0

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vz = math.sin(th) * (rad * 1.18) + (rnd() * 2.0 - 1.0) * 14.0
            vy = 50.0 + 18.0 * rnd()  # >0

            # 白金为主，夹少量紫/青“棱镜折射”
            if i % 13 == 0:
                ftype = T.circle
                col = GOLD
            elif i % 7 == 0:
                ftype = T.planet_ball
                col = PEARL
            else:
                ftype = T.nothing
                col = VIO if (i % 3 == 0) else (CYAN if i % 3 == 1 else ICE)

            fire((px, py, pz), (vx, vy, vz), ftype, col)

            if i % 22 == 0:
                time.sleep(0.005)

        # 最后再补一圈“星火”让冠冕更炸裂但不糊
        for i in range(spark_count):
            th = 2.0 * math.pi * rnd()
            rad = 18.0 + 20.0 * rnd()
            px = (rnd() * 2.0 - 1.0) * 4.0
            pz = (rnd() * 2.0 - 1.0) * 4.0
            py = crown_y + (rnd() * 2.0 - 1.0) * 2.0

            vx = math.cos(th) * rad + (rnd() * 2.0 - 1.0) * 8.0
            vz = math.sin(th) * rad + (rnd() * 2.0 - 1.0) * 10.0
            vy = 62.0 + 12.0 * rnd()

            fire((px, py, pz), (vx, vy, vz), T.circle, PEARL)

            if i % 10 == 0:
                time.sleep(0.01)

        time.sleep(0.25)

    def climax_blackhole_lens_cathedral(self, intensity=1.0):
        T = self.type_firework

        def fire(pos, vel, ftype, color):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 色彩：深空/冰蓝/紫/白金
        VOID  = (10, 12, 28)
        DEEP  = (40, 80, 180)
        CYAN  = (90, 210, 255)
        VIO   = (190, 90, 255)
        ROSE  = (255, 120, 200)
        ICE   = (245, 250, 255)
        PEARL = (255, 245, 230)
        GOLD  = (255, 220, 120)
        MINT  = (160, 255, 220)

        jewel_pool = [T.circle, T.planet_ball, T.planet_random_color, T.mixed_color_ball, T.double_ball]

        # intensity 只控制数量
        ring_count = int(240 * intensity) + 220
        lens_ticks = 28
        lens_per_tick = int(70 * intensity) + 60
        shear_per_tick = int(34 * intensity) + 30
        jet_count = int(240 * intensity) + 220
        halo_count = int(200 * intensity) + 200

        # 固定节奏（不随 intensity）
        dt = 0.06
        dt2 = 0.05

        # 黑洞/透镜几何（固定）
        cx, cy, cz = 0.0, 46.0, 0.0        # 透镜中心在高空
        R0 = 62.0                           # 透镜主环半径
        R1 = 92.0                           # 透镜外壳范围
        throat = 14.0                       # “黑洞喉口”尺度（吸入感）

        # ==========================================================
        # Phase 1：高空“引力透镜主环”（pos.y 直接画出环）
        # ==========================================================
        for i in range(ring_count):
            th = 2.0 * math.pi * (i / (ring_count + 1))
            # 环在 y=cy 周围有一点厚度
            py = cy + (rnd() * 2.0 - 1.0) * 3.0
            # 环的位置在高空
            px = cx + math.cos(th) * R0
            pz = cz + math.sin(th) * R0

            # 速度：沿切向轻轻滑动 + 向上（让环“活”）
            tx = -math.sin(th)
            tz =  math.cos(th)
            vx = tx * (18.0 + 10.0 * rnd()) + (rnd() * 2.0 - 1.0) * 3.0
            vz = tz * (20.0 + 12.0 * rnd()) + (rnd() * 2.0 - 1.0) * 4.5
            vy = 22.0 + 8.0 * rnd()  # >0

            # 颜色：白金/冰蓝交替，偶尔紫辉
            if i % 11 == 0:
                col = GOLD
                ftype = T.circle
            elif i % 5 == 0:
                col = VIO
                ftype = T.nothing
            else:
                col = ICE if (i % 2 == 0) else CYAN
                ftype = T.nothing

            fire((px, py, pz), (vx, vy, vz), ftype, col)

            if i % 26 == 0:
                time.sleep(0.005)

        time.sleep(0.18)

        # ==========================================================
        # Phase 2：透镜弯折光束（从不同高度/不同方位射入，然后“掠过”中心变向）
        # 关键：pos 在空间分布，vel 带强烈“绕行中心”的切向分量
        # ==========================================================
        for k in range(lens_ticks):
            t = k / (lens_ticks - 1)

            # 透镜壳随时间更大：从 R0 -> R1
            shellR = R0 + (R1 - R0) * (0.25 + 0.75 * t)

            # 1) 主体光束：像被引力弯折，绕着中心掠过
            for i in range(lens_per_tick):
                # 采样一条入射方向
                th = 2.0 * math.pi * rnd()

                # 入射点：在壳上某处，y 有层次（真正 3D）
                py = (14.0 + 70.0 * rnd())
                px = math.cos(th) * shellR
                pz = math.sin(th) * shellR

                # 指向中心的径向
                rx = (cx - px)
                ry = (cy - py)
                rz = (cz - pz)
                rm = (rx*rx + ry*ry + rz*rz) ** 0.5 + 1e-6
                rx, ry, rz = rx/rm, ry/rm, rz/rm

                # 切向方向：在 XZ 平面绕行（引力透镜“弯折”感）
                tx = -math.sin(th)
                tz =  math.cos(th)

                # 速度：径向吸向中心 + 强切向绕行 + 向上保持
                vx = rx * 26.0 + tx * 46.0 + (rnd() * 2.0 - 1.0) * 10.0
                vz = rz * 30.0 + tz * 52.0 + (rnd() * 2.0 - 1.0) * 14.0
                vy = 26.0 + (0.5 + 0.5 * math.sin(th + 2.2 * t)) * 44.0 + 6.0 * rnd()  # >0

                # 颜色：冷到暖的“光谱折射”
                m = (i + k) % 7
                if m == 0:
                    col = CYAN
                elif m == 1:
                    col = MINT
                elif m == 2:
                    col = VIO
                elif m == 3:
                    col = ROSE
                elif m == 4:
                    col = ICE
                elif m == 5:
                    col = GOLD
                else:
                    col = DEEP

                # 少量 jewel 点睛
                if i % 23 == 0:
                    ftype = jewel_pool[(i + k) % len(jewel_pool)]
                else:
                    ftype = T.nothing

                fire((px, py, pz), (vx, vy, vz), ftype, col)

                if i % 30 == 0:
                    time.sleep(0.0018)

            # 2) “喉口剪切层”：更靠近中心的薄环流，增强黑洞吞噬感
            for i in range(shear_per_tick):
                th = 2.0 * math.pi * rnd()
                r = throat + 10.0 * rnd()

                px = cx + math.cos(th) * r
                pz = cz + math.sin(th) * r
                py = cy + (rnd() * 2.0 - 1.0) * 10.0

                tx = -math.sin(th)
                tz =  math.cos(th)

                vx = tx * (70.0 + 18.0 * rnd()) + (rnd() * 2.0 - 1.0) * 10.0
                vz = tz * (76.0 + 22.0 * rnd()) + (rnd() * 2.0 - 1.0) * 14.0
                vy = 22.0 + 14.0 * rnd()  # >0

                col = VOID if i % 5 else PEARL
                fire((px, py, pz), (vx, vy, vz), T.nothing, col)

                if i % 22 == 0:
                    time.sleep(0.0015)

            time.sleep(dt)

        time.sleep(0.18)

        # ==========================================================
        # Phase 3：白金喷流 Jet（从中心直上贯穿天空，极其震撼）
        # ==========================================================
        for i in range(jet_count):
            # 喷流从中心附近不同高度发射，形成“柱状穿透”
            px = cx + (rnd() * 2.0 - 1.0) * 3.0
            pz = cz + (rnd() * 2.0 - 1.0) * 3.5
            py = cy - 10.0 + (rnd() * 2.0 - 1.0) * 6.0

            # 速度几乎纯竖直 + 微扩散
            vx = (rnd() * 2.0 - 1.0) * 9.0
            vz = (rnd() * 2.0 - 1.0) * 12.0
            vy = 86.0 + 28.0 * rnd()  # >0 且很高

            # 颜色：白金为主，夹少量冷蓝电晕
            if i % 17 == 0:
                col = GOLD
                ftype = T.planet_random_color
            elif i % 7 == 0:
                col = PEARL
                ftype = T.circle
            else:
                col = ICE if (i % 2 == 0) else CYAN
                ftype = T.nothing

            fire((px, py, pz), (vx, vy, vz), ftype, col)

            if i % 26 == 0:
                time.sleep(0.004)

        time.sleep(0.12)

        # ==========================================================
        # Phase 4：彩色薄环 Halo（喷流周围出现多个彩环收束）
        # ==========================================================
        for i in range(halo_count):
            th = 2.0 * math.pi * (i / (halo_count + 1))
            # 多个环：y 分层
            py = cy + 8.0 + (i % 6) * 6.0 + (rnd() * 2.0 - 1.0) * 2.0
            rr = 26.0 + 34.0 * rnd()

            px = cx + math.cos(th) * rr
            pz = cz + math.sin(th) * rr

            # 速度：向外+向上，让环“绽放”
            vx = math.cos(th) * (22.0 + 20.0 * rnd()) + (rnd() * 2.0 - 1.0) * 8.0
            vz = math.sin(th) * (26.0 + 22.0 * rnd()) + (rnd() * 2.0 - 1.0) * 10.0
            vy = 52.0 + 16.0 * rnd()

            m = i % 6
            if m == 0:
                col = CYAN
            elif m == 1:
                col = MINT
            elif m == 2:
                col = VIO
            elif m == 3:
                col = ROSE
            elif m == 4:
                col = GOLD
            else:
                col = PEARL

            ftype = T.nothing if i % 11 else T.circle
            fire((px, py, pz), (vx, vy, vz), ftype, col)

            if i % 24 == 0:
                time.sleep(0.004)

        time.sleep(0.25)

    def climax_2min_continuous(self, intensity=1.0):
        T = self.type_firework
        NYE=generate_func_type(self.type_firework.happy_birthday,self.type_firework.new_year)
        This_year=generate_func_type(self.type_firework.happy_birthday,self.type_firework.this_year)

        # intensity 只控制数量；为避免 intensity<=0 导致数量为0，这里做最小保护
        
        intensity = 0.5

        def fire(pos, vel, ftype, color=(-1, -1, -1)):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # 伪随机（不依赖 random）
        seed = int(time.time() * 1000) & 0x7fffffff
        def rnd():
            nonlocal seed
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            return seed / 0x7fffffff

        # 色板（主舞台：白金 + 冰蓝 + 霓虹紫粉）
        PEARL = (255, 245, 230)
        GOLD  = (255, 220, 120)
        ICE   = (245, 250, 255)
        CYAN  = (90, 210, 255)
        BLUE  = (60, 120, 255)
        VIO   = (190, 90, 255)
        ROSE  = (255, 120, 200)
        MINT  = (160, 255, 220)
        DEEP  = (20, 26, 70)

        burst_pool = [
            T.circle,
            T.ball,
            T.double_ball,
            T.planet_ball,
            T.planet_random_color,
            T.half_half_color_ball,
            T.mixed_color_ball,
            T.random_color,
            T.ball_up
        ]

        # =========================
        # 2 分钟全程节奏（固定，不随 intensity 变）
        # =========================
        SHOW_SECONDS = 10.0
        tick = 0.24  # 每拍间隔；全程约 500 拍，连续但仍可控
        start = time.time()

        # intensity 只控制数量
        N_SIDE = int(10 * intensity) + 10          # 两侧底部“旁白”喷射数量/拍
        N_MID  = int(14 * intensity) + 14          # 中空结构数量/拍
        N_HIGH = int(10 * intensity) + 10          # 高空壳层数量/拍
        N_SPARK = int(4 * intensity) + 3           # 点睛闪点/拍（少量但关键）

        # 大事件数量（随 intensity 只加密度，不改速度/节奏）
        N_SHOCK = int(70 * intensity) + 70         # “震波壳”一次的粒子数
        N_CROWN = int(110 * intensity) + 110       # “王冠环”一次的粒子数
        N_JET   = int(90 * intensity) + 90         # “穿云喷流”一次的粒子数

        # 舞台尺度（固定）
        X = 110.0
        Z = 80.0

        # =========================
        # 子模块：底部两侧“节奏旁白”（不抢主戏，但保证一直高潮）
        # =========================
        def emit_side_barrage(phase, beat):
            # 左右两侧，规律每次都变一点（避免重复）
            for s in range(N_SIDE):
                side = -1.0 if (s % 2 == 0) else 1.0
                px = side * (70.0 + 18.0 * (rnd() * 2.0 - 1.0))
                py = 0.0 + 3.0 * rnd()
                pz = (rnd() * 2.0 - 1.0) * 22.0

                # 速度：强上抬 + 少量横向“扫”
                vx = side * (6.0 + 10.0 * rnd()) + (rnd() * 2.0 - 1.0) * 4.0
                vz = (rnd() * 2.0 - 1.0) * (18.0 + 10.0 * rnd())
                vy = 34.0 + 22.0 * rnd()  # >0

                # 颜色：随 phase 变换冷暖
                m = (beat + s) % 6
                if phase < 0.5:
                    col = [CYAN, BLUE, ICE, CYAN, MINT, PEARL][m]
                else:
                    col = [ROSE, VIO, PEARL, GOLD, CYAN, ICE][m]

                # 大多数用 nothing 形成光轨
                fire((px, py, pz), (vx, vy, vz), T.nothing, col)

                # 少量小闪点让两侧更“炫”
                if s % 9 == 0:
                    fire((px, py, pz), (vx * 0.25, vy + 18.0, vz * 0.25), T.circle, PEARL)

        # =========================
        # 子模块：中空“棱镜拱脉冲”（pos.y 参与构型，3D 结构强）
        # =========================
        def emit_mid_arches(phase, beat):
            y0 = 18.0 + 24.0 * (0.5 + 0.5 * math.sin(phase * math.pi * 2.0))
            for i in range(N_MID):
                # 从四个象限“拱起”到中心上方
                quad = i % 4
                px = ( -55.0 if quad in (0, 3) else 55.0 ) + (rnd() * 2.0 - 1.0) * 18.0
                pz = ( -45.0 if quad in (0, 1) else 45.0 ) + (rnd() * 2.0 - 1.0) * 16.0
                py = y0 + (rnd() * 2.0 - 1.0) * 6.0

                # 向中心吸 + 轻切向，形成“拱脉冲”
                vx = (-px) * 0.20 + (rnd() * 2.0 - 1.0) * 10.0
                vz = (-pz) * 0.20 + (rnd() * 2.0 - 1.0) * 14.0
                vy = 38.0 + 28.0 * rnd()

                # 颜色：中空更霓虹
                m = (i + beat) % 7
                col = [VIO, CYAN, ROSE, ICE, MINT, BLUE, PEARL][m]

                # 偶尔用 burst 类型点亮“拱门节点”
                if i % 11 == 0:
                    ftype = burst_pool[(i + beat) % len(burst_pool)]
                else:
                    ftype = T.nothing

                fire((px, py, pz), (vx, vy, vz), ftype, col)

        # =========================
        # 子模块：高空“天穹壳层”（真正“天空很大”的感觉）
        # =========================
        def emit_high_shell(phase, beat):
            cy = 62.0 + 18.0 * math.sin(phase * math.pi * 2.0 + 1.2)
            for i in range(N_HIGH):
                # 在高空环带上取发射点（pos.y 高）
                th = 2.0 * math.pi * rnd()
                rr = 36.0 + 54.0 * rnd()

                px = math.cos(th) * rr
                pz = math.sin(th) * rr
                py = cy + (rnd() * 2.0 - 1.0) * 6.0

                # outward + upward：壳层扩张
                vx = math.cos(th) * (28.0 + 26.0 * rnd()) + (rnd() * 2.0 - 1.0) * 10.0
                vz = math.sin(th) * (34.0 + 32.0 * rnd()) + (rnd() * 2.0 - 1.0) * 14.0
                vy = 44.0 + 22.0 * rnd()

                m = (beat + i) % 8
                col = [ICE, PEARL, CYAN, BLUE, VIO, ROSE, GOLD, MINT][m]

                if i % 8 == 0:
                    ftype = T.planet_random_color
                else:
                    ftype = T.nothing

                fire((px, py, pz), (vx, vy, vz), ftype, col)

            # 少量“星火点睛”
            for j in range(N_SPARK):
                th = 2.0 * math.pi * rnd()
                px = 0.0 + math.cos(th) * (8.0 + 8.0 * rnd())
                pz = 0.0 + math.sin(th) * (8.0 + 8.0 * rnd())
                py = cy + 8.0 + (rnd() * 2.0 - 1.0) * 3.0
                vx = math.cos(th) * (18.0 + 18.0 * rnd())
                vz = math.sin(th) * (22.0 + 20.0 * rnd())
                vy = 60.0 + 16.0 * rnd()
                fire((px, py, pz), (vx, vy, vz), T.circle, PEARL)

        # =========================
        # 大事件A：360° 震波壳（一次就很震撼）
        # =========================
        def shockwave_shell(center_y, warm=False):
            for i in range(N_SHOCK):
                th = 2.0 * math.pi * (i / (N_SHOCK + 1))
                # 上半球为主（更像天穹炸开）
                c = rnd()  # 0..1
                phi = math.acos(c)  # 0..pi/2
                rad = 58.0 + 88.0 * rnd()

                ux = math.cos(th) * math.sin(phi)
                uy = math.cos(phi)        # >=0
                uz = math.sin(th) * math.sin(phi)

                px = 0.0
                py = center_y + (rnd() * 2.0 - 1.0) * 3.0
                pz = 0.0

                vx = ux * rad + (rnd() * 2.0 - 1.0) * 14.0
                vz = uz * (rad * 1.15) + (rnd() * 2.0 - 1.0) * 18.0
                vy = 52.0 + uy * 62.0 + 10.0 * rnd()

                if warm:
                    col = GOLD if (i % 5 == 0) else (PEARL if i % 3 == 0 else ROSE)
                else:
                    col = ICE if (i % 4 == 0) else (CYAN if i % 3 == 0 else VIO)

                ftype = T.mixed_color_ball if (i % 17 == 0) else T.nothing
                fire((px, py, pz), (vx, vy, vz), ftype, col)

                if i % 26 == 0:
                    time.sleep(0.0035)

        # =========================
        # 大事件B：穿云喷流（从多高度一起喷）
        # =========================
        def triple_jet():
            jets = [(0.0, 0.0, 0.0), (0.0, 22.0, 0.0), (0.0, 44.0, 0.0)]
            for (px0, py0, pz0) in jets:
                for i in range(N_JET // 3):
                    px = px0 + (rnd() * 2.0 - 1.0) * 4.0
                    py = py0 + (rnd() * 2.0 - 1.0) * 3.0
                    pz = pz0 + (rnd() * 2.0 - 1.0) * 4.5

                    vx = (rnd() * 2.0 - 1.0) * 12.0
                    vz = (rnd() * 2.0 - 1.0) * 18.0
                    vy = 92.0 + 34.0 * rnd()

                    if i % 9 == 0:
                        col = GOLD
                        ftype = T.planet_random_color
                    elif i % 4 == 0:
                        col = PEARL
                        ftype = T.circle
                    else:
                        col = ICE if (i % 2 == 0) else CYAN
                        ftype = T.nothing

                    fire((px, py, pz), (vx, vy, vz), ftype, col)

                    if i % 22 == 0:
                        time.sleep(0.004)

        # =========================
        # 大事件C：高空王冠环（极强收束感）
        # =========================
        def crown_ring(yc):
            for i in range(N_CROWN):
                th = 2.0 * math.pi * (i / (N_CROWN + 1))
                rr = 34.0 + 60.0 * rnd()

                px = 0.0 + math.cos(th) * 8.0
                pz = 0.0 + math.sin(th) * 8.0
                py = yc + (rnd() * 2.0 - 1.0) * 3.0

                vx = math.cos(th) * rr + (rnd() * 2.0 - 1.0) * 10.0
                vz = math.sin(th) * (rr * 1.20) + (rnd() * 2.0 - 1.0) * 14.0
                vy = 56.0 + 18.0 * rnd()

                if i % 13 == 0:
                    ftype = T.circle
                    col = GOLD
                elif i % 7 == 0:
                    ftype = T.planet_ball
                    col = PEARL
                else:
                    ftype = T.nothing
                    col = VIO if (i % 3 == 0) else (CYAN if i % 3 == 1 else ICE)

                fire((px, py, pz), (vx, vy, vz), ftype, col)

                if i % 22 == 0:
                    time.sleep(0.005)

        # =========================
        # 中间插入文字：NYE + This_year（必须插在中段）
        # =========================
        def insert_text_block():
            # 给文字留“可读空间”：仍然高潮，但把中心周围改成框架/两侧护航
            # 1) 两侧护航光柱
            for j in range(int(50 * intensity) + 40):
                side = -1.0 if (j % 2 == 0) else 1.0
                px = side * 85.0 + (rnd() * 2.0 - 1.0) * 6.0
                py = 0.0 + 10.0 * rnd()
                pz = (rnd() * 2.0 - 1.0) * 18.0
                vx = (rnd() * 2.0 - 1.0) * 4.0
                vz = (rnd() * 2.0 - 1.0) * 6.0
                vy = 58.0 + 20.0 * rnd()
                fire((px, py, pz), (vx, vy, vz), T.nothing, ICE if j % 3 else CYAN)
                if j % 18 == 0:
                    time.sleep(0.004)

            # 2) 插入 NYE（按你指定格式）
            self.firework_generator.generate_firework_thread(
                (0.0, 0.0, 0.0),
                (0.0, 30.0, 0.0),
                NYE
            )

            # 3) 文字周围“金白拱光”托底（不遮字）
            for i in range(int(80 * intensity) + 70):
                th = 2.0 * math.pi * (i / (int(80 * intensity) + 71))
                px = math.cos(th) * 46.0
                pz = math.sin(th) * 22.0
                py = 8.0 + (rnd() * 2.0 - 1.0) * 2.0
                vx = math.cos(th) * (18.0 + 10.0 * rnd())
                vz = math.sin(th) * (14.0 + 10.0 * rnd())
                vy = 36.0 + 10.0 * rnd()
                fire((px, py, pz), (vx, vy, vz), T.nothing, GOLD if i % 5 == 0 else PEARL)
                if i % 20 == 0:
                    time.sleep(0.003)

            time.sleep(1.2)

            # 4) 插入 This_year（按你指定格式）
            self.firework_generator.generate_firework_thread(
                (0.0, 0.0, 0.0),
                (0.0, 30.0, 0.0),
                This_year
            )

            # 5) 立刻接一次高空王冠（把文字段变成“高潮中的高潮”）
            crown_ring(78.0)

        # =========================
        # 主循环：全程一直高潮（不同层并行 + 周期性大事件）
        # =========================
        text_done = False
        beat = 0

        while True:
            now = time.time()
            t = now - start
            if t >= SHOW_SECONDS:
                break

            phase = t / SHOW_SECONDS  # 0..1

            # 永远有：两侧旁白 + 中空拱脉冲 + 高空壳层（连续高潮的核心）
            emit_side_barrage(phase, beat)
            emit_mid_arches(phase, beat)
            emit_high_shell(phase, beat)

            # 周期性“大事件”，让每 6~10 秒必然出现“震撼级变化”
            #（节奏固定，不受 intensity 影响）
            if beat % 34 == 0:
                shockwave_shell(center_y=30.0, warm=False)
            if beat % 47 == 0:
                triple_jet()
            if beat % 55 == 0:
                crown_ring(74.0)

            # 中间插入 NYE + This_year：放在 55s~75s 的中段
            if (not text_done) and (t >= 60.0):
                insert_text_block()
                text_done = True

            # 末段更“疯狂”：最后 20 秒提高事件频率（但仍是固定速度/节奏）
            if t >= 100.0:
                if beat % 18 == 0:
                    shockwave_shell(center_y=36.0, warm=True)
                if beat % 21 == 0:
                    crown_ring(82.0)

            time.sleep(tick)
            beat += 1

        # 结束再补一个“最终超新星壳 + 金白喷流”做收口（依旧全是高潮）
        shockwave_shell(center_y=40.0, warm=True)
        triple_jet()
        crown_ring(86.0)
        time.sleep(0.25)

    def climax_2min_rose_eternal_romance(self, intensity=1.0, text_list=None, text_start=60.0, text_gap=20.0, cycle_text=True):
        T = self.type_firework

        # intensity 只影响数量；为了更省粒子，这里用 DENSITY 再整体压一档
        if intensity <= 0:
            intensity = 0.1


        # 如果你想强制更省（你之前写 intensity=0.1），可以打开下一行
        intensity = 0.2
        text_start=5
        text_gap=5
        cycle_text=False

        DENSITY = 0.12
        eff = intensity * DENSITY

        # NYE = generate_func_type(self.type_firework.happy_birthday, self.type_firework.new_year)
        # This_year = generate_func_type(self.type_firework.happy_birthday, self.type_firework.this_year)

        # 如果外部没传文字列表，就用默认两句
        
        text_list = [
            generate_func_type(self.type_firework.text_display, arr)
            for arr in self.type_firework.text_arrays
        ]+[self.type_firework.love_3D,self.type_firework.love_2D]

        # 玫瑰整体缩放（更小）
        SCALE = 0.70

        def fire(pos, vel, ftype, color=(-1, -1, -1)):
            self.firework_generator.generate_firework_thread(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                (float(vel[0]), float(vel[1]), float(vel[2])),
                ftype,
                color=color
            )

        # ========= 固定色彩（浪漫玫瑰） =========
        STEM_G = (70, 180, 90)
        LEAF_G = (60, 210, 120)
        PETAL1 = (255, 70, 120)    # 外瓣红
        PETAL2 = (255, 120, 190)   # 内瓣粉
        PEARL  = (255, 245, 230)
        GOLD   = (255, 220, 120)
        ROSE   = (255, 120, 200)
        VIO    = (190, 90, 255)

        # ========= 数量（已经很省） =========
        STEM_PTS   = int(8 * eff) + 10
        LEAF_PTS   = int(7 * eff) + 7
        PETAL_S    = int(7 * eff) + 4
        HEART_PTS  = int(12 * eff) + 6
        COMET_PTS  = int(5 * eff) + 3
        PULSE_COUNT = int(18 * eff) + 9

        # ========= 陪衬数量（逐段升级，但仍受 eff 约束） =========
        FIRE_FLY   = int(10 * eff) + 2   # 萤火点
        BRIDGE_PTS = int(12 * eff) + 2    # 星带拱
        SHOWER_PTS = int(14 * eff) + 3    # 金粉花雨
        FAN_PTS    = int(12 * eff) + 2      # 瓣形扇扫

        # ========= 时间参数（固定 2 分钟） =========
        SHOW_SECONDS = 120.0
        tick = 0.22
        start = time.time()
        beat = 0

        def rot_y(x, y, z, ang):
            c = math.cos(ang); s = math.sin(ang)
            return (c*x + s*z, y, -s*x + c*z)

        def rot_x(x, y, z, ang):
            c = math.cos(ang); s = math.sin(ang)
            return (x, c*y - s*z, s*y + c*z)

        def clamp_vy(v):
            if v <= 0.0:
                return 12.0
            return v

        # ========= 玫瑰参数（缩放后） =========
        base = (0.0, 0.0, 0.0)
        stem_h  = 40.0 * SCALE
        bloom_y = 48.0 * SCALE

        petals_outer = 6
        petals_inner = 5

        L_outer = 28.0 * SCALE
        W_outer = 14.0 * SCALE
        H_outer = 16.0 * SCALE

        L_inner = 18.0 * SCALE
        W_inner = 9.0  * SCALE
        H_inner = 12.0 * SCALE

        # ========= 摇摆（确定性） =========
        def rose_sway_angles(t):
            t *= 4.0
            a = 0.10 * math.sin(2.0 * math.pi * (t / 10.0))
            b = 0.08 * math.sin(2.0 * math.pi * (t / 13.0) + 1.1)
            return a, b

        # ========= 枝干 =========
        def draw_stem(t):
            ax, ay = rose_sway_angles(t)
            for i in range(STEM_PTS):
                u = i / (STEM_PTS - 1) if STEM_PTS > 1 else 0.5
                y = stem_h * u

                x = (2.8 * (u*u) - 1.0) * SCALE
                z = (1.4 * math.sin(u * math.pi)) * SCALE

                x, y2, z = rot_x(x, y, z, ax)
                x, y2, z = rot_y(x, y2, z, ay)

                vx = (2.4 + 0.8 * math.cos(u * math.pi)) * SCALE
                vz = (0.6 * math.sin(u * math.pi)) * SCALE
                vy = clamp_vy(10.0 + 10.0 * u)

                fire((base[0] + x, base[1] + y2, base[2] + z), (vx, vy, vz), T.nothing, STEM_G)

        # ========= 叶片 =========
        def draw_leaf(t, side=1.0, y0=22.0):
            ax, ay = rose_sway_angles(t)

            L = 18.0 * SCALE
            W = 10.0 * SCALE

            for i in range(LEAF_PTS):
                u = i / (LEAF_PTS - 1) if LEAF_PTS > 1 else 0.5

                x = side * (2.0 * SCALE + L * u)
                z = (4.0 * math.sin(u * math.pi) * side) * SCALE
                y = (y0 * SCALE) + (2.0 * math.sin(u * math.pi)) * SCALE

                w = W * math.sin(u * math.pi) * (0.85 - 0.25*u)

                for sgn in (-1.0, 1.0):
                    px, py, pz = x, y, z + sgn * w
                    px, py, pz = rot_x(px, py, pz, ax)
                    px, py, pz = rot_y(px, py, pz, ay)

                    vx = (side * (18.0 - 6.0*u) * SCALE)
                    vz = (sgn  * (12.0 - 5.0*u) * SCALE)
                    vy = clamp_vy(15.0 + 8.0*u)

                    fire((px, py, pz), (vx, vy, vz), T.nothing, LEAF_G)

                # 中脉线
                px, py, pz = x, y, z
                px, py, pz = rot_x(px, py, pz, ax)
                px, py, pz = rot_y(px, py, pz, ay)
                fire((px, py, pz), (side * (14.0 - 4.0*u) * SCALE, clamp_vy(32.0 + 6.0*u), 0.0), T.nothing, STEM_G)

        # ========= 花瓣层 =========
        def draw_petal_layer(t, n_petals, L, W, H, color_main, phase_offset):
            ax, ay = rose_sway_angles(t)
            cx, cy0, cz = 0.0, bloom_y, 0.0
            nod = 0.06 * math.sin(2.0 * math.pi * (t / 7.0) + 0.8)

            for p in range(n_petals):
                theta = (2.0 * math.pi) * (p / n_petals) + phase_offset
                dx = math.cos(theta)
                dz = math.sin(theta)
                px_perp = -dz
                pz_perp = dx

                for si in range(PETAL_S):
                    s = si / (PETAL_S - 1) if PETAL_S > 1 else 0.5

                    width_s = W * (math.sin(math.pi * s)) * (0.95 - 0.25*s)
                    lift = H * (s ** 1.35)

                    bx = cx + dx * (L * s)
                    bz = cz + dz * (L * s)
                    by = cy0 + lift

                    flip = (s ** 2.0) * (6.0 * SCALE + 4.0 * SCALE * math.sin(2.0 * math.pi * (t / 9.0)))
                    bx2 = bx + dx * flip
                    bz2 = bz + dz * flip

                    for sgn in (-1.0, 1.0):
                        px = bx2 + px_perp * (sgn * width_s)
                        py = by
                        pz = bz2 + pz_perp * (sgn * width_s)

                        px, py, pz = rot_x(px, py, pz, nod)
                        px, py, pz = rot_x(px, py, pz, ax)
                        px, py, pz = rot_y(px, py, pz, ay)

                        vx = (dx * (12.0 + 10.0 * s) +
                            px_perp * (sgn * (8.0 - 4.0*s)) * (0.6 + 0.4*math.sin(theta))) * SCALE
                        vz = (dz * (16.0 + 12.0 * s) +
                            pz_perp * (sgn * (10.0 - 5.0*s)) * (0.6 + 0.4*math.cos(theta))) * SCALE
                        vy = clamp_vy(18.0 + 18.0 * s)

                        col = PEARL if (si % 5 == 0 and s > 0.62) else color_main
                        fire((px, py, pz), (vx, vy, vz), T.nothing, col)

                    if si % 2 == 0:
                        px, py, pz = bx2, by, bz2
                        px, py, pz = rot_x(px, py, pz, nod)
                        px, py, pz = rot_x(px, py, pz, ax)
                        px, py, pz = rot_y(px, py, pz, ay)

                        vx = dx * (16.0 + 8.0 * s) * SCALE
                        vz = dz * (18.0 + 10.0 * s) * SCALE
                        vy = clamp_vy(16.0 + 16.0 * s)

                        col = GOLD if (si % 6 == 0 and s > 0.48) else color_main
                        fire((px, py, pz), (vx, vy, vz), T.nothing, col)

                tipx = cx + math.cos(theta) * (L * 1.02)
                tipz = cz + math.sin(theta) * (L * 1.02)
                tipy = cy0 + H * 1.05

                tipx, tipy, tipz = rot_x(tipx, tipy, tipz, nod)
                tipx, tipy, tipz = rot_x(tipx, tipy, tipz, ax)
                tipx, tipy, tipz = rot_y(tipx, tipy, tipz, ay)

                fire((tipx, tipy, tipz),
                    (math.cos(theta) * 10.0 * SCALE, clamp_vy(22.0), math.sin(theta) * 12.0 * SCALE),
                    T.circle, PEARL)

        # ========= 心形丝带 =========
        def draw_heart_ribbon(t):
            spin = 2.0 * math.pi * (t / 18.0)
            base_y = (26.0 + 6.0 * math.sin(2.0 * math.pi * (t / 9.0))) * SCALE

            for i in range(HEART_PTS):
                u = (2.0 * math.pi) * (i / HEART_PTS)

                x = 16.0 * (math.sin(u) ** 3)
                y = 13.0 * math.cos(u) - 5.0 * math.cos(2*u) - 2.0 * math.cos(3*u) - math.cos(4*u)

                px = x * SCALE
                py = base_y + y * 0.9 * SCALE
                pz = 0.0

                px, py, pz = rot_y(px, py, pz, spin)
                px *= (1.1 * SCALE)
                pz *= (1.1 * SCALE)

                dx = 48.0 * (math.sin(u) ** 2) * math.cos(u)
                dy = -13.0 * math.sin(u) + 10.0 * math.sin(2*u) + 6.0 * math.sin(3*u) + 4.0 * math.sin(4*u)

                vx = 0.18 * dx * SCALE
                vz = 0.22 * dx * SCALE
                vy = clamp_vy(32.0 + 0.12 * abs(dy))

                col = ROSE if (i % 3 != 0) else PEARL
                fire((px, py, pz), (vx, vy, vz), T.nothing, col)

                if i % (HEART_PTS // 6 if HEART_PTS >= 6 else 3) == 0:
                    fire((px, py, pz), (vx * 0.25, clamp_vy(vy + 18.0), vz * 0.25), T.circle, PEARL)

        # ========= 心跳脉冲 =========
        def heartbeat_glow(beat_idx):
            period = 36
            k = beat_idx % period
            if k != 0 and k != 5:
                return

            rr = (26.0 if k == 0 else 34.0) * SCALE
            y0 = 44.0 * SCALE
            count = PULSE_COUNT

            for i in range(count):
                th = 2.0 * math.pi * (i / count)
                px = math.cos(th) * 2.0
                pz = math.sin(th) * 2.0
                py = y0

                vx = math.cos(th) * rr
                vz = math.sin(th) * (rr * 0.75)
                vy = clamp_vy(44.0)

                col = GOLD if (i % 5 == 0) else PEARL
                ftype = T.planet_ball if i % 23 == 0 else T.nothing
                fire((px, py, pz), (vx, vy, vz), ftype, col)

        # ========= 双人彗星 =========
        def twin_comets(beat_idx):
            if beat_idx % 55 != 0:
                return

            y0 = 20.0 * SCALE
            X0 = 52.0 * SCALE
            for i in range(COMET_PTS):
                u = i / (COMET_PTS - 1) if COMET_PTS > 1 else 0.5
                z = (-18.0 + 36.0 * u) * SCALE
                py = y0 + 18.0 * u * SCALE

                vxL = 28.0 * SCALE
                vxR = -28.0 * SCALE
                vz  = -2.0 * (z * 0.08)
                vy  = clamp_vy(46.0 - 6.0 * u)

                fire((-X0, py, z), (vxL, vy, vz), T.nothing, ROSE)
                fire(( X0, py, z), (vxR, vy, vz), T.nothing, PEARL)

                if i % 8 == 0:
                    fire((-X0, py, z), (vxL * 0.25, clamp_vy(vy + 18.0), vz * 0.25), T.circle, GOLD)

        # ===================== 陪衬（越来越绚丽，确定性） =====================
        def stage_of_show(t):
            u = t / SHOW_SECONDS
            if u < 0.34:
                return 1
            if u < 0.67:
                return 2
            return 3

        # 1) 萤火环：永远围绕玫瑰，但随阶段更亮、更密
        def companion_fireflies(t, beat_idx, stage):
            # 环绕半径随阶段增大一点点，避免挤在一起
            R = (18.0 + 6.0 * stage) * SCALE
            Y = (34.0 + 4.0 * stage) * SCALE
            k = FIRE_FLY + 2 * stage

            # 角速度随阶段更快一点，更“绚丽”
            ang0 = 0.18 * beat_idx + 0.7 * stage

            for i in range(k):
                th = 2.0 * math.pi * (i / k) + ang0
                px = math.cos(th) * R
                pz = math.sin(th) * (R * 0.78)
                py = Y + (6.0 * SCALE) * math.sin(2.0 * th)

                # 斜向飘：沿切向 + 上升
                tx = -math.sin(th)
                tz =  math.cos(th)
                vx = tx * (10.0 * SCALE)
                vz = tz * (12.0 * SCALE)
                vy = clamp_vy(22.0 + 6.0 * stage)

                if stage == 1:
                    col = PEARL if (i % 3 != 0) else ROSE
                elif stage == 2:
                    col = ROSE if (i % 4 != 0) else VIO
                else:
                    col = GOLD if (i % 5 == 0) else PEARL

                fire((px, py, pz), (vx, vy, vz), T.circle, col)

        # 2) 星带拱桥：中段开始出现，末段更明显（像浪漫的“光拱”）
        def companion_star_bridges(t, beat_idx, stage):
            if stage < 2:
                return

            # 每隔固定拍触发一次（末段更频繁）
            period = 18 if stage == 2 else 12
            if beat_idx % period != 0:
                return

            # 两条拱：前后对称
            z_front = 18.0 * SCALE
            z_back  = -18.0 * SCALE

            # 拱宽度与高度随阶段增强
            R = (46.0 + 10.0 * stage) * SCALE
            H = (18.0 + 8.0 * stage) * SCALE
            n = BRIDGE_PTS + 2 * stage

            for i in range(n):
                u = i / (n - 1) if n > 1 else 0.5
                ang = math.pi * u

                x = math.cos(ang) * R
                y = (bloom_y + 6.0 * SCALE) + math.sin(ang) * H

                # 让拱桥慢慢“摆动”一下（确定性）
                sway = 0.14 * math.sin(2.0 * math.pi * (t / 9.0))
                x2, y2, z2 = rot_y(x, y, z_front, sway)

                # 速度：向外斜飞 + 上抬（形成拱的“流光”）
                vx = (8.0 + 10.0 * math.sin(ang)) * SCALE * (1.0 if x2 >= 0 else -1.0)
                vz = (10.0 * SCALE) * (1.0 if stage == 3 else 0.7)
                vy = clamp_vy(26.0 + 8.0 * stage)

                col = PEARL if (i % 3 != 0) else (ROSE if stage == 2 else GOLD)
                fire((x2, y2, z2), (vx, vy, vz), T.nothing, col)

                # 后拱镜像
                x3, y3, z3 = rot_y(x, y, z_back, -sway)
                vz2 = -vz
                fire((x3, y3, z3), (vx, vy, vz2), T.nothing, col)

                # 固定节奏点睛
                if i % 5 == 0 and stage == 3:
                    fire((x2, y2, z2), (0.0, clamp_vy(vy + 18.0), 0.0), T.circle, GOLD)

        # 3) 金粉花雨 + 瓣形扇扫：末段逐渐拉满（但粒子仍不大）
        def companion_golden_shower(t, beat_idx, stage):
            if stage < 3:
                return

            # 末段持续，但用节拍控制“越来越绚丽”
            # 前半末段：period=10；最后 25 秒：period=6
            if t < 95.0:
                period = 10
            else:
                period = 6

            if beat_idx % period != 0:
                return

            # 花雨：从上方落下式的斜向光轨（这里用上升速度模拟“撒满天空”的感觉）
            n = SHOWER_PTS
            top_y = (78.0 * SCALE)

            for i in range(n):
                u = i / (n - 1) if n > 1 else 0.5
                # 横向分布是规则网格（无随机）
                px = (-38.0 * SCALE) + (76.0 * SCALE) * u
                pz = (22.0 * SCALE) * math.sin(2.0 * math.pi * u)

                py = top_y + (6.0 * SCALE) * math.sin(2.0 * math.pi * (u + t / 7.0))

                # 速度：斜向扫落（但 vy 必须 >0，所以用“向上+横扫”制造花雨幕）
                vx = (12.0 * SCALE) * math.cos(2.0 * math.pi * u)
                vz = (16.0 * SCALE) * math.sin(2.0 * math.pi * u)
                vy = clamp_vy(28.0 + 6.0 * math.sin(2.0 * math.pi * u))

                col = GOLD if i % 4 == 0 else PEARL
                fire((px, py, pz), (vx, vy, vz), T.nothing, col)

            # 瓣形扇扫：在花朵周围做 6 扇“瓣光”扫出去（超级浪漫、很像花开）
            m = FAN_PTS
            fans = 6
            base_y = bloom_y + 8.0 * SCALE
            sweep = 0.28 * math.sin(2.0 * math.pi * (t / 6.0))

            for f in range(fans):
                theta0 = (2.0 * math.pi) * (f / fans) + sweep
                dx = math.cos(theta0)
                dz = math.sin(theta0)
                px_perp = -dz
                pz_perp = dx

                for i in range(m):
                    s = i / (m - 1) if m > 1 else 0.5
                    rr = (18.0 + 38.0 * s) * SCALE
                    ww = (10.0 * math.sin(math.pi * s)) * SCALE

                    px = dx * rr + px_perp * ww
                    pz = dz * rr + pz_perp * ww
                    py = base_y + (10.0 * (s ** 1.2)) * SCALE

                    vx = dx * (22.0 + 14.0 * s) * SCALE
                    vz = dz * (24.0 + 16.0 * s) * SCALE
                    vy = clamp_vy(26.0 + 16.0 * s)

                    col = ROSE if (i % 3 != 0) else PEARL
                    fire((px, py, pz), (vx, vy, vz), T.nothing, col)

                    if i % 6 == 0:
                        fire((px, py, pz), (vx * 0.25, clamp_vy(vy + 18.0), vz * 0.25), T.circle, GOLD)

        # ===================== 通用文字插入：队列式 =====================
        text_idx = 0
        next_text_time = float(text_start)

        def text_spotlight(t):
            # 文字出现时的“柔光托底”，不打断玫瑰
            # 两侧护航 + 一圈柔光环
            side_x = 58.0 * SCALE
            y0 = 6.0 * SCALE
            z_span = 22.0 * SCALE
            n = int(16 * eff) + 16

            for i in range(n):
                u = i / (n - 1) if n > 1 else 0.5
                z = (-z_span) + (2.0 * z_span) * u

                fire((-side_x, y0, z), (0.0, clamp_vy(46.0), 0.0), T.nothing, PEARL)
                fire(( side_x, y0, z), (0.0, clamp_vy(46.0), 0.0), T.nothing, PEARL)

            # 中心柔光环
            ring_n = int(18 * eff) + 18
            R = 36.0 * SCALE
            py = 18.0 * SCALE
            for i in range(ring_n):
                th = 2.0 * math.pi * (i / ring_n)
                px = math.cos(th) * 2.0
                pz = math.sin(th) * 2.0
                vx = math.cos(th) * (R * 0.65)
                vz = math.sin(th) * (R * 0.50)
                fire((px, py, pz), (vx, clamp_vy(34.0), vz), T.nothing, GOLD if i % 5 == 0 else PEARL)

        # ========================= 主循环：2 分钟 =========================
        while True:
            t = time.time() - start
            if t >= SHOW_SECONDS:
                break

            # 玫瑰永驻：每帧重绘
            draw_stem(t)
            draw_leaf(t, side=1.0,  y0=22.0)
            draw_leaf(t, side=-1.0, y0=28.0)

            draw_petal_layer(t, petals_outer, L_outer, W_outer, H_outer, PETAL1, phase_offset=0.0)
            draw_petal_layer(t, petals_inner, L_inner, W_inner, H_inner, PETAL2, phase_offset=math.pi / petals_inner)

            # 基础浪漫元素（持续但不吵）
            draw_heart_ribbon(t)
            heartbeat_glow(beat)
            twin_comets(beat)

            # 陪衬升级（越来越绚丽）
            st = stage_of_show(t)
            companion_fireflies(t, beat, st)
            companion_star_bridges(t, beat, st)
            companion_golden_shower(t, beat, st)

            # 通用文字队列插入（你可以给很长的 text_list，甚至循环）
            if text_list and t >= next_text_time:
                # 先托底聚光，再放字
                text_spotlight(t)

                ftype = text_list[text_idx]
                self.firework_generator.generate_firework_thread(
                    (0.0, 0.0, 0.0),
                    (0.0, 30.0, 0.0),
                    ftype
                )

                text_idx += 1
                if text_idx >= len(text_list):
                    if cycle_text:
                        text_idx = 0
                    else:
                        text_list = []  # 不再插入

                next_text_time += float(text_gap)

            time.sleep(tick)
            beat += 1

        # 收束：两次温柔心跳（浪漫结束）
        for _ in range(2):
            heartbeat_glow(0)
            time.sleep(0.16)

        
    def double_random(self):
        type_1=self.type_firework.choose_random_type()
        self.firework_generator.generate_firework_thread(self.firework_generator.get_random_position(),
                                                  self.firework_generator.get_random_velocity(),
                                                  type_1)
        time.sleep(0.1)
        type_2=self.type_firework.choose_random_type()
        self.firework_generator.generate_firework_thread(self.firework_generator.get_random_position(),
                                                  self.firework_generator.get_random_velocity(),
                                                  type_2)

    def double_one_range(self):
        type_1=self.type_firework.choose_random_type()
        self.firework_generator.generate_firework_thread((-17,-5,0),
                                                  (0,20,0),
                                                  type_1)
        self.firework_generator.generate_firework_thread((17,-5,0),
                                                  (0,20,0),
                                                  type_1)
        time.sleep(0.1)
        type_2=self.type_firework.choose_random_type()
        self.firework_generator.generate_firework_thread((0,-5,0),
                                                  (0,30,0),
                                                  type_2)

    def single(self):
        type_1=self.type_firework.choose_random_type()
        self.firework_generator.generate_firework_thread(self.firework_generator.get_random_position(),
                                                  self.firework_generator.get_random_velocity(),
                                                  type_1)
        
    def fan(self):
        
        vel_left=np.array([
            [25],
            [25],
            [0]
        ])

        vel_right=np.array([
            [-25],
            [25],
            [0]
        ])
        for first in range(10):
            type_1=self.type_firework.choose_random_type()
            
            vel_left=Rz(90/10)*vel_left
            self.firework_generator.generate_firework_thread((-10,0,0),(vel_left[0,0],vel_left[1,0],vel_left[2,0]),type_1)

            vel_right=Rz(-90/10)*vel_right
            self.firework_generator.generate_firework_thread((10,0,0),(vel_right[0,0],vel_right[1,0],vel_right[2,0]),type_1)


            time.sleep(0.3)

        
        for second in range(10):
            type_2=self.type_firework.choose_random_type()
            
            vel_left=Rz(-90/10)*vel_left
            self.firework_generator.generate_firework_thread((-10,0,0),(vel_left[0,0],vel_left[1,0],vel_left[2,0]),type_2)

            vel_right=Rz(90/10)*vel_right
            self.firework_generator.generate_firework_thread((10,0,0),(vel_right[0,0],vel_right[1,0],vel_right[2,0]),type_2)


            time.sleep(0.3)


    def happy_birthday(self):
        h_b=generate_func_type(self.type_firework.happy_birthday,self.type_firework.h_b)
        kaka=generate_func_type(self.type_firework.happy_birthday,self.type_firework.kaka)
        age=generate_func_type(self.type_firework.happy_birthday,self.type_firework.age)
        love=self.type_firework.double_love_2D

        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),h_b)
        time.sleep(1)

        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),kaka)
        time.sleep(1)

        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),age)
        time.sleep(1)

        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),love)
        time.sleep(1)

    def extrimely_big_fire_1(self):

        self.firework_generator.generate_firework_thread((0,0,0),(0,50,0),self.type_firework.extrimely_big_fire_1)
        time.sleep(5.5)
        music=self.firework_generator.getMusic(self.firework_generator.crackle_sounds)
        music.set_volume(0.5)
        music.play()
        time.sleep(5)

    def extrimely_big_fire_2(self):

        self.firework_generator.generate_firework_thread((0,0,0),(0,70,0),self.type_firework.extrimely_big_fire_2)
        time.sleep(5)
        music=self.firework_generator.getMusic(self.firework_generator.crackle_sounds)
        music.set_volume(0.8)
        music.play()
        time.sleep(0.4)
        music.play()
        time.sleep(5)

    def extrimely_big_fire_3(self):
        """超级壮观的8尺玉烟花"""
        self.firework_generator.generate_firework_thread((0,0,0),(0,60,0),self.type_firework.extrimely_big_fire_3)
        time.sleep(6)
        # 多次播放爆裂声模拟连续爆炸
        music=self.firework_generator.getMusic(self.firework_generator.crackle_sounds)
        music.set_volume(1.0)
        music.play()
        time.sleep(0.3)
        music.play()
        time.sleep(0.3)
        music.play()
        time.sleep(6)

    def extrimely_big_fire_4(self):
        """「千重菊」- 优雅的日式冠菊烟花"""
        self.firework_generator.generate_firework_thread((0,0,0),(0,55,0),self.type_firework.extrimely_big_fire_4)
        time.sleep(6.5)
        # 单次深沉的爆裂声，配合优雅的视觉效果
        music=self.firework_generator.getMusic(self.firework_generator.crackle_sounds)
        music.set_volume(0.7)
        music.play()
        time.sleep(7)

    def nothing_queue(self,color):
        vel_left=np.array([
                [20],
                [20],
                [0]
            ])
        interval=2
        for i in range(10):
                vel_left=Rz(90/10)*vel_left
                
                self.firework_generator.generate_firework_thread((5*interval-interval*i,0,0),(vel_left[0,0],vel_left[1,0],vel_left[2,0]),self.type_firework.nothing,color)
        vel_left_2=np.array([
                [15],
                [15],
                [15]
            ])
        for ii in range(10):
            vel_left_2=Rz(90/10)*vel_left_2
            
            self.firework_generator.generate_firework_thread((5*interval-interval*ii,0,0),(vel_left_2[0,0],vel_left_2[1,0],vel_left_2[2,0]),self.type_firework.nothing,color)

    def ball_queue(self,color):
        interval=2
        for i in range(30):
            
            
            self.firework_generator.generate_firework_thread((random.randint(12,18)*interval-interval*i,0,0),(0,random.randint(28,32),0),self.type_firework.ball,color)

    def interval_firework(self):
        for i in range(10):
            self.firework_generator.generate_firework_thread((random.randint(-10,10),0,0),(0,random.randint(15,20),0),self.type_firework.ball_up,(245,194,84))

    def upper_firework(self,color,type):
        for i in range(10):
            self.firework_generator.generate_firework_thread((random.randint(-20,20),0,0),(0,random.randint(25,33),0),type,color)

    def lower_firework_1(self):
        for i in range(250):
            self.firework_generator.generate_firework_thread((random.randint(-5,5),0,0),(0,random.randint(5,10),0),self.type_firework.random_color,(255,255,255))
            time.sleep(0.05)

    def lower_firework_2(self,color,displacement=0):
        vel_left=np.array([
                [10],
                [10],
                [0]
            ])
        interval=2
        for i in range(10):
                vel_left=Rz(90/10)*vel_left
                
                self.firework_generator.generate_firework_thread(((5*interval-interval*i)+displacement,0,0),(vel_left[0,0],vel_left[1,0],vel_left[2,0]),self.type_firework.nothing,color)

    def large_range(self,type,color):
        for i in range(10):
            self.firework_generator.generate_firework_thread((random.randint(-10,10),0,0),(0,random.randint(15,33),0),type,color)

    def firework_final_1(self,type):
        color=COLOR[random.randint(0,len(COLOR)-1)]
        for total in range(10):
            for each in range(3):
                self.firework_generator.generate_firework_thread((random.randint(-30,30),0,0),(0,random.randint(28,32),0),type,color)
                time.sleep(0.05)
    def firework_final_2(self):
        for i in range(300):
            color=COLOR[random.randint(0,len(COLOR)-1)]
            self.lower_firework_2(color,random.randint(-5,5))
            time.sleep(0.05)
    def firework_final_3(self):
        for total in range(80):
            for each in range(2):
                color=COLOR[random.randint(0,len(COLOR)-1)]
                self.firework_generator.generate_firework_thread((random.randint(-30,30),0,0),(0,random.randint(18,22),0),self.type_firework.ball_up,color)
                time.sleep(0.05)
    

        
    def starter(self):
        self.nothing_queue((255,255,255))
        self.ball_queue((255,0,255))

        time.sleep(5)

        self.nothing_queue((245,194,84))
        self.ball_queue((205,45,65))

        time.sleep(5)

        self.nothing_queue((255,255,255))
        self.ball_queue((60,122,240))

        time.sleep(5)

        self.nothing_queue((245,194,84))
        self.ball_queue((217,217,217))

        time.sleep(5)

        self.nothing_queue((255,255,255))
        self.ball_queue((171,37,200))

    def main_fire_1(self):
        thread=threading.Thread(target=self.lower_firework_1,args=())
        thread.start()

        main_list=[self.type_firework.planet_ball,self.type_firework.mixed_color_ball,self.type_firework.double_ball,self.type_firework.flower]
        for typ in main_list:
            self.upper_firework(COLOR[random.randint(0,len(COLOR)-1)],typ)
            time.sleep(0.5)
            self.interval_firework()
            time.sleep(4)

    def main_fire_2(self):
        main_list=[self.type_firework.planet_ball,self.type_firework.mixed_color_ball,self.type_firework.double_ball]

        for i in main_list:
            color=COLOR[random.randint(0,len(COLOR)-1)]
            self.large_range(i,color)
            
            self.lower_firework_2(color,1)
            time.sleep(0.3)
            self.lower_firework_2(color,-1)
            time.sleep(0.3)
            self.lower_firework_2(color,1)
            time.sleep(0.3)
            self.lower_firework_2(color,-1)
            time.sleep(3)

    def final_word(self):
        #time.sleep(3)
        kaka=generate_func_type(self.type_firework.happy_birthday,self.type_firework.kaka)
        NYE=generate_func_type(self.type_firework.happy_birthday,self.type_firework.new_year)
        LU=generate_func_type(self.type_firework.happy_birthday,self.type_firework.love_you)
        forever=generate_func_type(self.type_firework.happy_birthday,self.type_firework.forever)
        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),kaka)
        time.sleep(1)
        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),NYE)
        time.sleep(1)
        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),LU)
        time.sleep(1)
        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),forever)
        time.sleep(1)

    def birth_day_word(self):
        #time.sleep(3)
        aray=generate_func_type(self.type_firework.happy_birthday,self.type_firework.aray)
        h_b=generate_func_type(self.type_firework.happy_birthday,self.type_firework.h_b)
        
        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),aray)
        time.sleep(1)
        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),h_b)
        time.sleep(1)

        

    def final_fire(self):
        thread=threading.Thread(target=self.final_word,args=())
        thread.start()
        thread=threading.Thread(target=self.firework_final_2,args=())
        thread.start()
        thread=threading.Thread(target=self.firework_final_3,args=())
        thread.start()
        main_list=[self.type_firework.planet_random_color,self.type_firework.half_half_color_ball,self.type_firework.double_ball,self.type_firework.love_2D_odd]
        for i in main_list:
            self.firework_final_1(i)
            self.firework_final_1(i)

    def happy_new_year(self):


        
        self.starter()
        self.main_fire_2()

        for i in range(2):
            self.main_fire_1()
        
        self.final_fire()
        time.sleep(2)

        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),self.type_firework.extrimely_big_fire_1)
        time.sleep(4.5)
        music=self.firework_generator.getMusic(self.firework_generator.crackle_sounds)
        music.set_volume(0.5)
        music.play()
        time.sleep(3)

        self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),self.type_firework.extrimely_big_fire_2)
        time.sleep(3.5)
        music=self.firework_generator.getMusic(self.firework_generator.crackle_sounds)
        music.set_volume(0.8)
        music.play()
        time.sleep(0.4)
        music.play()


    def starter_v2(self):
        self.circle_around()
        self.line_around()
        self.fan_2()
        time.sleep(1)

        for i in range(2):
            self.one_wave_show()
            time.sleep(1)

            self.one_wave_vortex()
            time.sleep(1)

            self.one_wave_breathing_petal()
            time.sleep(1)


            self.one_wave_pendulum_clash()
            time.sleep(1)

            self.one_wave_shockwave_climax()
            time.sleep(1)

            self.one_wave_sky_net_overload()
            time.sleep(1)

            
            


    def main_fire_2_v2(self):
        transition=[
            self.transition_origami_fold,
            self.transition_shutter_flip,
            self.transition_teleport_afterimage,
            self.transition_sky_calligraphy,
            self.transition_cushion,
        ]
        

        main_list=[
            self.one_wave_helical_sphere_rupture,
            self.one_wave_spatial_fault_collapse,
            self.one_wave_volumetric_phase_explosion,
            
            self.one_wave_aurora_blossom_dome,
            self.one_wave_infinity_ribbon_lanterns,
            self.one_wave_aurora_cathedral,
            self.one_wave_tesseract_flip,
            self.one_wave_hypernova_storm,
            self.one_wave_blooming_canopy,
            self.one_wave_pulse_bouquet,
            self.one_wave_prismatic_gate,
            self.one_wave_nebula_lattice_overdrive,
        ]

        for i in range(1):
            random.shuffle(main_list)
            for j in main_list:
                j()
                time.sleep(2)

                random.choice(transition)()
                time.sleep(1)

        
    def final_fire_v2(self):
        transition=[
            self.transition_origami_fold,
            self.transition_shutter_flip,
            self.transition_teleport_afterimage,
            self.transition_sky_calligraphy,
            self.transition_cushion,
        ]
        main_list=[
            self.one_wave_aurora_braid_marathon,
            self.one_wave_meteor_cathedral_rain,
            
            
            
            self.one_wave_living_nebula_collapse,
            self.one_wave_skyfall_constellation_ruin,
            self.one_wave_temporal_shockwave_cascade,
            self.one_wave_nebula_lattice_overdrive,
            self.one_wave_quantum_crown_overdrive,
        ]
        for i in range(1):
            random.shuffle(main_list)
            for i in main_list:
                i()
                time.sleep(5)

                random.choice(transition)()
                time.sleep(1)


    def special_firework(self):
        fire_list=[
            self.climax_hypernova_symphony,
            self.climax_tree_shape,
            self.climax_van_gogh_starry_night,
            self.climax_aurora_gate_10,
            self.climax_bloom_superfield_low_flower_love,
            self.climax_rainbow_waterfall,
            self.climax_kaleidoscope_rift,
            self.climax_phoenix_rise,
            self.climax_rose_window,
            self.climax_confetti_hurricane,
            self.climax_fountain_throne,
            self.climax_cloud_sea_gate,
            self.climax_prism_burst_corridor,
            self.climax_hyper_torus_bloom,
            self.climax_milkyway_bridgefall,
            self.climax_day_night_flip,
            self.climax_stargate_array_overload,
            self.climax_rift_canyon_panorama,
            self.climax_aurora_cathedral,
            self.climax_romantic_binary_constellation,
            self.climax_romantic_moonlit_vows,
            self.climax_dream_bubble_nebula,
            self.climax_whirlwind_tornado,
            self.climax_rotating_world_tree,
            self.climax_christmas_tree_persistent,
            self.climax_pillar_forest_uplift,
            self.climax_hypercube_lattice_collapse,
            self.climax_dna_helix_ascension,
            self.climax_lissajous_knot_sculpture,
            self.climax_mobius_loom,
            self.climax_mushroom_cloud,
            self.climax_prism_cathedral_overdrive,
            self.climax_blackhole_lens_cathedral,
            self.climax_2min_continuous

        ]

        for i in range(1):
            random.shuffle(fire_list)
            for i in fire_list:
                i()
                time.sleep(7)

                
    def finiah_fire_v2(self):
        self.climax_2min_rose_eternal_romance()

        self.one_wave_big8_thick_build()

        self.one_wave_searchlight_lightning_big2()
        

    def happ_new_year_v2(self):
        #self.climax_2min_rose_eternal_romance()
        
        
        self.starter_v2()
        self.start_narration_fireworks()
        
        self.main_fire_2_v2()
        
        self.final_fire_v2()
        self.special_firework()
        self.stop_narration_fireworks()
        self.finiah_fire_v2()

        

        # for i in range(2):
        #     self.main_fire_1_v2()
        
        # self.final_fire_v2()
        # time.sleep(2)

        # self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),self.type_firework.extrimely_big_fire_1)
        # time.sleep(4.5)
        # music=self.firework_generator.getMusic(self.firework_generator.crackle_sounds)
        # music.set_volume(0.5)
        # music.play()
        # time.sleep(3)

        # self.firework_generator.generate_firework_thread((0,0,0),(0,30,0),self.type_firework.extrimely_big_fire_2)
        # time.sleep(3.5)
        # music=self.firework_generator.getMusic(self.firework_generator.crackle_sounds)
        # music.set_volume(0.8)
        # music.play()
        # time.sleep(0.4)
        # music.play()
        
