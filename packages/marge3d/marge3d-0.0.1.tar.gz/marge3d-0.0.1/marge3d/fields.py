"""
The 3D velocity field here is (-y, x, 0). This is just the 2D vortex taken along z direction.
"""
import math

class VelocityField3D:

  def __init__(self, omega):
    self.omega    = omega
    self.limits   = False
    self.periodic = False

  def get_velocity(self, x, y, z, t):
    u1 =  -y * self.omega
    u2 =  x * self.omega
    u3 =  0.0 * self.omega
    return u1, u2, u3

  def get_gradient(self, x, y, z, t):
    # TODO : why is there no dependency on x, y, z and t ?
    u1x =  0.0
    u1y =  -1.0 * self.omega
    u1z =  0.0
    u2x =  1.0 * self.omega
    u2y =  0.0
    u2z =  0.0
    u3x =  0.0
    u3y =  0.0
    u3z =  0.0 * self.omega
    return u1x, u1y, u1z, u2x, u2y, u2z, u3x, u3y, u3z

  def get_dudt(self, x, y, z, t):
    # TODO : why is there no dependency on x, y, z and t ?
    u1t = 0.0
    u2t = 0.0
    u3t = 0.0
    return u1t, u2t, u3t


class velocity_field_3d_nondim():

  def __init__(self, omega, char_vel, char_time):
    self.char_vel  = char_vel
    self.char_time = char_time
    self.char_len = char_vel
    self.omega    = omega*char_time
    self.limits   = False
    self.periodic = False

  def get_velocity(self, x, y, z, t):
    u1 =  -y * self.omega*self.char_len
    u2 =  x * self.omega*self.char_len
    u3 =  0.0 * self.omega*self.char_len
    return u1/self.char_vel, u2/self.char_vel, u3/self.char_vel

  def get_gradient(self, x, y, z, t):
    # TODO : why is there no dependency on x, y, z and t ?
    u1x =  0.0
    u1y =  -1.0 * self.omega
    u1z =  0.0
    u2x =  1.0 * self.omega
    u2y =  0.0
    u2z =  0.0
    u3x =  0.0
    u3y =  0.0
    u3z =  0.0 * self.omega
    return u1x*self.char_time, u1y*self.char_time, u1z*self.char_time, u2x*self.char_time, u2y*self.char_time, u2z*self.char_time, u3x*self.char_time, u3y*self.char_time, u3z*self.char_time

  def get_dudt(self, x, y, z, t):
    # TODO : why is there no dependency on x, y, z and t ?
    u1t = 0.0
    u2t = 0.0
    u3t = 0.0
    return u1t, u2t, u3t

class velocity_field_3d_oscillatory():

  def __init__(self):

    self.limits   = False
    self.periodic = False

  def get_velocity(self, x, y, z, t):
    u1 = 0.05
    u2 = math.sin(6*t)
    u3 = 0.0
    return u1, u2, u3

  def get_gradient(self, x, y, z, t):
    u1x =  0.0
    u1y =  0.0
    u1z =  0.0
    u2x =  0.0
    u2y =  0.0
    u2z =  0.0
    u3x =  0.0
    u3y =  0.0
    u3z =  0.0
    return u1x, u1y, u1z, u2x, u2y, u2z, u3x, u3y, u3z

  def get_dudt(self, x, y, z, t):
    u1t = 0.0
    u2t = 6*math.cos(6*t)
    u3t = 0.0
    return u1t, u2t, u3t
