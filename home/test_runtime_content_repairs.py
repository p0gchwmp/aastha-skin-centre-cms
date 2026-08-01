from bs4 import BeautifulSoup
from django.test import SimpleTestCase

from home.clinical_results_local import gallery_markup
from home.templatetags.clinical_results import repair_legacy_list_markup


class RuntimeContentRepairTests(SimpleTestCase):
    def test_orphaned_item_paragraphs_are_rejoined_to_clean_list(self):
        source = """
        <main><section>
          <ul class="clean-list"><li>Existing item</li></ul>
          <p>The patient has a history of keloids</p>
          <p>Active acne is still recurring</p>
          <hr>
        </section></main>
        """
        repaired = BeautifulSoup(repair_legacy_list_markup(source), "html.parser")
        items = [item.get_text(" ", strip=True) for item in repaired.select("ul.clean-list > li")]
        self.assertEqual(
            items,
            [
                "Existing item",
                "The patient has a history of keloids",
                "Active acne is still recurring",
            ],
        )
        self.assertFalse(
            any(
                paragraph.get_text(" ", strip=True) in items[1:]
                for paragraph in repaired.find_all("p")
            )
        )

    def test_runtime_repair_is_idempotent(self):
        source = '<main><ul class="clean-list"><li>One</li></ul><p>Two</p></main>'
        once = repair_legacy_list_markup(source)
        twice = repair_legacy_list_markup(once)
        self.assertEqual(
            BeautifulSoup(once, "html.parser").prettify(),
            BeautifulSoup(twice, "html.parser").prettify(),
        )

    def test_gallery_error_starts_force_hidden(self):
        html = gallery_markup("/treatments/acne-scar-treatment/")
        soup = BeautifulSoup(html, "html.parser")
        error = soup.select_one("[data-clinical-error]")
        self.assertIsNotNone(error)
        self.assertTrue(error.has_attr("hidden"))
        self.assertEqual(error.get("data-suppressed"), "true")
        self.assertEqual(error.get("style"), "display:none")

    def test_gallery_runtime_moves_verified_media_into_hero(self):
        html = gallery_markup("/treatments/acne-treatment/")
        self.assertIn("placeGalleryInHero", html)
        self.assertIn("root.classList.add('clinical-results--hero')", html)
        self.assertIn("visual.classList.add('clinical-results__replaced-placeholder')", html)
        self.assertIn("visual.parentNode.insertBefore(root, visual)", html)

    def test_deferred_images_do_not_trigger_false_load_error(self):
        html = gallery_markup("/treatments/acne-scar-treatment/")
        self.assertIn("img[src]", html)
        self.assertNotIn(
            "querySelectorAll('[data-clinical-slide] img')];\n    const failed",
            html,
        )
