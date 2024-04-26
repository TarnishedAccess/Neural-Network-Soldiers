import numpy as np
import random
import json
from datetime import datetime
import os

class NeuralNetwork():
    def __init__(self, inputs, hidden, hidden2, outputs):

        #Adding a multiplier here to make sure weights are on the lower side as otherwise its always going to tend to 1 since we're using sigmoid
        #Or maybe my implementation is dogwater that's a possibility
        self.multiplier = random.uniform(0, 0.3)
        self.W1 = np.random.rand(hidden, inputs) * self.multiplier
        self.B1 = np.random.rand(hidden, 1) * self.multiplier
        self.W2 = np.random.rand(hidden2, hidden) * self.multiplier
        self.B2 = np.random.rand(hidden2, 1) * self.multiplier
        self.W3 = np.random.rand(outputs, hidden2) * self.multiplier
        self.B3 = np.random.rand(outputs, 1) * self.multiplier

    def print_data(self):
        print(f"multiplier: {self.multiplier}")
        print(f"W1: {self.W1}")
        print(f"B1: {self.B1}")
        print(f"W2: {self.W2}")
        print(f"B2: {self.B2}")
        print(f"W3: {self.W3}")
        print(f"B3: {self.B3}")

    def ReLU(self, Z):
        return np.maximum(0, Z)

    def sigmoid(self, Z):
        return 1 / (1 + np.exp(-Z))

    def predict(self, X):
        Z1 = np.dot(self.W1, X.reshape(-1, 1)) + self.B1
        A1 = self.sigmoid(Z1)
        Z2 = np.dot(self.W2, A1) + self.B2
        A2 = self.ReLU(Z2) 
        Z3 = np.dot(self.W3, A2) + self.B3
        A3 = self.ReLU(Z3)
        return A3

    def save(self, filename):
        arrays = [self.W1, self.B1, self.W2, self.B2, self.W3, self.B3]
        list_conversion = [array.tolist() for array in arrays]
        datetime_now = datetime.now()
        datetime_now = datetime_now.strftime("%Y%m%d%H%M%S")
        save_path = os.path.join("neural_network", "network_storage", filename)
        with open(f"{save_path}_{datetime_now}.json", "w") as network_file:
            json.dump(list_conversion, network_file)
