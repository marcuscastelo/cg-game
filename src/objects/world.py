from pickle import APPEND
import random
import time
from typing import Text
from utils.geometry import Vec2, Vec3
from utils.logger import LOGGER
from gl_abstractions.texture import Texture2D
from objects.cube import Cube
from objects.element import Element
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
        world = self

        # LOGGER.log_trace('Emptying scene', 'world:setup_scene')
        # self.elements.clear()

        cube1 = Cube(world)
        cube1.transform.scale = Vec3(0.2, 0.2, 0.2)
        cube1.transform.translation.xyz = Vec3(10, 10, 10)
        cube2 = Cube(world)
        cube2.transform.translation.xyz = Vec3(1,1,1)
        cube2.transform.scale = Vec3(0.2, 0.2, 0.2)

        ground = Cube(world, custom_texture=Texture2D.from_image_path('textures/ground.png'))
        ground.transform.scale = Vec3(10, 0, 10)

        sky = Cube(world, custom_texture=Texture2D.from_image_path('textures/sky.jpg'))
        sky.transform.scale = Vec3(-300, 300, 300)

        diamond_block_texture = Texture2D.from_image_path('textures/diamond_block.png')
        self.diamond_blocks = []
        for i in range(10):
            for j in range(10):
                # for k in range(10):
                    diamond_block = Cube(world, custom_texture=diamond_block_texture)
                    diamond_block.transform.translation.xyz = Vec3(2 + i, 0.5 + 0, 0 + j)
                    diamond_block.transform.scale = Vec3(1,1,1) * 0.5
                    self.diamond_blocks.append(diamond_block)

        LOGGER.log_info('Done setting up scene', 'world:setup_scene')
        
    def spawn(self, element: Element):
        self.elements.append(element)

    def destroy(self, element: Element):
        element.destroy()

    def update(self):
        '''
        This function is called every frame.
        It updates the world and all the elements in it.
        '''
        t = time.time()
        delta_time = t - self._last_update_time

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
        camera_xyz = self.elements[0].transform.translation.xyz

        # for element in self.elements[1:]:
        #     center = element.transform.translation.xyz
        #     side_size = element.transform.scale.xyz
        #     min_x, max_x = (center.x - side_size.x / 2, center.x + side_size.x / 2)
        #     min_y, max_y = (center.y - side_size.y / 2, center.y + side_size.y / 2)
        #     min_z, max_z = (center.z - side_size.z / 2, center.z + side_size.z / 2)
        #     if min_x <= camera_xyz.x <= max_x and min_y <= camera_xyz.y-1.8 <= max_y and min_z <= camera_xyz.z <= max_z:
        #         element.select()
        #     # else:
        #     #     element.unselect()
        
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