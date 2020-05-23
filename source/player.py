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
                "radius": 50,
                "offset": (0, 0)
            },
            sprite=pyglet.shapes.Circle(
                x=0, y=0,
                radius=50,
                batch=application.world_batch
            )
        )
        self.sprite.group = self.application.layers["player_body"]

        self.gun_sprite = pyglet.shapes.Rectangle(
            x=self.position.x,
            y=self.position.y,
            width=70,
            height=20,
            color=(200, 200, 200),
            batch=self.application.world_batch,
            group=self.application.layers["player_gun"]
        )

    def update(self, dt):
        SPEED = 2000000

        vx, vy = 0, 0

        if (
            (
                self.application.key_handler[key.UP] ^
                self.application.key_handler[key.DOWN]
            ) and (
                self.application.key_handler[key.LEFT] ^
                self.application.key_handler[key.RIGHT]
            )
        ):
            SPEED /= 2**0.5

        if self.application.key_handler[key.UP]:
            vy += SPEED*dt
        if self.application.key_handler[key.DOWN]:
            vy -= SPEED*dt
        if self.application.key_handler[key.LEFT]:
            vx -= SPEED*dt
        if self.application.key_handler[key.RIGHT]:
            vx += SPEED*dt

        self.apply_force_at_local_point((vx, vy), (0, 0))

        self._update_sprite()

    def _update_sprite(self):
        super()._update_sprite()
        self.gun_sprite.x = self.position.x
        self.gun_sprite.y = self.position.y
        mouse_position = pymunk.vec2d.Vec2d(
            *self.application.screenToWorld(
                self.application.mouse_handler["x"],
                self.application.mouse_handler["y"]
            )
        )
        rotation = self.position.get_angle_degrees_between(mouse_position)
        self.gun_sprite.rotation = rotation
