import random
import numpy as np 
from .utils import pol2cart


class State(object):
    """Common base class for state & assoc methods
    """
    def __init__(self):
        pass

    def init_state(self):
        """Undefined initializing state method
        """
        pass
    
    def reward_func(self):
        """Undefined reward calc method
        """
        pass

    def update_state(self):
        """Undefined state updating method
        """
        pass


class RFState(State):
    """RF State
    """
    def __init__(self, prob=0.9, target_speed=None, target_movement=None):

        # Transition probability
        self.prob = prob
        # Target speed
        self.target_speed = float(target_speed) if target_speed is not None else 1.
        # Target movement pattern
        self.target_movement = target_movement if target_movement is not None else 'random'
        self.target_move_iter = 0 
        # Setup an initial random state
        self.target_state = self.init_target_state()
        # Setup an initial sensor state 
        self.sensor_state = self.init_sensor_state()
    

    def init_target_state(self):
        """Function to initialize a random state

        Returns
        -------
        array_like
            Randomly generated state variable array
        """
        # state is [range, bearing, relative course, own speed]
        return np.array([random.randint(25,100), random.randint(0,359), random.randint(0,11)*30, 1])
   
    def init_sensor_state(self): 
        # state is [range, bearing, relative course, own speed]
        return np.array([0,0,0,0])

    # returns reward as a function of range, action, and action penalty or as a function of range only
    def reward_func(self, state, action_idx=None, action_penalty=-.05):
        """Function to calculate reward based on state and selected action

        Parameters
        ----------
        state : array_like
            List of current state variables
        action_idx : integer
            Index for action to make step
        action_penalty : float
            Penalty value to reward if action provided

        Returns
        -------
        reward_val : float
            Calculated reward value
        """
    
        # Set reward to 0/. as default
        reward_val = 0.
        state_range = state[0]

        if action_idx is not None: # returns reward as a function of range, action, and action penalty
            if (2 < action_idx < 5):
                action_penalty = 0

            if state_range >= 150:
                reward_val = -2 + action_penalty # reward to not lose track of contact
            elif state_range <= 10:
                reward_val = -2 + action_penalty # collision avoidance
            else:
                reward_val = 0.1 + action_penalty # being in "sweet spot" maximizes reward
        else: # returns reward as a function of range only
            if state_range >= 150:
                reward_val = -2 # reward to not lose track of contact
            elif state_range <= 10:
                reward_val = -200 # collision avoidance
            else:
                reward_val = 0.1
        return reward_val


    # returns new state given last state and action (control)
    def update_state(self, state, control, target_update=False):
        """Update state based on state and action

        Parameters
        ----------
        state_vars : list
            List of current state variables
        control : action (tuple)
            Action tuple

        Returns
        -------
        State (array_like)
            Updated state values array
        """
        # Get current state vars
        r, theta, crs, spd = state
        spd = control[1]
        
        theta = theta % 360
        theta -= control[0]
        theta = theta % 360
        if theta < 0:
            theta += 360

        crs = crs % 360
        crs -= control[0]
        if crs < 0:
            crs += 360
        crs = crs % 360
       
        # Get cartesian coords
        x, y = pol2cart(r, np.radians(theta))

        # Generate next course given current course
        if target_update: 
            if self.target_movement == 'circular': 
                crs += self.circular_control(5)[0]
            else: 
                if random.random() >= self.prob:
                    crs += random.choice([-1, 1]) * 30
        else: 
            if random.random() >= self.prob:
                crs += random.choice([-1, 1]) * 30
        crs %= 360
        if crs < 0:
            crs += 360

        # Transform changes to coords to cartesian
        dx, dy = pol2cart(self.target_speed, np.radians(crs))
        pos = [x + dx - spd, y + dy]

        r = np.sqrt(pos[0]**2 + pos[1]**2)
        theta_rad = np.arctan2(pos[1], pos[0])
        theta = np.degrees(theta_rad)
        if theta < 0:
            theta += 360

        return (r, theta, crs, spd)

    def update_sensor(self, control): 
        r, theta_deg, crs, spd = self.sensor_state
        
        spd = control[1]

        crs = crs % 360
        crs += control[0]
        if crs < 0:
            crs += 360
        crs = crs % 360

        x, y = pol2cart(r, np.radians(theta_deg))

        dx, dy = pol2cart(spd, np.radians(crs))
        pos = [x + dx, y + dy]

        r = np.sqrt(pos[0]**2 + pos[1]**2)
        theta_deg = np.degrees(np.arctan2(pos[1], pos[0]))
        if theta_deg < 0:
            theta_deg += 360

        self.sensor_state = np.array([r, theta_deg, crs, spd])

    # returns absolute state given base state(absolute) and relative state 
    def get_absolute_state(self, relative_state):
        r_t, theta_t, crs_t, spd = relative_state
        r_s, theta_s, crs_s, _ = self.sensor_state

        x_t, y_t = pol2cart(r_t, np.radians(theta_t))
        x_s, y_s = pol2cart(r_s, np.radians(theta_s))

        x = x_t + x_s
        y = y_t + y_s 
        r = np.sqrt(x**2 + y**2)
        theta_deg = np.degrees(np.arctan2(y, x))
        if theta_deg < 0:
            theta_deg += 360

        return [r, theta_deg, crs_s+crs_t, spd]

    def circular_control(self, size):
        d_crs = 30 if self.target_move_iter%size == 0 else 0 
        self.target_move_iter += 1 
        return [d_crs, self.target_speed]



AVAIL_STATES = {'rfstate' : RFState,
                }

def get_state(state_name=''):
    """Convenience function for retrieving BirdsEye state methods
    Parameters
    ----------
    state_name : {'rfstate'}
        Name of state method.
    Returns
    -------
    state_obj : State class object
        BirdsEye state method.
    """
    state_name = state_name.lower()
    if state_name in AVAIL_STATES:
        state_obj = AVAIL_STATES[state_name]
        return state_obj
    else:
        raise ValueError('Invalid action method name, {}, entered. Must be '
                         'in {}'.format(state_name, AVAIL_STATES.keys()))

