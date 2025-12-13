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
            self.extrimely_big_fire_2
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
            self.type_firework.extrimely_big_fire_1
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
            self.type_firework.extrimely_big_fire_2
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

        for i in range(2):
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
        for i in range(2):
            random.shuffle(main_list)
            for i in main_list:
                i()
                time.sleep(5)

                random.choice(transition)()
                time.sleep(1)

    def finiah_fire_v2(self):
        self.climax_30s_continuous()

        self.climax_60s_with_nye_text()

        self.one_wave_big8_thick_build()

        self.one_wave_searchlight_lightning_big2()
        

    def happ_new_year_v2(self):
        #self.one_wave_show()
        
        self.starter_v2()
        self.start_narration_fireworks()
        
        self.main_fire_2_v2()
        
        self.final_fire_v2()
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
        
