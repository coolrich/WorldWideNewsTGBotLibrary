import logging
import time
from abc import ABC, abstractmethod
from typing import List, Any

import requests
from bs4 import BeautifulSoup
from wwntgbotlib.country_codes import CountryCodes
from wwntgbotlib.loader_interface import LoaderInterface
from wwntgbotlib.news_article import NewsArticle
import logging

logger = logging.getLogger(__name__)


class NewsScraperInterface(ABC, LoaderInterface):
    def __init__(self, address: str, country: CountryCodes):
        self.__address = address
        self.__country = country

    # Create properties for address
    @property
    def address(self):
        return self.__address

    # Create properties for country
    @property
    def country_code(self):
        return self.__country

    @staticmethod
    def __get_html_source(url) -> str:
        logger.debug("Start of __get_html_source")
        response = requests.get(url)
        if response.status_code == 200:
            page_source = response.text
            logging.info(f"Successfully fetched HTML source from {url}")
        else:
            logging.info("Failed to fetch HTML source: {}".format(response.status_code))
            page_source = None

        logger.debug("End of __get_html_source")
        return page_source

    @staticmethod
    def __get_html_source_from_folder(absolute_file_path):
        logger.debug("Start of __get_html_source_from_folder")
        encoding = "UTF-8"
        with open(absolute_file_path, "r", encoding=encoding) as f:
            html_str = f.read()
        page_source = html_str
        logger.debug(f"End of __get_html_source_from_folder: {absolute_file_path}")
        return page_source

    # add hints to method
    def __parse_news(self, base_url, html_source) -> List[NewsArticle]:
        logger.debug(f"Start of parsing {base_url}")
        base_url = base_url.split('.com')[0] + '.com'
        bs = BeautifulSoup(html_source, 'html5lib')
        try:
            news_list: list[NewsArticle] = self._parser(base_url, bs)
            return news_list
        except Exception as e:
            logger.error(f"An unexpected error when parsing {base_url}: {e}")
        logger.debug(f"End of parsing {base_url}")
        return []

    @abstractmethod
    def _parser(self, base_url: str, bs: BeautifulSoup) -> List[NewsArticle]:
        pass

    def load_news(self) -> (float, List[NewsArticle]):
        """
        Load news from a specified address.

        Returns:
            A tuple containing the Countries object and a list of News objects.
        """
        if self.address.startswith("http"):
            page = self.__get_html_source(self.address)
        else:
            page = self.__get_html_source_from_folder(self.address)
        news_list = self.__parse_news(self.address, page)
        timestamp = time.time()
        return timestamp, news_list
