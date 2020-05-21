import pyglet
from pyglet.window import key


class Player:
    def __init__(self, application):
        self.application = application

        self.sprite = pyglet.shapes.Circle(
            self.application.window.width//2,
            self.application.window.height//2,
            radius=50
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

    def draw(self):
        self.sprite.draw()


class Application:
    def __init__(self):
        self.window = pyglet.window.Window(caption="Test", resizable=True)

        self.key_handler = key.KeyStateHandler()
        self.window.push_handlers(self.key_handler)

        self.player = Player(self)

        self.window.push_handlers(self)

    def update(self, dt):
        self.player.update(dt)

    def on_draw(self):
        self.window.clear()
        self.player.draw()

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()


if __name__ == "__main__":
    application = Application()
    application.run()
