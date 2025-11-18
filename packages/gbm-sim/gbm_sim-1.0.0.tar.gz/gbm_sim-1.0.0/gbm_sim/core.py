from signal import Sigmasks


class BaseGBM:
    def __init__(self,y0, mu, sigma):
        self.y0 = y0
        self.mu = mu
        self.sigma = sigma
