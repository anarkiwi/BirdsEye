import random

class Sensor(object):
    def __init__(self):
        pass
    def observation(self):
        pass

    def weight(self): 
        pass

class Drone(Sensor): 
    def __init__(self): 
        pass

    # importance weight of state given observation
    def weight(self, hyp, o, xp):
        if o == 1: 
            return self.obs1_prob(xp)
        else: 
            return 1-self.obs1_prob(xp)

    # samples observation given state
    def observation(self, x):
        weights = [1-self.obs1_prob(x), self.obs1_prob(x)]
        obsers = [0, 1]
        return random.choices(obsers, weights)[0]

    # probability of observation 1 
    def obs1_prob(self, x): 
        rel_bearing = x[1]
        if -60 <= rel_bearing <= 60: 
            return 0.9
        elif 120 <= rel_bearing <= 240: 
            return 0.1
        else: 
            return 0.5 
            
    # sample state from observation 
    def gen_state(self, obs): 
        
        if obs == 1: 
            bearing = random.randint(-60,60)
        elif obs == 0: 
            bearing = random.randint(120, 240)
        
        if bearing < 0: 
            bearing += 360
            
        return [random.randint(25,100), bearing, random.randint(0,11)*30, 1]


class Bearing(Sensor): 
    def __init__(self, sensor_range = 150): 
        self.sensor_range = sensor_range

    # importance weight of state given observation
    def weight(self, hyp, o, xp):
        if o == 0:
            return self.obs0(xp)
        if o == 1:
            return self.obs1(xp)
        if o == 2:
            return self.obs2(xp)
        if o == 3:
            return self.obs3(xp)

    # samples observation given state
    def observation(self, x):
        weights = [self.obs0(x), self.obs1(x), self.obs2(x), self.obs3(x)]
        obsers = [0, 1, 2, 3]
        return random.choices(obsers, weights)[0]

    # sample state from observation 
    def gen_state(self, obs): 
        
        if obs == 0: 
            bearing = random.randint(-60,60)
        elif obs == 1: 
            bearing = random.choice([random.randint(60,90), random.randint(270, 300)])
        elif obs == 2: 
            bearing = random.choice([random.randint(90,120), random.randint(240,270)])
        elif obs == 3: 
            bearing = random.randint(120, 240)
        
        if bearing < 0: 
            bearing += 360
            
        return [random.randint(25,100), bearing, random.randint(0,11)*30, 1]

    def obs1(self, state):
        #rel_brg = state[1] - state[3]
        rel_brg = state[1]
        state_range = state[0]
        if rel_brg < 0:
            rel_brg += 360
        if ((60 < rel_brg < 90) or (270 < rel_brg < 300)) and (state_range < self.sensor_range/2):
            return 1
        elif ((60 < rel_brg < 90) or (270 < rel_brg < 300)) and (state_range < self.sensor_range):
            return 2-2*state_range/self.sensor_range
        else:
            return 0.0001

    def obs2(self, state):
        #rel_brg = state[1] - state[3]
        rel_brg = state[2]
        state_range = state[1]
        if rel_brg < 0:
            rel_brg += 360
        if ((90 <= rel_brg < 120) or (240 < rel_brg <= 270)) and (state_range < self.sensor_range/2):
            return 1
        elif ((90 <= rel_brg < 120) or (240 < rel_brg <= 270)) and (state_range < self.sensor_range):
            return 2-2*state_range/self.sensor_range
        else:
            return 0.0001

    def obs3(self, state):
        #rel_brg = state[1] - state[3]
        rel_brg = state[1]
        state_range = state[0]
        if rel_brg < 0:
            rel_brg += 360
        if (120 <= rel_brg <= 240) and (state_range < self.sensor_range/2):
            return 1
        elif (120 <= rel_brg <= 240) and (state_range < self.sensor_range):
            return 2-2*state_range/self.sensor_range
        else:
            return 0.0001

    def obs0(self, state):
        #rel_brg = state[1] - state[3]
        rel_brg = state[1]
        state_range = state[0]
        if rel_brg < 0:
            rel_brg += 360
        if (rel_brg <= 60) or (rel_brg >=300) or (state_range >= self.sensor_range):
            return 1
        if (not(self.obs1(state) > 0) and not(self.obs2(state) > 0) and not(self.obs3(state) > 0)):
            return 1
        elif (120 <= rel_brg <= 240) and (self.sensor_range/2 < state_range < self.sensor_range):
            return 2*state_range/self.sensor_range - 1
        elif ((90 <= rel_brg < 120) or (240 < rel_brg <= 270)) and (self.sensor_range/2 < state_range < self.sensor_range):
            return 2*state_range/self.sensor_range -1
        elif ((60 <= rel_brg < 90) or (270 < rel_brg <= 300)) and (self.sensor_range/2 < state_range < self.sensor_range):
            return 2*state_range/self.sensor_range - 1
        else:
            return 0.0001