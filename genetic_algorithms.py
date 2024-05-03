import random
import numpy

def selection(character_list, num):
    score_list = [character.score for character in character_list]
    min_score = min(score_list)
    shifted_scores = [score - min_score + 1 for score in score_list]
    total_sum = sum(shifted_scores)
    probabilities = [x / total_sum for x in shifted_scores]
    choice = numpy.random.choice(character_list, size=num, replace=False, p=probabilities)
    return list(choice)

def crossing(network_1, network_2):
    child_1 = []
    child_2 = []
    for layer_index in range(len(network_1)):
        layer_1 = []
        layer_2 = []
        for neuron_index in range(len(network_1[layer_index])):
            neuron_1 = []
            neuron_2 = []
            for weight_index in range(len(network_1[layer_index][neuron_index])):
                choice = random.randint(0,1)
                if choice:
                    neuron_1.append(network_1[layer_index][neuron_index][weight_index])
                    neuron_2.append(network_2[layer_index][neuron_index][weight_index])
                else:
                    neuron_2.append(network_1[layer_index][neuron_index][weight_index])
                    neuron_1.append(network_2[layer_index][neuron_index][weight_index])
            layer_1.append(neuron_1)
            layer_2.append(neuron_2)
        child_1.append(layer_1)
        child_2.append(layer_2)
    return (child_1, child_2)

def mutate(network, lower_bound, upper_bound):
    mutations = random.randint(lower_bound, upper_bound)
    while mutations > 0:

        layer_index = random.randint(0, len(network)-1)
        neuron_index = random.randint(0, len(network[layer_index])-1)
        weight_index = random.randint(0, len(network[layer_index][neuron_index])-1)
        chosen_weight = network[layer_index][neuron_index][weight_index]
        print(network[layer_index][neuron_index][weight_index])
        mutated_weight = random.uniform(chosen_weight - chosen_weight/4, chosen_weight + chosen_weight/4)
        network[layer_index][neuron_index][weight_index] = mutated_weight
        mutations -= 1
