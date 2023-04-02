import os

import common
from urllib.parse import urljoin

AUDIO_BASE_PATH = "www/asset/"
FEED_BASE_PATH = "www/feed/"
WATCHLIST_PATH = "config/watchlist.yaml"
CONFIG_PATH = "config/config.yaml"


def get_audio_base_path():
    return AUDIO_BASE_PATH


def get_feed_base_path():
    return FEED_BASE_PATH


def get_watchlist_path():
    return WATCHLIST_PATH


def get_feed_path(channel_id):
    return os.path.join(get_feed_base_path(), channel_id, "feed.xml")


def get_audio_dir_path(channel_id):
    return os.path.join(get_audio_base_path(), channel_id)


def build_audio_api_path(channel_id, audio_path):
    audio_name = os.path.basename(audio_path)
    return build_url("audio/{}/{}".format(channel_id, audio_name))


def build_url(path):
    config = common.load_yml(CONFIG_PATH)
    host = config["host"]
    return urljoin(host, path)
