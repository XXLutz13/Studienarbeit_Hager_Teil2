import pybcapclient.bcapclient as bcapclient    # Denso library for Cobotta access
import numpy as np

def coordinates(num_images, center):
    R = 80
    spacing = num_images//8

    # phi = np.linspace(0, 0.5 * np.pi, spacing)
    phi = np.linspace(0.85*np.pi, 0.5*np.pi, spacing)
    X = [center[0]]*spacing
    Y = center[1] - R * np.cos(phi)
    Z = center[2] + R * np.sin(phi)
    rx = np.linspace(1.15*90, 180, spacing)
    ry = [0]*spacing
    rz = [0]*spacing
    num_steps = [50]*8
    # type conversions
    rx = rx.tolist()
    Y = Y.tolist()
    Z = Z.tolist()

    # print(type(Y[0]))

    cords = list(zip(X, Y, Z, rx, ry, rz))
    # Round every element in the list of tuples using list comprehension and round()
    cords = [(round(a, 4), round(b, 4), round(c, 4), round(d, 4), round(e, 4), round(f, 4)) for a,b,c,d,e,f in cords]
    
    return cords, num_steps


# set IP Address , Port number and Timeout of connected RC8
host = '192.168.0.1'
port = 5007
timeout = 2000

#---------------------------------------------------------------------
#   starting robot connection
#---------------------------------------------------------------------
# Connection processing of tcp communication
m_bcapclient = bcapclient.BCAPClient(host, port, timeout)

# start b_cap Service
m_bcapclient.service_start("")

# set Parameter
Name = ""
Provider = "CaoProv.DENSO.VRC"
Machine = host
Option = ""

# Connect to RC8 (RC8(VRC)provider)
RC8 = m_bcapclient.controller_connect(Name, Provider, Machine, Option)
print('connected')

HRobot = m_bcapclient.controller_getrobot(RC8, "Arm", "")
print("AddRobot")

# TakeArm
Command = "TakeArm"
Param = [0, 0]
m_bcapclient.robot_execute(HRobot, Command, Param)
print("TakeArm")

# Motor On
Command = "Motor"
Param = [1, 0]
m_bcapclient.robot_execute(HRobot, Command, Param)
print("Motor On")

# calculate arrays with roboter coordinates
Objekt_cords = [190, -40, 110]
cords, motorStepps = coordinates(40, Objekt_cords) 
value = cords[0]
# print(cords[0])

# P90_handler = m_bcapclient.controller_getvariable(RC8, id, "P90")
# m_bcapclient.variable_putvalue(P90_handler, value)

# set ExtSpeed Speed,Accel,Decel
Command = "ExtSpeed"
Speed = 100
Accel = 100
Decel = 100
Param = [Speed, Accel, Decel]
m_bcapclient.robot_execute(HRobot, Command, Param)
print("ExtSpeed")


#---------------------------------------------------------------------
#   moving robot 
#---------------------------------------------------------------------
try:
    # Comp = 1
    # Pose = "P90"
    m_bcapclient.robot_move(HRobot, 1, "P90", "NEXT")   # nect weglassen? weil des für asynchrone Bewegung ist? P90 falsch -> "@P P90"
    print("Complete Move P90")
except:
    print("Failed to move robot")

try:
    Comp = 1
    position_Value = [190.0,-22.0,180.0,145.0,0.0,0.0,261]
    Pose = [position_Value,"P","@E"]                    # @E falsch?
    m_bcapclient.robot_move(HRobot,Comp,Pose,"")
except:
    print("Failed to move robot")

#---------------------------------------------------------------------
#   closing robot connection
#---------------------------------------------------------------------
# Motor Off
Command = "Motor"
Param = [0, 0]
m_bcapclient.robot_execute(HRobot, Command, Param)
print("Motor Off")

# Give Arm
Command = "GiveArm"
Param = None
m_bcapclient.robot_execute(HRobot, Command, Param)
print("GiveArm")

# Disconnect
if(HRobot != 0):
    m_bcapclient.robot_release(HRobot)
    print("Release Robot Object")
# End If
if(RC8 != 0):
    m_bcapclient.controller_disconnect(RC8)
    print("Release Controller")
# End If
m_bcapclient.service_stop()
print("B-CAP service Stop")


