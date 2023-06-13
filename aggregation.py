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
    time = 50




class Cockroach(Agent):
    config: AggregationConfig

    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING", check_site=False):
        super().__init__(images=images, simulation=simulation)
        self.state = state
        self.check_site = check_site


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
        # p_leave = self.probability(0.01) / (1 + neighbours_count)
        p_leave = 0.9
        p_join = 1 - p_leave
        timer = 10 # has to be integer
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


        if self.state == "WANDERING":
            self.pos += self.move * self.config.delta_time # wandering
            if self.on_site() and p_join > randomx:
                self.state = "JOIN"
                self.config.counter = 0
        if self.state == "JOIN":
            self.config.counter += 1
            if self.config.counter > 50 and self.on_site():
                self.state = "STILL"
                self.config.counter = 0
            else:
                self.pos += self.move * self.config.delta_time

                    # if p_leave > randomx:
        if self.state == "STILL":
            self.freeze_movement()
            if p_leave > randomx:
                self.state = "LEAVING"
                self.config.counter = 0

        if self.state == "LEAVING":
            self.config.counter += 1
            if self.config.counter > 50 and self.on_site():
                self.state = "WANDERING"
                self.config.counter = 0


















        # if self.state == "LEAVE":
        #     # prob of leaving is low when it is on the site and the group is bigger
        #     if p_join: # prob of joining is high when it is not on the site and neighbors are around
        #         self.continue_movement() # but does stop on the edge
        #     if p_leave:
        #         self.pos += self.move * self.config.delta_time
        #     else:
        #         if time.time() - start_time >= timer:
        #             self.freeze_movement() #still
        # if not self.on_site():
        #
        #     if p_join:  # prob of joining is high when it is not on the site and neighbors are around
        #         self.continue_movement()  # but does stop on the edge
        #     if p_leave:
        #         self.pos += self.move * self.config.delta_time
        #     else:
        #         if time.time() - start_time >= timer:
        #             self.freeze_movement()  # still
        # if not self.on_site():



class AggregationLive(Simulation):
    config: AggregationConfig


(
    AggregationLive(
        AggregationConfig(
            image_rotation=True,
            movement_speed=1,
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
