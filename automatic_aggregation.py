from enum import Enum, auto
from typing import Optional
import random
import time
import pygame as pg
import numpy as np
import polars as pl
import pygame.display
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

    def update(self):
        site = self.on_site()
        self.save_data("site", site)
        site_id = self.on_site_id()
        self.save_data("site_id", site_id)

    def change_position(self):
        self.there_is_no_escape()
        neighbours_count = self.in_proximity_accuracy().count()

        # p_join = 1 / (1 + np.exp(-5*neighbours_count))
        # # print(p_leave)
        # p_leave = 1 - p_join
        p_join = 1 / (1 + np.exp(-5*neighbours_count))
        # print(p_leave)
        p_leave = 1 - p_join
        randomx = random.random()
        # screen_info = pygame.display.Info()
        # print(screen_info)

        if not self.on_site():
            self.check_site = False

        if self.state == "WANDERING":
            self.pos += self.move * self.config.delta_time  # wandering

            if self.on_site() and p_join > randomx and not self.check_site:
                self.state = "JOIN"
                self.config.counter1 = 0

        if self.state == "JOIN":
            self.config.counter1 += 1
            if self.config.counter1 > 25 and self.on_site():
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
            if self.config.counter > 50:
                self.state = "WANDERING"
                self.config.counter = 0


class AggregationLive(Simulation):
    config: AggregationConfig

# Define a function to run the simulation with the given radius and save the CSV file with the provided name
def run_simulation(radius: int, csv_filename: str):
    simulation = AggregationLive(
        AggregationConfig(
            image_rotation=True,
            movement_speed=10,
            radius=radius,
            seed=1,
            duration = 15000
        )
    ).spawn_site("images/oneforthcircle.png", 187.5, 562.5) \
    .spawn_site("images/oneforthcircle.png", 562.5, 187.5) \
    .spawn_site("images/oneforthcircle.png", 562.5, 562.5) \
    .spawn_site("images/oneforthcircle.png", 187.5, 187.5) \
    .batch_spawn_agents(50, Cockroach, images=["images/orange_dot.png"]) \
    .run() \
    .snapshots \
    .write_csv(csv_filename)

# Define a function to generate a unique CSV filename based on the radius
def generate_csv_filename(radius: int, run_index: int):
    return f"4circle_aggregation_radius_{radius}_run_{run_index}.csv"

# Define the radius values and the number of runs
radius_values = [10, 20, 40]  # Add more values as needed
num_runs = 5  # Change this to the desired number of runs

# Run the simulation multiple times with different radii and save the CSV files
for radius in radius_values:
    for run in range(num_runs):
        csv_filename = generate_csv_filename(radius, run)
        run_simulation(radius, csv_filename)
        print(f"Simulation with radius {radius} completed. CSV file saved as {csv_filename}.")
