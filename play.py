import numpy as np
import pygame
from collections import defaultdict
from policy_holder import Policy
from diceblackjack import DBJ
from plotting import *

# basic setting
env = DBJ()
env.set_verbose()
# policy = Policy(env)
# basic setting


def game():
    # get input
    x = input("stand or hit?: ")
    x = x.strip()
    if x=='stand' or x=='s': #
        pass
    elif x=='hit' or x=='h':
        pass
    else:
        pass # invalid

