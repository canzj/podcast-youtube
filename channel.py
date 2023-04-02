import hashlib

from feedparser import FeedParserDict


class Channel:
    def __init__(self, rss, link, title, description):
        self.rss = rss
        self.link = link
        self.title = title
        self.description = description

    def get_channel_id(self):
        digest = hashlib.md5(self.link.encode()).hexdigest()
        return digest[-7:]

    def to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "rss": self.rss,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data['rss'],
            data['link'],
            data['title'],
            data['description'])

    @classmethod
    def of_feedparser_dict(cls, rss_url, feed: FeedParserDict):
        return cls(
            rss_url,
            feed.feed.link,
            feed.feed.title,
            feed.feed.description if hasattr(feed.feed, 'description') else None
        )

    def validate(self):
        if not self.rss:
            raise ValueError("RSS URL is empty")
        if not self.link:
            raise ValueError("Link is empty")
        if not self.title:
            raise ValueError("Title is empty")

    def __str__(self):
        return f"Channel(title={self.title}, link={self.link}, rss={self.rss}, description={self.description})"

    def __repr__(self):
        return self.__str__()
