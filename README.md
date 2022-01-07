# slam-visualized
Create your own 2d floorplan and drop a robot in. Move it around and use its Lidar scanner to help it map its unknown environment. *yes i know it currently uses the position of the robot in calculations, which is completely counterintuitive for SLAM. currently it maps its surrounding walls using line feature detection, but i will soon implement landmark-based localization.*

# how to use
The button to end each step is, by default, the **RETURN** key. 

Step 1: Drawing lines. This should be self-explanatory with the UI

Step 2: Placing the robot: Also self-explanatory

Step 3: Detecting lines. Press **SPACE** to run 1 cycle of the Lidar scanner. The scanner returns a bunch of points and extracts line features out of them.
