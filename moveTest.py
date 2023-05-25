import pybcapclient.bcapclient as bcapclient    # Denso library for Cobotta access

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



#---------------------------------------------------------------------
#   moving robot 
#---------------------------------------------------------------------
# Move Initialize Position
# Comp = 1
# Pos_value = [0.0, 0.0, 90.0, 0.0, 90.0, 0.0]
# Pose = [Pos_value, "P", "@E"]
# m_bcapclient.robot_move(HRobot, Comp, Pose, "")
# print("Complete Move P,@E J(0.0, 0.0, 90.0, 0.0, 90.0, 0.0)")

# PoseData (array [Index , Variavletype , Pass])
Comp = 1
Pose = [2, "P", "@90"]
m_bcapclient.robot_move(HRobot, Comp, Pose, "")
print("Complete Move P90")



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