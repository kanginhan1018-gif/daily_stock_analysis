"""Offline checks; run with python -m unittest discover -s scripts -p test_tech_newsletter.py."""
import unittest
import json
import tempfile
from pathlib import Path
from PIL import Image
from newsletter_picture import render_picture
from datetime import datetime, timezone

from tech_newsletter import parse_feed, render, parse_generation


class NewsletterTest(unittest.TestCase):
    def test_feed_freshness_and_atom(self):
        now = datetime(2026, 11, 12, tzinfo=timezone.utc)
        raw = b'<rss><channel><item><title>New</title><link>https://example.org/new</link><pubDate>Wed, 11 Nov 2026 10:00:00 GMT</pubDate></item><item><title>Old</title><link>https://example.org/old</link><pubDate>Wed, 01 Jan 2020 00:00:00 GMT</pubDate></item></channel></rss>'
        self.assertEqual(len(parse_feed(raw, 'RSS', now)), 1)
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Atom</title><link href="https://example.org/atom"/><updated>2026-11-11T00:00:00Z</updated></entry></feed>'
        self.assertEqual(parse_feed(atom, 'Atom', now)[0]['url'], 'https://example.org/atom')

    def test_model_response_variants(self):
        items = [dict(title='A', url='https://example.org/a'), dict(title='B', url='https://example.org/b')]
        stories = [dict(index=i, en='x' * 250, ko='한' * 200) for i in range(2)]
        for raw in (json.dumps(stories), '```json\n' + json.dumps(stories) + '\n```'):
            text = parse_generation(dict(result=raw), items)
            self.assertIn('KR:', text)
            self.assertLess(len(text.encode('utf-16-le')) // 2, 4000)
        for raw in ('not JSON', '{}', '[null]'):
            with self.assertRaises((ValueError, TypeError)):
                parse_generation(dict(result=raw), items)

    def test_visual_contract_and_image(self):
        items = [dict(title='Engineering / 공학', source=('Example A' if i == 0 else 'Example B'), url='https://example.org/' + str(i)) for i in range(3)]
        stories = [dict(index=i, en='A method for small datasets.', ko='작은 데이터셋을 위한 방법입니다.',
                        before='Small dataset', after='Generate candidate designs', icon='optimization') for i in range(3)]
        _, selected = parse_generation(dict(result=json.dumps(stories)), items, visual=True)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'newsletter.png'
            render_picture(selected, items, output, '2026-11-13')
            with Image.open(output) as picture:
                self.assertEqual(picture.size, (1440, 2400))
            self.assertLess(output.stat().st_size, 10_000_000)
        stories[0]['after'] = ''
        with self.assertRaises(ValueError):
            parse_generation(dict(result=json.dumps(stories)), items, visual=True)

    def test_message_boundaries(self):
        items = [dict(title='A', url='https://example.org/a'), dict(title='B', url='https://example.org/b')]
        stories = [dict(index=i, en='New method; preliminary research.', ko='초기 연구입니다.') for i in range(2)]
        text = render(stories, items)
        self.assertEqual(text.count('https://'), 2)
        self.assertLess(len(text.encode('utf-16-le')) // 2, 4000)
        invalid = [
            [stories[0], stories[0]],
            [dict(index=99, en='x', ko='y'), stories[1]],
            [dict(index=0, en='x' * 221, ko='y'), stories[1]],
        ]
        for story in invalid:
            with self.assertRaises(ValueError):
                render(story, items)


if __name__ == '__main__':
    unittest.main()
