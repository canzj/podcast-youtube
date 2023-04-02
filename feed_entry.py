from feedparser import FeedParserDict


class FeedEntry:
    def __init__(self, title, link, author, description, pub_date, audio_url):
        self.title = title
        self.link = link
        self.author = author
        self.description = description
        self.pub_date = pub_date
        self.audio_url = audio_url

    def to_feedparser_entry(self) -> FeedParserDict:
        entry = FeedParserDict()
        entry.title = self.title
        entry.link = self.link
        entry.author = self.author
        entry.description = self.description
        entry.published = self.pub_date

        enclosure = FeedParserDict()
        enclosure.href = self.audio_url
        enclosure.length = 0
        enclosure.type = "audio/mpeg"

        entry.enclosures = [enclosure]

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
            None
        )

    def to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "author": self.author,
            "description": self.description,
            "pub_date": self.pub_date,
            "audio_url": self.audio_url,
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
        )
