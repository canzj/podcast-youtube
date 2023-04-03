from feedparser import FeedParserDict


class FeedEntry:
    def __init__(self, title, link, author, description, pub_date, audio_url, thumbnail_url):
        self.title = title
        self.link = link
        self.author = author
        self.description = description
        self.pub_date = pub_date
        self.audio_url = audio_url
        self.thumbnail_url = thumbnail_url

    def to_feedparser_entry(self) -> FeedParserDict:
        entry = FeedParserDict()
        entry.title = self.title
        entry.link = self.link
        entry.author = self.author
        entry.description = self.description
        entry.published = self.pub_date

        audio = FeedParserDict()
        audio.href = self.audio_url
        audio.length = 0
        audio.type = "audio/mpeg"

        entry.enclosures = [audio]

        return entry

    @classmethod
    def from_feedparser_dict(cls, entry: FeedParserDict):
        return cls(
            entry.title,
            entry.link,
            entry.author,
            entry.description,
            entry.published,
            # entry.enclosures[0].href,
            None, None
        )

    def to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "author": self.author,
            "description": self.description,
            "pub_date": self.pub_date,
            "audio_url": self.audio_url,
            "thumbnail_url": self.thumbnail_url
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data['title'],
            link=data['link'],
            author=data['author'],
            description=data['description'],
            pub_date=data['pub_date'],
            audio_url=data['audio_url'],
            thumbnail_url=data['thumbnail_url']
        )
