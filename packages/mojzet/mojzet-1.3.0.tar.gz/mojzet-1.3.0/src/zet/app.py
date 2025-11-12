import asyncio
from os import path
from pathlib import Path

from aiohttp import ClientSession
from textual import work
from textual.app import App
from textual.binding import Binding
from textual.screen import Screen
from textual.types import CSSPathType
from textual.widgets import (
    Footer,
    Header,
    Static,
    TabbedContent,
)

from zet import api
from zet.config import get_stylesheet_path
from zet.entities import News, Route, Stop
from zet.panes.news import NewsPane
from zet.panes.routes import RoutesPane
from zet.panes.stops import StopsPane


class ZetApp(App[None]):
    def __init__(self, session: ClientSession):
        super().__init__(css_path=self._get_css_paths())
        self.session = session
        self.animation_level = "none"

    def _get_css_paths(self) -> CSSPathType:
        base_css = Path("./app.css")
        user_css = get_stylesheet_path()
        return [base_css, user_css] if path.exists(user_css) else [base_css]

    async def on_mount(self):
        self.push_screen(LoadingScreen())
        self.load()

    @work
    async def load(self):
        stops, routes, news = await asyncio.gather(
            api.get_stops(self.session),
            api.get_routes(self.session),
            api.get_newsfeed(self.session),
        )
        self.switch_screen(MainScreen(stops.json(), routes.json(), news.json()))


class MainScreen(Screen):
    BINDINGS = [
        Binding("f1", "goto_stops", "Stops"),
        Binding("f2", "goto_routes", "Routes"),
        Binding("f3", "goto_news", "News"),
    ]

    def __init__(self, stops: list[Stop], routes: list[Route], news: list[News]) -> None:
        super().__init__()
        self.stops = stops
        self.routes = routes
        self.news = news

    def compose(self):
        with TabbedContent():
            yield StopsPane(self.stops)
            yield RoutesPane(self.routes)
            yield NewsPane(self.news)
        yield Footer()

    def action_goto_stops(self):
        self.query_one(TabbedContent).active = "stops_pane"

    def action_goto_routes(self):
        self.query_one(TabbedContent).active = "routes_pane"

    def action_goto_news(self):
        self.query_one(TabbedContent).active = "news_pane"


class LoadingScreen(Screen):
    TITLE = "Loading"

    def compose(self):
        yield Header()
        yield Static("Loading...")
        yield Footer()
