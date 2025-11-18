#%%
from .base_gbm import baseGBM
import numpy as np
import matplotlib.pyplot as plt

import matplotlib
# Set a GUI backend
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt

#%%
class GBMSimulator(baseGBM):
    def __init__(self, y0, mu, sigma):
        super().__init__(y0, mu, sigma)

    def simulate_path(self, T, N):
        dt = T/N
        t_values = np.linspace(0, T, N+1)
        y_values = np.zeros(N+1)
        y_values[0] = self.y0
        for i in range(1, N+1):
            dB = np.random.normal(0, np.sqrt(dt))
            y_values[i] = y_values[i-1] * np.exp((self.mu - 0.5 * self.sigma**2) * dt + self.sigma * dB)
        return t_values, y_values
    
    def plot_path(self, t_values, y_values, output=None):
        plt.figure()
        plt.plot(t_values, y_values)
        plt.xlabel('Time')
        plt.ylabel('Path')
        plt.title('GBM Path')
        if output:
            plt.savefig(output)
        plt.show()
        plt.close()


    









