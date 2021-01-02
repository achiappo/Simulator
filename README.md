# Robotised machines simulator

Driven by the curiosity to address a domestic problem, I started this project. 

### Problem description
Consider a lawn enclosed by a property perimeter and two robotised lawn mowers. The machines start mowing  
always from the same fixed positions, located along the lawn perimeter, which coincide with the recharging  
stations. At the start of every operation, each mowing unit disconnects from its station, takes a direction  
at random and proceeds in a straight line until it reaches the lawn's perimeter or bumps into its sister  
machine. After each collision, the unit backs slightly, rotates into a new, random direction and starts again,  
advancing straight. When low on battery, each unit will stop mowing, proceed until it finds the perimeter,  
and follow it back to the first available recharging station encountered.  
Operation cycles last for about 1 hour, during which the two units clearly cannot mow the entire lawn, but  
only a fraction thereof. This aspect results from the chaotic motion of the machines, implying that each unit  
might pass repeated times over the same patch of grass. 

### Objectives
The aim of this project is to build the infrastructure to simulate two mowers moving randomly over some user-defined area.  
Given a lawn and the random nature of the mowers' motion, using this tool it's possible to determine the average number of  
