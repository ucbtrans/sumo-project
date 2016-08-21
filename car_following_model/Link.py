"""
Link object.

"""


import numpy as np


class Link:
    def __init__(self, num, dx, l, gap_min, v_max=20, rho_init=0, v_init=0, a_max=1.5, b_max=2, tau=2.05, is_stop=False):
        '''
        Constructor...
        '''
        
        self.id = num
        self.is_stop = is_stop
        self.dx = dx
        self.gap_min = gap_min
        self.l = l
        self.rho_jam = float(1.0/(gap_min + l))
        self.v_max = v_max
        self.rho = rho_init
        self.v = v_init
        self.f = self.rho * self.v
        self.a = 0
        
        self.a_max = a_max
        self.b_max = b_max
        self.tau = tau
        self.p1 = 4
        self.p2 = 8
        self.udv = 0
        self.ddv = 0
        
        self.time = [0]
        self.density = [1609.34*self.rho]
        self.flow = [self.f]
        self.speed = [self.v]
        self.acceleration = []
        self.desired_gap = []
        
        return
        
        
    
  
    def update_acceleration(self, dt, ulink, dlink):
        if ulink == None:
            self.udv = self.v
        else:
            self.udv = self.v-ulink.v
        self.udv = -self.udv
        if dlink == None:
            self.ddv = self.v - self.v_max
        else:
            self.ddv = self.v - dlink.v
        #self.ddv = -self.ddv

        gap_desired = (((1/self.rho_jam) - self.l) + self.v*self.tau + 
                        #self.v*self.ddv/(2*self.dx*np.sqrt(self.a_max*self.b_max)))
                        self.v*self.ddv/(2*np.sqrt(self.a_max*self.b_max)))
        if self.rho == 0:
            gap = self.gap_min
            gap = gap_desired
        else:
            gap = ((1.0/self.rho)) - self.l

        z = gap_desired / gap
        a_free = self.a_max * (1 - (self.v/self.v_max)**self.p1)
        
        if z >= 1:
            a = a_free + self.a_max*(1 - z**self.p2)
        else:
            a = a_free
        
        #a = self.a_max * (1 - (self.v/self.v_max)**self.p1 - z**self.p2) # Pure IDM
        
        if self.is_stop:
            a = 0
        
        if self.rho == 0:
            a = 0
        
        self.a = a
        #a = np.min([self.a_max, a])
        #a = np.max([-self.b_max, a])
        #self.a = a
        
        self.acceleration.append(a)
        self.desired_gap.append(gap_desired)
        
        return


    
    def update_flow(self, dt):
        self.f = self.rho * self.v
        #if self.is_stop:
         #   self.f = 0
        self.flow.append(3600*self.f)
        
        return
    
    
    
    def update_density(self, dt, ulink):
        if ulink == None:
            uf = self.f
        else:
            uf = ulink.f
        self.rho = np.max([0, self.rho + (dt/self.dx) * (uf - self.f)])
        self.rho = np.min([self.rho_jam, self.rho])
        self.density.append(1609.34*self.rho)
        
        return
    
    
    
    def update_speed(self, dt, ulink, dlink):
        self.v = self.v + dt*((-self.v*self.ddv/self.dx) + self.a)
        #self.v = self.v + dt*self.a
        self.v = np.max([0, self.v])
        self.v = np.min([self.v_max, self.v])
        if self.is_stop:
            self.v = 0
        #if self.rho == 0:
         #   self.v = 0
        if dlink == None:
            self.v = ulink.v
        self.speed.append(self.v)

        return
    
    
    
    def update_state(self, dt, ulink, dlink):
        t = self.time[-1]
        self.time.append(t+dt)
        self.update_flow(dt)
        self.update_density(dt, ulink)
        self.update_speed(dt, ulink, dlink)
        
    
    
    
    def get_history(self, dtype='t'):
        '''
        dtype - type of data requested:
            't' - time
            'v' - speed
            'a' - acceleration
            'f' - flow
            'd' - distance headway
        '''
        
        if dtype == 't':
            return self.time
        if dtype == 'v':
            return self.speed
        if dtype == 'a':
            return self.acceleration
        if dtype == 'g':
            return self.desired_gap
        if dtype == 'f':
            return self.flow
        if dtype == 'd':
            return self.density
        
        return None
        
        
        
        
        
        