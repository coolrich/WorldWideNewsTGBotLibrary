import textwrap
from typing import List
from urllib.parse import urljoin
from wwntgbotlib.country_codes import CountryCodes
from wwntgbotlib.news_article import NewsArticle
from wwntgbotlib.news_scraper_interface import NewsScraperInterface
import logging

logger = logging.getLogger(__name__)


class UANewsScraper(NewsScraperInterface):
    def __init__(self, an_address: str = r"https://www.bbc.com/ukrainian"):
        super().__init__(an_address, CountryCodes.UA)

    def _parser(self, base_url, bs):
        news_list = []
        section_tags = bs.find('main').find_all('section')
        for section in section_tags:
            try:
                h3_tag = section.h3
                if h3_tag:
                    heading = h3_tag.text.replace('\n', ' ').title()
                    href_link = h3_tag.a['href']
                    full_url = urljoin(base_url.rstrip('/') + '/', href_link.lstrip('/'))
                    text = textwrap.fill(h3_tag.next_sibling.text.replace('\n', ''), 50)
                    logger.debug(f"Heading: {heading}")
                    logger.debug(f"Url: {full_url}")
                    logger.debug(f"Text: {text}\n")
                    news_list.append(NewsArticle(heading, text, full_url))
            except AttributeError as e:
                logger.error(f"AttributeError in bbc-ukraine parser: {e}")
                continue
        logger.debug("End of parse_bbc_ukraine")
        return news_list


class WorldNewsScraper(NewsScraperInterface):
    def __init__(self, an_address: str = r"https://www.bbc.com/news"):
        super().__init__(an_address, CountryCodes.WORLD)

    def _parser(self, base_url, bs) -> List[NewsArticle]:
        news_list = []
        posts = bs.find_all("div", {"data-testid": "edinburgh-card"})
        for post in posts:
            try:
                heading = post.find("h2").get_text(strip=True)
                text = post.find("p").get_text(strip=True) or ""  # Handle missing paragraphs
                full_url = urljoin(base_url.rstrip("/"), post.find("a")["href"].lstrip("/"))
                logging.info(f"Heading: {heading}\nUrl: {full_url}\nText: {text}\n")
                news_list.append(NewsArticle(heading, text, full_url))
            except AttributeError as e:
                logger.warning(f"AttributeError in bbc parser: {e}")
                continue
        logger.debug("End of parse_bbc")
        return news_list


if __name__ == '__main__':
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )
    logger = logging.getLogger()
    logger.debug("Start of the __main__() method in NewsScraper class")
    ns = WorldNewsScraper()
    data = ns.load_news()
    logger.debug(f"Count of {ns.country_code} news: {len(data[1])}")
    logger.debug("End of the __main__() method in NewsScraper class")
