from math import cos, sin
import pygame
import Robot
from typing import Tuple, List
from LaserSensor import LaserSensor
from detection import LineDetector, detect_lines

'''returns true if this key is pressed or if exit is used'''
def check_quit(exit_key = pygame.K_RETURN) -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        if event.type == pygame.KEYDOWN and event.key == exit_key:
            return True
    return False

'''allows user to draw a floor plan. returns a list of coordinate pairs for the walls'''
def draw_board(Map: pygame.Surface, exit_key = pygame.K_RETURN, hint_color=(0, 255, 0), wall_color=(0, 0, 0), width=3) -> List[Tuple[Tuple[int, int]]]:
    pygame.init()

    walls = []

    running = True
    drawing = None
    previous_frame = None
    new_drawing = None
    while running:
        pygame.time.delay(5)
        running = not check_quit(exit_key=exit_key)
            
        focused = pygame.mouse.get_focused()
        left_click = pygame.mouse.get_pressed()[0]
        right_click = pygame.mouse.get_pressed()[2]
        position = tuple(pygame.mouse.get_pos())

        if focused:
            # on the initial left click, save the first point as drawing
            if drawing:
                new_drawing = previous_frame.copy()

                # we can use right click to cancel this line
                if right_click:
                    drawing = None
                    Map.blit(previous_frame, (0, 0))

                # drawing dotted lines while user is still dragging mouse
                elif left_click:
                    pygame.draw.line(new_drawing, hint_color, drawing, position, width=width)
                    Map.blit(new_drawing, (0, 0))

                # when user lets go of left click, draw our actual line
                else:
                    pygame.draw.line(new_drawing, wall_color, drawing, position, width=width)
                    Map.blit(new_drawing, (0, 0))
                    drawing = None
                    walls.append((drawing, position))

            elif left_click:
                drawing = position
                previous_frame = Map.copy()
        
        pygame.display.update()

    return walls

'''pauses the program to allow user to place down the robot. returns original surface and location of the robot'''
def place_robot(Map: pygame.Surface, exit_key=pygame.K_RETURN, robot_color=(0, 0, 255), radius=3) -> Tuple[Tuple[int, int], pygame.Surface]:
    print("placing robot")
    pygame.init()
    blank_map = Map.copy() # store a copy of the map without a robot
    running = True
    origin = None
    position = None
    while running:
        pygame.time.delay(5)
        running = not check_quit(exit_key=exit_key)
        if not running: break

        focused = pygame.mouse.get_focused()
        pressed = pygame.mouse.get_pressed()[0]
        position = pygame.mouse.get_pos()

        if focused and pressed:
            origin = position
            new_map = blank_map.copy()
            pygame.draw.circle(new_map, color=robot_color, center=origin, radius=radius)
            Map.blit(new_map, (0, 0))

        pygame.display.update()
    
    return tuple(origin), blank_map

def mainloop(Map: pygame.Surface, original_map: pygame.Surface, robot_location, exit_key=pygame.K_RETURN, robot_color=(0, 0, 255), wall_color=(0, 0, 0)):
    rob = Robot.Robot(robot_location)
    ls = LaserSensor(200, original_map.copy()) 
    ld = LineDetector()

    ld.EPSILON = 4
    ld.DELTA = 50
    ld.P_MIN = 5
    ld.L_MIN = 50


    running = True
    sensor_points, sensor_lines = [], []
    while running:
        pygame.time.delay(5)

        sensor_on = False

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == exit_key:
                    running = False
                
                # key handling
                if event.key == pygame.K_SPACE:
                    sensor_on = True

        new_map = original_map.copy() # for all drawings that only last the current frame

        vector = Robot.Robot.get_moves()
        rob.move(vector)

        ls.position = rob.pos

        if sensor_on:
            sensordata = ls.sense_obstacles(wall_color)
            new_points = data_to_points(sensordata)
            line_data = detect_lines(new_points, rob.pos, ld, overlap=1)[0]
            new_lines = data_to_lines(line_data)

            sensor_lines += new_lines
            sensor_points += new_points
            display_sensor_data(original_map, new_points)
            display_lines(original_map, new_lines)

        pygame.draw.circle(new_map, robot_color, rob.pos, 7)
        Map.blit(new_map, (0, 0))

        pygame.display.update()


def display_sensor_data(original_map: pygame.Surface, points, radius=3, color=pygame.Color("#b7adcf")) -> None:
    for p in points:
        pygame.draw.circle(original_map, color, p, radius)


def display_lines(original_map: pygame.Surface, lines, thickness=4, color=pygame.Color("#a9f8fb")) -> None:
    for start, end in lines:
        pygame.draw.line(original_map, color, start, end, thickness)

def data_to_points(data):
    points = []
    for d, theta, loc in data:
        x0, y0 = loc
        x = x0 + d * cos(theta)
        y = y0 + d * sin(theta)
        points.append((x, y))
    return points

def data_to_lines(data):
    return [d[4] for d in data]

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("drawing floor plans")
    Map = pygame.display.set_mode((1080, 720))

    # colors
    BACKGROUND = pygame.Color("#E8E9F3")
    HINT_COLOR = pygame.Color("#a6a6a8")
    WALL_COLOR = pygame.Color("#272635")
    ROBOT_COLOR = pygame.Color("#B1E5F2")

    Map.fill(BACKGROUND)
    walls = draw_board(Map, hint_color=HINT_COLOR, wall_color=WALL_COLOR, width=10)
    robot_location, blank_map = place_robot(Map, robot_color=ROBOT_COLOR, radius=7)
    mainloop(Map, blank_map, robot_location, robot_color=ROBOT_COLOR, wall_color=WALL_COLOR)
