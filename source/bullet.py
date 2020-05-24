import pyglet
import pymunk

from . import basic


class Bullet(basic.Basic):
    def __init__(self, application, x, y, size, vel, collision_type):
        super().__init__(
            application,
            x=x, y=y, body_type=pymunk.Body.DYNAMIC,
            collider={
                "type": "circle",
                "radius": size,
                "offset": (0, 0),
                "id": collision_type
            },
            sprite=pyglet.shapes.Circle(
                x=0, y=0,
                radius=size,
                color=(255, 50, 50),
                batch=application.world_batch,
                group=application.layers["projectile"]
            )
        )

        def zero_resistance(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, 1, dt)

        self.velocity_func = zero_resistance

        self.apply_impulse_at_local_point(vel)

        pyglet.clock.schedule_interval(self.update, 1/120)

    def update(self, dt):
        self._updateSprite()
