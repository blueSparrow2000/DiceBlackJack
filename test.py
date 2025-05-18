from collections import defaultdict
import numpy as np
from plotting import *

#
# Q = defaultdict(lambda:[0 for i in range(2)])
#
# Q[1][1] = 1
# Q[1][0] = 0
#
#
# Q[2][1] = 1
# Q[2][0] = 1
#
# Q[3][1] = 2
# Q[3][0] = 3
#
# Q[4][1] = 3
# Q[4][0] = 4
#
# plot_Q(Q)

#
# Q = np.array([[1,1,1],[1,1,1]])
# print(Q.shape)

x = [1,2]
z = [True,False]
print([x[i]*z[i] for i in range(len(x))])