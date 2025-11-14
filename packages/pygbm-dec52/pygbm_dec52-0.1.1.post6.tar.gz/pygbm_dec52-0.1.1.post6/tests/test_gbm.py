import pygbm

y0 = 1
mu = 0.05
sigma = 0.2
T = 1.0
N = 200

simulator = pygbm.gbm_simulator.GBMSimulator(y0, mu, sigma)
t, y = simulator.simulate_path(T, N)

def test_init():
    assert simulator.y0 == y0
    assert simulator.mu == mu
    assert simulator.sigma == sigma

def test_length():
    assert len(t) == N + 1
    assert len(y) == N + 1