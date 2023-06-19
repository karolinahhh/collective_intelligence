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
    energy: int = 50
    eat_threshold: int = 50
    prey_worth: int = 10
    reproduction_threshold: int = 90
    reproduction_cost: int = 50
    death_threshold: int = 20
    energy_loss: float = 0.05
    reproduction_chance: float = 0.003
    image_rotation: bool = True
    movement_speed: int = 3
    radius: int = 15
    seed: int = 1


class Predator(Agent):
    config: PPConfig

    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING", energy=50, agent_type=0):
        super().__init__(images=images, simulation=simulation)
        self.state = state
        self.agent_type = agent_type
        self.energy = self.config.energy
        self.eat_threshold = self.config.eat_threshold
        self.prey_worth = self.config.prey_worth
        self.reproduction_threshold = self.config.reproduction_threshold
        self.reproduction_cost = self.config.reproduction_cost
        self.death_threshold = self.config.death_threshold
        self.energy_loss = self.config.energy_loss

    def update(self):
        # check if eating rabbit in proximity ?
        prey = (
            self.in_proximity_accuracy()
            .without_distance() # removes distance (?)
            .filter_kind(Prey)
            .first()
         )

        if prey is not None:
            prob_eat = random.random()
            if prob_eat < self.eat_threshold:
                prey.kill()
                self.energy += self.prey_worth
                if self.energy >= self.reproduction_threshold:
                    self.reproduce()
                    self.energy -= self.reproduction_cost

        if self.energy < self.death_threshold:
             self.kill()

        self.energy -= self.energy_loss

        agent_type= self.agent_type
        self.save_data("agent", agent_type)

    def change_position(self):
          self.there_is_no_escape()

          if self.state == "WANDERING":
                
                prng = self.shared.prng_move
                should_change_angle = prng.random()
                deg = prng.uniform(-30,30)

                if 0.2 > should_change_angle:
                    self.move.rotate_ip(deg)

                self.pos += self.move * self.config.delta_time  # wandering


class Prey(Agent):
    config: PPConfig
    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING", agent_type=1):
        super().__init__(images=images, simulation=simulation)
        self.state = state
        self.agent_type= agent_type
        self.reproduction_chance = self.config.reproduction_chance

    def update(self):
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

                if 0.2 > should_change_angle:
                    self.move.rotate_ip(deg)

                self.pos += self.move * self.config.delta_time  # wandering
    

class PPLive(Simulation):
      config: PPConfig

(
    PPLive(
        PPConfig(
            image_rotation=True,
            movement_speed=3,
            radius=15,
            seed=1,
        )
    )

    .batch_spawn_agents(5, Predator, images=["images/medium-bird.png"])
    .batch_spawn_agents(25, Prey, images = ["images/red.png"])
    .run()
    .snapshots
    .write_csv("predprey.csv")
)

