import sys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
from numpy.random import randn

def plot_V(V):
    Vx = list(V)
    Vx.sort()
    Vy = [V[x] for x in Vx]

    plt.plot(Vx,Vy,linewidth=2.0, color='r')
    #plt.axis(())
    plt.xlabel('state')
    plt.ylabel('expected reward(V)')
    plt.show()

def plot_heatmap(DATA,  extent=False, xlabel = 'state',ylabel='restricted num'):
    if extent:
        plt.imshow(DATA, cmap=cm.gray ,extent=extent) #plt.imshow(DATA, cmap=cm.hot ,extent=extent)
    else:
        plt.imshow(DATA, cmap=cm.hot)
    plt.colorbar()
    # y가 restricted 임
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()



def plot_3D(DATA, xlabel ='state' ,ylabel='action',clabel='expected reward(V)'):
    # print(DATA)
    Xs = DATA[:, 0]
    Ys = DATA[:, 1]
    Zs = DATA[:, 2]

    # ======
    ## plot:

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_trisurf(Xs, Ys, Zs, cmap=cm.jet, linewidth=0)
    fig.colorbar(surf)

    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.zaxis.set_major_locator(MaxNLocator(5))

    fig.tight_layout()

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.clabel(clabel)

    plt.show()  # or:
    # fig.savefig('3D.png')


def plot_Q(Q):
    Qstate = list(Q)
    Qstate.sort()
    n_actions = len(Q[Qstate[0]])

    DATA = []
    for s in (Qstate):
        for a in range(n_actions):
            DATA.append([s,a,Q[s][a]])
    DATA = np.array(DATA)
    plot_3D(DATA)


