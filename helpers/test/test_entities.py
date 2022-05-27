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
            assert len(entity_list) == 72
        else:
            assert len(entity_list) == 56
        for e in entity_list:
            assert 'text' in e
            assert len(e['text']) > 0
            assert 'type' in e
            assert e['type'] in ['ORG', 'PER', 'LOC', 'C_DATE', 'MISC']


if __name__ == "__main__":
    unittest.main()
