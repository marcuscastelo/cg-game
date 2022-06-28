from json import load
import math
from pickle import APPEND
import random
from textwrap import wrap
import time
from typing import Text
import glm
from utils.geometry import Vec2, Vec3
from utils.logger import LOGGER
# from app_vars import APP_VARS
from gl_abstractions.shader import ShaderDB
from gl_abstractions.texture import Texture2D, TextureParameters
from line import Line
from objects.bot import Bot
from objects.cube import CUBE_MODEL, Cube
from objects.cube_target import CubeTarget
from objects.model_element import ModelElement
from objects.element import Element
import constants
from objects.aux_robot import AuxRobot
from objects.spawner import Spawner, SpawnerRegion, SpawningProperties
from objects.wood_target import WoodTarget
from transform import Transform
from wavefront.material import Material
from wavefront.model import Model
from wavefront.reader import ModelReader

from objects.selection_ray import SelectionRay

from OpenGL import GL as gl

class World:
    '''
    Class responsible for describing the world.
    It holds all the elements in a list and updates them.
    When they are marked for removal, they are removed from the list in the next update.
    '''
    
    def __init__(self):
        self.elements: list[Element] = []
        self._updating_inner = False
        self._last_update_time = time.time()

    def setup_scene(self):
        '''
        This function is called when the user presses the 'r' key and when the application starts.
        It populates the world with the elements that are needed to play the game.

        Objects declared at the "bottom" of the code (last line) as rendered behind the upper ones.
        '''
        LOGGER.log_trace('Setting up scene', 'world:setup_scene')

        def load_model(filename: str) -> Model:
            return ModelReader().load_model_from_file(filename)

        # LOGGER.log_trace('Emptying scene', 'world:setup_scene')
        # self.elements.clear()
        from app_vars import APP_VARS
        self.spawn(APP_VARS.camera)

        # wall = Cube('Wall', texture=Texture2D.from_image_path('textures/metal.jpg'), ray_destroyable=False)
        # wall.transform.scale = Vec3(0.1, 3, 3)
        # wall.transform.translation.xyz = Vec3(4, 0, 0)
        # wall.transform.rotation.xyz = Vec3(0, 0, 0)
        # self.spawn(wall)

        ground_main = ModelElement('GroundMain', texture=Texture2D.from_image_path('textures/floor3.png'), model=load_model('models/cube.obj'), ray_selectable=False, ray_destroyable=False)
        ground_main.transform.scale = Vec3(constants.WORLD_SIZE, 0.1, constants.WORLD_SIZE)
        ground_main.transform.translation = Vec3(0, -0.1, 0)
        self.spawn(ground_main)

        ground_spawn =ModelElement('GroundSpawn', texture=Texture2D.from_image_path('textures/floor4.png'), model=load_model('models/cube.obj'), ray_selectable=False, ray_destroyable=False)
        ground_spawn.transform.scale = Vec3(20, 0.01, 20)
        ground_spawn.transform.translation = Vec3(0, +0.1, 10)
        self.spawn(ground_spawn)

        sky = ModelElement('Sky', texture=Texture2D.from_image_path('textures/sky_wave.png'), model=load_model('models/cube.obj'), ray_selectable=False, ray_destroyable=False)

        sky.transform.translation = Vec3(0, -150, 0)
        sky.transform.scale = Vec3(-300, 300, -300)
        self.spawn(sky)
        
        # TODO: remove hardcode (used for light adjustment)
        self.sky = sky 
        self.sky.shape_specs[0].material = Material('Hardcoded Ka always bright', Ka=Vec3(0,0,0)) # Ka = 0 -> no directional light

        # TODO: rename 
        light_cube = AuxRobot('Aux Robot', model=load_model('models/aux_robot.obj'), ray_selectable=False, ray_destroyable=False)
        light_cube.transform.translation = APP_VARS.lighting_config.light_position # TODO: remove this hacky stuff (also hack_is_light)
        light_cube.transform.translation.y = 2
        light_cube.transform.scale = Vec3(1,1,1) * 0.1
        self.spawn(light_cube)


        TREE_MODEL = load_model('models/tree.obj')
        trees_positions = [
            Vec3(10, 0, -10),
            Vec3(13, 0, -10),
            Vec3(11, 0, -9),
            Vec3(9, 0, -9),
            Vec3(7, 0, -12.3),
            Vec3(6, 0, -14),
            Vec3(13, 0, -18),
            Vec3(14, 0, -10.4),
            Vec3(-9, 0, -12),
        ]

        trees = [
            ModelElement(
                name=f'Tree_{index}', 
                model=TREE_MODEL, 
                ray_destroyable=False,
                transform=Transform(
                    translation=translation,
                    rotation=Vec3(0,random.random() * 2 * math.pi,0)
                )
            ) for index, translation in enumerate(trees_positions)

        ]

        for rock in trees:
            self.spawn(rock)

        ROCK_MODEL = load_model('models/rock.obj')
        rocks_transforms = [
            Transform(Vec3(-10, 0, -10), Vec3(0, 1, 0), Vec3(1, 1, 1)),
            Transform(Vec3(-13, 0, -13), Vec3(0, 4, 0), Vec3(1, 2, 1)),
            Transform(Vec3(-13, 0, -12), Vec3(0, 12, 0), Vec3(3, 3, 3)),
            Transform(Vec3(13, 0, -18))
        ]

        rocks = [
            ModelElement(
                name=f'Rock_{index}', 
                model=ROCK_MODEL, 
                ray_destroyable=False,
                transform=transform
            ) for index, transform in enumerate(rocks_transforms)

        ]
        for rock in rocks:
            self.spawn(rock)


        BOT_MODEL = load_model('models/bot.obj')
        TARGET_MODEL = load_model('models/alvo2.obj')

        HOUSE_XYZ = Vec3(0, 0, -15)

        house = ModelElement('house', model=load_model('models/house.obj'), ray_destroyable=False)
        house.transform.translation.xyz = HOUSE_XYZ
        house.transform.scale.xyz = Vec3(3,3,3)
        self.spawn(house)

        def spawn_bot():
            bot = Bot('Spawned Bot')
            bot.transform.scale *= 1.8
            return bot

        bot_spawner = Spawner(
            name='BotSpawner',
            region=SpawnerRegion(Vec3(-10,0.01,20), Vec3(10,0.01,0)),
            element_factory=spawn_bot,
        )
        self.spawn(bot_spawner)
        TARGET_SMALL_MODEL = load_model('models/target_small.obj')
        house_target_spawner = Spawner(
            name='HouseTargetSpawner',
            region=SpawnerRegion(HOUSE_XYZ + Vec3(-1.7, 0.69, -3), HOUSE_XYZ + Vec3(1.7 , 4, -3)),
            spawning_properties=SpawningProperties(
                max_spawned_elements=2, 
                min_interval=0.3, 
                max_interval=1, 
                insta_replace_destroyed=True,
            ),
            element_factory=lambda: ModelElement('Spawned Target', model=TARGET_SMALL_MODEL, transform=Transform(scale=Vec3(0.4,0.4,1))),
        )
        self.spawn(house_target_spawner)

        ALVO_2_MODEL = load_model('models/alvo2.obj')
        ALVO_2_TEXTURE = Texture2D.from_image_path('textures/wood.jpg')
        outside_target_spawning_properties=SpawningProperties(
            max_spawned_elements=1, 
            min_interval=5, 
            max_interval=10, 
            insta_replace_destroyed=False
        )

        distances_z = [-3, 0, 3]
        outside_target_spawners = [
            Spawner(
                name=f'OutsideTargetSpawner_{idx}',
                region=SpawnerRegion(HOUSE_XYZ + Vec3(-3.023,3.5,distance_z), HOUSE_XYZ + Vec3(-3.023,3.5,distance_z)),
                spawning_properties=outside_target_spawning_properties,
                element_factory=lambda: WoodTarget('alvo2', model=ALVO_2_MODEL, texture=ALVO_2_TEXTURE, ray_selectable=True, ray_destroyable=True),
            ) for idx, distance_z in enumerate(distances_z)
        ]

        fren = ModelElement('Fren', model=load_model('models/fren.obj'))
        fren.transform.translation.xyz = HOUSE_XYZ + Vec3(-2, 0, +3.5)
        fren.transform.rotation.y = math.pi/4 + math.pi/2
        fren.transform.scale *= 0.8
        self.spawn(fren)

        for spawner in outside_target_spawners:
            self.spawn(spawner)

        LOGGER.log_info('Done setting up scene', 'world:setup_scene')
        
    def spawn(self, element: Element):
        self.elements.append(element)
        element.on_spawned(world=self)

    def destroy(self, element: Element):
        element.destroy()

    def update(self):
        '''
        This function is called every frame.
        It updates the world and all the elements in it.
        '''
        t = time.time()
        delta_time = t - self._last_update_time

        from app_vars import APP_VARS
        if APP_VARS.lighting_config.do_daylight_cycle:
            APP_VARS.lighting_config.Ka_x *= 0.999
            APP_VARS.lighting_config.Ka_y *= 0.999
            APP_VARS.lighting_config.Ka_z *= 0.999
        
        # Update elements
        for element in self.elements[::-1]:
            if not element.destroyed: # In case the element was destroyed while updating
                element.update(delta_time)

        # Remove elements that are marked for removal
        self.elements[:] = [ element for element in self.elements if not element.destroyed ]

        self._last_update_time = t

        # SIZE = 0.1
        # self.diamond_blocks[random.randint(0, len(self.diamond_blocks)-1)].transform.scale *= 1 + (SIZE) - (random.random() * 2 * SIZE)

        from camera import Camera
        assert isinstance(self.elements[0], Camera), "0th element is not a camera!"

        global_Ka = Vec3(APP_VARS.lighting_config.Ka_x, APP_VARS.lighting_config.Ka_y, APP_VARS.lighting_config.Ka_z)
        global_Ka.x = glm.clamp(global_Ka.x, 0, 1)
        global_Ka.y = glm.clamp(global_Ka.y, 0, 1)
        global_Ka.z = glm.clamp(global_Ka.z, 0, 1)
        inv_global_Ka = Vec3(1/(global_Ka.x+0.01), 1/(global_Ka.y+0.01), 1/(global_Ka.z+0.01),) 
        
        self.sky.shape_specs[0].material.Kd = (inv_global_Ka * global_Ka**2)

    def is_player_victory(self) -> bool:
        '''
        If no more enemies or garbage is left, the player has won.
        '''
        return False

    def is_player_defeat(self) -> bool:
        '''
        If the player has been destroyed, he has lost.
        '''
        return False

WORLD = World()