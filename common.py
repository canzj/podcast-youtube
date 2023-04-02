import json
import os

import yaml

from feed_entry import FeedEntry


def serialize_feed_entries(feed_entries: list[FeedEntry]) -> str:
    data_list = [entry.to_dict() for entry in feed_entries]
    json_data = json.dumps(data_list, indent=2)
    return json_data


def deserialize_feed_entries(json_data: str) -> list[FeedEntry]:
    data_list = json.loads(json_data)
    feed_entries = [FeedEntry.from_dict(entry_data) for entry_data in data_list]
    return feed_entries


def touch(path):
    """
    Creates an empty file at the specified path if it doesn't exist.
    Also creates any parent directories if they don't exist.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a'):
        os.utime(path, None)


def load_yml(file_path) -> dict:
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
