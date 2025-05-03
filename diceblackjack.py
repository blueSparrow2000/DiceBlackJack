import random
from variables import *

class DBJ():
    burst_num = 21
    def __init__(self):
        self.actions = [0,1] # 0,1
        self.states = [i for i in range(2,22)]# 2~21 valid states
        self.dice = [i for i in range(6)]

        self.player_hand=self.roll()
        self.dealer_hand=self.roll()

        self.verbose = False

    def set_verbose(self):
        self.verbose = True

    def compare(self,a,b):
        return float(a>b)-float(a<b)

    def roll(self):
        return [int(random.choice(self.dice)) for i in range(2)]

    def sum_hand(self,h):
        return sum(h)

    def is_burst(self,h):
        return self.sum_hand(h) > DBJ.burst_num

    def hand_score(self,h):
        return 0 if self.is_burst(h) else self.sum_hand(h)

    def get_observation(self):
        return self.hand_score(self.player_hand)

    def reset(self):
        self.player_hand=self.roll() # roll initially
        self.dealer_hand=self.roll()
        if self.verbose:
            print("Reset")
            print("Dealer: {:2d} | Player: {:2d}".format(self.sum_hand(self.dealer_hand),
                                                               self.sum_hand(self.player_hand)))


        return self.get_observation()

    '''
    action is expected to be 1 (hit) or 0 (stand)
    '''
    def step(self,action):
        reward=0
        done=False
        if action: # hit
            self.player_hand += self.roll()
            if self.is_burst(self.player_hand):
                done=True
                reward=-1
        else: # stand
            done=True
            stop_dealer_hit_threshold = self.sum_hand(self.player_hand)
            while self.sum_hand(self.dealer_hand) < stop_dealer_hit_threshold: # hit
                self.dealer_hand += self.roll()
            reward = self.compare(self.hand_score(self.player_hand), self.hand_score(self.dealer_hand))

        if self.verbose:
            print("Dealer: {:2d} | Player: {:2d} |Reward: {:.1f}".format(self.sum_hand(self.dealer_hand), self.sum_hand(self.player_hand),reward))
            if done:
                print("END episode\n")

        return self.get_observation(), reward, done













