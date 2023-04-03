import atexit
import logging
import os
import signal
import sys

from apscheduler.schedulers.background import BackgroundScheduler

import config
import crawler
import downloader
import feed_manager


def fetch_one_channel(channel):
    feed_entry = crawler.crawl_channel(channel)
    try:
        feed_manager.update_feed(channel, feed_entry)
    except Exception as e:
        logging.error(f"Failed to update feed for {channel.get_channel_id()}: {e}", exc_info=True)
        raise ValueError(f"Failed to update feed for {channel.get_channel_id()}: {e}")


def fetch_update_of_channel(channel_id):
    fetch_one_channel(feed_manager.watchlist_manager().get_channel(channel_id))


def fetch_all_channel():
    logging.info("Start fetching all channels...")
    for feed_entry in feed_manager.watchlist_manager().get_all_channels():
        fetch_one_channel(feed_entry)


def add_one_channel(rss_url):
    channel = crawler.fetch_channel_info(rss_url)
    channel.validate()
    feed_manager.watchlist_manager().set_channel(channel)
    fetch_one_channel(channel)
    return channel.get_channel_id()


def update_one_channel(channel_id, rss_url, description, title):
    channel = feed_manager.watchlist_manager().get_channel(channel_id)
    channel.title = title
    channel.rss = rss_url
    channel.description = description
    feed_manager.watchlist_manager().set_channel(channel)


def delete_one_channel(channel_id):
    feed_manager.watchlist_manager().delete_channel(channel_id)


def query_channels():
    return feed_manager.watchlist_manager().get_all_channels()


def get_feed_path(channel_id):
    return config.get_feed_path(channel_id=channel_id)


def get_audio_directory(channel_id):
    return os.path.join(config.get_audio_dir_path(channel_id))


def setup_signal_handlers():
    signals_to_handle = [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]
    for sig in signals_to_handle:
        signal.signal(sig, lambda signum, frame: signal_handler(signum, frame))


def signal_handler(signum, frame):
    """
    Clean up before exit
    :param signum:
    :param frame:
    :return:
    """
    print(f"Received signal {signum}. Shutting down...")
    downloader.download_manager().shutdown()
    sys.exit(0)


def setup(update_period_in_hours):
    # update scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=fetch_all_channel, trigger="interval", hours=update_period_in_hours)
    scheduler.start()
    # clean up before exit
    atexit.register(downloader.download_manager().shutdown)
    setup_signal_handlers()
