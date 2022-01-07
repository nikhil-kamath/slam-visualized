import pygame
from draw_board import check_quit
from typing import Tuple

'''robot handles movement and stores a location. it also has the scanning functions'''
class Robot:
    def __init__(self, initial_position: Tuple[int, int]) -> None:
        self.pos = tuple(initial_position)
    
    def move(self, vector: Tuple[int, int]) -> None:
        self.pos = tuple(a + b for a, b in zip(self.pos, vector))

    '''handles one frame of movement and returns the corresponding movement vector'''
    def get_moves(vel: int=1) -> Tuple[int, int]:
        pygame.init()
        keys = pygame.key.get_pressed()
        directions = {pygame.K_w: [0, -vel],
                    pygame.K_a: [-vel, 0],
                    pygame.K_s: [0, vel],
                    pygame.K_d: [vel, 0]}

        return (sum(a) for a in zip(*[directions[d] for d in directions if keys[d]], [0, 0]))
            
