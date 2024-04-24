# Neural Network Soldiers
 
-Run one of the generation algorithms to generate a map  
-Run game  
  
## OPTIONAL:
-More/Better generation algorithms  
-interface for terrain gen  
-UI/info on soldiers during runtime  
-darken walls  
-more obstacle/rock sprites  

## TODO:
-add rotation  
-add FOV  
-add directional line  
-add raycasting lines  
-check raycasting collision  			
	-obstacle collision detection  
	-enemy collision detection  
	-friendly collision detection  
-give characters team specific sprites  
-calculate collision distance instead of 0s and 1s  
-make shooting function  
-make neural network  
-implement neural network to game (let neural network control actions)  
-optimize model 	                                                    
-implement score system  <= YOU ARE HERE  
-implement selection function  
-implement crossing function  
-implement mutation function  
-finishing touches  

#===TRAINING===  
add score to characters  
track kills  
add reward/penalty system  
	enemy kill:				+30  
	friendly kill:				-50  
	bullet wasted:				-3  
	time survived:				+1/s  
	staring at wall:			-3/s  
	keep enemy in outlying vision:		-4/s  
	keep enemy in center vision:		+6/s  
	keep enemy in center vision in cover:	+12/s  
	keep friendlies in outlying vision:	+4/s  
	multiple enemies in vision:		-5/s  
	camping penalty:			-5/s  
Note: Values are experimental and prone to change  

## PROJECT TRACKING:

24/03/2024
Excellent
Map rendue
Sprite en mouvement 


15/04/2024
RayCasting OK
Neural Net OK
Collision Detection
Firing

22/05/2024
Neural Net connected to sprites
no Learning
random walks
