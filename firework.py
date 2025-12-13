import pygame
import numpy as np
import random
import threading
from numba import njit

from rotate import *
from functions import *
from obj import *


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

    def create_new(self):
        
        check=False
        for i in range(self.counter_index,self.counter_index+self.num_each):
            if self.boolean[self.counter_index]:
                check=True
        
        if check:
            self.counter_index+=self.num_each
            self.check_limit()
            return self.create_new()
        else:
            result=range(self.counter_index,self.counter_index+self.num_each)
            for i in result:
                self.boolean[i]=True
            self.counter_index+=self.num_each
            self.check_limit()
            return result


    def remove(self,index):
        self.boolean[index]=False

    def get_data(self,start=0,end=0):
        if end==0:
            return self.arr[self.boolean]
        else:
            return self.arr[self.boolean][:,start:end]
        

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
        

        
        #self.firework_ready=[]
    def start_auto_fire(self):
        self.auto=Auto_fire(self.auto_para[1],self,self.auto_para[2])
        if self.auto_para[0]:
            
            
            self.auto.start_auto_fire()
            self.auto_para[0]=False

    def start_auto_fire_new_year_eve(self):
          
        self.auto=Auto_fire(self.auto_para[1],self,self.auto_para[2])
        self.auto.start_auto_fire_new_year_eve()
        

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

    
    def update(self):
        self.check_thread()# used in threading
        self.change_position_particle()# upate the state of particle
        
        self.change_position_effect()# upate the state of effect


    def change_position_effect(self):#position,color,velocity,live,live_change
        improved_change_position_effect(self.effect_position_np.arr,self.effect_position_np.boolean)
        

    def change_position_particle(self):#changed_position(3),color(3),velocity(3),angle,angle_change,live,live_change,size,size_change,org_position(3),change_tri,horizontal,vertical,time_counter,tail
        effects=improved_change_position_particle(self.particle_posiiton_np.arr,self.particle_posiiton_np.boolean)
        for i in range(effects.shape[0]//6):
            index=i*6
            self.effects.append(Tail_Effect(effects[index,15:18].reshape(3,1)+np.random.rand(3, 1)*0.1,effects[index,3:6],self.effect_position_np))
        
      

        


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
@njit
def improved_change_position_effect(arr,arr_bool):
    orgData=arr[arr_bool]
    if orgData.size:
        time_inter=TIME_INTERVAL
        G=9.81
        M=0.1
        K_f=2
        force_g=-G*M
        force_friction=-orgData[:,6:9]*0.5*K_f
        force_friction[:,1]+=force_g
        acc=force_friction/M
        orgData[:,6:9]+=acc*time_inter
        orgData[:,0:3]+=orgData[:,6:9]*time_inter
        orgData[:,9]-=orgData[:,10]
        arr[arr_bool]=orgData
        arr_bool[arr[:,9]<0]=False

@njit
def improved_change_position_particle(arr,arr_bool):
    orgData=arr[arr_bool]
    if orgData.size:
        time_inter=TIME_INTERVAL
        G=9.81
        M=1
        K_f=0.7
        force_g=-G*M
        force_friction=-orgData[:,6:9]*0.5*K_f
        force_friction[:,1]+=force_g
        acc=force_friction/M
        orgData[:,6:9]+=acc*time_inter
        orgData[:,15:18]+=orgData[:,6:9]*time_inter
        orgData[:,9]+=orgData[:,10]
        orgData[:,11]-=orgData[:,12]
        orgData[:,13]-=orgData[:,14]

        orgData[:,0]=orgData[:,13]*np.cos(orgData[:,18]+orgData[:,9])+orgData[:,15]#15,16,17
        orgData[:,1]=(orgData[:,13]*np.sin(orgData[:,18]+orgData[:,9])*orgData[:,19])+orgData[:,16]
        orgData[:,2]=(orgData[:,13]*np.sin(orgData[:,18]+orgData[:,9])*orgData[:,20])+orgData[:,17]

        orgData[:,21]+=orgData[:,22]


        #print(orgData[:,:3])
        
        arr[arr_bool]=orgData

        # arr_bool[arr[:,11]<0]=False
        # arr_bool[arr[:,13]<0]=False
    
    return arr[arr_bool][arr[arr_bool][:,21]%(40//(TIME_INTERVAL/0.001))==1]






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
        self.age=pygame.surfarray.array2d(
            self.font.render(str(age), True, (255, 255, 255),(0,0,0))
            ).T
        
        self.h_b=pygame.surfarray.array2d(
            self.font.render("Happy Birthday", True, (255, 255, 255),(0,0,0))
            ).T
        self.new_year=pygame.surfarray.array2d(
            self.font.render("Happy New Year!", True, (255, 255, 255),(0,0,0))
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
            self.extrimely_big_fire_1,
            self.extrimely_big_fire_2
            
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
        thread=threading.Thread(target=self.happy_new_year,args=())
        thread.start()

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
        
