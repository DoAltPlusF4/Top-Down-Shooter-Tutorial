import random

import pyglet
import pymunk
from pyglet.window import key

from . import basic, bullet
from . import constants as c


class Player(basic.Basic):
    def __init__(self, application):
        super().__init__(
            application,
            0, 0,
            body_type=pymunk.Body.DYNAMIC,
            collider={
                "type": "circle",
                "radius": 40,
                "offset": (0, 0),
                "id": c.COLLISION_TYPES["player"]
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
            radius=12,
            segments=50,
            color=(128, 128, 128),
            batch=self.application.world_batch,
            group=self.application.layers["player_hinge"]
        )

        self.application.window.push_handlers(self)

    def update(self, dt):
        vx, vy = 0, 0

        controls = {
            "up": (self.application.key_handler[key.UP] or self.application.key_handler[key.W]),
            "down": (self.application.key_handler[key.DOWN] or self.application.key_handler[key.S]),
            "left": (self.application.key_handler[key.LEFT] or self.application.key_handler[key.A]),
            "right": (self.application.key_handler[key.RIGHT] or self.application.key_handler[key.D]),
        }

        if controls["up"]:
            vy += c.PLAYER_SPEED
        if controls["down"]:
            vy -= c.PLAYER_SPEED
        if controls["left"]:
            vx -= c.PLAYER_SPEED
        if controls["right"]:
            vx += c.PLAYER_SPEED

        if (
            (
                controls["up"] ^
                controls["down"]
            ) and (
                controls["left"] ^
                controls["right"]
            )
        ):
            vx /= 2**0.5
            vy /= 2**0.5

        self.apply_force_at_local_point((vx, vy), (0, 0))

        self._updateSprite()

    def on_mouse_press(self, x, y, button, modifiers):

        mouse_position = pymunk.Vec2d(
            *self.application.screenToWorld(
                self.application.mouse_handler["x"],
                self.application.mouse_handler["y"]
            )
        )
        rotation = (mouse_position-self.position).get_angle_degrees()

        position = pymunk.Vec2d(
            60,
            0
        )
        position.rotate_degrees(rotation)

        velocity = pymunk.Vec2d(
            1000,
            random.randint(-10, 10)
        )
        velocity.rotate_degrees(rotation)

        self.application.projectiles.append(bullet.Bullet(
            application=self.application,
            x=self.position.x + position.x,
            y=self.position.y + position.y,
            size=10,
            vel=velocity,
            collision_type=c.COLLISION_TYPES["player_bullet"]
        ))
        self.application.resources["audio"]["shoot"].play()

    def _updateSprite(self):
        super()._updateSprite()

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
