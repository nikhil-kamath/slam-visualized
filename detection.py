import numpy as np
from scipy.optimize import curve_fit
import math

'''class with methods to detect seeds and grow them according to parameters of the class'''
class LineDetector:
    def __init__(self):
        self.EPSILON = 25  # maximum distance from any point to the fit line
        self.DELTA = 200  # maximum distance from any point to its predicted location
        self.SEGMENT_LENGTH = 5  # number of points in seed segment
        self.P_MIN = 5  # minimum number of points in extracted line segment
        self.L_MIN = 200  # minimum length of a detected line segment
        # if seed detection has a different epsilon as the growing
        self.SEED_EPSILON = self.EPSILON

    '''Returns a valid seed segment given initialization parameters. 
    Requires that points are ordered counterclockwise around origin.'''

    def Detect(self, points, origin, start_index=0):
        N_P = len(points)  # number of points
        for i in range(start_index, 1 + N_P - self.P_MIN):
            flag = True
            j = i + self.SEGMENT_LENGTH
            params = self.fit(points[i:j])

            for k in points[i:j]:
                prediction = self.predict(params, origin, k)

                # break cases
                delta_failure = math.dist(k, prediction) > self.DELTA
                epsilon_failure = self.dist_point2line(
                    k, params) > self.SEED_EPSILON
                if delta_failure or epsilon_failure:
                    flag = False
                    break

            if flag:
                return [params, points[i:j], (i, j), points, self.get_points(params)]
        return None

    def to_optimize(self, x, a, b, c):
        return (- (a * x + c) / b)

    '''using scipy curve_fit method to find lines of best fit'''

    def fit(self, points):
        return curve_fit(self.to_optimize, [p[0] for p in points], [p[1] for p in points])[0]

    '''uses line parameters, origin point, and original point to find the predicted location of a point'''

    def predict(self, params, origin, point):
        return self.intersect(params, self.draw_line(origin, point))

    '''calculates intersection of lines with parameters param1 and param2'''

    def intersect(self, params1, params2):
        a, b, c = params1
        j, k, l = params2

        x = (c * k - b * l) / (b * j - a * k)
        y = (a * l - c * j) / (b * j - a * k)
        return x, y

    '''finds the parameters of a line going through points p1 and p2'''

    def draw_line(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        a = y1-y2
        b = x2-x1
        c = (x1-x2)*y1 + (y2-y1)*x1
        return a, b, c

    def dist_point2line(self, p, params):
        a, b, c = params
        x, y = p
        numerator = abs(a*x+b*y+c)
        denominator = math.sqrt(a**2 + b**2)
        return numerator / denominator

    def get_points(self, params):
        x0, x1 = 10, 1000
        return (x0, self.to_optimize(x0, *params)), (x1, self.to_optimize(x0, *params))

    '''grows line segment forwards and backwards until it reaches a point greater than epsilon away'''

    def Grow(self, seed, points):
        _, seed_points, indices, _, _ = seed
        N_P = len(points)
        line = self.fit(seed_points)
        i, j = indices
        L, P = 0, 0
        FRONT, BACK = j, i

        '''maybe make it so it doesn't do one before the other and does them at the same time instead.
         otherwise the line overadapts to the front side, then when it goes backwards it doesn't connect to otherwise pretty close points'''
        while FRONT < N_P and self.dist_point2line(points[FRONT], line) < self.EPSILON:
            line = self.fit(points[BACK:FRONT])
            FRONT += 1
        # FRONT -= 1

        while BACK >= 0 and self.dist_point2line(points[BACK], line) < self.EPSILON:
            line = self.fit(points[BACK:FRONT])
            BACK -= 1
        BACK += 1

        P_BACK = self.orthoproject(points[BACK], line)
        P_FRONT = self.orthoproject(points[FRONT-1], line)

        L = math.dist(P_BACK, P_FRONT)
        P = FRONT - BACK

        if L >= self.L_MIN and P >= self.P_MIN:
            return [line, points[BACK: FRONT], (BACK, FRONT), points, (P_BACK, P_FRONT)]

    '''finds closest point on line params to point p'''

    def orthoproject(self, p, params):
        a, b, c = params
        x, y = p
        a2 = -b
        b2 = a
        c2 = -a * y + b * x
        return self.intersect(params, (a2, b2, c2))


'''helper method that returns multiple valid seeds from a set of points. seeds do not overlap'''


def find_seeds(points, origin):
    seeds = []
    ssd = LineDetector()
    start_index = 0
    while start_index < len(points):
        seed = ssd.Detect(points, origin, start_index=start_index)

        # keep finding seeds until our method returns None
        if not seed:
            break

        seed_start, seed_end = seed[2]
        start_index = seed_end

        seeds.append(seed)

    return seeds


'''detects all lines by finding a seed, growing it, then finding the next one. does not use findSeeds method'''


def detect_lines(points, origin, ssd: LineDetector, overlap=0):
    lines = []
    seeds = []
    start_index = 0
    print(origin)
    while start_index < len(points):
        seed = ssd.Detect(points, origin, start_index=start_index)

        # we are finished if there isn't a seed remaining
        if not seed:
            break
        seeds.append(seed)

        line = ssd.Grow(seed, points)

        # if this seed can't grow into a line, try again with a new seed from the next point
        if not line:
            start_index = seed[2][0] + 1
            continue

        line_equation, line_points, indices, _, helper_points = line
        line_start, start_index = indices
        start_index -= overlap
        lines.append(line)

    return lines, seeds
