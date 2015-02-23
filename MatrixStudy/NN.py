__author__ = 'Ari'

import numpy as np
import random
import MatrixClass as MC
import math

inputs = []

def main():
    print "\n"
    MC_ = MC.Matrix()
    MC_.setInputs([1,2,3])
    inputs = MC_.getInputs()

    L0_len = len(inputs)
    L1 = [1,2,3,4,5]
    L1_len = len(L1)
    L2_len = L1_len
    # init1 = np.random.uniform(-1,1).reshape(L0_len,L1_len)
    initWeights_L1 = [[random.uniform(-1,1) for x in range(L0_len)] for y in range(L1_len)]
    initWeights_L2 = [[random.uniform(-1,1) for x in range(L1_len)] for y in range(L2_len)]
    bias = [random.random() for x in range(L1_len)]
    nodeSum = sumWeights(initWeights_L1,inputs,bias)
    newNode = stepFuction(nodeSum,-1)
    print newNode

def sumWeights(W, p, b):
    Msum = [0 for i in range(len(W))]
    r = [0 for i in range(len(p))]
    for row in range(len(W)):
        for col in range(len(W[row])):
            r[col] = W[row][col]*p[col]
        Msum[row] = sum(r)

    newP = [0 for i in range(len(b))]
    for i in range(len(Msum)):
        newP[i] = Msum[i] + b[i]

    return newP

def stepFuction(arr, lowerlimit):
    out = [0 for i in range(len(arr))]
    for i in range(len(out)):
        if lowerlimit == -1:
            if arr[i] > 0:
                out[i] = 1
            else: out[i] = -1
        if lowerlimit == 0:
            if arr[i] > 0:
                out[i] = 1
            else: out[i] = 0
    return out

def sigmoidUnitFunction(arr):
    sig = [0 for i in range(len(arr))]
    for i in range(len(sig)):
        sig[i] = 1/(1+math.exp(arr[i]))
    return sig

def updateWeight(t,o,nu,wi,xi):
    wi = wi + nu*(t-o)*xi
    delw = nu*(t-o)*xi #Delta rule of gradient descent


if __name__ == '__main__':
    main()