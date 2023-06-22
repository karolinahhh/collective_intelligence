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
    delta_time: float = 2 #####
    mass: int = 20#####
    energy: int = 40 #50
    eat_threshold: int = 0.5
    prey_worth: int = 15 #was 10
    reproduction_threshold: int = 50
    reproduction_cost: int = 30
    death_threshold: int = 20 #20
    energy_loss: float = 0.05
    reproduction_chance: float = 0.0015 #0.002
    prob_reproduce: float = 0.5
    prey_count: int= 0

    # delta_time: float = 2  # 1
    # mass: int = 20
    # energy: int = 40  # 50
    # eat_threshold: int = 0.5
    # prey_worth: int = 10  # was 10
    # reproduction_threshold: int = 60
    # reproduction_cost: int = 30
    # death_threshold: int = 25  # 20
    # energy_loss: float = 0.05
    # reproduction_chance: float = 0.002  # 0.002
    # prob_reproduce: float = 0.5
    # fear_factor: float = 0.0005  # 10 predators to never reproduce

class Predator(Agent):
    config: PPConfig

    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING", agent_type=0):
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
        self.prey_count = self.config.prey_count

    def update(self):
        # check if eating rabbit in proximity ?
        prey = (
            self.in_proximity_accuracy()
            .filter(lambda x: x[1] < 15)
            .without_distance()  # removes distance (?)
            .filter_kind(Prey)
            .first()
        )
        if prey is not None:
            prob_eat = random.random()
            if prob_eat < self.eat_threshold:
                prey.kill()
                prey_c=1
                # self.prey_count = 1
                self.energy += self.prey_worth
            else:
                prey_c=0
        else:
            prey_c=0

        if self.energy >= self.reproduction_threshold:
            self.reproduce()
            self.energy -= self.reproduction_cost


        if self.energy < self.death_threshold:
             self.kill()

        self.energy -= self.energy_loss

        agent_type= self.agent_type
        # prey_c = self.config.prey_count
        self.save_data("agent", agent_type)
        self.save_data("prey consumed", prey_c)
        # self.config.prey_count = 0

    def change_position(self):
          self.there_is_no_escape()

          if self.state == "WANDERING":
                
                prng = self.shared.prng_move
                should_change_angle = prng.random()
                deg = prng.uniform(-30, 30)

                if 0.2 > should_change_angle:
                    self.move.rotate_ip(deg)

                self.pos += self.move * self.config.delta_time

class Prey(Agent):
    config: PPConfig
    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING", agent_type=1):
        super().__init__(images=images, simulation=simulation)
        self.state = state
        self.agent_type= agent_type
        self.reproduction_chance = self.config.reproduction_chance

    def update(self):
        predator_count = self.in_proximity_accuracy().filter_kind(Predator).count()
        # print(predator_count)
        # should_reproduce = min(1.0, random.random() + predator_count * self.fear_factor)
        #should_reproduce = 1 / (1 + np.exp(-predator_count*0.1))
        should_reproduce = random.random()
        # print(should_reproduce)

        if should_reproduce < self.reproduction_chance:
            self.reproduce()  # reproduce needs to be implemented better later

        agent_type = self.agent_type
        # prey_c = self.config.prey_count
        self.save_data("agent", agent_type)
        self.save_data("prey consumed", 0)

    def change_position(self):
        self.there_is_no_escape()

        if self.state == "WANDERING":

            prng = self.shared.prng_move
            should_change_angle = prng.random()
            deg = prng.uniform(-30, 30)

            if 0.2 > should_change_angle:
                self.move.rotate_ip(deg)
            self.pos += self.move * self.config.delta_time  # wandering
    
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

        # print(f"rep.thr.: {self.config.reproduction_threshold:.1f} - rep.cost: {self.config.reproduction_cost:.1f} - death thr: {self.config.death_threshold:.1f}")



# Define a function to run the simulation with the given radius and save the CSV file with the provided name
def run_simulation(csv_filename: str):
    simulation = PPLive(
        PPConfig(
            image_rotation=True,
            movement_speed=1,
            radius=150,
            duration=40000
        )
    ).batch_spawn_agents(20, Predator, images=["images/medium-bird.png"]) \
    .batch_spawn_agents(45, Prey, images = ["images/red.png"]) \
    .run()\
    .snapshots\
    .write_csv(csv_filename)


# Define a function to generate a unique CSV filename based on the radius
def generate_csv_filename(run_index: int):
    return f"energy_run_{run_index}.csv"

# Define the radius values and the number of runs
num_runs = 30  # Change this to the desired number of runs

# Run the simulation multiple times with different radii and save the CSV files

for run in range(num_runs):
    csv_filename = generate_csv_filename(run)
    run_simulation(csv_filename)
    print(f"CSV file saved as {csv_filename}.")