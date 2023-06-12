from enum import Enum, auto
#from random import random
from typing import Optional
import random
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize

@deserialize
@dataclass
class FlockingConfig(Config):
    delta_time: float = 0.7
    mass: int = 20
class Bird(Agent):
    config: FlockingConfig

    def get_alignment_weight(self):
        return self.config.alignment_weight
    def probability(self, threshold: float) -> bool:
        """Randomly retrieve True or False depending on the given probability
        The probability should be between 0 and 1.
        """
        return random.random() < threshold

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        neighbours_count = self.in_proximity_accuracy().count()
        p = self.probability(0.05)
        if neighbours_count > 1:
            if p:
                self.pos += self.move * self.config.delta_time
        else:
            self.pos += self.move * self.config.delta_time

class FlockingLive(Simulation):
    config: FlockingConfig

(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    #.spawn_obstacle("images/triangle@200px.png", 300,300)
    # .spawn_obstacle("images/blue_circle.png", 200, 500)
    # .spawn_obstacle("images/blue_circle.png", 500, 200)
    .spawn_obstacle("images/blue_circle.png", 400, 400)
    .batch_spawn_agents(50, Bird, images=["images/orange_dot.png"])
    .run()
)
