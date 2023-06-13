from enum import Enum, auto
from typing import Optional
import random
import time
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
        p_leave = self.probability(0.01) / (1 + neighbours_count)
        p_join = 1 - p_leave
        timer = 1 # has to be integer
        start_time = time.time()
        randomx = random.random()


        # if self.on_site(): #
        #     if p_join > randomx: # still
        #         self.freeze_movement()
        #
        #     else: # leaving the site
        #         if (time.time() - start_time) >= timer:
        #             self.continue_movement()
        # else:
        #     # if p_join > randomx: # join an aggregate
        #     #     if (time.time() - start_time) >= timer:
        #     #         self.pos += self.move * self.config.delta_time
        #     # else: # wandering
        #     self.pos += self.move * self.config.delta_time



        if self.on_site(): # prob of leaving is low when it is on the site and the group is bigger
            if p_join > randomx: # prob of joining is high when it is not on the site and neighbors are around
                self.continue_movement() # but does stop on the edge
            if p_leave > randomx:
                self.pos += self.move * self.config.delta_time
            else:
                if time.time() - start_time >= timer:
                    self.freeze_movement() #still
        else:
            self.pos += self.move * self.config.delta_time # wandering



class AggregationLive(Simulation):
    config: AggregationConfig


(
    AggregationLive(
        AggregationConfig(
            image_rotation=True,
            movement_speed=5,
            radius=50,
            seed=1,
        )
    )
        # .spawn_obstacle("images/triangle@200px.png", 300,300)
        # .spawn_obstacle("images/blue_circle.png", 200, 500)
        #.spawn_obstacle("images/blue_circle.png", 500, 200)
        .spawn_site("images/light_blue_circle.png", 500, 200)
        #.spawn_site("images/light_blue_circle.png", 500, 200)
        # .spawn_obstacle("images/blue_circle.png", 400, 400)
        .batch_spawn_agents(50, Cockroach, images=["images/orange_dot.png"])
        
        .run()
)
