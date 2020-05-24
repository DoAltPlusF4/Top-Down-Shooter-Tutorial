import pyglet
import pymunk
from pyglet.window import key

from . import basic


class Player(basic.Basic):
    def __init__(self, application):
        super().__init__(
            application,
            0, 0,
            body_type=pymunk.Body.DYNAMIC,
            collider={
                "type": "circle",
                "radius": 35,
                "offset": (0, 0)
            },
            sprite=pyglet.shapes.Circle(
                x=0, y=0,
                radius=40,
                batch=application.world_batch,
                group=application.layers["player_body"]
            )
        )

        self.gun_sprite = pyglet.shapes.Rectangle(
            x=self.position.x,
            y=self.position.y,
            width=70,
            height=20,
            color=(180, 180, 180),
            batch=self.application.world_batch,
            group=self.application.layers["player_gun"]
        )

        self.hinge_sprite = pyglet.shapes.Circle(
            x=self.position.x,
            y=self.position.y,
            radius=10,
            color=(128, 128, 128),
            batch=self.application.world_batch,
            group=self.application.layers["player_hinge"]
        )

    def update(self, dt):
        SPEED = 2000000

        vx, vy = 0, 0

        controls = {
            "up": (self.application.key_handler[key.UP] or self.application.key_handler[key.W]),
            "down": (self.application.key_handler[key.DOWN] or self.application.key_handler[key.S]),
            "left": (self.application.key_handler[key.LEFT] or self.application.key_handler[key.A]),
            "right": (self.application.key_handler[key.RIGHT] or self.application.key_handler[key.D]),
        }

        if (
            (
                controls["up"] ^
                controls["down"]
            ) and (
                controls["left"] ^
                controls["right"]
            )
        ):
            SPEED /= 2**0.5

        if controls["up"]:
            vy += SPEED*dt
        if controls["down"]:
            vy -= SPEED*dt
        if controls["left"]:
            vx -= SPEED*dt
        if controls["right"]:
            vx += SPEED*dt

        self.apply_force_at_local_point((vx, vy), (0, 0))

        self._update_sprite()

    def _update_sprite(self):
        super()._update_sprite()

        mouse_position = pymunk.Vec2d(
            *self.application.screenToWorld(
                self.application.mouse_handler["x"],
                self.application.mouse_handler["y"]
            )
        )
        rotation = (mouse_position-self.position).get_angle_degrees()

        position = pymunk.Vec2d(0, -10)
        position.rotate_degrees(rotation)

        self.gun_sprite.position = (
            self.position.x + position.x,
            self.position.y + position.y
        )

        self.gun_sprite.rotation = -rotation

        self.hinge_sprite.position = tuple(self.position)
