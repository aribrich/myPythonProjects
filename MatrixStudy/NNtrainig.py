__author__ = 'Ari'


class NNtraining():

    def __init__(self, t, o, n, xi, wi, dw):
        wi = wi + dw
        dw = n*(t-o)*xi

    def updateWeight(self):
        wi = self.wi + self.dw
        dw = NNtraining(self.t,self.o,self.n,self.xi,self.wi)
