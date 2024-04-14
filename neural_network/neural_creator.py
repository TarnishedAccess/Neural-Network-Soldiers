import numpy as np
import tensorflow as tf
from tensorflow import keras


input_size = 21
hidden1_size = 30
hidden2_size = 10
output_size = 3

initializer = keras.initializers.RandomUniform(minval=0, maxval=1.0)

model = keras.Sequential([
    keras.layers.Dense(hidden1_size, activation='sigmoid', input_shape=(input_size,), kernel_initializer=initializer, bias_initializer=initializer),
    keras.layers.Dense(hidden2_size, activation='sigmoid', kernel_initializer=initializer, bias_initializer=initializer),
    keras.layers.Dense(output_size, activation=None, kernel_initializer=initializer, bias_initializer=initializer)
])

model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])


X_train = np.random.rand(1000, input_size)
Y_train = np.random.rand(1000, output_size)

model.fit(X_train, Y_train, epochs=10, batch_size=32)

model.save("neural_network/dummy_model.keras")
