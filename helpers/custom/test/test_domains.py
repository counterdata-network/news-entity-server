import unittest

import helpers.custom.domains as domains


class TestCanonicalDomain(unittest.TestCase):

    def test_french_domain(self):
        test_url = "https://observers.france24.com/en/20190826-mexico-african-migrants-trapped-protest-journey"
        domain = domains.get_canonical_mediacloud_domain(test_url)
        assert domain == "france24.com"

    def test_org(self):
        test_url = "https://www.kpbs.org/news/2019/jul/09/migrants-cameroon-protest-immigration-process-tiju/"
        domain = domains.get_canonical_mediacloud_domain(test_url)
        assert domain == "kpbs.org"

    def test_hyphen(self):
        test_url = "https://www.kenya-today.com/media/moi-burial-confused-ruto-as-matiangi-declares-tuesday-a-public-holiday#comments"
        domain = domains.get_canonical_mediacloud_domain(test_url)
        assert domain == "kenya-today.com"
