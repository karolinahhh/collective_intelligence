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


# introduce flocking (flocking/not)
# stopping after full (full/nofull)

@deserialize
@dataclass
class PPConfig(Config):
    delta_time: float = 2  # 1
    mass: int = 20
    energy: int = 30  # 50
    eat_threshold: int = 0.5
    prey_worth: int = 10  # was 10
    reproduction_threshold: int = 50
    reproduction_cost: int = 10
    death_threshold: int = 25  # 20
    full_threshold: int = 50 == 70
    energy_loss: float = 0.05
    reproduction_chance: float = 0.002  # 0.002
    prob_reproduce: float = 0.5
    fear_factor: float = 0.0005  # 10 predators to never reproduce
    probability_of_being_eaten: float = 1.0



red_image_path = "images/red.png"
green_image_path = "images/green.png"


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
        self.full_threshold = self.config.full_threshold
        self.prey_type = 2

    def update(self):

        prey_color = self.prey_type
        # print(prey_color)
        self.save_data("prey type", prey_color)
        if self.energy >= self.full_threshold:
            self.state = 'FULL'



        else:
            self.state = 'WANDERING'

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
                if (prob_eat < self.eat_threshold) or (prey._image_index == 1 and prob_eat < self.eat_threshold/2):
                    prey.kill()
                    self.energy += self.prey_worth


            if self.energy >= self.reproduction_threshold:
                reproduction_prob = random.random()
                if reproduction_prob > 0.5:
                    self.reproduce()
                    self.energy -= self.reproduction_cost

        if self.energy < self.death_threshold:
            self.kill()

        self.energy -= self.energy_loss

        agent_type = self.agent_type
        self.save_data("agent", agent_type)

    def change_position(self):
        self.there_is_no_escape()

        if self.state == "WANDERING":

            prng = self.shared.prng_move
            should_change_angle = prng.random()
            deg = prng.uniform(-30, 30)

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
        self.agent_type = agent_type
        self.prey_type = 0
        self.reproduction_chance = self.config.reproduction_chance
        self.fear_factor = self.config.fear_factor
        self.probability_of_being_eaten = self.config.probability_of_being_eaten


    def update(self):
        predator_count = self.in_proximity_accuracy().filter_kind(Predator).count()
        # print(predator_count)
        should_reproduce = min(1.0, random.random() + predator_count * self.fear_factor)

        # should_reproduce = 1 / (1 + np.exp(-predator_count*0.1))
        # should_reproduce = random.random()
        # Check if fear_factor exceeds the threshold

        if predator_count * self.fear_factor >= 0.0015:
            self.change_image(1)
            self.state = "CAMOUFLAGE"
            self.prey_type = 1
        else:
            self.change_image(0)
            self.state = "WANDERING"
            self.prey_type = 0

        prey_color = self.prey_type
        self.save_data("prey type", prey_color)

        if should_reproduce < self.reproduction_chance:
            self.reproduce()  # reproduce needs to be implemented better later

        agent_type = self.agent_type
        self.save_data("agent", agent_type)


    def change_position(self):
        self.there_is_no_escape()

        if self.state == "WANDERING" or "CAMOUFLAGE":

            prng = self.shared.prng_move
            should_change_angle = prng.random()
            deg = prng.uniform(-30, 30)

            if 0.2 > should_change_angle:
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

        # # Calculate the sum of birds with green pictures
        # green_birds_sum = (
        #     agents
        #         .filter((pl.col("agent_type") == 1) & (pl.col("_image_index") == 0))
        #         .filter(pl.col("image_index") == 1)  # Green pictures have image_index 1
        #         .sum()
        # )
        #
        # # Calculate the sum of prey with red pictures
        # red_prey_sum = (
        #     agents
        #         .filter((pl.col("agent_type") == 1) & (pl.col("_image_index") == 0))
        #         .filter(pl.col("image_index") == 0)  # Red pictures have image_index 0
        #         .sum()
        # )
        #
        # # Save the data for the current frame
        # self.save_data("green_birds_sum", green_birds_sum)
        # self.save_data("red_prey_sum", red_prey_sum)

        preds = agents.eq(0).sum()
        prey = agents.eq(1).sum()


        # print("preds", preds)
        # print("prey", prey)

        if preds == 0 or prey == 0 or preds == 200 or prey == 200:
            self.stop()


def run_simulation(csv_filename):
    config = PPConfig(
        delta_time=1,  # 1
        mass=20,
        energy=60,  # 50
        eat_threshold=0.3,
        prey_worth=25,  # was 10
        reproduction_threshold=90,
        reproduction_cost=20,
        death_threshold=30,  # 20
        full_threshold=70,
        energy_loss=0.08,
        reproduction_chance=0.0015,  # 0.002
        prob_reproduce=0.5,
        image_rotation=True,
        movement_speed=3,
        radius=150,
        fear_factor=0.0005
    )

    start_time = time.time()
    simulation = (
        PPLive(config)
            .batch_spawn_agents(25, Predator, images=["images/medium-bird.png"])
            .batch_spawn_agents(45, Prey, images=[red_image_path, green_image_path])
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
num_runs = 1
# Change this to the desired number of runs
simulation_durations = []

for run in range(num_runs):
    csv_filename = f"camouflage_{run}.csv"  # Customize the filename as needed
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
