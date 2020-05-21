import pyglet

window = pyglet.window.Window(caption="Test", resizable=True)

label = pyglet.text.Label(
    text="Hello World!",
    x=window.width//2,
    y=window.height//2,
    anchor_x="center",
    anchor_y="center"
)


@window.event
def on_draw():
    window.clear()
    label.draw()


@window.event
def on_resize(width, height):
    label.x = width//2
    label.y = height//2


pyglet.app.run()
