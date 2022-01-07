import pygame
import math
import numpy as np

'''adjusts distance and angle based on a binomial distribution with variance sigma'''


def uncertainty_add(distance, angle, sigma):
    mean = np.array([distance, angle])
    covariance = np.diag(sigma ** 2)
    distance, angle = np.random.multivariate_normal(mean, covariance)
    distance = max(distance, 0)
    angle = max(angle, 0)
    return [distance, angle]


class LaserSensor:
    '''constructor'''

    def __init__(self, Range, map: pygame.Surface, uncertainty=[.5, .01]) -> None:
        self.Range = Range
        # sensor measurement noise (distance, angle)
        self.sigma = np.array([uncertainty[0], uncertainty[1]])
        self.position = (0, 0)  # initial location

        self.map = map
        self.W, self.H = pygame.display.get_surface().get_size()
        self.sensedObstacles = []

    '''returns distance from our sensor to an object'''

    def distance(self, obstaclePosition):
        return math.dist(obstaclePosition, self.position)

    '''searches in a 360 degree range for any obstacles'''

    def sense_obstacles(self, WALL_COLOR):
        data = []
        x1, y1 = self.position[0], self.position[1]

        # for each angle around us
        for angle in np.linspace(0, 2*math.pi, 60, False):
            # calculate the end of the laser beam using our sensor's max range
            dx, dy = self.Range * math.cos(angle), self.Range * math.sin(angle)

            # for many iterations along this laser beam, search for objects
            for i in range(100):
                u = i / 100
                x = int(x1 + u * dx)
                y = int(y1 + u * dy)

                # check this point to see if there is an obstacle
                if 0 < x < self.W and 0 < y < self.H:
                    color = self.map.get_at((x, y))

                    if color == WALL_COLOR:
                        distance = self.distance((x, y))
                        output = uncertainty_add(distance, angle, self.sigma)

                        # output is now: [distance to object, angle to object, [current X, current Y]]
                        output.append(self.position)

                        # store in data
                        data.append(output)

                        # we can't see through walls
                        break

        return data