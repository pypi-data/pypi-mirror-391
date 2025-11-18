from .core import BaseGBM
import numpy as np
import matplotlib.pyplot as plt

class GBMSimulator(BaseGBM):
    
    def __init__(self, y0, mu, sigma):
        """this allows us to pass the values into this sub class imediately and then this passes them up to the main class"""
        super().__init__(y0, mu, sigma)
    
    def simulate_path(self,T,N):
        """Assume T is the total time, N is the number of steps, dt = T/N"""
        
        t = np.linspace(0,T,N+1)
        y = np.empty(N+1)
        y[0] = self.y0 

        dt = T/N
        
        for step in range(N):
            dB = np.random.normal(0,np.sqrt(dt)) #this is the brownian motion step, with mean = 0 and s.d. = sqrt(dt)
            y[step+1] = y[step]*np.exp(( self.mu - ((self.sigma**2)/2))*dt + self.sigma*dB) #time step equation
        
        return y, t

    def plot_path(self, t, y, output=None):
        plt.plot(t,y)
        plt.title("Brownian motion simulation")
        if output:
            plt.savefig(output)
        else:
            plt.show()
        