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

    # def probability(self, threshold: float) -> bool:
    #     """Randomly retrieve True or False depending on the given probability
    #     The probability should be between 0 and 1.
    #     """
    #     return random.random() < threshold

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        neighbours_count = self.in_proximity_accuracy().count()
        #p = self.probability(0.01)
        p_leave = 0.1 / (1 + neighbours_count)
        p_join = 1 - p_leave
        randomx = random.random()

        if not self.on_site():
            self.check_site = False

        if self.state == "WANDERING":
            self.pos += self.move * self.config.delta_time  # wandering
            # self.check_site = False
            if self.on_site() and p_join > randomx and not self.check_site:
                self.state = "JOIN"
                self.config.counter1 = 0

        if self.state == "JOIN":
            self.config.counter1 += 1
            if self.config.counter1 > 50 and self.on_site():
                self.state = "STILL"
                self.config.counter1 = 0
            else:
                self.pos += self.move * self.config.delta_time

        if self.state == "STILL":
            if p_leave > randomx:
                self.state = "LEAVING"
                self.check_site = True
                self.config.counter = 0

        if self.state == "LEAVING":

            self.config.counter += 1
            print(self.config.counter)
            # self.continue_movement()
            if self.config.counter > 500:#:
                self.state = "WANDERING"
                self.config.counter = 0
            # else:
            #     self.pos += self.move * self.config.delta_time
                #self.check_site = False
        #print(not(False))


class AggregationLive(Simulation):
    config: AggregationConfig


(
    AggregationLive(
        AggregationConfig(
            image_rotation=True,
            movement_speed=3,
            radius=25,
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
