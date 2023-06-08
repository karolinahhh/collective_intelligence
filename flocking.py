from enum import Enum, auto

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.8
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5

    delta_time: float = 3

    mass: int = 20

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig

    def get_alignment_weight(self):
        return self.config.alignment_weight

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        neighbours_count = self.in_proximity_accuracy().count()
        
        if neighbours_count != 0:
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

            f_total = (alignment*FlockingConfig().weights()[0] + separation*FlockingConfig().weights()[2] + cohesion*FlockingConfig().weights()[1])/self.config.mass

            self.move += f_total
            if self.move.length() > self.config.movement_speed:
                self.move = self.move.normalize() * self.config.movement_speed

        self.pos += self.move * self.config.delta_time


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()
        #self.screen.fill((0, 0, 255))
        #self.simulation.screen.fill((0, 0, 255))

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")

(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["images/white_bird.png"])
    .run()
)
