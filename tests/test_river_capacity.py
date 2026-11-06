"""Regression tests: every island count the River constructor accepts can be placed.

The original generator gave up after 100 random draws, so rivers with more than 100
islands, or nearly full ones, failed for every seed although their capacity was valid."""
import random
import unittest

from river_mdp.river import River


def original_islands(rows, cols, count, seed):
    """The layout the submitted generator produced for a seed, or None if it gave up."""
    rng = random.Random(seed)
    rng.randint(0, rows - 1)  # the start row is drawn first
    islands, attempts = set(), 0
    while len(islands) < count:
        if attempts >= 100:
            return None
        islands.add((rng.randint(1, rows - 2), rng.randint(1, cols - 2)))
        attempts += 1
    return islands


class IslandCapacity(unittest.TestCase):
    def test_layouts_that_used_to_be_generated_are_unchanged(self):
        checked = 0
        for rows, cols, count in ((7, 5, 2), (5, 12, 20), (3, 12, 8), (6, 6, 12), (7, 5, 0)):
            for seed in range(200):
                expected = original_islands(rows, cols, count, seed)
                if expected is None:
                    continue
                with self.subTest(rows=rows, cols=cols, count=count, seed=seed):
                    self.assertEqual(River(rows, cols, count, seed=seed).islands, expected)
                    checked += 1
        self.assertGreater(checked, 500)

    def test_default_layout_for_the_stored_seed_is_unchanged(self):
        river = River(seed=5121111)
        self.assertEqual(river.islands, original_islands(7, 5, 2, 5121111))

    def test_full_and_oversized_counts_place_every_island(self):
        for rows, cols, count in ((3, 103, 101), (3, 60, 58), (5, 12, 30), (4, 4, 4), (12, 12, 100)):
            for seed in range(25):
                with self.subTest(rows=rows, cols=cols, count=count, seed=seed):
                    river = River(rows, cols, count, seed=seed)
                    self.assertEqual(len(river.islands), count)
                    self.assertTrue(all(1 <= i <= rows - 2 and 1 <= j <= cols - 2
                                        for i, j in river.islands))
                    self.assertEqual(river.islands, River(rows, cols, count, seed=seed).islands)

    def test_a_count_above_the_capacity_is_still_rejected(self):
        with self.assertRaises(ValueError):
            River(3, 60, 59, seed=1)


if __name__ == '__main__':
    unittest.main()
