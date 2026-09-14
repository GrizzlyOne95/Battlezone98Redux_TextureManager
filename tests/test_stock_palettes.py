import hashlib
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from stock_palettes import STOCK_PALETTE_NAMES, get_stock_palette, get_stock_palette_bytes


EXPECTED_SHA256 = {
    'achilles.act': '9ed5bb3150b01a645ad331a07d5bab62db8df1dafb3e2264cfec422f77b55436',
    'black.act': 'a797fb381160a1ba5a515b2036835f3d3bafb040c7f0069b514891c612d37a45',
    'brown.act': '1bec6dfa325bfb51a78bf02ea55c755e792a76455e0541edfe489b95c9d7961a',
    'elysium.act': '8ea41a03249de524bdf62cbec800640a839c7b7c30ab6e55e1574fce70f364a1',
    'europa.act': '0402c1996d175cd9e7330d4c53c348b458232a4544dfa421e23b8e524dee76af',
    'explode.act': '8a84859e5b86cb4f975da5f9b86296f29b83fc2296ef7b6bab418b9d5126f952',
    'ganymede.act': '459c39bd9413ed9592a95ef6065e9e83f594257cf21d927fb3de79bbfb812a59',
    'grey.act': '6f9b0c563eea010fd85e4e8bf3b96bf22c2242426982ee93c8385d9b6a343a99',
    'hblack.act': 'dc2893a6f889490ff61e8e195b39bb58d917636b906b330c6ed27a7c9845f5c5',
    'hblue.act': '85a273861a1aa1624b4d9018fa560445bf046d615cf8ff077bcc8f0c760f837d',
    'hbrown.act': '8e849c72532de9190a1ff579f0b67156ba662615563aac40916123806c567acd',
    'hcyan.act': '75acb67e27dc0dc6b4c7b22e7a669bc22d26ad11b7846e1f213b0cd7a3621249',
    'hgreen.act': 'ba2792eff2c0d094ee11b3126e41be9f217d64b2b8f2798807428516e18a5ddf',
    'hgrey.act': 'b87b37356c2d25c6cb1e01bfe1b628b8c00e4d335fd9c73914420e523efc9ee8',
    'hplasblu.act': 'af0047654460281d070e78a41bb2c95b94bd37f5ed1b79f878b9d8c60e3b73f1',
    'hplasgrn.act': '49a423e4b312c8de9bb2070f94ab9060460bcc6e4d77045dc3291eef1102e570',
    'hplasred.act': '08ec3b21579d19e6e256e595733ed64369ee8a9a7b1421a267b2697065192234',
    'hred.act': '56292c850b9f4ca1e068b8fdf2a422133127848b551e8369214f24ac34e02756',
    'htan.act': 'bc58b97156f11c266756818901238593029d0d6d16b14c1a778f400b6f585d75',
    'hwhite.act': '2e27101622c18cdb8084913783839df7eb694ea30f823c6cab62eea6e102274f',
    'hyellow.act': '8258328310b355a65aa8cc6923ce17016ececa43e32af1e9861646a4ea40f7a4',
    'interface.act': 'fa3b007f42c0283834d12ab77304c8657a2b624f2f08c97d9b000c4098363df8',
    'io.act': 'be1bfef135786ba88e97a4aad5f0a053793aab6898f11d47a568c8d42db910b8',
    'mars.act': 'd20af8a7fbd06b1c177685ac11a4da81a89296c1a8f650a51b2b93904a85cb70',
    'moon.act': 'cb63b8cb3d95f6d537b5a3aacb4201ce0b16395c0da311e59453315d2a9900fa',
    'objects.act': '4e21b939e4851c9f4b119620ce671894538781438017b01474544f4d42da90c8',
    'plasblue.act': 'bbdf70a03c703e3be4e277bffb44ac18b6382b07b3868ce41d23de194428b18b',
    'plasgrn.act': '2801ff65b8b7c1a58aec53ec668a83c2a2247de88d283c63be2fd35b6228260a',
    'plasred.act': 'eb72c9ce56afad9a7952af816305c55911456877cdb4b99e6945c9402637ab2a',
    'tan.act': '0bd22e8f2f7f8f1d9c92c3e242ba181c5c480eb22d4eb9bcc205c1d0b4037a8b',
    'titan.act': '3aa4174be029a0de2a64d293a5d3e8f75bf73c508e79491f59efdfb6f1943e71',
    'venus.act': '7f47f8f0bdc57fca87c872c034870bf4f71f120f9b288eb7cb21eecdf5f8a138',
    'white.act': '5f090a06c04e4f6e5a1262ab41254489169543363194741d28fb5f30cab20ab4',
}


class StockPaletteTests(unittest.TestCase):
    def test_all_stock_palettes_are_present(self):
        self.assertEqual(tuple(EXPECTED_SHA256), STOCK_PALETTE_NAMES)

    def test_payloads_are_exact_256_color_act_palettes(self):
        for name in STOCK_PALETTE_NAMES:
            with self.subTest(name=name):
                raw = get_stock_palette_bytes(name)
                self.assertEqual(len(raw), 768)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256[name])

                palette = get_stock_palette(name)
                self.assertEqual(len(palette), 256)
                self.assertTrue(all(len(rgb) == 3 for rgb in palette))
                self.assertTrue(all(0 <= channel <= 255 for rgb in palette for channel in rgb))

    def test_unknown_palette_raises(self):
        with self.assertRaises(KeyError):
            get_stock_palette("not-a-stock-palette.act")


if __name__ == "__main__":
    unittest.main()
