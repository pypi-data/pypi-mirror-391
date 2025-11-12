from dateutil.parser import parse
from textual.containers import VerticalScroll
from textual.widgets import Markdown, TabPane

from zet.entities import News


class NewsPane(TabPane):
    def __init__(self, news: list[News]) -> None:
        super().__init__("News", id="news_pane")
        self.news = news

    def compose(self):
        markdown = "\n".join(self._news_generator())
        with VerticalScroll():
            yield Markdown(markdown)

    def _news_generator(self):
        first = True
        for item in self.news:
            if not first:
                yield ""
                yield "---"
                yield ""
            yield f"**{item['title']}**"
            yield ""
            yield item["description"]
            yield ""
            yield item["link"]
            yield ""
            yield parse(item["datePublished"]).strftime("%d.%m.%Y %H:%M")
            first = False
