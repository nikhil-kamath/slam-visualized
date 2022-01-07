import pygame

from detection import LineDetector, detect_lines
from draw_board import (data_to_lines, data_to_points, display_lines,
                        display_sensor_data, draw_board, place_robot)
from LaserSensor import LaserSensor
from Robot import Robot


def main() -> None:
    pygame.init()
    pygame.display.set_caption("slam visualized")
    Map = pygame.display.set_mode((1080, 720))
    exit_key = pygame.K_RETURN

    # colors
    BACKGROUND = pygame.Color("#E8E9F3")
    HINT_COLOR = pygame.Color("#a6a6a8")
    WALL_COLOR = pygame.Color("#272635")
    ROBOT_COLOR = pygame.Color("#B1E5F2")

    Map.fill(BACKGROUND)
    walls = draw_board(Map, hint_color=HINT_COLOR, wall_color=WALL_COLOR, width=10)
    robot_location, blank_map = place_robot(Map, robot_color=ROBOT_COLOR, radius=7)
    
    rob = Robot(robot_location)
    ls = LaserSensor(200, blank_map.copy())
    ld = LineDetector()

    ld.EPSILON = 4
    ld.DELTA = 50
    ld.P_MIN = 5
    ld.L_MIN = 50
    
    sensor_points, sensor_lines = [], []

    running = True
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

        new_map = blank_map.copy()  # for all drawings that only last the current frame

        vector = Robot.get_moves()
        rob.move(vector)

        ls.position = rob.pos

        if sensor_on:
            sensordata = ls.sense_obstacles(WALL_COLOR)
            new_points = data_to_points(sensordata)
            line_data = detect_lines(new_points, rob.pos, ld, overlap=1)[0]
            new_lines = data_to_lines(line_data)

            sensor_lines += new_lines
            sensor_points += new_points
            display_sensor_data(blank_map, new_points)
            display_lines(blank_map, new_lines)

        pygame.draw.circle(new_map, ROBOT_COLOR, rob.pos, 7)
        Map.blit(new_map, (0, 0))

        pygame.display.update()


if __name__ == "__main__":
    main()
