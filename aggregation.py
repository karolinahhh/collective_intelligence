from enum import Enum, auto
from typing import Optional
import random
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class AggregationConfig(Config):
    delta_time: float = 0.9
    mass: int = 20


class Cockroach(Agent):
    config: AggregationConfig

    def probability(self, threshold: float) -> bool:
        """Randomly retrieve True or False depending on the given probability
        The probability should be between 0 and 1.
        """
        return random.random() < threshold
    

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        neighbours_count = self.in_proximity_accuracy().count()
        p = self.probability(0.01)


        if neighbours_count > 1 and self.on_site():
            if p: 
                self.pos += self.move * self.config.delta_time
            else:
                self.freeze_movement()

        else:
            self.pos += self.move * self.config.delta_time


class AggregationLive(Simulation):
    config: AggregationConfig


(
    AggregationLive(
        AggregationConfig(
            image_rotation=True,
            movement_speed=3,
            radius=50,
            seed=1,
        )
    )
        # .spawn_obstacle("images/triangle@200px.png", 300,300)
        # .spawn_obstacle("images/blue_circle.png", 200, 500)
        #.spawn_obstacle("images/blue_circle.png", 500, 200)
        .spawn_site("images/light_blue_circle.png", 500, 200)
        # .spawn_obstacle("images/blue_circle.png", 400, 400)
        .batch_spawn_agents(50, Cockroach, images=["images/orange_dot.png"])
        
        .run()
)
