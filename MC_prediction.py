import numpy as np
import pygame
from collections import defaultdict
from policy_holder import Policy
from diceblackjack import DBJ
from plotting import *

# basic setting
env = DBJ()
policy = Policy(env)
# basic setting


def rollout(policy, env, num_steps,restricted = False):
    state = env.reset()
    episode=[]
    for step in range(num_steps):
        action = policy.random() # policy.greedy(state,Q)
        if restricted:
            action = policy.restricted(state)
        next_state, reward, done = env.train_step(action)
        episode.append([state,action,reward,next_state,done])
        if done:
            break
        state = next_state
    return episode


def mc_Q(policy, env, num_ep, ep_len=100, discount=1.0,restricted = False):
    # for Q learning
    Q = defaultdict(lambda:np.zeros(len(env.actions)))
    returns = defaultdict(lambda:[[] for i in range(len(env.actions))])
    for ep_idx in range(num_ep):
        episode = rollout(policy,env,ep_len,restricted=restricted)
        G_t = 0
        episode.reverse()
        prev_states = [(one_step[0],one_step[1]) for one_step in episode]
        for i in range(len(episode)):
            step = episode[i]
            if step[4]:  # only update G_t on done (total return in an episode)
                G_t = step[2]

            # update Q on first visit
            if not ((step[0],step[1]) in prev_states[i+1:]):
                returns[step[0]][step[1]].append(G_t)
                if len(returns[step[0]][step[1]]) == 0:
                    Q[step[0]][step[1]] = 0
                else:
                    Q[step[0]][step[1]] = sum(returns[step[0]][step[1]]) / len(returns[step[0]][step[1]])

    plot_Q(Q)


def mc_V(policy, env, num_ep, ep_len=100, discount = 1.0 , graph = True,restricted = False):
    V = defaultdict(float)
    returns = defaultdict(list)

    for ep_idx in range(num_ep):
        episode = rollout(policy,env,ep_len,restricted=restricted)
        G_t = 0
        episode.reverse()
        prev_states = [one_step[0] for one_step in episode]
        for i in range(len(episode)): # visit episode in reverse order
            step = episode[i]
            # print(step)
            if step[4]: # only update G_t on done (total return in an episode)
                G_t = step[2]
                # print(G_t)

            # update V on first visit
            if not (step[0] in prev_states[i+1:]):
                returns[step[0]].append(G_t)
                if len(returns[step[0]]) == 0:
                    V[step[0]] = 0
                else:
                    V[step[0]] = sum(returns[step[0]]) / len(returns[step[0]])
    # print(V)
    if graph:
        plot_V(V)
        return [],[]
    else:
        Vx = list(V)
        Vx.sort()
        Vlist = [[x,V[x]] for x in Vx]
        Vy = []
        for s in (env.states):
            if s in Vx:
                Vy.append(V[s])
            else:
                Vy.append(-1) #  if not reached, give lowest reward

        # print(Vlist)
        return Vlist,Vy


# comparing restricted policies
def compare_restricted_policies(env,num_ep=1000):
    def action_translate(a):
        if a==1:
            return 'hit'
        elif a==0:
            return 'stand'
        else:
            return 'invalid action'

    # do restriced policy from 8 to 20
    DATA = []
    HeatDATA = []
    for i in range(2,21):
        policy.restricted_threshold = i
        Vlist,Vy = mc_V(policy, env, num_ep = num_ep, graph = False,restricted=True)
        MiniDATA = [[i]+VV for VV in Vlist]
        DATA+=MiniDATA
        HeatDATA.append(Vy)

    DATA = np.array(DATA)
    #plot_3D(DATA , xlabel ='restricted num' ,ylabel='state',clabel='expected reward(V)')

    HeatDATA = np.array(HeatDATA)
    TDATA = HeatDATA.T
    for state in range(20):
        r_arg = np.argmax(TDATA[state])
        restrict_num = r_arg + 2
        action_to_do = action_translate(int(restrict_num > state+2))
        print("state: {:2d} |best r: {:2d} |reward: {:.2f} |action to do: {}".format(state+2,restrict_num,TDATA[state][r_arg], action_to_do))

    plot_heatmap(HeatDATA, extent=[2,21,20,2])


# env.set_verbose()
# mc_V(policy, env, num_ep = 10, graph = False,restricted=True)
#mc_Q(policy, env, num_ep=100)

compare_restricted_policies(env,num_ep=10000) # 이것도 17에서 멈춰야 하는듯