import pyglet
from pyglet.window import key

import source


class Application:
    def __init__(self):
        self.window = pyglet.window.Window(
            width=1280,
            height=720,
            caption="Test",
            resizable=True
        )

        self.world_batch = pyglet.graphics.Batch()
        self.world_camera = source.camera.Camera(
            scroll_speed=0,
            min_zoom=0,
            max_zoom=float("inf")
        )

        self.key_handler = key.KeyStateHandler()
        self.window.push_handlers(self.key_handler)

        self.player = source.player.Player(self)

        self.centre_block = pyglet.shapes.Rectangle(
            x=0, y=60,
            width=40, height=40,
            batch=self.world_batch
        )

        self.window.push_handlers(self)

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

        x += self.player.sprite.x
        y += self.player.sprite.y

        if self.world_camera.position != (x, y):
            self.world_camera.position = (x, y)

    def update(self, dt):
        self.player.update(dt)
        self._position_camera()

    def on_draw(self):
        self.window.clear()
        with self.world_camera:
            self.world_batch.draw()

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()


if __name__ == "__main__":
    application = Application()
    application.run()
