import feedparser

import config
import downloader
from channel import Channel
from feed_entry import FeedEntry


def crawl_channel(channel: Channel) -> list[FeedEntry]:
    # todo: opt build audio in podcast.py
    """Crawl a channel and return a list of new entries."""
    entries = []
    feed = feedparser.parse(channel.rss)
    for entry in feed.entries:
        try:
            audio_name, thumbnail_url = downloader.download_mp3(entry.link,
                                                                config.get_audio_dir_path(channel.get_channel_id()))
        except Exception as e:
            print(f"[Failed] Download {entry}, skipped: {e}")
            continue
        feed_entry = FeedEntry.from_feedparser_dict(entry)
        feed_entry.audio_url = config.build_audio_api_path(channel.get_channel_id(), audio_name)
        feed_entry.thumbnail_url = thumbnail_url
        entries.append(feed_entry)
    return entries


def fetch_channel_info(rss_url: str) -> Channel:
    """Fetch channel info from a RSS URL."""
    feed = feedparser.parse(rss_url)
    channel = Channel.of_feedparser_dict(rss_url, feed)
    return channel
