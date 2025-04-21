import unittest
import json
import os

from helpers import MODEL_MODE, MODEL_MODE_SMALL
import helpers.entities as entities

this_dir = os.path.dirname(os.path.abspath(__file__))


class TestEntities(unittest.TestCase):

    def test_spanish(self):
        story = json.load(open(os.path.join(this_dir, 'fixtures', '2210723002.json')))
        entity_list = entities.from_text(story['story_text'], story['language'])
        if MODEL_MODE == MODEL_MODE_SMALL:
            assert len(entity_list) == 68
        else:
            assert len(entity_list) == 50
        for e in entity_list:
            assert 'text' in e
            assert len(e['text']) > 0
            assert 'type' in e
            assert e['type'] in ['ORG', 'PER', 'LOC', 'C_DATE', 'MISC']

    def test_korean(self):
        stories = json.load(open(os.path.join(this_dir, 'fixtures', 'ko_sample_stories.json')))
        entity_list = entities.from_text(stories[0], 'ko')
        if MODEL_MODE == MODEL_MODE_SMALL:
            assert len(entity_list) == 69
        else:
            assert len(entity_list) == 77
        for e in entity_list:
            assert 'text' in e
            assert len(e['text']) > 0
            assert 'type' in e
            assert e['type'] in ['DT', 'LC', 'OG', 'PS', 'QT', 'TI']

    def test_swahili(self):
        story = json.load(open(os.path.join(this_dir, 'fixtures', 'sw_sample_story.json')))
        entity_list = entities.from_text(story['results']['text'], story['results']['language'])
        assert len(entity_list) == 37
        for e in entity_list:
            assert 'text' in e
            assert len(e['text']) > 0
            assert 'type' in e
            assert e['type'] in ['DATE', 'PER', 'LOC', 'ORG']


if __name__ == "__main__":
    unittest.main()
