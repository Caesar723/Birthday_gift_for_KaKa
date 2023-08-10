import numpy as np




def angleConvert(angle):

    return np.pi*2*angle/360

def change_Size(size):
    return np.matrix([
        [size,0,0],
        [0,size,0],
        [0,0,size]
    ])

def Rz(angle):

    angle=angleConvert(angle)
    result=np.matrix([
        [np.cos(angle),-np.sin(angle),0],
        [np.sin(angle),np.cos(angle),0],
        [0,0,1]
    ])

    return result

def Ry(angle):

    angle=angleConvert(angle)
    result=np.matrix([
        [np.cos(angle),0,-np.sin(angle)],
        [0,1,0],
        [np.sin(angle),0,np.cos(angle)]
    ])

    return result

def Rx(angle):

    angle=angleConvert(angle)
    result=np.matrix([
        [1,0,0],
        [0,np.cos(angle),-np.sin(angle)],
        [0,np.sin(angle),np.cos(angle)]
    ])

    return result

def Rotate(x,y,z):
    return Ry(y)*Rx(x)*Rz(z)
