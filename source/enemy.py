import pyglet
import pymunk

from . import basic
from . import constants as c


class Enemy(basic.Basic):
    def __init__(self, application, x, y, size):
        super().__init__(
            application,
            body_type=pymunk.Body.DYNAMIC,
            collider={
                "type": "circle",
                "radius": size,
                "offset": (0, 0),
                "id": c.COLLISION_TYPES["enemy"]
            },
            sprite=pyglet.shapes.Circle(
                x=0, y=0,
                radius=size,
                color=(255, 0, 0),
                batch=application.world_batch,
                group=application.layers["enemy"]
            ),
            x=x, y=y
        )

        pyglet.clock.schedule_interval(self.update, 1/120)

    def kill(self):
        pyglet.clock.unschedule(self.update)
        self.sprite.delete()
        self.application.enemies.remove(self)
        self.application.space.remove(self, self.collider)

    def update(self, dt):
        target = self.application.player.position
        relative_position = target-self.position
        rotation = relative_position.get_angle_degrees()

        velocity = pymunk.Vec2d(
            c.ENEMY_SPEED,
            0
        )

        self.apply_force_at_local_point(
            velocity.rotated_degrees(rotation), (0, 0)
        )

        self._updateSprite()
