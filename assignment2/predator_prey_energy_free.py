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
    reproduction_threshold: int = 0.2
    reproduction_chance: float = 0.0015
    counter: int = 500


class Predator(Agent):
    config: PPConfig

    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING", agent_type=0):
        super().__init__(images=images, simulation=simulation)
        self.state = state
        self.agent_type = agent_type
        self.counter = self.config.counter
        self.reproduction_threshold = self.config.reproduction_threshold

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
            self.counter += 220
            should_reproduce = random.random()
            if self.counter > 100:
                self.freeze_movement()
                if should_reproduce < self.reproduction_threshold:
                    self.reproduce() # reproduce needs to be implemented better later
                    self.counter -= 100

        if self.counter == 10:
            self.kill()

        self.counter -= 1

        agent_type = self.agent_type
        self.save_data("agent", agent_type)

    def change_position(self):
          self.there_is_no_escape()

          if self.state == "WANDERING":
                
                prng = self.shared.prng_move
                should_change_angle = prng.random()
                deg = prng.uniform(-30,30)

                if 0.5 > should_change_angle:
                    self.move.rotate_ip(deg)

                self.pos += self.move * self.config.delta_time  # wandering


class Prey(Agent):
    config: PPConfig

    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING", agent_type=1):
        super().__init__(images=images, simulation=simulation)
        self.state = state
        self.agent_type = agent_type
        self.reproduction_chance = self.config.reproduction_chance


    def update(self):
     # Adjust the reproduction chance as desired
        should_reproduce = random.random()
        if should_reproduce < self.reproduction_chance:
            self.reproduce()  # reproduce needs to be implemented better later

        agent_type = self.agent_type
        self.save_data("agent", agent_type)

    def change_position(self):
          self.there_is_no_escape()

          if self.state == "WANDERING":
                
                prng = self.shared.prng_move
                should_change_angle = prng.random()
                deg = prng.uniform(-30,30)

                if 0.5 > should_change_angle:
                    self.move.rotate_ip(deg)

                self.pos += self.move * self.config.delta_time  # wandering
    

class PPLive(Simulation):
      config: PPConfig

(
    PPLive(
        PPConfig(
            image_rotation=True,
            movement_speed=1,
            radius=10,
            # seed=1,
        )
    )

    .batch_spawn_agents(20, Predator, images=["images/medium-bird.png"])
    .batch_spawn_agents(45, Prey, images=["images/red.png"])
    .run()
    .snapshots
    .write_csv("predprey_no_energy.csv")
)