import pyglet
from pyglet.window import key, mouse
import pymunk
import pymunk.pyglet_util

import source


class Application:
    def __init__(self):
        self.createLayers()
        self.loadResources()
        self.window = pyglet.window.Window(
            width=1280,
            height=720,
            caption="Test",
            resizable=True
        )

        self.fps_display = pyglet.window.FPSDisplay(window=self.window)

        self.space = pymunk.Space()
        self.space.damping = 0
        self.space.collision_slop = 1

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

        self.WORLD_DIMENSIONS = (3000, 1500)

        self.floor = {}
        for x in range(-self.WORLD_DIMENSIONS[0]//200, self.WORLD_DIMENSIONS[0]//200+1):
            for y in range(-self.WORLD_DIMENSIONS[1]//200, self.WORLD_DIMENSIONS[1]//200+1):
                self.floor[(x, y)] = pyglet.sprite.Sprite(
                    img=self.resources["floor"],
                    x=x*100, y=y*100,
                    batch=self.world_batch,
                    group=self.layers["floor"]
                )

        self.borders = {
            "top": source.basic.Basic(
                self,
                -self.WORLD_DIMENSIONS[0]//2,
                self.WORLD_DIMENSIONS[1]//2,
                collider={
                    "type": "rect",
                    "x": 0, "y": 0,
                    "width": self.WORLD_DIMENSIONS[0]+100,
                    "height": 100,
                    "radius": 0
                },
                sprite=pyglet.shapes.Rectangle(
                    x=0, y=0,
                    width=self.WORLD_DIMENSIONS[0]+100,
                    height=100,
                    batch=self.world_batch,
                    group=self.layers["obstacle"]
                )
            ),
            "bottom": source.basic.Basic(
                self,
                -self.WORLD_DIMENSIONS[0]//2 - 100,
                -self.WORLD_DIMENSIONS[1]//2 - 100,
                collider={
                    "type": "rect",
                    "x": 0, "y": 0,
                    "width": self.WORLD_DIMENSIONS[0]+100,
                    "height": 100,
                    "radius": 0
                },
                sprite=pyglet.shapes.Rectangle(
                    x=0, y=0,
                    width=self.WORLD_DIMENSIONS[0]+100,
                    height=100,
                    batch=self.world_batch,
                    group=self.layers["obstacle"]
                )
            ),
            "left": source.basic.Basic(
                self,
                -self.WORLD_DIMENSIONS[0]//2 - 100,
                -self.WORLD_DIMENSIONS[1]//2,
                collider={
                    "type": "rect",
                    "x": 0, "y": 0,
                    "width": 100,
                    "height": self.WORLD_DIMENSIONS[1]+100,
                    "radius": 0
                },
                sprite=pyglet.shapes.Rectangle(
                    x=0, y=0,
                    width=100,
                    height=self.WORLD_DIMENSIONS[1]+100,
                    batch=self.world_batch,
                    group=self.layers["obstacle"]
                )
            ),
            "right": source.basic.Basic(
                self,
                self.WORLD_DIMENSIONS[0]//2,
                -self.WORLD_DIMENSIONS[1]//2 - 100,
                collider={
                    "type": "rect",
                    "x": 0, "y": 0,
                    "width": 100,
                    "height": self.WORLD_DIMENSIONS[1]+100,
                    "radius": 0
                },
                sprite=pyglet.shapes.Rectangle(
                    x=0, y=0,
                    width=100,
                    height=self.WORLD_DIMENSIONS[1]+100,
                    batch=self.world_batch,
                    group=self.layers["obstacle"]
                )
            )
        }

        self.window.push_handlers(self)
        self._position_camera()

    def loadResources(self):
        self.resources = {}
        self.resources["floor"] = pyglet.resource.image("resources/floor.png")

    def createLayers(self):
        self.layers = {}
        self.layers["world_master"] = pyglet.graphics.OrderedGroup(0)
        self.layers["floor"] = pyglet.graphics.OrderedGroup(
            1, parent=self.layers["world_master"]
        )
        self.layers["enemy"] = pyglet.graphics.OrderedGroup(
            2, parent=self.layers["world_master"]
        )
        self.layers["player_body"] = pyglet.graphics.OrderedGroup(
            3, parent=self.layers["world_master"]
        )
        self.layers["player_gun"] = pyglet.graphics.OrderedGroup(
            4, parent=self.layers["world_master"]
        )
        self.layers["player_hinge"] = pyglet.graphics.OrderedGroup(
            5, parent=self.layers["world_master"]
        )
        self.layers["projectile"] = pyglet.graphics.OrderedGroup(
            6, parent=self.layers["world_master"]
        )
        self.layers["obstacle"] = pyglet.graphics.OrderedGroup(
            7, parent=self.layers["world_master"]
        )

    def _position_camera(self):
        DEFAULT_SIZE = (1280, 720)

        scale = min(
            self.window.width/DEFAULT_SIZE[0],
            self.window.height/DEFAULT_SIZE[1]
        ) / 1.5

        self.world_camera.zoom = scale

        x = (-self.window.width//2)/scale
        y = (-self.window.height//2)/scale

        x += self.player.position.x
        y += self.player.position.y

        x = min(
            max(
                x, -self.WORLD_DIMENSIONS[0]//2 - 100
            ),
            self.WORLD_DIMENSIONS[0]//2 - (self.window.width)/scale + 100
        )

        y = min(
            max(
                y, -self.WORLD_DIMENSIONS[1]//2 - 100
            ),
            self.WORLD_DIMENSIONS[1]//2 - (self.window.height)/scale + 100
        )

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
        self.fps_display.draw()
        with self.world_camera:
            options = pymunk.pyglet_util.DrawOptions()
            self.space.debug_draw(options)
            self.world_batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_handler["x"] = x
        self.mouse_handler["y"] = y

    def run(self):
        pyglet.clock.schedule(self.update)
        pyglet.app.run()


if __name__ == "__main__":
    application = Application()
    application.run()
