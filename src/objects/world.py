import math
import random
import sys
import time
from utils.geometry import Vec3
from utils.logger import LOGGER
from gl_abstractions.texture import Texture2D
from objects.bot import Bot
from objects.fren import Fren
from objects.model_element import ModelElement
from objects.element import Element
import constants
from objects.aux_robot import AuxRobot
from objects.sky import Sky
from objects.spawner import Spawner, SpawnerRegion, SpawningProperties
from objects.target_small import TargetSmall
from objects.wood_target import WoodTarget
from transform import Transform
from wavefront.model import Model
from wavefront.model_reader import ModelReader

class World:
    '''
    Class responsible for describing the world.
    It holds all the elements in a list and updates them.
    When they are marked for removal, they are removed from the list in the next update.
    '''
    
    def __init__(self):
        self.elements: list[Element] = []
        self._last_update_time = time.time()
        self.setup_finished = False

    def setup(self):
        '''
        This function is called when the user presses the 'r' key and when the application starts.
        It populates the world with the elements that are needed to play the game.

        Objects declared at the "bottom" of the code (last line) as rendered behind the upper ones.
        '''

        CURRENT_FUNCTION_NAME = f'{__name__}:{sys._getframe().f_code.co_name}()'
        LOGGER.log_info('Setting up scene', CURRENT_FUNCTION_NAME)

        assert not self.setup_finished, 'Trying to setup scene twice!'
        
        def load_model(filename: str) -> Model:
            '''Shorthand for loading a model from a file.'''
            return ModelReader().load_model_from_file(filename)

        from app_vars import APP_VARS
        self.spawn(APP_VARS.camera)

        #### External environment #####

        ground_main = ModelElement('GroundMain', texture=Texture2D.from_image_path('textures/floor3.png'), model=load_model('models/cube.obj'), ray_selectable=False, ray_destroyable=False)
        ground_main.transform.scale = Vec3(constants.WORLD_SIZE, 0.1, constants.WORLD_SIZE)
        ground_main.transform.translation = Vec3(0, -0.1, 0)
        self.spawn(ground_main)

        ground_spawn = ModelElement('GroundSpawn', texture=Texture2D.from_image_path('textures/floor4.png'), model=load_model('models/cube.obj'), ray_selectable=False, ray_destroyable=False)
        ground_spawn.transform.scale = Vec3(20, 0.01, 20)
        ground_spawn.transform.translation = Vec3(0, +0.1, 10)
        self.spawn(ground_spawn)

        BASE_SKY_SIZE = 340
        sky = Sky(
            name='Sky', 
            transform=Transform(
                scale=Vec3(
                    -(BASE_SKY_SIZE-constants.WORLD_SIZE), 
                    (BASE_SKY_SIZE-constants.WORLD_SIZE), 
                    (BASE_SKY_SIZE-constants.WORLD_SIZE),
                ),
                translation=Vec3(
                    0,
                    -(BASE_SKY_SIZE-constants.WORLD_SIZE)/2,
                    0,
                ),
            ),
        )
        self.spawn(sky)
        
        aux_robot = AuxRobot(
            'Aux Robot',
            transform=Transform(scale=Vec3(0.1, 0.1, 0.1), translation=Vec3(0, APP_VARS.camera._ground_y, 0)),
        )
        self.spawn(aux_robot)

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

        bot_spawner = Spawner(
            name='BotSpawner',
            region=SpawnerRegion(Vec3(-10,0.01,20), Vec3(10,0.01,0)),
            element_factory=lambda: Bot('Spawned Bot', transform=Transform(scale=Vec3(1.8,1.8,1.8))),
        )
        self.spawn(bot_spawner)

        outside_target_spawning_properties=SpawningProperties(
            spawn_cap=1, 
            min_interval=5, 
            max_interval=10, 
            insta_replace_destroyed=False
        )
        HOUSE_XYZ = Vec3(0, 0, -15)

        distances_z = [-3, 0, 3]
        outside_target_spawners = [
            Spawner(
                name=f'OutsideTargetSpawner_{idx}',
                region=SpawnerRegion(HOUSE_XYZ + Vec3(-3.023,3.5,distance_z), HOUSE_XYZ + Vec3(-3.023,3.5,distance_z)),
                spawning_properties=outside_target_spawning_properties,
                element_factory=lambda: WoodTarget(f'Wood Target {idx}'),
            ) for idx, distance_z in enumerate(distances_z)
        ]

        #### /External environment #####

        #### Internal environment #####

        house = ModelElement('house', model=load_model('models/house.obj'), ray_destroyable=False)
        house.transform.translation.xyz = HOUSE_XYZ
        house.transform.scale.xyz = Vec3(3,3,3)
        self.spawn(house)

        house_target_spawner = Spawner(
            name='HouseTargetSpawner',
            region=SpawnerRegion(HOUSE_XYZ + Vec3(-1.7, 0.69, -3), HOUSE_XYZ + Vec3(1.7 , 4, -3)),
            spawning_properties=SpawningProperties(
                spawn_cap=2, 
                min_interval=0.3, 
                max_interval=1, 
                insta_replace_destroyed=True,
            ),
            element_factory=lambda: TargetSmall('target_small', transform=Transform(scale=Vec3(0.4,0.4,1))),
        )
        self.spawn(house_target_spawner)

        fren = Fren('Fren')
        fren.transform.translation.xyz = HOUSE_XYZ + Vec3(-2, 0, +3.5)
        fren.transform.rotation.y = math.pi/4 + math.pi/2
        fren.transform.scale *= 0.8
        self.spawn(fren)

        for spawner in outside_target_spawners:
            self.spawn(spawner)

        #### /Internal environment #####

        LOGGER.log_info('Done setting up scene', CURRENT_FUNCTION_NAME)
        self.setup_finished = True
        
    def spawn(self, element: Element):
        ''' Spawns an element in the scene, triggering its on_spawned method. '''
        self.elements.append(element)
        element.on_spawned(world=self)

    def destroy(self, element: Element):
        ''' Asks an element to be destroyed (usually marks it as destroyed right away, but each element has its own way of doing this). '''
        element.destroy()

    def _update_daylight(self, delta_time: float):
        '''Update the daylight (Ambient Light intensity)'''
        from app_vars import APP_VARS
        if APP_VARS.lighting_config.do_daylight_cycle:
            APP_VARS.lighting_config.Ka_x *= 0.999 * delta_time * 60
            APP_VARS.lighting_config.Ka_y *= 0.999 * delta_time * 60
            APP_VARS.lighting_config.Ka_z *= 0.999 * delta_time * 60

    def update(self):
        '''
        This function is called every frame.
        It updates the world and all the elements in it.
        Update means:
            - Update the physics engine
            - Update the elements visuals
            - Update the elements logic
            - Render in OpenGL
        '''
        t = time.time()
        delta_time = t - self._last_update_time

        self._update_daylight(delta_time)
        self._update_elements(delta_time)
        self._remove_destroyed_elements()

        self._last_update_time = t

    def _update_elements(self, delta_time: float):
        '''Update all elements in the world'''
        for element in self.elements[::-1]:
            if not element.destroyed: # In case the element was destroyed while updating another element
                element.update(delta_time)

    def _remove_destroyed_elements(self):
        '''Remove all the destroyed elements from the world'''
        self.elements[:] = [ element for element in self.elements if not element.destroyed ]
        