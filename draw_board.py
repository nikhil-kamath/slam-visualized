from math import cos, sin
import pygame
from typing import Tuple, List

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
