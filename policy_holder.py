import random
import numpy as np
from variables import *

class Policy():
    epsilon = 0.1
    def __init__(self,env):
        self.env = env
        self.actions = self.env.actions
        self.states = self.env.states

        # threshold for restricted policy
        self.restricted_threshold = 7

    def random(self):
        return random.choice(self.actions)

    def greedy(self,state,Q):
        return np.argmax(Q[state]) # best action

    def epsilon_greedy(self,state,Q):
        do_random = random.random()
        if do_random < Policy.epsilon:
            return self.random()
        else:
            return self.greedy(state,Q)

    # custom policy
    def restricted(self, state):
        if state < self.restricted_threshold:
            return 1
        else:
            return 0