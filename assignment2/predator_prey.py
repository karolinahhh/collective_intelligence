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

#introduce flocking (flocking/not)
#stopping after full (full/nofull)

@deserialize
@dataclass
class PPConfig(Config):
    delta_time: float = 1
    mass: int = 20
    energy: int = 60 #50
    eat_threshold: int = 0.3
    prey_worth: int = 25 #was 10
    reproduction_threshold: int = 90
    reproduction_cost: int = 20
    death_threshold: int = 30 #20
    full_threshold: int = 70
    energy_loss: float = 0.08
    reproduction_chance: float = 0.0018#0.003
    # image_rotation: bool = True
    # movement_speed: int = 3
    #radius: int = 10
    # seed: int = 1
    # counter: int = 120 #check counter later
    prob_reproduce: float = 0.5
    alignment_weight: float = 10
    cohesion_weight: float = 25
    separation_weight: float = 25
    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)

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
        # self.counter = self.config.counter
        self.full_threshold = self.config.full_threshold
        self.prob_reproduce = self.config.prob_reproduce

    def update(self):
        if self.energy >= self.full_threshold:
            self.state = 'FULL'
            # if random.random() < self.prob_reproduce:
            #     self.reproduce()
            #     self.energy -= self.reproduction_cost

        else:
            self.state = 'WANDERING'

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
                # self.counter=0
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
          elif self.state == "FULL":
              self.freeze_movement()

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
        neighbours_count = self.in_proximity_accuracy().count()
        p_join = 1 / (1 + np.exp(-5 * neighbours_count))

        # if neighbours_count != 0:
        if neighbours_count != 0 and random.random() < p_join:
            sum_velocities = Vector2()
            separation = Vector2()
            sum_positions = Vector2()
            collect_agents = list(self.in_proximity_accuracy())
            for agent, _ in collect_agents:
                sum_velocities += agent.move.normalize()
                separation += self.pos - agent.pos
                sum_positions += agent.pos
            # alignment
            sum_velocities = sum_velocities / neighbours_count
            alignment = sum_velocities - self.move
            # separation
            separation = separation / neighbours_count
            # cohesion
            avg_pos_neighbouring_birds = sum_positions / neighbours_count
            cohesion_force = avg_pos_neighbouring_birds - self.pos
            cohesion = cohesion_force - self.move

            f_total = (alignment * PPConfig().weights()[0] + separation * PPConfig().weights()[
                2] + cohesion * PPConfig().weights()[1]) / self.config.mass

            self.move += f_total
            if self.move.length() > self.config.movement_speed:
                self.move = self.move.normalize() * self.config.movement_speed

        self.pos += self.move * self.config.delta_time
          # self.there_is_no_escape()
          #
          # if self.state == "WANDERING":
          #
          #       prng = self.shared.prng_move
          #       should_change_angle = prng.random()
          #       deg = prng.uniform(-30,30)
          #
          #       if 0.2 > should_change_angle:
          #           self.move.rotate_ip(deg)
          #
          #       self.pos += self.move * self.config.delta_time  # wandering
    
class Selection(Enum):
    REP_THR = auto()
    REP_COST = auto()
    DEATH_THR = auto()

class PPLive(Simulation):
    selection: Selection = Selection.REP_THR
    config: PPConfig


    def handle_event(self, by: float):
        if self.selection == Selection.REP_THR:
            self.config.reproduction_threshold += by
        elif self.selection == Selection.REP_COST:
            self.config.reproduction_cost += by
        elif self.selection == Selection.DEATH_THR:
            self.config.death_threshold += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-1)
                elif event.key == pg.K_1:
                    self.selection = Selection.REP_THR
                elif event.key == pg.K_2:
                    self.selection = Selection.REP_COST
                elif event.key == pg.K_3:
                    self.selection = Selection.DEATH_THR

        print(f"rep.thr.: {self.config.reproduction_threshold:.1f} - rep.cost: {self.config.reproduction_cost:.1f} - death thr: {self.config.death_threshold:.1f}")

(
    PPLive(
        PPConfig(
            image_rotation=True,
            movement_speed=1,
            radius=15,
            seed=1,
        )
    )

    .batch_spawn_agents(20, Predator, images=["images/medium-bird.png"]) #5
    .batch_spawn_agents(45, Prey, images = ["images/red.png"]) #25
    .run()
    .snapshots
    .write_csv("predprey.csv")
)

