import numpy as np
import random

#outputs = 3
#inputs = 21

#hidden?
#1 layer with 14

#activation: sigmoid, relu

example_input = [0, 0, 0.2999999999999997, 0, 0, 0.40000000000000024, 0, 0, 0.900000000000001, 0, 0, 0.8999999999999988, 0, 0, 0.6499999999999988, 0, 0, 0.44999999999999873, 0, 0, 0.40000000000000113]

class NeuralNetwork():
    def __init__(self, inputs, hidden, outputs):

        #Adding a multiplier here to make sure weights are on the lower side as otherwise its always going to tend to 1 since we're using sigmoid
        #Or maybe my implementation is dogwater that's a possibility
        self.multiplier = random.uniform(0, 0.3)
        self.W1 = np.random.rand(hidden, inputs) * self.multiplier
        self.B1 = np.random.rand(hidden, 1) * self.multiplier
        self.W2 = np.random.rand(outputs, hidden) * self.multiplier
        self.B2 = np.random.rand(outputs, 1) * self.multiplier

    def print_data(self):
        print(f"multiplier: {self.multiplier}")
        print(f"W1: {self.W1}")
        print(f"B1: {self.B1}")
        print(f"W2: {self.W2}")
        print(f"B2: {self.B2}")

    def ReLU(self, Z):
        return np.maximum(0, Z)

    def sigmoid(self, Z):
        return 1 / (1 + np.exp(-Z))

    def predict(self, X):
        Z1 = np.dot(self.W1, X.reshape(-1, 1)) + self.B1
        A1 = self.sigmoid(Z1)
        Z2 = np.dot(self.W2, A1) + self.B2
        A2 = self.ReLU(Z2) 
        return A2
