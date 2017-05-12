"""
Link object.

"""


import numpy as np


class Link:
    def __init__(self, num, dx, l, gap_min, v_max=20, rho_init=0, v_init=0, a_max=1.5, b_max=2, tau=2.05, is_stop=False):
        '''
        Constructor...
        '''

        #self.model = "gipps"        
        self.model = "iidm"
        #self.model = "idm"
        self.model = "helly"
        
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
        self.alpha1 = 0.5
        self.alpha2 = 0.25
        self.ulink = None
        self.dlink = None
        self.udv = 0
        self.ddv = 0
        
        self.eps = 0.00001
        self.veh_count = 0
        
        self.time = [0]
        self.density = [1609.34*self.rho]
        self.flow = [self.f]
        self.speed = [self.v]
        self.acceleration = []
        self.acceleration2 = []
        self.desired_gap = []
        self.actual_gap = []
        
        return
        
        
    
  
    def update_acceleration(self, dt, ulink, dlink):
        if ulink == None:
            self.udv = self.v
        else:
            self.udv = self.v-ulink.v
#            if ulink.ulink != None:
#                self.udv = self.v-ulink.ulink.v
#                if ulink.ulink.ulink != None:
#                    self.udv = self.v-ulink.ulink.ulink.v
#                    if ulink.ulink.ulink.ulink != None:
#                        self.udv = self.v-ulink.ulink.ulink.ulink.v

        if dlink == None:
            self.ddv = self.v - self.v_max
        else:
            self.ddv = self.v - dlink.v

        g_min = 1.0/self.rho_jam - self.l
        gap_desired = g_min + np.max([0, self.v*self.tau + self.v*self.ddv/(2*np.sqrt(self.a_max*self.b_max))])
        #gap_desired = (1/self.rho_jam) - self.l + self.v*self.tau + self.v*self.ddv/(2*np.sqrt(self.a_max*self.b_max))
        
        b = self.b_max
 
        if self.rho == 0:
            #gap = gap_desired
            gap = 1000000000000
        else:
            if dlink == None:
                gap = self.get_gap()
            else:
                gap = (self.get_gap() + dlink.get_gap()) / 2
        
        z = gap_desired / gap
          
        if self.model == "gipps":
            v = self.v_max
            if dlink != None:
                v = dlink.v
            v_bar = (self.v + v) / 2
            gap_desired = g_min + self.v*self.tau
            a1 = (-b*self.tau + np.sqrt((b*self.tau)**2 + v**2 + 2*b*(gap - g_min)) - self.v) / dt
            #a1 = v + ((gap - gap_desired)/((v_bar/b) + self.tau))
            a2 = (self.v_max - self.v) / dt
            a = np.min([self.a_max, a1, a2])
            #a = np.max([-b, a])
        elif self.model == "iidm":
            a_free = self.a_max * (1 - (self.v/self.v_max)**self.p1)
            if z >= 1:
                a = self.a_max*(1 - z**self.p2)
            else:
                a = a_free * (1 - z**(self.p2*self.a_max/a_free))    
        elif self.model == "idm":
            a = self.a_max * (1 - (self.v/self.v_max)**self.p1 - z**self.p2) # Pure IDM
        elif self.model == "helly":
            v = self.v_max
            if dlink != None:
                v = dlink.v
            gap_desired = g_min + self.v*self.tau
            a1 = self.alpha1*(v - self.v) + self.alpha2*(gap - gap_desired)
            a2 = (self.v_max - self.v) / dt
            a = np.min([self.a_max, a1, a2])
        
        if self.is_stop:
            a = 0
        
        self.a = a
        
        a2 = 0
        if len(self.speed) > 1:
            a2 = (self.speed[-1] - self.speed[-2]) /dt
            
        self.acceleration.append(a)
        self.acceleration2.append(a2)
        self.desired_gap.append(gap_desired)
        #self.actual_gap.append(np.min([50, self.get_gap()]))
        self.actual_gap.append(self.udv)
        
        return


    
    def update_flow(self, dt, dlink):
        self.f = int(np.max(self.density) > 25) * self.rho * self.v
        if dlink == None and self.rho == 0:
            self.f = 0
        self.veh_count += self.f*dt
        self.flow.append(3600*self.f)
        
        return
    
    
    
    def update_density(self, dt, ulink):
        if ulink == None:
            uf = self.f
            #uf = 0
        else:
            uf = ulink.f

        self.rho = np.max([0, self.rho + (dt/self.dx) * (uf - self.f)])
        self.rho = np.min([self.rho_jam, self.rho])
        self.density.append(1609.34*self.rho)
        
        return
    
    
    
    def update_speed(self, dt, ulink, dlink):
        self.v = self.v + dt*(self.a - self.v*self.ddv/self.dx)
        #self.v = self.v + dt*(-np.min([0, (self.v*self.udv/self.dx)]) + self.a)
        #self.v = self.v + dt*self.a
        #self.v = np.max([0, self.v])
        #self.v = np.min([self.v_max, self.v])

        if self.is_stop:
            self.v = 0

        if dlink == None:
            self.v = ulink.v
        if self.rho < -self.eps**4:
            self.v = ulink.v
        
        self.speed.append(self.v)

        return
    
    
    
    def update_state(self, dt, ulink, dlink):
        if self.ulink == None:
            self.ulink = ulink
        if self.dlink == None:
            self.dlink = dlink
        t = self.time[-1]
        self.time.append(t+dt)
        self.update_flow(dt, dlink)
        self.update_density(dt, ulink)
        self.update_speed(dt, ulink, dlink)
        
        return
        
    
    
    def get_gap(self):
        if self.rho == 0:
            return 1000000
        return ((1.0/self.rho)) - self.l




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
        if dtype == 'o':
            return self.acceleration2
        if dtype == 'g':
            return self.desired_gap
        if dtype == 'h':
            return self.actual_gap
        if dtype == 'f':
            return self.flow
        if dtype == 'd':
            return self.density
        
        return None
        
        
        
        
        
        