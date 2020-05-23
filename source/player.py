import pyglet
from pyglet.window import key


class Player:
    def __init__(self, application):
        self.application = application

        self.sprite = pyglet.shapes.Circle(
            0, 0,
            radius=50,
            batch=self.application.world_batch
        )

        self.application.window.push_handlers(self)

    def update(self, dt):
        SPEED = 250

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
            self.sprite.y += SPEED*dt
        if self.application.key_handler[key.DOWN]:
            self.sprite.y -= SPEED*dt
        if self.application.key_handler[key.LEFT]:
            self.sprite.x -= SPEED*dt
        if self.application.key_handler[key.RIGHT]:
            self.sprite.x += SPEED*dt
