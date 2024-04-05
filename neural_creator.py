import tensorflow as tf

def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(21,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(3, activation='sigmoid')
    ])
    return model

model = create_model()

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

import numpy as np
X_train = np.random.rand(1000, 21)
y_train = np.random.rand(1000, 3)

model.fit(X_train, y_train, epochs=10, batch_size=32)
model.save('dummy_model')
