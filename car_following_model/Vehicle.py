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
        
        self.t = 0
        self.v = 0
        self.a_actual = 0
        self.gap = g_min
        self.time = [0]
        self.trajectory = [x]
        self.speed = [0]
        self.acceleration = [0]
        
        return
    
    
    def update_arrays(self):
        self.time.append(self.t)
        self.trajectory.append(self.x)
        self.speed.append(self.v)
        self.acceleration.append(self.a_actual)
        
        return


        
    def step_krauss(self, x_l, v_l, dt=1):
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
        self.a_actual = float(new_v - self.v) / dt
        self.v = new_v
        self.t += dt
        
        self.update_arrays()
        
        return
        
        

    def step_idm(self, x_l, v_l, dt=1):
        '''
        x_l - position of the leading car
        v_l - speed of the leading car
        dt - size of the simulation step in seconds
        '''
        
        if v_l == 0:
            return
               
        gap = x_l - self.x - self.l
        gap_desired = self.g_min + self.v*self.tau + (self.v*(self.v-v_l))/(2*np.sqrt(self.a*(self.b-0)))
        self.a_actual = self.a * (1 - (self.v/self.v_max)**4 - (gap_desired/gap)**2)
        v = self.v + self.a_actual * dt
        new_v = np.max([0, v])
        
        self.gap = gap
        self.x = self.x + ((self.v + new_v)/2)*dt
        #self.x = self.x + new_v*dt
        self.v = new_v
        self.t += dt
        
        self.update_arrays()
        
        return
    
    
    
    def step_gipps(self, x_l, v_l, dt=1):
        '''
        x_l - position of the leading car
        v_l - speed of the leading car
        dt - size of the simulation step in seconds
        '''
        
        if v_l == 0:
            return
            
        b = self.b #- 2
               
        gap = x_l - self.x - self.l
        if gap > 100000:
            v = np.min([self.v_max, (self.v + self.a*dt)])
        else:
            v1 = self.v + 2.5*self.a*dt*(1 - (self.v/self.v_max))*np.sqrt(0.025 + (self.v/self.v_max))
            #v1 = self.v + self.a*dt
            v2 = b*self.tau + np.sqrt((b*self.tau)**2 - b*(2*gap - self.v*self.tau - (v_l**2/self.b)))
            v = np.min([v1, v2, self.v_max])
        
        new_v = np.max([0, v])
        
        self.gap = gap
        self.x = self.x + ((self.v + new_v)/2)*dt
        #self.x = self.x + new_v*dt
        self.a_actual = float(new_v - self.v) / dt
        self.v = new_v
        self.t += dt
        
        self.update_arrays()
        
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
    
    
    
    def get_acceleration(self):
        return self.a_actual
    
    
    
    def get_headway(self):
        return (self.gap + self.l)/self.v
    
    
    
    def get_distance_headway(self):
        return (self.gap + self.l)
        
        