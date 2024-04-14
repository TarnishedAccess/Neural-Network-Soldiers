import tensorflow as tf
import numpy as np
import random

#model = tf.keras.layers.TFSMLayer("neural_network\dummy_model", call_endpoint="serving_default")
model = tf.keras.models.load_model("neural_network\dummy_model.keras")

for j in range(5):

    collision_data = [0] * 21

    data = []

    for i in range(7):
        data_portion = [0]*3
        choice = random.randint(0,2)
        data_portion[choice] = random.random()
        data.extend(data_portion)

    print(data)

    results = model.predict(np.array(data).reshape(1, -1))

    print(results)
    print("==============")