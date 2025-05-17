import random

class DBJ():
    burst_num = 21
    def __init__(self):
        self.actions = [0,1] # 0,1
        self.states = [(i,j) for i in range(2,22) for j in range(2,22)]# 2~21 valid states
        self.player_states = [i for i in range(2,22)]
        self.dice = [i+1 for i in range(6)]

        self.player_hand=self.roll()
        self.dealer_initial_roll = self.roll()
        self.dealer_hand=self.dealer_initial_roll

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

    def player_burst(self):
        return self.is_burst(self.player_hand)

    def dealer_burst(self):
        return self.is_burst(self.dealer_hand)

    def hand_score(self,h):
        return 0 if self.is_burst(h) else self.sum_hand(h)

    def get_player_hand(self):
        return self.sum_hand(self.player_hand)

    def get_dealer_hand(self):
        return self.sum_hand(self.dealer_hand)

    def get_observation(self):
        return (self.hand_score(self.player_hand),self.hand_score(self.dealer_hand))

    def get_hand_sums(self):
        return (self.sum_hand(self.player_hand),self.sum_hand(self.dealer_hand))


    def get_reward(self):
        return self.compare(self.hand_score(self.player_hand), self.hand_score(self.dealer_hand)) # -1: player lost / 0: Tie / 1: player win


    def reset(self):
        self.player_hand=self.roll() # roll initially
        self.dealer_initial_roll = self.roll()
        self.dealer_hand=self.dealer_initial_roll
        if self.verbose:
            print("Reset")
            print("Dealer: {:2d} | Player: {:2d}".format(self.sum_hand(self.dealer_hand),
                                                               self.sum_hand(self.player_hand)))
        return self.get_observation()

    '''
    action is expected to be 1 (hit) or 0 (stand)
    '''
    def player_prompt_step(self, action):
        reward = 0
        done = False
        if action:  # hit
            roll = self.roll()
            self.player_hand += roll
            print("You rolled {} and {}\nYour hand: {:2d}\n".format(roll[0], roll[1], self.get_player_hand()))
            if self.player_burst():
                done = True
                reward = -1
                print("You burst!")
        else:  # stand
            print("="*30,"Dealer's Turn","="*30)
            done = True
            stop_dealer_hit_threshold = self.sum_hand(self.player_hand)
            while self.sum_hand(self.dealer_hand) < stop_dealer_hit_threshold:  # hit
                roll = self.roll()
                self.dealer_hand += roll
                print("Dealer rolled {} and {}\nDealer hand: {:2d}\n".format(roll[0],roll[1], self.get_dealer_hand()))

            reward = self.compare(self.hand_score(self.player_hand), self.hand_score(self.dealer_hand))
        return self.get_observation(), reward, done

    '''
    light weight function that plays only an essential step
    used for fast training NN model 
    '''
    def train_step(self, action):
        reward=0
        done=False
        if action: # hit
            self.player_hand += self.roll()
            if self.player_burst():
                done=True
                reward=-1
        else: # stand
            done=True
            stop_dealer_hit_threshold = self.sum_hand(self.player_hand)
            while self.sum_hand(self.dealer_hand) < stop_dealer_hit_threshold:  # hit
                self.dealer_hand += self.roll()
            reward = self.compare(self.hand_score(self.player_hand), self.hand_score(self.dealer_hand))

        # print current step info
        if self.verbose:
            print("Dealer: {:2d} | Player: {:2d} |Reward: {:.1f}".format(self.get_dealer_hand(), self.get_player_hand(), reward))
            if done:
                print("END episode\n")
        return self.get_observation(), reward, done

    '''
    These functions are for animated player interaction
    Separates player step and dealer step
    '''
    def player_step(self,action):
        reward=0
        done=False
        roll=[]
        if action: # hit
            roll = self.roll()
            self.player_hand += roll
            if self.player_burst():
                done=True
                reward=-1
        else: # stand
            done = True

        # print current step info
        if self.verbose:
            print("Dealer: {:2d} | Player: {:2d} |Reward: {:.1f}".format(self.get_dealer_hand(), self.get_player_hand(), reward))
            if done:
                print("END episode\n")
        return roll, done

    def get_dealer_action(self): # 나중에 NN으로부터 딜러 액션을 가져올수도 있다
        stop_dealer_hit_threshold = self.sum_hand(self.player_hand)
        return self.sum_hand(self.dealer_hand) < stop_dealer_hit_threshold

    def dealer_step(self):
        done = False
        roll=[]
        if self.get_dealer_action():  # True => hit
            roll = self.roll()
            self.dealer_hand += roll
            if self.dealer_burst():
                done=True
                reward=1
        else: # stand => end
            done=True

        # print current step info
        if self.verbose:
            reward = self.get_reward()
            print("Dealer: {:2d} | Player: {:2d} |Reward: {:.1f}".format(self.get_dealer_hand(), self.get_player_hand(), reward))
            if done:
                print("END episode\n")
        return roll, done # not done
        # self.get_reward()

