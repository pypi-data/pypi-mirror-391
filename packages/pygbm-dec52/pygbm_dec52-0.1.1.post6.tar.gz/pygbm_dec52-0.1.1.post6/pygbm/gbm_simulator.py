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
    """
    A class to simulate paths of a Geometric Brownian Motion (GBM) process.

    The GBM is a commonly used stochastic process in quantitative finance to model 
    stock prices and other quantities that evolve continuously with both drift and volatility.
    
    The process follows the stochastic differential equation (SDE):
        dY(t) = μY(t)dt + σY(t)dW(t)
    where:
        - μ (mu) is the drift term (expected rate of return),
        - σ (sigma) is the volatility term,
        - W(t) is a standard Wiener process (Brownian motion).

    Attributes
    ----------
    y0 : float
        The initial value of the process, Y(0).
    mu : float
        The drift coefficient.
    sigma : float
        The volatility coefficient.
    """
    
    def __init__(self, y0: float, mu: float, sigma: float):
        """
        Initializes the GBMSimulator with given model parameters.

        Parameters
        ----------
        y0 : float
            Initial value of the process.
        mu : float
            Drift parameter of the process.
        sigma : float
            Volatility (standard deviation) of the process.
        """
        self.y0 = y0
        self.mu = mu
        self.sigma = sigma

    def simulate_path(self, T: int, N: int) -> Tuple[List[float], List[float]]:
        """
        Simulates a single sample path of a geometric Brownian motion (GBM).

        The GBM path is generated using the analytical solution:
        Y(t) = Y0 * exp((μ - 0.5σ²)t + σB(t))
        where B(t) is a standard Brownian motion.

        Parameters
        ----------
        T : float
            Total time horizon for the simulation (end time).
        N : int
            Number of discrete time steps in the simulation.

        Returns
        -------
        Tuple[List[float], List[float]]
            A tuple containing:
                - t_values: List of time points from 0 to T.
                - y_values: List of simulated Y(t) values corresponding to each time point.
        
        Notes
        -----
        The Brownian motion increments are drawn from a standard normal distribution, 
        scaled by sqrt(Δt). Randomness is controlled by the global NumPy random seed.

        Example
        -------
        >>> simulator = GBMSimulator(1.0, 0.05, 0.2)
        >>> t, y = simulator.simulate_path(2.0, 300)
        >>> len(t), len(y)
        (301, 301)
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