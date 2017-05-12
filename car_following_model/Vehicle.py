'''
Vehicle class implemets the car following model.

'''

import numpy as np



class Vehicle:
    
    def __init__(self, id, x, l=5, v=0, a=1, b=4, v_max=20, g_min=4, tau=2.05, stop_x=500, model='k'):
        '''
        id - vehicle number
        x - position in meters
        l - car length in meters
        a - acceleration in m/s^2
        b - deceleration in m/s^2
        v_max - maximal speed in m/s
        g_min - minimal distance gap in meters
        tau - reaction time in seconds
        model - model type: 'k' = Krauss; 'i' = IDM; 'g' = Gipps; 'h' = Helly
        '''
        
        self.id = id
        self.model = model
        self.stop_x = stop_x
        self.x = x
        self.x0 = x
        self.l = l
        self.a = a
        self.b = b
        self.v_max = v_max
        self.g_min = g_min
        if id > 1:
            self.g_min += 0
        self.tau = tau
        
        self.t = 0
        self.v = v
        self.a_actual = 0
        self.gap = g_min
        self.noise = 0
        self.time = [0]
        self.trajectory = [x]
        self.speed = [0]
        self.acceleration = [0]
        self.distance_headway = [g_min+l]
        self.headway = [tau]
        self.leader_trajectory = [x+l+g_min]
        self.flow = [0]
        
        return
    


    def update_flow_history(self):
        
        sz = len(self.leader_trajectory)
        i = -1
        while (i >= -sz) and (self.leader_trajectory[i] > self.x):
            i -= 1
        
        if i < -sz:
            self.flow.append(0)
            return
        
        t_l = self.time[i+1]
        if (self.leader_trajectory[i+1] - self.x) > (self.x - self.leader_trajectory[i]):
            t_l = self.time[i]
        
        theta = self.t - t_l
        if theta > 0:            
            self.flow.append(3600.0/(theta))
        else:
            self.flow.append(0)
        
        return



    def update_arrays(self):
        self.time.append(self.t)
        self.trajectory.append(self.x)
        self.leader_trajectory.append(self.x_l)
        self.speed.append(self.v)
        self.acceleration.append(self.a_actual)
        if self.id == 1:
            self.distance_headway.append(self.g_min+self.l)
        else:
            self.distance_headway.append(self.gap+self.l)
        if (self.v > 1) and (self.id > 1):
            self.headway.append((self.gap+self.l)/self.v)
        else:
            self.headway.append(0)
        
        self.update_flow_history()
        
        return


    
    def step_leader(self, x_l, v_l, dt=1):
        '''
        x_l - position of the leading car
        v_l - speed of the leading car
        dt - size of the simulation step in seconds
        '''
        
        time_to_stop = float(self.v / self.b)
        
        if (self.v * time_to_stop / 2) >= (self.stop_x - self.x):
            new_v = np.max([(self.v - self.b*dt), 0])
        else:
            new_v = np.min([(self.v + self.a*dt), self.v_max])

        
        self.gap = x_l - self.x - self.l
        self.x = self.x + ((self.v + new_v)/2)*dt
        self.a_actual = float(new_v - self.v) / dt
        self.v = new_v
        
        return



    def step_krauss(self, x_l, v_l, dt=1):
        '''
        x_l - position of the leading car
        v_l - speed of the leading car
        dt - size of the simulation step in seconds
        '''
        
        if self.id == 1:
            x_l = self.stop_x + self.l + self.g_min
            v_l = 0
            
        sigma1 = 0.1
        sigma2 = 0.05
        if len(self.time) < 2:
            self.noise = sigma1*np.random.uniform()
        else:
            self.noise += np.random.normal(0, sigma2)
            self.noise = np.min([1, np.max([0, self.noise])])
            #self.noise = 0
            
        v_bar = (self.v + v_l) / 2
        
        gap = x_l - self.x - self.l
        gap_desired = self.g_min + v_l*self.tau

        v_safe = v_l + ((gap - gap_desired)/((v_bar/self.b) + self.tau))
        if v_safe > self.noise:
        #if v_safe > 10:
            v_safe -= self.noise    
        v = np.min([(self.v + self.a*dt), v_safe, self.v_max])
        
        new_v = np.max([0, v])
        
        self.gap = gap
        self.x = self.x + ((self.v + new_v)/2)*dt
        self.a_actual = float(new_v - self.v) / dt
        self.v = new_v
        
        return
        
        

    def step_idm(self, x_l, v_l, dt=1):
        '''
        x_l - position of the leading car
        v_l - speed of the leading car
        dt - size of the simulation step in seconds
        '''
        
        if self.id == 1:
            x_l = self.stop_x + self.l + self.g_min
            v_l = 0
            
        gap = x_l - self.x - self.l
        #gap_desired = self.g_min + np.max([0, (self.v*self.tau + self.v*(self.v-v_l))/(2*np.sqrt(self.a*(self.b-0)))])
        #gap_desired = self.g_min + self.v*self.tau + np.max([0, ((self.v*(self.v-v_l))/(2*np.sqrt(self.a*(self.b-0))))])
        gap_desired = self.g_min + np.max([0, self.v*self.tau + self.v*(self.v-v_l)/(2*np.sqrt(self.a*(self.b-0)))])
        #gap_desired = np.max([0, self.v*self.tau + self.v*(self.v-v_l)/(2*np.sqrt(self.a*(self.b-0)))])
        
        p1, p2 = 4, 8        
        self.a_actual = self.a * (1 - (self.v/self.v_max)**p1 - (gap_desired/gap)**p2)
            
        v = self.v + self.a_actual * dt
        new_v = np.max([0, v])
        
        self.gap = gap
        self.x = self.x + ((self.v + new_v)/2)*dt
        self.a_actual = float(new_v - self.v) / dt
        self.v = new_v
        
        return
    
    
    
    def step_iidm(self, x_l, v_l, dt=1):
        '''
        x_l - position of the leading car
        v_l - speed of the leading car
        dt - size of the simulation step in seconds
        '''
       
        if self.id == 1:
            x_l = self.stop_x + self.l + self.g_min
            v_l = 0
            
        b = self.b #/ 2
        gap = x_l - self.x - self.l
        gap_desired = self.g_min + np.max([0, self.v*self.tau + self.v*(self.v-v_l)/(2*np.sqrt(self.a*self.b))])
        #gap_desired = self.g_min + self.v*self.tau + self.v*(self.v-v_l)/(2*np.sqrt(self.a*(self.b-0)))
        
        
        p1, p2 = 4, 8
        a_free = self.a * (1 - (self.v/self.v_max)**p1)
        z = gap_desired / gap
        #if self.v == 0:
         #   self.a_actual = self.a * (1 - (self.v/self.v_max)**p1 - z**p2)
        if z >= 1:
            #self.a_actual = a_free + self.a*(1 - z**p2)
            self.a_actual = self.a*(1 - z**p2)
        else:
            #self.a_actual = a_free
            self.a_actual = a_free * (1 - z**(p2*self.a/a_free))
                    
        v = self.v + self.a_actual * dt
        new_v = np.max([0, v])
        
        self.gap = gap
        self.x = self.x + ((self.v + new_v)/2)*dt
        self.a_actual = float(new_v - self.v) / dt
        self.v = new_v
        
        return
    
    
    
    def step_gipps(self, x_l, v_l, dt=1):
        '''
        x_l - position of the leading car
        v_l - speed of the leading car
        dt - size of the simulation step in seconds
        '''
        
        if self.id == 1:
            x_l = self.stop_x + self.l + self.g_min
            v_l = 0
            
        b = self.b #- 2
               
        gap = x_l - self.x - self.l
        
        #v1 = self.v + 2.5*self.a*dt*(1 - (self.v/self.v_max))*np.sqrt(0.025 + (self.v/self.v_max))
        #v2 = b*self.tau + np.sqrt((b*self.tau)**2 - b*(2*gap - self.v*self.tau - (v_l**2/self.b)))
        v1 = self.v + self.a*dt            
        v2 = -b*self.tau + np.sqrt((b*self.tau)**2 + v_l**2 + 2*b*(gap - self.g_min))
        #v2 = -b*dt + np.sqrt((b*dt)**2 + v_l**2 + 2*b*(gap - self.g_min))
        v = np.min([v1, v2, self.v_max])
        
        new_v = np.max([0, v])
        
        self.gap = gap
        self.x = self.x + ((self.v + new_v)/2)*dt
        self.a_actual = float(new_v - self.v) / dt
        self.v = new_v
        
        return
        
        
        
    def step_helly(self, x_l, v_l, dt=1):
        '''
        x_l - position of the leading car
        v_l - speed of the leading car
        dt - size of the simulation step in seconds
        '''
        
        if self.id == 1:
            x_l = self.stop_x + self.l + self.g_min
            v_l = 0
            
        alpha = 0.5
        beta = 0.25
        
        #b = self.b
        gap = x_l - self.x - self.l
        gap_desired = self.g_min + self.v*self.tau
        
        self.a_actual = alpha*(v_l - self.v) + beta*(gap - gap_desired)
        
        if gap <= self.g_min:
            self.a_actual = np.min([self.a_actual, (v_l-self.v)/dt])
        self.a_actual = np.min([self.a, self.a_actual])
        #self.a_actual = np.max([-self.b, self.a_actual])
        v = np.min([(self.v+self.a_actual*dt), self.v_max])
        new_v = np.max([0, v])
        
        self.gap = gap
        self.x = self.x + ((self.v + new_v)/2)*dt
        self.a_actual = float(new_v - self.v) / dt
        self.v = new_v
        
        return
    
    
    
    def step_platoon(self, leader, dt=1):
        '''
        leader - vehicle in front, if such exists.
        dt - size of the simulation step in seconds.
        '''
        
        x_l = leader.x
        v_l = leader.v
        alpha = 2
        beta = 2
        c = 1 # c% ACC, (1-c)% IIDM
        b = self.b
               
        a_bar = np.min([leader.a_actual, self.a])
        gap = x_l - self.x - self.l
        
        a_cah = 0
        if v_l > 0:
            a_cah = (self.v**2 * a_bar) / (v_l**2 - alpha*gap*a_bar)
            
            if v_l*(self.v - v_l) > -alpha*gap*a_bar:
                theta = 0
                if self.v - v_l >= 0:
                    theta = 1
                a_cah = a_bar - theta * (self.v - v_l)**2 / (beta*gap)
        
        #a_cah = np.min([a_cah, (v_l-self.v)/dt])
        
        gap_desired = self.g_min + np.max([0, self.v*self.tau + self.v*(self.v-v_l)/(2*np.sqrt(self.a*self.b))])        
        
        p1, p2 = 4, 8
        a_free = self.a * (1 - (self.v/self.v_max)**p1)
        a_iidm = a_cah

        if self.id == 1:
            time_to_stop = float(self.v / b)
            if (self.v * time_to_stop / 2) >= (self.stop_x - self.x):
                a_iidm = -b
            else:
                a_iidm = a_free
        else:
            z = gap_desired / gap
            if z >= 1:
                a_iidm = self.a*(1 - z**p2)
            else:
                a_iidm = a_free * (1 - z**(p2*self.a/a_free))
        
        a_cacc = a_iidm
        if a_iidm < a_cah and False:
            a_cacc = (1-c)*a_iidm + c*(a_cah + b*np.tanh((a_iidm-a_cah)/b))
        if gap <= self.g_min:
            a_cacc = np.min([a_cacc, (v_l-self.v)/dt])
            
        new_v = self.v + a_cacc*dt
            
        self.gap = gap
        self.x = self.x + ((self.v + new_v)/2)*dt
        self.a_actual = float(new_v - self.v) / dt
        self.v = new_v
        
        return
    
    
    
    def step(self, leader, dt=1):
        '''
        leader - vehicle in front, if such exists.
        dt - size of the simulation step in seconds
        '''
        
        if leader == None:
            x_l = 1000000000
            v_l = self.v_max
        else:
            x_l = leader.x
            v_l = leader.v
        
        self.t += dt
        self.x_l = x_l
        
        if v_l == 0 and self.v == 0:
            self.update_arrays()
            return
    
        if self.model == 'krauss':
            self.step_krauss(x_l, v_l, dt=dt)
        elif self.model == 'idm':
            self.step_idm(x_l, v_l, dt=dt)
        elif self.model == 'iidm':
            self.step_iidm(x_l, v_l, dt=dt)
        elif self.model == 'gipps':
            self.step_gipps(x_l, v_l, dt=dt)
        elif self.model == 'helly':
            self.step_helly(x_l, v_l, dt=dt)
        elif self.model == 'platoon':
            self.step_platoon(leader, dt=dt)
            
        self.update_arrays()
            
        return
    



   
    def get_history(self, dtype='t'):
        '''
        dtype - type of data requested:
            't' - time
            'x' - trajectory
            'v' - speed
            'a' - acceleration
            'h' - headway
            'f' - flow
            'd' - distance headway
        '''
        
        if dtype == 't':
            return self.time
        if dtype == 'x':
            return self.trajectory
        if dtype == 'v':
            return self.speed
        if dtype == 'a':
            return self.acceleration
        if dtype == 'h':
            return self.headway
        if dtype == 'f':
            return self.flow
        if dtype == 'd':
            return self.distance_headway
        
        return None


        
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
        if self.id == 1:
            return self.tau
        return (self.gap + self.l)/self.v
    
    
    
    def get_distance_headway(self):
        if self.id == 1:
            return self.l
        return (self.gap + self.l)
        





