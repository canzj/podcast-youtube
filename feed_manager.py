import logging
import os.path
from datetime import datetime

import feedparser
import pytz
import yaml
from dateutil.parser import parse
from feedgen.feed import FeedGenerator
from feedparser import FeedParserDict

import common
import config
from channel import Channel
from feed_entry import FeedEntry

watchlist = None


def watchlist_manager():
    if watchlist is None:
        return Watchlist(config.get_watchlist_path())
    else:
        return watchlist


class Watchlist:
    def __init__(self, file_path):
        self.file_path = file_path
        self.channels = self.load()

    def load(self):
        try:
            with open(self.file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def save(self):
        common.touch(self.file_path)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.channels, f, default_flow_style=False)

    def set_channel(self, channel: Channel):
        self.channels[channel.get_channel_id()] = channel.to_dict()
        self.save()

    def remove_channel(self, channel_id):
        if channel_id in self.channels:
            del self.channels[channel_id]
            self.save()

    def get_channel(self, channel_id) -> Channel:
        return Channel.from_dict(self.channels.get(channel_id))

    def get_all_channels(self) -> list[Channel]:
        return [Channel.from_dict(channel) for channel in self.channels.values()]


def update_feed(channel: Channel, feed_entries: list[FeedEntry]):
    """
    Update feed for a channel
    :param channel:
    :param feed_entries:
    :return: path/to/feed
    """
    logging.info(f"Start building feed for channel {channel.get_channel_id()}")
    # Combine existing entries and new entries
    origin_entries = load_origin_entry(channel)
    latest_entries = []
    for f in feed_entries:
        latest_entry = f.to_feedparser_entry()
        latest_entries.append(latest_entry)
    all_entries = latest_entries + origin_entries

    # Keep track of unique title and link combinations
    unique_entries = []

    # Get unique entries using a list comprehension
    unique_entries = [entry for i, entry in enumerate(all_entries) if
                      entry.link not in [e.link for e in all_entries[:i]]]

    # Sort unique_entries by published time in descending order
    sorted_unique_entries = sorted(unique_entries, key=lambda x: int(parse_date_str(x.published).timestamp()),
                                   reverse=False)

    fg = FeedGenerator()
    # Create an empty feed using FeedGenerator
    fg.title(channel.title)
    fg.link(href=channel.rss)
    fg.description(channel.description if channel.description else "null")
    fg.language("zh-cn")
    if feed_entries:
        fg.image(feed_entries[0].thumbnail_url)
    # todo bug
    # if len(sorted_unique_entries) > 0:
    #     fg.author({'name': sorted_unique_entries[0].author, 'email': 'none@none.com'})

    # Iterate through sorted unique entries and add them to the feed
    for entry in sorted_unique_entries:
        fe = fg.add_entry()
        fe.title(entry.title)
        fe.link(href=entry.link)
        fe.description(entry.description)
        fe.pubDate(entry.published)
        cur_enclosure_href = config.build_audio_api_path(channel.get_channel_id(), entry.enclosures[0].href)
        fe.enclosure(cur_enclosure_href, entry.enclosures[0].length, entry.enclosures[0].type)

        # Save the empty feed to a file
        os.makedirs(os.path.dirname(config.get_feed_path(channel.get_channel_id())), exist_ok=True)
        with open(config.get_feed_path(channel.get_channel_id()), 'w') as f:
            f.write(fg.rss_str(pretty=True).decode('utf-8'))
    logging.info(f"Finish building feed for channel {channel.get_channel_id()}")
    return config.get_feed_path(channel.get_channel_id())


def parse_date_str(time_str: str) -> datetime:
    date_obj = parse(time_str)
    return date_obj.astimezone(pytz.timezone('Asia/Shanghai'))


def load_origin_entry(channel: Channel) -> list[FeedParserDict]:
    feed_file_path = config.get_feed_path(channel.get_channel_id())
    # Check if the feed file exists
    if not os.path.exists(feed_file_path):
        return []

    # Read the existing feed from the local disk
    with open(feed_file_path, 'r') as f:
        feed_content = f.read()

    # Parse the feed content
    return feedparser.parse(feed_content).entries
