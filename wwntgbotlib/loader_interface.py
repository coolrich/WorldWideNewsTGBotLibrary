from typing import List

from wwntgbotlib.country_codes import CountryCodes
from wwntgbotlib.news_article import NewsArticle


class LoaderInterface:
    def load_news(self) -> (CountryCodes, List[NewsArticle]):
        pass
