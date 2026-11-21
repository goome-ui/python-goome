from .core import CLOSE, QUIT, Pacer, open_app


class App(object):
    """A ready made app loop on top of Ui. Decorate a draw function with `@app.frame`, then `app.run()`.

    Args:
        title, width, height: the window.
        flags: APP_* flags for the root panel.
        fps: frame rate while something moves.
        idle_ms: how long to wait for an event when nothing is changing.
        light: start with the light theme.
        **opts: more options for `open_app()`.
    """
    _dirty = 0

    def __init__(self, title="goome", width=960, height=640, flags=0, fps=60, idle_ms=500, light=False, **opts):
        self.title = title
        self.width = width
        self.height = height
        self.flags = flags
        self.fps = fps
        self.idle_ms = idle_ms
        self.light = light
        self.opts = opts
        self.animate = False
        self.running = False
        self.frames = 0
        self.g = None
        self.ui = None
        self._draw = None
        self._handlers = []
        self._close = None
        self._start = None

    def frame(self, fn):
        """Decorator that sets the draw function, called with the Ui every frame."""
        self._draw = fn
        return fn

    def event(self, fn):
        """Decorator that adds an event handler. Return True to say you handled it and keep it from the ui."""
        self._handlers.append(fn)
        return fn

    def on_close(self, fn):
        """Decorator for a function called when the window is closed. Return False to stay open."""
        self._close = fn
        return fn

    def on_start(self, fn):
        """Decorator for a function called once after the window opens."""
        self._start = fn
        return fn

    def redraw(self):
        """Ask for another frame, for when something changed outside an event."""
        self._dirty = max(self._dirty, 1)

    def quit(self):
        """Stop the loop after this frame."""
        self.running = False

    def _handle(self, ev):
        for h in self._handlers:
            if h(ev):
                return
        self.ui.feed(ev)
        if ev.type == QUIT:
            self.running = False
        elif ev.type == CLOSE and (self._close is None or self._close() is not False):
            self.running = False

    def _paint(self):
        ui = self.ui
        if ui.begin(0) is None:
            return
        try:
            with ui.app(self.title, self.flags):
                if self._draw is not None:
                    self._draw(ui)
        finally:
            ui.end()
        self.frames += 1

    def start(self):
        """Open the window and ui without running the loop, for when you run it yourself with `step()`."""
        g = open_app(self.title, self.width, self.height, **self.opts)
        ui = g.ui()
        self.g, self.ui = g, ui
        if self.light:
            ui.theme.light()
        self._every = g.backend_name.split()[0] == "test"
        self._pace = Pacer(self.fps)
        self._dirty = 2
        self.running = True
        if self._start is not None:
            self._start()
        return self

    def step(self, wait=True):
        """Run one loop turn and return False once the app is done. `wait=False` doesnt wait for events."""
        ui = self.ui
        busy = self._every or self.animate or self._dirty > 0 or ui.animating
        if self._dirty > 0:
            self._dirty -= 1
        timeout = (self._pace.wait() if busy else self.idle_ms) if wait else 0
        for ev in self.g.events(timeout):
            self._handle(ev)
            self._dirty = max(self._dirty, 1)
            if not self.running:
                return False
        if self.running and (busy or self._dirty > 0):
            self._paint()
        return self.running

    def stop(self):
        """Close the window and ui."""
        self.running = False
        g, ui = self.g, self.ui
        self.g, self.ui = None, None
        if ui is not None:
            ui.close()
        if g is not None:
            g.close()

    def run(self, draw=None):
        """Open the window, run until it closes, then clean up. `draw` is the same as the `frame` decorator."""
        if draw is not None:
            self._draw = draw
        self.start()
        try:
            while self.step():
                pass
        finally:
            self.stop()
