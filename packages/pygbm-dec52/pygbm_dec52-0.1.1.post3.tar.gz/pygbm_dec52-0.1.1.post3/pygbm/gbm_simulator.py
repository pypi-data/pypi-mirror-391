# Class for GBM simulator
# Takes parameters Y0, mu, sigma

# Must have method simulate_path
# Takes parameters T and N, which represent ending time, and number of discrete steps
# Should return t_values, y_values which can then be plotted

# Must be able to have a command line interface interaction for this
# It should then output a picture file of the plot

import numpy as np
from typing import Tuple, List

np.random.seed(42)

class GBMSimulator():
    def __init__(self, y0: float, mu: float, sigma: float):
        self.y0 = y0
        self.mu = mu
        self.sigma = sigma

    def simulate_path(self, T: int, N: int) -> Tuple[List[float], List[float]]:
        """
        Simulates a geometric Brownian motion path from t=0 to T, with N discrete steps.
        Equation: Y(t) = Y0 * exp( (mu - sigma^2/2) * t + sigma * B(t)), where B(t) is a Brownian motion process
        """

        t_values = np.linspace(0, T, N+1)

        dt = T/N
        increments = np.sqrt(dt) * np.random.standard_normal(N)
        b_values = np.insert(np.cumsum(increments), 0, 0)
        
        y_values = self.y0 * np.exp(
                            ((self.mu - ((self.sigma)**2)/2) * t_values)
                            + self.sigma * b_values)

        return t_values, y_values

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    y0 = 1.0
    mu = 0.05
    sigma = 0.2
    T = 2.0
    N = 300

    simulator = GBMSimulator(y0, mu, sigma)
    t, y = simulator.simulate_path(T, N)

    plt.plot(t, y, label="GBM Path")
    plt.xlabel("Time")
    plt.ylabel("Y(t)")
    plt.title("Simulated Geometric Brownian Motion Path")
    plt.legend()
    plt.show()