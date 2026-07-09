import numpy as np
import matplotlib.pyplot as plt
x = np.linspace(-4*np.pi, 4*np.pi, 10)
y = np.tan(x)
xvals = np.linspace(-4*np.pi, 4*np.pi, 200)
yinterp = np.interp(xvals, x, y)

plt.plot(x, y,'o')
plt.plot(xvals, yinterp, '-x')
plt.show()
plt.show()