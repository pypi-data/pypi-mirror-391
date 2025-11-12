import logging

from textual import on, work
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Input, TabPane

from zet import api
from zet.entities import Route, Trip
from zet.output import format_time
from zet.widgets import Title

logger = logging.getLogger(__name__)


class RoutesPane(TabPane):
    BINDINGS = [
        Binding("f", "toggle_favourite", "Toggle Favourite"),
    ]

    DEFAULT_CSS = """
    #routes_search {
        margin-bottom: 1;
    }
    #routes_list {
        width: 1fr;
    }
    #routes_departures_a {
        border-left: thick $secondary;
        width: 1fr;
    }
    #routes_departures_b {
        border-left: thick $secondary;
        width: 1fr;
    }
    """

    def __init__(self, routes: list[Route]) -> None:
        super().__init__("Routes", id="routes_pane")
        self.routes = routes
        self.routes_map = {s["id"]: s for s in routes}
        self.selected_route: Route | None = None

    def compose(self):
        yield Vertical(
            Input(id="routes_search", placeholder="Search routes"),
            Horizontal(
                Vertical(
                    Title("Routes"),
                    DataTable(cursor_type="row", id="routes_list"),
                ),
                RouteDepartures(title="Departures A", direction=0, id="routes_departures_a"),
                RouteDepartures(title="Departures B", direction=1, id="routes_departures_b"),
            ),
        )

    @on(Input.Changed, "#routes_search")
    def on_search(self, message: Input.Changed):
        query = message.value.strip().lower()
        dt = self.query_one("#routes_list", DataTable)
        dt.clear()
        for route in self.routes:
            if query in route["normalizedSearchName"]:
                self.add_route_row(dt, route)

    @on(DataTable.RowHighlighted, "#routes_list")
    def on_route_highlighted(self, message: DataTable.RowHighlighted):
        if message.row_key.value is not None:
            route_id = message.row_key.value
            route = self.routes_map[route_id]
            self.selected_route = route
            self.load_route_trips(route_id)

    @work(exclusive=True)
    async def load_route_trips(self, route_id: str):
        response = await api.get_route_trips(self.app.session, route_id)  # type: ignore
        if response.ok:
            trips = response.json()
            logger.error(f"Loaded {len(trips)} trips for route {route_id}")

            self.query_one("#routes_departures_a", RouteDepartures).trips = trips
            self.query_one("#routes_departures_b", RouteDepartures).trips = trips
        else:
            # TODO: handle error
            logger.error("Failed loading trips")

    def on_mount(self):
        dt = self.query_one("#routes_list", DataTable)
        dt.add_columns("ID", "From", "To")
        for route in self.routes:
            self.add_route_row(dt, route)

    def add_route_row(self, dt: DataTable, route: Route):
        # For circular trips the departure is null
        departure = (
            route["departureHeadsign"]
            if route["departureHeadsign"]
            else route["destinationHeadsign"]
        )

        dt.add_row(
            route["id"],
            departure,
            route["destinationHeadsign"],
            key=route["id"],
        )

    def action_toggle_favourite(self):
        pass  # TODO


class RouteDepartures(Widget):
    trips: reactive[list[Trip] | None] = reactive(None)

    DEFAULT_CSS = """
    DataTable {
        width: auto;
    }
    """

    def __init__(self, title: str, direction: int, id):
        self.title = title
        self.direction = direction
        super().__init__(id=id)

    def compose(self):
        dt = DataTable(cursor_type="row")
        dt.add_columns("Destination", "Departure", "Arrival", "Tracked?")
        yield Vertical(Title(self.title), dt)

    def watch_trips(self, _, new_trips: list[Trip] | None) -> None:
        dt = self.query_one(DataTable)
        dt.clear(columns=False)

        if new_trips:
            for trip in new_trips:
                if trip["direction"] == self.direction:
                    dt.add_row(
                        trip["headsign"],
                        format_time(trip["departureDateTime"]),
                        format_time(trip["arrivalDateTime"]),
                        "[green]Yes[/]" if trip["hasLiveTracking"] else "[gray]No[/]",
                        label="*" if trip["tripStatus"] == 2 else "",
                    )
