from argparse import ArgumentParser

import nltk
from django.core.management.base import BaseCommand
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

from job.processors import MainProcessor

from .common_words import common_words

trash_words = common_words | set(stopwords.words("english")) | {"yes", "no"}
tokenizer = nltk.RegexpTokenizer(r"\w+")


def is_good_token(t: str):
    return (
        len(t) > 1
        and not t.lower() in trash_words
        and not t.isnumeric()
        and not any(wn.synsets(t, pos=pos) for pos in [wn.VERB, wn.ADJ, wn.ADV])
        # and len(wn.synsets(t)) < 2
        # and t[0].isupper()
    )


def remove_trash_words(s: str) -> list[str]:
    tokens = tokenizer.tokenize(s)
    return sorted(list({t.lower(): t for t in tokens if is_good_token(t)}.values()))


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("class_name", type=str, nargs="?")

    def handle(self, *args, **options):
        class_name = options.get("class_name")
        MainProcessor.process(class_name)
