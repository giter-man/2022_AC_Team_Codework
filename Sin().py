import numpy as np
import pylab as plt

x = np.linspace(0, 3*np.pi, 500)
y = np.sin(x)
plt.plot(x,y)

plt.show()