import pika

from pika.adapters.blocking_connection import BlockingChannel
from pika.connection import URLParameters
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy.utils.misc import load_object

from crawler_utils.rabbitmq.schemas import CrawlRequestSchema, CrawlResponseSchema

RABBITMQ_HOST = 'amqp://guest:guest@localhost:5672'


def connect_to_rabbitmq(parameters: URLParameters) -> BlockingChannel:
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    return channel


def get_from_crawler_or_connect(
    crawler: Crawler, parameters: URLParameters
):
    if hasattr(crawler, "rabbitmq_channel") and isinstance(
        crawler.rabbitmq_channel,
        BlockingChannel,  # type: ignore
    ):
        channel = crawler.rabbitmq_channel  # type: ignore
    else:
        channel = connect_to_rabbitmq(parameters)
        setattr(crawler, "rabbitmq_channel", channel)
    return channel


def make_connection_parameters_from_settings(
    settings: Settings,
) -> URLParameters:
    url = settings.get("RABBITMQ_HOST", RABBITMQ_HOST)
    assert url

    params = URLParameters(url)
    return params


def queue_name_from_settings(settings: Settings, settings_name: str):
    queue_name = settings.get(settings_name)
    assert queue_name
    return queue_name


def schema_from_settings(
    settings: Settings,
    setting_name: str,
    default: type[CrawlRequestSchema] | type[CrawlResponseSchema],
):
    schema = load_object(settings.get(setting_name, default))
    assert schema
    return schema
