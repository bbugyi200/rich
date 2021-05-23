from typing import TYPE_CHECKING

from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live

from . import events
from ._context import active_app
from .message_pump import MessagePump
from .widget import Widget
from .widgets.header import Header

if TYPE_CHECKING:
    from .app import App


class View(MessagePump):
    @property
    def app(self) -> "App":
        return active_app.get()

    @property
    def console(self) -> Console:
        return active_app.get().console

    async def on_resize(self, event: events.Resize) -> None:
        pass


class LayoutView(View):
    layout: Layout

    def __init__(
        self, layout: Layout = None, title: str = "Layout Application"
    ) -> None:
        self.title = title
        if layout is None:
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3, ratio=0),
                Layout(name="main", ratio=1),
                Layout(name="footer", size=1, ratio=0),
            )
            layout["main"].split_row(
                Layout(name="left", size=30, visible=True),
                Layout(name="body", ratio=1),
                Layout(name="right", size=30, visible=False),
            )
        self.layout = layout
        super().__init__()

    def __rich__(self) -> RenderableType:
        return self.layout

    async def on_create(self, event: events.Created) -> None:
        await self.mount(Header(self.title))

    async def mount(self, widget: Widget, *, slot: str = "main") -> None:
        self.layout[slot].update(widget)
        await self.app.add(widget)
        await widget.post_message(events.Mount(sender=self))

    async def on_startup(self, event: events.Startup) -> None:
        await self.mount(Header(self.title), slot="header")