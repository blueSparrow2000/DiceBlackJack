import numpy as np
import pygame
from collections import defaultdict
from policy_holder import Policy
from diceblackjack import DBJ
from plotting import *

# pygame stuff
pygame.init()
font = pygame.font.SysFont('arial', 25)
# pygame stuff

# basic setting
env = DBJ()
# policy = Policy(env)
# basic setting

def game(env):
    run = True
    while run:
        print("=" * 30, "New game", "=" * 30)
        state = env.reset()
        print("Initial roll")
        print("Dealer: {:2d} | Player: {:2d}".format(env.get_dealer_hand(),
                                                     env.get_player_hand()))
        while True:
            ##### get input = action #####
            get_input = True
            action = 0
            while get_input:
                x = input("stand or hit?: ")
                x = x.strip()
                if x=='stand' or x=='s' or x=='0':
                    action = 0
                    get_input = False
                    # print("You stand")
                elif x=='hit' or x=='h' or x=='1':
                    action = 1
                    get_input = False
                    # print("You hit")
                elif x=='q' or x=='':
                    run = False
                    get_input = False
                else:
                    print("invalid argument! Please type 's'/'0' for stand, 'h'/'1' for hit")
            ##### get input = action #####

            # play a step
            next_state, reward, done = env.step(action)

            # check end condition
            if done:
                if reward >0:
                    print("You win!")
                elif reward<0:
                    print("You lost!")
                elif reward == 0:
                    print("Tie!")
                else:
                    print("Unexpected termination")
                break
            state = next_state

        # ask to play again
        x = input("Press any key to play again: ")
        if x:
            pass
        else:
            run = False

# run
game(env)










