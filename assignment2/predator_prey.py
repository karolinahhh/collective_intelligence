from enum import Enum, auto
from typing import Optional
import random
import time
import pygame as pg
import numpy as np
import polars as pl
import pygame.display
from pygame.math import Vector2
from pygame.surface import Surface
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
from vi.simulation import HeadlessSimulation

@deserialize
@dataclass
class PPConfig(Config):
    delta_time: float = 0.9
    mass: int = 20


class Predator(Agent):
    config: PPConfig

    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING"):
        super().__init__(images=images, simulation=simulation)
        self.state = state

    def update(self):
        # check if eating rabbit in proximity ?
        prey = (
            self.in_proximity_accuracy()
            .without_distance() # removes distance (?)
            .filter_kind(Prey)
            .first()
         )

        if prey is not None:
            prey.kill()
            self.reproduce() # reproduce needs to be implemented better later

    def change_position(self):
          self.there_is_no_escape()

          if self.state == "WANDERING":
                
                prng = self.shared.prng_move
                should_change_angle = prng.random()
                deg = prng.uniform(-10,10)

                if 0.25 > should_change_angle:
                    self.move.rotate_ip(deg)

                self.pos += self.move * self.config.delta_time  # wandering


class Prey(Agent):
    config: PPConfig
    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING"):
        super().__init__(images=images, simulation=simulation)
        self.state = state

    def change_position(self):
          self.there_is_no_escape()

          if self.state == "WANDERING":
                
                prng = self.shared.prng_move
                should_change_angle = prng.random()
                deg = prng.uniform(-10,10)

                if 0.25 > should_change_angle:
                    self.move.rotate_ip(deg)

                self.pos += self.move * self.config.delta_time  # wandering

class PPLive(Simulation):
      config: PPConfig

(
    PPLive(
        PPConfig(
            image_rotation=True,
            movement_speed=3,
            radius=10,
            seed=1,
        )
    )

    .batch_spawn_agents(10, Predator, images=["images/medium-bird.png"])
    .batch_spawn_agents(50, Prey, images = ["images/red.png"])
    .run()
)
