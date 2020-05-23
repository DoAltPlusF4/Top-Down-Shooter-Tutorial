import pyglet
import pymunk


class Basic(pymunk.Body):
    def __init__(
        self,
        application,
        x, y,
        body_type=pymunk.Body.STATIC,
        collider=None,
        sprite=None
    ):
        self.application = application

        super().__init__(
            mass=1,
            moment=float("inf"),
            body_type=body_type
        )
        self.position = (x, y)
        self.application.space.add(self)
        if collider is not None:
            if collider["type"] == "rect":
                self.collider = pymunk.Poly(
                    body=self,
                    vertices=[
                        (
                            collider["x"],
                            collider["y"]
                        ),
                        (
                            collider["x"]+collider["width"],
                            collider["y"]
                        ),
                        (
                            collider["x"]+collider["width"],
                            collider["y"]+collider["height"]
                        ),
                        (
                            collider["x"],
                            collider["y"]+collider["height"]
                        )
                    ],
                    radius=collider["radius"]
                )
            elif collider["type"] == "circle":
                self.collider = pymunk.Circle(
                    body=self,
                    radius=collider["radius"],
                    offset=collider["offset"]
                )
            self.application.space.add(self.collider)

        if sprite is not None:
            self.sprite = sprite

    def _update_sprite(self):
        if hasattr(self, "sprite"):
            self.sprite.x = self.position.x
            self.sprite.y = self.position.y
