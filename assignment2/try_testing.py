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

    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING"):
        super().__init__(images=images, simulation=simulation)
        self.state = state
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
    def __init__(self, images: list[pg.Surface], simulation: Simulation, state="WANDERING"):
        super().__init__(images=images, simulation=simulation)
        self.state = state
        self.reproduction_chance = self.config.reproduction_chance

    def update(self):

        should_reproduce = random.random()
        if should_reproduce < self.reproduction_chance:
            self.reproduce()  # reproduce needs to be implemented better later


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

def run_simulation(config: PPConfig, csv_filename: str):
    simulation = PPLive(config)
    simulation.batch_spawn_agents(5, Predator, images=["images/medium-bird.png"])
    simulation.batch_spawn_agents(25, Prey, images=["images/red.png"])
    
    # Run the simulation until either population dies
    while len(simulation.get_agents_by_type(Predator)) > 0 and len(simulation.get_agents_by_type(Prey)) > 0:
        simulation.tick()

    # Record the necessary data for the EA
    # Modify this part according to your desired data collection process
    predator_population = simulation.get_agents_by_type(Predator)
    prey_population = simulation.get_agents_by_type(Prey)
    predator_count = len(predator_population[-1]) if predator_population else 0
    prey_count = len(prey_population[-1]) if prey_population else 0
    
    # Write the data to a CSV file
    data = {
        'Predator Population': predator_count,
        'Prey Population': prey_count,
    }
    df = pl.DataFrame(data)
    df.write_csv(csv_filename)

def generate_csv_filename(radius: int, run_index: int):
    return f"predator_prey_radius_{radius}_run_{run_index}.csv"

# Define the radius values and the number of runs
radius_values = [20, 40]  # Add more values as needed
num_runs = 5  # Change this to the desired number of runs

# Run the simulation multiple times with different radii and save the CSV files
for radius in radius_values:
    for run in range(num_runs):
        csv_filename = generate_csv_filename(radius, run)
        config = PPConfig(
            delta_time=0.9,
            mass=20,
            image_rotation=True,
            movement_speed=3,
            radius=radius,
            seed=1
        )
        run_simulation(config, csv_filename)
        print(f"Simulation with radius {radius} completed. CSV file saved as {csv_filename}.")



def calculate_fitness(simulation):
    # Get the population data from the simulation
    predator_population = simulation.get_agents_by_type(Predator)
    prey_population = simulation.get_agents_by_type(Prey)

    # Calculate the average population sizes over time
    predator_sizes = [len(predator_population[step]) for step in range(simulation.step_count)]
    prey_sizes = [len(prey_population[step]) for step in range(simulation.step_count)]
    avg_predator_size = sum(predator_sizes) / len(predator_sizes)
    avg_prey_size = sum(prey_sizes) / len(prey_sizes)

    # Calculate the oscillation factor
    oscillation_factor = max(predator_sizes) / min(predator_sizes)

    # Calculate the longevity factor
    longevity_factor = len(predator_sizes)

    # Define weights for the factors (adjust according to your priorities)
    oscillation_weight = 0.6
    longevity_weight = 0.4

    # Calculate the overall fitness score
    fitness = (oscillation_factor * oscillation_weight) + (longevity_factor * longevity_weight)

    return fitness

def evaluate_population(population):
    # Create an empty list to store the fitness results for each parameter combination
    fitness_results = []

    for params in population:
        # Run the simulation with the current parameter combination
        simulation = PPLive(PPConfig(**params))
        simulation.batch_spawn_agents(5, Predator, images=["images/medium-bird.png"])
        simulation.batch_spawn_agents(25, Prey, images=["images/red.png"])
        simulation.run()

        # Calculate the fitness metric based on the simulation results
        fitness = calculate_fitness(simulation)  # Implement your fitness calculation logic

        # Store the fitness result along with the parameter combination
        fitness_results.append({"params": params, "fitness": fitness})

    return fitness_results

def create_random_params():
    # Create a dictionary with the parameter names and their respective value ranges
    params = {
        "energy": random.uniform(40, 60),
        "eat_threshold": random.uniform(0.4, 0.6),
        "prey_worth": random.uniform(5, 15),
        "reproduction_threshold": random.uniform(80, 100),
        "reproduction_cost": random.uniform(40, 60),
        "death_threshold": random.uniform(10, 30),
        "energy_loss": random.uniform(0.03, 0.07),
        "reproduction_chance": random.uniform(0.001, 0.005),
    }

    return params

def breed(parent1, parent2):
    # Create a new parameter combination by randomly selecting values from parents
    child = {}
    for param in parent1:
        if random.random() < 0.5:
            child[param] = parent1[param]
        else:
            child[param] = parent2[param]

    return child

def mutate(params):
    # Mutate a random parameter within a certain range
    param_to_mutate = random.choice(list(params.keys()))
    mutation_range = {
        "energy": (-5, 5),
        "eat_threshold": (-0.05, 0.05),
        "prey_worth": (-2, 2),
        "reproduction_threshold": (-5, 5),
        "reproduction_cost": (-5, 5),
        "death_threshold": (-2, 2),
        "energy_loss": (-0.01, 0.01),
        "reproduction_chance": (-0.0005, 0.0005),
    }

    mutation = random.uniform(*mutation_range[param_to_mutate])
    params[param_to_mutate] += mutation

    # Ensure the mutated parameter stays within the valid range
    params[param_to_mutate] = max(params[param_to_mutate], mutation_range[param_to_mutate][0])
    params[param_to_mutate] = min(params[param_to_mutate], mutation_range[param_to_mutate][1])

    return params

# Genetic Algorithm
population_size = 20
num_generations = 10

# Generate an initial population with random parameter combinations
population = [create_random_params() for _ in range(population_size)]

for generation in range(num_generations):
    # Evaluate the fitness of the population
    results = evaluate_population(population)

    # Select parents for breeding (e.g., based on fitness)
    parents = random.choices(population, weights=[result["fitness"] for result in results], k=population_size)

    # Breed the parents to create a new population
    population = [breed(parent1, parent2) for parent1, parent2 in zip(parents[::2], parents[1::2])]

    # Mutate the population
    population = [mutate(params) for params in population]

    # Add elite individuals (optional)
    # ...

# Find the best parameter combination based on the final evaluation results
best_result = max(results, key=lambda result: result["fitness"])
best_params = best_result["params"]

print("Best Parameters:", best_params)

# Run the simulation with the best parameters
simulation = PPLive(PPConfig(**best_params))
simulation.batch_spawn_agents(5, Predator, images=["images/medium-bird.png"])
simulation.batch_spawn_agents(25, Prey, images=["images/red.png"])
simulation.run()

# (
#     PPLive(
#         PPConfig(
#             image_rotation=True,
#             movement_speed=3,
#             radius=15,
#             seed=1,
#         )
#     )

#     .batch_spawn_agents(5, Predator, images=["images/medium-bird.png"])
#     .batch_spawn_agents(25, Prey, images = ["images/red.png"])
#     .run()
# )


