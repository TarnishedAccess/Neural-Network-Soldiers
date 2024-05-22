# Neural Network Soldiers
 
-Run one of the generation algorithms to generate a map  
-Run game  
  
## OPTIONAL:
[ ] More/Better generation algorithms  
[ ] interface for terrain gen  
[X] UI/info on soldiers during runtime  
[X] darken walls  
[X] more obstacle/rock sprites  

## TODO:
[X] add rotation  
[X] add FOV  
[X] add directional line  
[X] add raycasting lines  
[X] check raycasting collision  			
[X] obstacle collision detection  
[X] enemy collision detection  
[X] friendly collision detection  
[X] give characters team specific sprites  
[X] calculate collision distance instead of 0s and 1s  
[X] make shooting function  
[X] make neural network  
[X] implement neural network to game (let neural network control actions)  
[X] optimize model 	                                                    
[X] implement score system  
[X] implement selection function  
[X] implement crossing function  <= YOU ARE HERE  
[X] implement mutation function  
[X] finishing touches  

#===TRAINING===  
[X] add score to characters  
[X] track kills  
[X] add reward/penalty system  <= YOU ARE HERE  
	enemy kill:				+30  
	friendly kill:				-50  
	bullet wasted:				-3  
	time survived:				+1/s  
	staring at wall:			-3/s  
	camping penalty:			-5/s  
	dying penalty:				-30 (?)  
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

22/04/2024
Neural Net connected to sprites
no Learning
random walks


29/04/2024
Fitness pondérés survie + kill_enemy - kill_friend + distance
Sélection best fitness

Last check:
Excellent
