__author__ = 'Ari'

import numpy as np

class Matrix:
    M = []
    inputs = []

    # def __init_s_(self,M):
    #     self.M = M

    def setMatrix(self, arr):
        M = np.matrix(arr)
        return M

    def getMatrix(self):
        return self.M

    def setInputs(self, input):
        self.inputs = input

    def getInputs(self):
        return self.inputs
