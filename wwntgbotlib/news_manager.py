import pickle

from google.cloud import storage
from google.cloud.exceptions import NotFound

from wwntgbotlib.country_codes import CountryCodes
from wwntgbotlib.news_article import NewsArticle
from wwntgbotlib.news_scrapers import UANewsScraper, WorldNewsScraper
import logging

logger = logging.getLogger(__name__)


class NewsManager:
    bucket_name: str = "my_news_bucket"
    client = storage.Client()

    def __init__(self):
        self.__scrapers = [WorldNewsScraper(), UANewsScraper()]

    @staticmethod
    def get_filename(country_code: CountryCodes):
        return f"{country_code.name}-news.pkl"

    def update_news(self) -> dict[CountryCodes, int]:
        news_count_dict = {}
        for scraper in self.__scrapers:
            logger.debug("In task get_news")
            filename = NewsManager.get_filename(scraper.country_code)
            logger.info(f"Loading {scraper.country_code} news from {scraper.address}...")
            timestamp, news_list = scraper.load_news()
            NewsManager.save_to_gcs_bucket(filename, timestamp, news_list)
            news_count_dict[scraper.country_code] = len(news_list)
            logger.info(f"News has been saved to {filename} on GCS!")
            logger.info(f"Number of {scraper.country_code} news: {len(news_list)}")
            logger.debug(f"End of task {scraper.address}")
        return news_count_dict

    @staticmethod
    def save_to_gcs_bucket(filename, timestamp: float, news_list: list[NewsArticle]) -> None:
        """
        Save the given news articles to a specified Google Cloud Storage (GCS) bucket.

        Args:
            filename (str): The name of the file to be saved in the GCS bucket.
            timestamp (float): The timestamp associated with the news articles.
            news_list (list[NewsArticle]): A list of NewsArticle objects to be saved.

        Returns:
            None: This function does not return any value.

        Raises:
            None: This function does not raise any exceptions.
        """
        bucket_name = NewsManager.bucket_name
        bucket = NewsManager.client.bucket(bucket_name)
        blob = bucket.blob(filename)
        data = pickle.dumps((timestamp, news_list))
        blob.upload_from_string(data)

    @staticmethod
    def load_from_gcs_bucket(filename) -> (float, list[NewsArticle]):
        """
        A static method that loads data from a Google Cloud Storage (GCS) bucket.

        Args:
            filename (str): The name of the file to load from the GCS bucket.

        Returns:
            tuple: A tuple containing the timestamp (float) and a list of NewsArticle objects.

        Raises:
            NotFound: If the specified file is not found in the GCS bucket.
        """
        timestamp, news_list = None, None
        bucket_name = NewsManager.bucket_name
        bucket: storage.bucket.Bucket = NewsManager.client.bucket(bucket_name)
        blob = bucket.blob(filename)
        try:
            data_string = blob.download_as_string()
        except NotFound:
            return timestamp, news_list
        data = pickle.loads(data_string)
        timestamp, news_list = data
        return timestamp, news_list

    @staticmethod
    def get_articles_list_from_gcs_bucket() -> list:
        """
        Loads all files from a Google Cloud Storage (GCS) bucket and returns a list of articles.

        This static method takes no parameters and returns a list of articles. It assumes that the
        bucket name is stored in the `bucket_name` attribute of the `NewsManager` class.

        Returns:
            list: A list of articles, where each article is a deserialized object obtained from
            the files in the GCS bucket. Each element is a tuple of (timestamp, news_list, country_code).

        Raises:
            NotFound: If a file in the GCS bucket is not found or cannot be downloaded.

        """
        bucket_name = NewsManager.bucket_name
        bucket: storage.bucket.Bucket = NewsManager.client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        articles_list = []
        for blob in blobs:
            try:
                data_string = blob.download_as_string()
            except NotFound:
                continue
            data = pickle.loads(data_string)
            articles_list.append(data)
        return articles_list

    @staticmethod
    def get_news_data(country_code: CountryCodes) -> (float, list[NewsArticle], CountryCodes):
        """
        Retrieves the list of news articles and country codes for a given country code.

        Args:
            country_code (CountryCodes): The country code for which news articles are to be retrieved.

        Returns:
            tuple: A tuple containing the following elements:
                - float: The timestamp of the news articles.
                - list[NewsArticle]: The list of news articles.
                - CountryCodes: The country code.

        """
        filename = NewsManager.get_filename(country_code)
        news_data = NewsManager.load_from_gcs_bucket(filename)
        return news_data


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(filename)s - %(levelname)s - %(lineno)d - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )
    # logger = logging.getLogger(__name__)
    news_manager = NewsManager()
    print(news_manager.update_news())
