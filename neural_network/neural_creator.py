import numpy as np
import tensorflow as tf

# Define the number of neurons in each layer
input_size = 21
hidden1_size = 30
hidden2_size = 10
output_size = 3

# Custom random initializer
initializer = tf.keras.initializers.RandomUniform(minval=0, maxval=1.0)

# Create the model with random weights
model = tf.keras.Sequential([
    tf.keras.layers.Dense(hidden1_size, activation='sigmoid', input_shape=(input_size,), kernel_initializer=initializer, bias_initializer=initializer),
    tf.keras.layers.Dense(hidden2_size, activation='sigmoid', kernel_initializer=initializer, bias_initializer=initializer),
    tf.keras.layers.Dense(output_size, activation=None, kernel_initializer=initializer, bias_initializer=initializer)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

# Generate random training data (replace with actual data)
X_train = np.random.rand(1000, input_size)
Y_train = np.random.rand(1000, output_size)

# Train the model (not really necessary for your use case)
model.fit(X_train, Y_train, epochs=10, batch_size=32)

# Save the model
model.save("neural_network/dummy_model")
