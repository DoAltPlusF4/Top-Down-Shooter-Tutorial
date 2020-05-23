import pyglet
from pyglet.window import key, mouse
import pymunk
import pymunk.pyglet_util

import source


class Application:
    def __init__(self):
        self.createLayers()
        self.window = pyglet.window.Window(
            width=1280,
            height=720,
            caption="Test",
            resizable=True
        )

        self.space = pymunk.Space()
        self.space.damping = 0

        self.world_batch = pyglet.graphics.Batch()
        self.world_camera = source.camera.Camera(
            scroll_speed=0,
            min_zoom=0,
            max_zoom=float("inf")
        )

        self.key_handler = key.KeyStateHandler()
        self.mouse_handler = mouse.MouseStateHandler()
        self.mouse_handler["x"] = 0
        self.mouse_handler["y"] = 0
        self.window.push_handlers(self.key_handler, self.mouse_handler)

        self.player = source.player.Player(self)

        self.centre_block = source.basic.Basic(
            self,
            0, 60,
            collider={
                "type": "rect",
                "x": -10,
                "y": 0,
                "width": 20,
                "height": 20,
                "radius": 0
            }
        )

        self.window.push_handlers(self)
        self._position_camera()

    def createLayers(self):
        self.layers = {}
        self.layers["enemy"] = pyglet.graphics.OrderedGroup(0)
        self.layers["player_body"] = pyglet.graphics.OrderedGroup(1)
        self.layers["player_gun"] = pyglet.graphics.OrderedGroup(2)
        self.layers["projectile"] = pyglet.graphics.OrderedGroup(3)
        self.layers["obstacle"] = pyglet.graphics.OrderedGroup(4)

    def _position_camera(self):
        DEFAULT_SIZE = (1280, 720)

        scale = min(
            self.window.width/DEFAULT_SIZE[0],
            self.window.height/DEFAULT_SIZE[1]
        )

        if self.world_camera.zoom != scale:
            self.world_camera.zoom = scale

        x = (-self.window.width//2)/scale
        y = (-self.window.height//2)/scale

        x += self.player.position.x
        y += self.player.position.y

        if self.world_camera.position != (x, y):
            self.world_camera.position = (x, y)

    def screenToWorld(self, x, y):

        world_x = self.world_camera.offset_x
        world_x += x/self.world_camera.zoom

        world_y = self.world_camera.offset_y
        world_y += y/self.world_camera.zoom

        return (world_x, world_y)

    def update(self, dt):
        self.space.step(dt)
        self.player.update(dt)
        self._position_camera()

    def on_draw(self):
        self.window.clear()
        with self.world_camera:
            options = pymunk.pyglet_util.DrawOptions()
            self.space.debug_draw(options)
            self.world_batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_handler["x"] = x
        self.mouse_handler["y"] = y

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()


if __name__ == "__main__":
    application = Application()
    application.run()
