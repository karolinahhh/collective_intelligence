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
import pandas as pd


@deserialize
@dataclass
class PPConfig(Config):
    delta_time: float = 1
    mass: int = 20
    reproduction_threshold: int = 0.5
    reproduction_chance: float = 0.0015
    die_threshold: float = 0.005
    eat_threshold: float = 0.5


class Predator(Agent):
    config: PPConfig

    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING", agent_type=0):
        super().__init__(images=images, simulation=simulation)
        self.state = state
        self.agent_type = agent_type
        self.reproduction_threshold = self.config.reproduction_threshold
        self.die_threshold = self.config.die_threshold
        self.eat_threshold = self.config.eat_threshold

    def update(self):
        # check if eating rabbit in proximity ?
        prey = (
            self.in_proximity_accuracy()
                .without_distance()  # removes distance (?)
                .filter_kind(Prey)
                .first()
        )

        if prey is not None:
            eat_probability = random.random()
            if eat_probability < self.eat_threshold:
                prey.kill()
                should_reproduce = random.random()
                if should_reproduce < self.reproduction_threshold:
                    self.reproduce() 

        should_die = random.random()
        if should_die < self.die_threshold:
            self.kill()

        agent_type = self.agent_type
        self.save_data("agent", agent_type)

    def change_position(self):
        self.there_is_no_escape()

        if self.state == "WANDERING":

            prng = self.shared.prng_move
            should_change_angle = prng.random()
            deg = prng.uniform(-30, 30)

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
            deg = prng.uniform(-30, 30)

            if 0.5 > should_change_angle:
                self.move.rotate_ip(deg)

            self.pos += self.move * self.config.delta_time  # wandering


class PPLive(Simulation):
    config: PPConfig

    def after_update(self):
        super().after_update()
    
        agents = (
            self._metrics.snapshots
                .filter(pl.col("frame") == self.shared.counter)
                .get_column("agent")
        )

        preds = agents.eq(0).sum()
        prey = agents.eq(1).sum()

        # print("preds", preds)
        # print("prey", prey)
        
        if preds == 0 or prey == 0:
            self.stop()
    
def run_simulation(csv_filename):
    config = PPConfig(
        delta_time = 1,
        mass = 20,
        reproduction_threshold = 0.5,
        reproduction_chance = 0.0015,
        die_threshold = 0.0025,
        eat_threshold = 0.5,
        image_rotation=True,
        movement_speed=3,
        radius=15
    )

    start_time = time.time()
    simulation = (
        PPLive(config)
        .batch_spawn_agents(20, Predator, images=["images/medium-bird.png"])
        .batch_spawn_agents(45, Prey, images=["images/red.png"])
        .run()
        .snapshots
        .write_csv(csv_filename)
    )

    end_time = time.time()

    duration = end_time - start_time
    return duration

def generate_csv_filename(parameters: dict, run_index: int):
    excluded_params = ['delta_time', 'mass', 'image_rotation', 'movement_speed', 'radius', 'seed']
    filtered_params = {key: value for key, value in parameters.items() if key not in excluded_params}
    parameter_str = "_".join([f"{key}_{value}" for key, value in filtered_params.items()])
    return f"simulation_{parameter_str}_run_{run_index}.csv"

# Run the simulation multiple times with different parameter combinations
total_duration = 0
num_runs = 25  # Change this to the desired number of runs
simulation_durations = []

for run in range(num_runs):
    csv_filename = f"energy_free_run_{run}.csv"  # Customize the filename as needed
    duration = run_simulation(csv_filename)
    simulation_durations.append(duration)
    total_duration += duration
    print(f"Simulation Run {run + 1}:")
    print(f"CSV file saved as {csv_filename}.")
    print(f"Duration: {duration} seconds.")
    print()

average_duration = total_duration / num_runs
print(f"Average Duration: {average_duration} seconds.")

# Convert the simulation durations list to a pandas DataFrame for easier analysis
df = pd.DataFrame({'Simulation Duration': simulation_durations})
df.index.name = 'Run Index'
df.sort_values(by='Simulation Duration', ascending=False, inplace=True)

# Print the sorted DataFrame
print(df)

