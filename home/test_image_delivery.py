from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from home.templatetags.exact_pages import optimise_image_delivery


class ImageDeliveryTests(SimpleTestCase):
    def test_first_image_is_prioritised_and_following_images_are_lazy(self):
        source = (
            '<main><img src="hero.jpg" width="720" height="520">'
            '<img src="card.jpg" width="640" height="360" loading="eager">'</n            '</main>'
        )
        result = optimise_image_delivery(source)

        self.assertIn(
            'src="hero.jpg" width="720" height="520" '
            'loading="eager" decoding="async" fetchpriority="high"',
            result,
        )
        self.assertIn(
            'src="card.jpg" width="640" height="360" '
            'loading="lazy" decoding="async"',
            result,
        )
        self.assertEqual(result.count('fetchpriority="high"'), 1)

    def test_image_delivery_rewrite_preserves_non_image_markup(self):
        source = '<section><h1>Acne care</h1><p>Reviewed content.</p></section>'
        self.assertEqual(optimise_image_delivery(source), source)

    def test_future_wagtail_templates_define_loading_policy(self):
        templates = settings.PROJECT_DIR / "templates" / "home"
        hero = (templates / "blocks" / "hero.html").read_text(encoding="utf-8")
        cards = (templates / "blocks" / "card_grid.html").read_text(
            encoding="utf-8"
        )
        gallery = (templates / "blocks" / "gallery.html").read_text(
            encoding="utf-8"
        )

        self.assertIn('loading="eager"', hero)
        self.assertIn('fetchpriority="high"', hero)
        self.assertIn('loading="lazy"', cards)
        self.assertIn('loading="lazy"', gallery)
