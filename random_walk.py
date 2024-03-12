import json
import random

"""
-1: rock
0: floor
1: object
2: wall
"""

#Parameters
width = 40
height = 40
steps = 2500

#We initialize the map with walls all around
map = [[-1 for _ in range(width)] for _ in range(height)]
start_position = [random.randint(height // 7, height // 1.2), random.randint(width // 7, width // 1.2)]
position = start_position #Useless line but I cba removing it

#We make a 'walker', start him off at the starting position and make him randomly walk. Each tile he walks on is turned into a floor tile.
for i in range(steps):
    map[position[0]][position[1]] = 0
    direction = random.randint(1,4)
    #We ensure that he isn't out of bounds. -2 to make sure the outermost layer is always a wall, mostly aesthetic purposes.
    if direction == 1 and position[0] < height - 3:
        position[0] += 1
    elif direction == 2 and position[1] < width - 3:
        position[1] += 1
    elif direction == 3 and position[0] > 2:
        position[0] -= 1
    elif direction == 4 and position[1] > 2:
        position[1] -= 1

#We change it to use rocks and inner walls
for i in range(1, len(map)-1):
    for j in range(1, len(map[i])-1):
        if map[i][j] == -1:
            if (map[i][j-1] == 0) or (map[i][j+1] == 0) or (map[i+1][j] == 0) or (map[i-1][j] == 0) or (map[i-1][j-1] == 0) or (map[i+1][j+1] == 0) or (map[i-1][j+1] == 0) or (map[i+1][j-1] == 0):
                map[i][j] = 2
                
#Save the result to a json
with open("walker_map.json", 'w') as f:
    json.dump(map, f)
