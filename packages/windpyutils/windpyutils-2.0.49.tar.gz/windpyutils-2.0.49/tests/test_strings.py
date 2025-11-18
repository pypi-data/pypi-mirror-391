from unittest import TestCase
from windpyutils.strings import place_substrings


class TestPlaceSubstrings(TestCase):

    def test_empty_string(self):
        s = ""
        result = place_substrings(s, [("abc", 0)])
        self.assertEqual(result, "abc")

    def test_single_insertion(self):
        s = "Hello World"
        result = place_substrings(s, [(" Beautiful", 5)])
        self.assertEqual(result, "Hello Beautiful World")

    def test_multiple_insertions(self):
        s = "abcdef"
        substrings = [("X", 2), ("Y", 4), ("Z", 6)]
        result = place_substrings(s, substrings)
        self.assertEqual(result, "abXcdYefZ")

    def test_out_of_bounds_insertion(self):
        s = "Hello"
        with self.assertRaises(ValueError):
            place_substrings(s, [("World", 10)])

    def test_already_sorted(self):
        s = "12345"
        substrings = [("A", 4), ("B", 2), ("C", 0)]
        result = place_substrings(s, substrings, already_sorted=True)
        self.assertEqual(result, "C12B34A5")



