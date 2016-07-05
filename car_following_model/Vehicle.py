'''
Vehicle class implemets the car following model.

'''

import numpy as np



class Vehicle:
    
    def __init__(self, x, l=5, a=1, b=4, v_max=20, g_min=4, tau=2.05):
        '''
        x - position in meters
        l - car length in meters
        a - acceleration in m/s^2
        b - deceleration in m/s^2
        v_max - maximal speed in m/s
        g_min - minimal distance gap in meters
        tau - reaction time in seconds
        '''
        
        self.x = x
        self.l = l
        self.a = a
        self.b = b
        self.v_max = v_max
        self.g_min = g_min
        self.tau = tau
        
        self.v = 0
        self.gap = g_min
        
        return
    
    
    
    def step(self, x_l, v_l, dt=1):
        '''
        x_l - position of the leading car
        v_l - speed of the leading car
        dt - size of the simulation step in seconds
        '''
        
        if v_l == 0:
            return
        
        v_bar = (self.v + v_l) / 2
        
        gap = x_l - self.x - self.l
        gap_desired = self.g_min + v_l*self.tau
        v_safe = v_l + (gap - gap_desired)/((v_bar/self.b) + self.tau)
        v = np.min([(self.v + self.a*dt), v_safe, self.v_max])
        new_v = np.max([0, v])
        
        self.gap = gap
        self.x = self.x + ((self.v + new_v)/2)*dt
        #self.x = self.x + new_v*dt
        self.v = new_v
        
        return
    
    
    
    
    def get_max_speed(self):
        return self.v_max
        
        

    def get_position(self):
        return self.x
    
    
    
    def get_safe_speed(self, x_l, v_l):
        v_bar = (self.v + v_l) / 2        
        gap = x_l - self.x - self.l
        gap_desired = self.g_min + v_l*self.tau
        return v_l + (gap - gap_desired)/((v_bar/self.b) + self.tau)



    def get_speed(self):
        return self.v
    
    
    
    def get_headway(self):
        return (self.gap + self.l)/self.v
    
    
    
    def get_distance_headway(self):
        return (self.gap + self.l)
        
        