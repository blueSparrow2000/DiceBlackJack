import random

class DBJ():
    burst_num = 21
    def __init__(self):
        self.actions = [0,1] # 0,1
        self.states = [(i,j) for i in range(2,22) for j in range(2,22)]# 2~21 valid states
        self.player_states = [i for i in range(2,22)]
        self.dice = [i+1 for i in range(6)]
        self.last_roll = [0,0]
        self.freeze_hand_pos = [False,False]

        self.player_hand=[0,0]
        self.dealer_initial_roll = [0,0]
        self.dealer_hand=self.dealer_initial_roll

        self.verbose = False

        self.who_rolled = "player"

    def set_dealer_turn(self):
        self.who_rolled = "dealer"
        self.freeze_hand_pos = [False, False] # unfreeze
        self.last_roll = self.dealer_initial_roll

    def set_freeze(self, freeze_index):
        self.freeze_hand_pos[freeze_index] = True
        if self.verbose:
            print("Set freeze")


    def set_verbose(self):
        self.verbose = True

    def compare(self,a,b):
        return float(a>b)-float(a<b)

    def roll(self):
        roll = [int(random.choice(self.dice)) for i in range(2)]
        roll_result = [roll[i]*(not self.freeze_hand_pos[i]) + self.last_roll[i] * (self.freeze_hand_pos[i]) for i in range(2)]
        self.last_roll = roll_result
        self.freeze_hand_pos = [False, False] # remove freeze after a roll
        if self.verbose:
            print("The {} rolled {:2d} , {:2d}".format(self.who_rolled, roll_result[0],roll_result[1] ))
        return roll_result

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
        reward = self.compare(self.hand_score(self.player_hand), self.hand_score(self.dealer_hand)) # -1: player lost / 0: Tie / 1: player win
        if self.verbose:
            if reward > 0:
                # player win
                print("You won")
            elif reward == 0:
                # tie
                print("Tie")
            else:
                # player lost
                print("You lost")
            print()
        return reward

    def subtract_player_hand(self, dice_index, amount):
        # player hand is a list [ a, b ] of a: left dice's cumulative sum, b: right dice's cumulative sum
        self.player_hand[dice_index] -= amount
        if self.verbose:
            print("subtracted {:2d} from player hand!".format(amount))
            print("Dealer: {:2d} | Player: {:2d}".format(self.sum_hand(self.dealer_hand),
                                                               self.sum_hand(self.player_hand)))

    def reset(self):
        if self.verbose:
            print("Reset")
        self.freeze_hand_pos = [False, False]
        # roll initially
        self.who_rolled = "dealer"
        self.dealer_initial_roll = self.roll()
        self.dealer_hand=self.dealer_initial_roll

        self.who_rolled = "player"
        player_initial_roll = self.roll()
        self.player_hand=player_initial_roll
        self.last_roll = player_initial_roll

        if self.verbose:
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
                print("END {} turn\n".format(self.who_rolled))
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
                print("END {} turn\n".format(self.who_rolled))
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
                print("END {} turn\n".format(self.who_rolled))
        return roll, done # not done
        # self.get_reward()

