from math import cos, sin
from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

from utils.geometry import Rect2, Vec2, Vec3
from utils.logger import LOGGER
from objects.element import Element, ElementSpecification, ShapeSpec

from OpenGL import GL as gl

from transform import Transform

import numpy as np

if TYPE_CHECKING:
    from objects._2d.ship import Ship
    from objects._2d._2dworld import World

@dataclass
class ProjectileSpecs(ElementSpecification):
    """
    This class is used to store the movement of the ship.
    User input is stored in this class. (in the current frame)
    """
    # Basic variables that define the projectile's visible properties
    initial_speed: float = 0.06
    acceleration: float = +0.005
    decay_rate: float = 0.1
    length: float = 0.16
    width: float = 0.5
    color: Vec3 = Vec3(1, 0, 0)

@dataclass
class Projectile(Element):
    '''
    The projectile is shot by both the ship and the enemies. It can also kill them both.
    When a projectile hits a ship, an enemym, the screen border or the satellite, it
    spreads into smaller non-damage projectile, as if it's shattering itself
    '''
    def __init__(self, world: 'World', specs: ProjectileSpecs, *args, **kwargs):
        self.live_time = 0
        self.specs = specs
        
        # TODO: avoid scale overwriting somehow (if user already set scale before)
        self.specs.initial_transform.scale.y = self.specs.length
        self.specs.shape_specs = [
            ShapeSpec(vertices=np.array([
                [*(0.0,  -1.0,   0.0)],
                [*(0.0,  +1.0,   0.0)],
            ], dtype=np.float32),
            render_mode=gl.GL_LINES,
            )
        ]

        assert isinstance(self.specs.initial_speed, float), f"{self.specs.initial_speed} is not a float, but {type(self.specs.initial_speed)}"

        super().__init__(world, specs, *args, **kwargs)
        self.specs = specs # TODO: HACK: this is a hack to reoverwrite the specs of the parent class (Element)
        assert isinstance(self.specs.initial_speed, float), f"{self.specs.initial_speed} is not a float, but {type(self.specs.initial_speed)}"

        self.is_particle = True # TODO: remove this and create a proper particle class
        self.is_enemy = False # TODO: better way to do this?
        self.speed = self.specs.initial_speed

    def _generate_bounding_box_2d_vertices(self) -> np.ndarray:
        '''
        Overrides the generate_bounding_box_vertices of class Element.
        '''
        return np.array([
            [-0.01, -0.1, 0],
            [+0.01, +0.1, 0],
        ])

    def _render(self):
        '''
        Overrides the render of class Element.
        '''
        gl.glLineWidth(self.specs.width)
        return super()._render()

    @classmethod
    def create_from_ship(cls, ship: 'Ship', specs: ProjectileSpecs = None) -> 'Projectile':
        '''
        The projectile is created by a ship, getting the position and the angle of the latter,
        so it can represent with fidelity what is supposed to happen
        '''
        shiplike_len = 1 # ship.get_bounding_box_2d().size.y


        relatite_weapon_distance = Vec3(-sin(ship.transform.rotation.z), cos(ship.transform.rotation.z), 0) * shiplike_len
        projectile_pos = ship.transform.translation.xyz + relatite_weapon_distance 

        if specs is None:
            specs = ProjectileSpecs()

        specs.initial_transform.translation.xyz = projectile_pos
        specs.initial_transform.rotation = Vec3(0, 0, ship.transform.rotation.z)

        obj = cls(
            world = ship.world,
            specs = specs,
        )

        obj.is_particle = False
        return obj

    def too_small(self):
        '''
        Small method to determine if the projectile is smaller than a pre-set value
        '''
        return self.transform.scale.y < 0.01
    
    def _physics_update(self, delta_time: float):
        
        '''
        Overrides the generate_bounding_box_vertices of class Element.
        Physics update method, which also verify if the projectile is out of bounds.
        If outside of the screen or too small, it gets destroyed.
        '''
        self.live_time += delta_time
        if self.destroyed:
            LOGGER.log_error(f"Trying to update destroyed projectile {self}")
            return

        dx = np.cos(self.transform.rotation.z + math.radians(90)) * 1 * self.speed
        dy = np.sin(self.transform.rotation.z + math.radians(90)) * 1 * self.speed
        self.transform.translation.xy += Vec2(dx, dy)
        
        self.speed = max(self.speed + self.speed * self.specs.acceleration, 0)

        self.transform.scale.y *= (1 - self.specs.decay_rate)

        screen = Rect2(-1, -1, 1, 1)
        outside_screen = not screen.contains(self.transform.translation.xy)

        if outside_screen or self.too_small():
            if not self.destroyed:
                self.destroy()

        return super()._physics_update(delta_time)

    def destroy(self):
        '''
        Overrides the generate_bounding_box_vertices of class Element.
        When destroyed, the projectile shatters itself in an certain amount of
        small projectile (up to 25), based on the distance it traveled.
        They are spread with an equal angle, and also decay as they go by the space.
        '''
        if not self.destroyed and not self.too_small() and not self.is_particle:
            impact_xyz = self.transform.translation.xyz
            TIME_TO_TRAVEL_SCREEN = 1 # seconds
            MAX_PARTICLES = 25
            particle_lifetime_completion = min(1, self.live_time / TIME_TO_TRAVEL_SCREEN)

            number_of_minibullets = int(math.ceil(MAX_PARTICLES * particle_lifetime_completion)) + 3
            start_angle = self.transform.rotation.z
            angle_step = 2 * math.pi / number_of_minibullets

            initial_speed=self.specs.initial_speed * 0.5
            decay_rate=self.specs.decay_rate * 4
            
            mini_bullets = [
                Projectile(
                    self.world, 
                    specs=ProjectileSpecs(
                        initial_speed=initial_speed,
                        decay_rate=decay_rate,
                        initial_transform=Transform(
                            translation=impact_xyz + Vec3(0, 0, 0.1), 
                            rotation=Vec3(0, 0, start_angle + math.pi/2 + angle_step/2 * i)
                        )
                    )
                ) for i in range(number_of_minibullets)
            ]

            for bullet in mini_bullets:
                bullet.transform.scale.y = 0.1

        return super().destroy()

    
