from datetime import datetime

from textual import on, work
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Input, Label, Static, TabPane

from zet import api, config
from zet.entities import IncomingTrip, Stop
from zet.output import format_time
from zet.widgets import Title


class StopsPane(TabPane):
    BINDINGS = [
        Binding("f", "toggle_favourite", "Toggle Favourite"),
    ]

    DEFAULT_CSS = """
    #stops_search {
        margin-bottom: 1;
    }
    #stops_list {
        width: 1fr;
    }
    #stops_details {
        width: 1fr;
        background: $surface;
        border-left: thick $secondary;
    }
    """

    def __init__(self, stops: list[Stop]) -> None:
        super().__init__("Stops", id="stops_pane")
        self.stops = stops
        self.stops_map = {s["id"]: s for s in stops}
        self.selected_stop: Stop | None = None
        self.favourite_stop_ids = set(config.load_config()["favourite_stops"])

    def compose(self):
        yield Vertical(
            Input(id="stops_search", placeholder="Search stops"),
            Horizontal(
                Vertical(
                    Title("Stops"),
                    DataTable(cursor_type="row", id="stops_list"),
                ),
                StopDetails(id="stops_details"),
            ),
        )

    def on_mount(self):
        dt = self.query_one(DataTable)
        dt.add_column("F", key="favourite")
        dt.add_column("ID", key="id")
        dt.add_column("Name", key="name")
        dt.add_column("Routes", key="routes")

        for stop in self._get_filtered_stops():
            self.add_stop_row(dt, stop)

    @on(Input.Changed, "#stops_search")
    def on_search(self, message: Input.Changed):
        query = message.value.strip().lower()
        dt = self.query_one(DataTable)
        dt.clear()
        for stop in self._get_filtered_stops(query):
            self.add_stop_row(dt, stop)

    def _get_filtered_stops(self, query: str = ""):
        def sort_key(stop: Stop):
            # This places favourited stops on top
            return stop["id"] not in self.favourite_stop_ids

        query = query.strip()
        if query:
            return sorted(
                (s for s in self.stops if query in s["normalizedSearchName"]),
                key=sort_key,
            )
        else:
            return sorted(self.stops, key=sort_key)

    @on(DataTable.RowHighlighted, "#stops_list")
    def on_stop_selected(self, message: DataTable.RowHighlighted):
        assert message.row_key.value is not None
        stop = self.stops_map[message.row_key.value]
        self.selected_stop = stop
        self.query_one(StopDetails).stop = stop

    def add_stop_row(self, dt: DataTable, stop: Stop):
        favourite = "*" if stop["id"] in self.favourite_stop_ids else ""
        routes = ", ".join([t["routeCode"] for t in stop["trips"]])
        dt.add_row(
            favourite,
            stop["id"],
            stop["name"],
            routes,
            key=stop["id"],
        )

    def action_toggle_favourite(self):
        if stop := self.selected_stop:
            if stop["id"] in self.favourite_stop_ids:
                config.remove_favourite_stop(stop)
            else:
                config.add_favourite_stop(stop)

            self.favourite_stop_ids = set(config.load_config()["favourite_stops"])
            is_favourite = stop["id"] in self.favourite_stop_ids

            # Update table
            dt = self.query_one(DataTable)
            dt.update_cell(stop["id"], "favourite", "*" if is_favourite else "")

            # Re-sort the table and reselect the row
            self._sort_by_favourite(dt)
            dt.move_cursor(row=dt.get_row_index(stop["id"]))

    def _sort_by_favourite(self, dt: DataTable):
        dt = self.query_one(DataTable)
        dt.sort("favourite", key=lambda f: f == "")


class StopDetails(Widget):
    stop: reactive[Stop | None] = reactive(None, recompose=True)

    def compose(self):
        if self.stop is not None:
            yield Title(f"{self.stop['name']} ({self.stop['id']})")
            yield Vertical(id="stop_trips")
            self.load_trips(self.stop["id"])
        else:
            yield Label("No stop selected")

    @work(exclusive=True)
    async def load_trips(self, stop_id: str):
        response = await api.get_incoming_trips(self.app.session, stop_id)  # type: ignore
        if response.ok:
            trips = response.json()
            widget = IncomingTrips(trips)
            self.query_one("#stop_trips", Vertical).mount(widget)


class IncomingTrips(Widget):
    def __init__(self, trips: list[IncomingTrip]) -> None:
        super().__init__()
        self.trips = trips

    def compose(self):
        dt = DataTable(cursor_type="row", id="incoming_trips_table")
        dt.add_columns("Route", "Headsign", "Arrival", "Tracked?")
        for trip in self.trips:
            dt.add_row(
                trip["routeShortName"],
                trip["headsign"],
                format_time(trip["expectedArrivalDateTime"]),
                "[green]Yes[/]" if trip["hasLiveTracking"] else "[gray]No[/]",
            )

        yield dt

        # TODO: make this update as time passes
        now = datetime.now()
        yield Static()
        yield Static(f"Fetched: {now}")
