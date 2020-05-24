import random

import pyglet
import pymunk
import pymunk.pyglet_util
from pyglet.window import key, mouse

import source
from source import constants as c


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
        self.window.push_handlers(self)

        self.debug_mode = False

        self.fps_display = pyglet.window.FPSDisplay(window=self.window)

        self.space = pymunk.Space()
        self.space.damping = 0

        self.createCollisionHandlers()

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

        self.projectiles = []
        self.enemies = []

        self.player = source.player.Player(self)

        self.enemy_timer = 0

        self.floor = {}
        for x in range(-c.WORLD_DIMENSIONS[0]//200, c.WORLD_DIMENSIONS[0]//200+1):
            for y in range(-c.WORLD_DIMENSIONS[1]//200, c.WORLD_DIMENSIONS[1]//200+1):
                self.floor[(x, y)] = pyglet.sprite.Sprite(
                    img=self.resources["floor"],
                    x=x*100, y=y*100,
                    batch=self.world_batch,
                    group=self.layers["floor"]
                )

        self.borders = {
            "top": source.basic.Basic(
                self,
                -c.WORLD_DIMENSIONS[0]//2,
                c.WORLD_DIMENSIONS[1]//2,
                collider={
                    "type": "rect",
                    "x": 0, "y": 0,
                    "width": c.WORLD_DIMENSIONS[0]+100,
                    "height": 100,
                    "radius": 0,
                    "id": c.COLLISION_TYPES["obstacle"]
                },
                sprite=pyglet.shapes.Rectangle(
                    x=0, y=0,
                    width=c.WORLD_DIMENSIONS[0]+100,
                    height=100,
                    batch=self.world_batch,
                    group=self.layers["obstacle"]
                )
            ),
            "bottom": source.basic.Basic(
                self,
                -c.WORLD_DIMENSIONS[0]//2 - 100,
                -c.WORLD_DIMENSIONS[1]//2 - 100,
                collider={
                    "type": "rect",
                    "x": 0, "y": 0,
                    "width": c.WORLD_DIMENSIONS[0]+100,
                    "height": 100,
                    "radius": 0,
                    "id": c.COLLISION_TYPES["obstacle"]
                },
                sprite=pyglet.shapes.Rectangle(
                    x=0, y=0,
                    width=c.WORLD_DIMENSIONS[0]+100,
                    height=100,
                    batch=self.world_batch,
                    group=self.layers["obstacle"]
                )
            ),
            "left": source.basic.Basic(
                self,
                -c.WORLD_DIMENSIONS[0]//2 - 100,
                -c.WORLD_DIMENSIONS[1]//2,
                collider={
                    "type": "rect",
                    "x": 0, "y": 0,
                    "width": 100,
                    "height": c.WORLD_DIMENSIONS[1]+100,
                    "radius": 0,
                    "id": c.COLLISION_TYPES["obstacle"]
                },
                sprite=pyglet.shapes.Rectangle(
                    x=0, y=0,
                    width=100,
                    height=c.WORLD_DIMENSIONS[1]+100,
                    batch=self.world_batch,
                    group=self.layers["obstacle"]
                )
            ),
            "right": source.basic.Basic(
                self,
                c.WORLD_DIMENSIONS[0]//2,
                -c.WORLD_DIMENSIONS[1]//2 - 100,
                collider={
                    "type": "rect",
                    "x": 0, "y": 0,
                    "width": 100,
                    "height": c.WORLD_DIMENSIONS[1]+100,
                    "radius": 0,
                    "id": c.COLLISION_TYPES["obstacle"]
                },
                sprite=pyglet.shapes.Rectangle(
                    x=0, y=0,
                    width=100,
                    height=c.WORLD_DIMENSIONS[1]+100,
                    batch=self.world_batch,
                    group=self.layers["obstacle"]
                )
            )
        }
        self._position_camera()

    def loadResources(self):
        self.resources = {}
        self.resources["floor"] = pyglet.resource.image("resources/floor.png")

        pyglet.media.synthesis.Silence(0.5).play()
        self.resources["audio"] = {}
        self.resources["audio"]["shoot"] = pyglet.media.load(
            "resources/shoot.wav", streaming=False
        )

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

    def createCollisionHandlers(self):
        h = self.space.add_collision_handler(
            c.COLLISION_TYPES["player_bullet"],
            c.COLLISION_TYPES["obstacle"]
        )

        def begin(arbiter, space, data):
            shapes = arbiter.shapes
            bullet = shapes[0]

            pyglet.clock.unschedule(bullet.body.update)
            self.space.remove(bullet.body, bullet)

            try:
                bullet.body.sprite.delete()
            except AttributeError:
                pass

            try:
                self.projectiles.remove(bullet.body)
            except ValueError:
                pass

            return False

        h.begin = begin

        h = self.space.add_collision_handler(
            c.COLLISION_TYPES["player_bullet"],
            c.COLLISION_TYPES["enemy"]
        )

        def post_solve(arbiter, space, data):
            shapes = arbiter.shapes
            bullet = shapes[0]
            enemy = shapes[1]

            pyglet.clock.unschedule(bullet.body.update)
            self.space.remove(bullet.body, bullet)

            try:
                bullet.body.sprite.delete()
            except AttributeError:
                pass

            try:
                self.projectiles.remove(bullet.body)
            except ValueError:
                pass

            radius = enemy.radius
            space.remove(enemy)
            del enemy.body.collider
            enemy.body.collider = pymunk.Circle(
                enemy.body,
                radius=radius - 20
            )
            enemy.body.collider.collision_type = c.COLLISION_TYPES["enemy"]
            space.add(enemy.body.collider)
            enemy.body.sprite.radius = enemy.body.collider.radius

            if enemy.body.collider.radius < 20:
                pyglet.clock.unschedule(enemy.body.update)
                self.space.remove(enemy.body, enemy.body.collider)

                try:
                    enemy.body.sprite.delete()
                except AttributeError:
                    pass

                try:
                    self.enemies.remove(enemy.body)
                except ValueError:
                    pass

        h.post_solve = post_solve

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
                x, -c.WORLD_DIMENSIONS[0]//2 - 100
            ),
            c.WORLD_DIMENSIONS[0]//2 - (self.window.width)/scale + 100
        )

        y = min(
            max(
                y, -c.WORLD_DIMENSIONS[1]//2 - 100
            ),
            c.WORLD_DIMENSIONS[1]//2 - (self.window.height)/scale + 100
        )

        self.world_camera.position = (x, y)

    def screenToWorld(self, x, y):

        world_x = self.world_camera.offset_x
        world_x += x/self.world_camera.zoom

        world_y = self.world_camera.offset_y
        world_y += y/self.world_camera.zoom

        return (world_x, world_y)

    def update(self, dt):

        self.enemy_timer += dt
        if self.enemy_timer > c.ENEMY_FREQUENCY:
            self.enemy_timer = 0
            self.enemies.append(source.enemy.Enemy(
                self,
                random.randint(
                    -c.WORLD_DIMENSIONS[0]//2 + 100,
                    c.WORLD_DIMENSIONS[0]//2 - 100
                ),
                random.randint(
                    -c.WORLD_DIMENSIONS[1]//2 + 100,
                    c.WORLD_DIMENSIONS[1]//2 - 100
                ),
                random.randint(*c.ENEMY_SIZE_RANGE)
            ))

        self.space.step(dt)
        self.player.update(dt)
        self._position_camera()

    def on_draw(self):
        self.window.clear()
        self.fps_display.draw()
        with self.world_camera:
            self.world_batch.draw()
            if self.debug_mode:
                options = pymunk.pyglet_util.DrawOptions()
                self.space.debug_draw(options)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_handler["x"] = x
        self.mouse_handler["y"] = y

    def on_key_press(self, button, modifiers):
        if button == key.F3:
            self.debug_mode = not self.debug_mode

    def run(self):
        pyglet.clock.schedule(self.update)
        pyglet.app.run()


if __name__ == "__main__":
    application = Application()
    application.run()
