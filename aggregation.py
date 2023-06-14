from enum import Enum, auto
from typing import Optional
import random
import time
import pygame as pg
import polars as pl
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
        self.data = []

    def update(self):
        site = self.on_site()
        self.save_data("site", site)
        site_id = self.on_site_id()
        self.save_data("site_id", site_id)

    def change_position(self):
        self.there_is_no_escape()
        neighbours_count = self.in_proximity_accuracy().count()
        p_leave = 0.01 / (1 + neighbours_count)
        p_join = 1 - p_leave
        randomx = random.random()

        if not self.on_site():
            self.check_site = False

        if self.state == "WANDERING":
            self.pos += self.move * self.config.delta_time  # wandering
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
            if self.config.counter > 700:
                self.state = "WANDERING"
                self.config.counter = 0

class AggregationLive(Simulation):
    config: AggregationConfig

print(
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
        .spawn_site("images/light_blue_circle1.png", 200, 500)
        #.spawn_site("images/light_blue_circle.png", 500, 200)
        # .spawn_obstacle("images/blue_circle.png", 400, 400)
        .batch_spawn_agents(50, Cockroach, images=["images/orange_dot.png"])
        
        .run()
        .snapshots
        # .filter(pl.col("id") == 0)\
        .write_csv("aggregation.csv")
)
