from __future__ import annotations

from enum import Enum
from dataclasses import dataclass


@dataclass
class Shortcut:
    name: str
    jpn: int
    usa: int
    eur: int
    chn: int
    kor: int
    twn: int


SHORTCUTS = Shortcut.load_list_from_file()


class Title:
    # list of titles in 16 different languages
    locale: list[str]


class BadgeData:
    # at most 100 badge sets
    badge_sets: list[BadgeSet]
    nnid: int

    @property
    def unique_badges(self) -> int:
        pass

    @property
    def total_badges(self) -> int:
        pass


class BadgeSet:
    title: Title
    badges: list[Badge]
    # in RGB format
    image: bytes


class Badge:
    # in RGBA format
    image_64: bytes
    image_32: bytes

    # [1,2]
    width: int = 1
    height: int = 1

    # [0, 65535]
    quantity: int = 256
    shortcut_title: Shortcut = None
