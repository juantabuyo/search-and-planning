"""Regression tests: palaces too small for their elements fail fast instead of hanging or raising IndexError."""
import random
import unittest
from unittest.mock import patch

from beliefs.palace import Palace as BeliefPalace
from logic_search.palace import Palace as LogicPalace


class DrawBudget:
    """Wrap random.randint so a placement loop that never ends fails the test instead of hanging it."""

    def __init__(self, limit=10_000):
        self.limit, self.calls, self.original = limit, 0, random.randint

    def __call__(self, a, b):
        self.calls += 1
        if self.calls > self.limit:
            raise RuntimeError('placement did not terminate')
        return self.original(a, b)


class PalaceSizes(unittest.TestCase):
    def test_too_small_sizes_raise_value_error(self):
        # 2x2 is rejected for both models, although some beliefs seeds used to build it.
        for palace, sizes in ((LogicPalace, (1, 2)), (BeliefPalace, (1, 2))):
            for n in sizes:
                for seed in range(20):
                    with self.subTest(palace=palace.__module__, n=n, seed=seed):
                        random.seed(seed)
                        with patch('random.randint', DrawBudget()), self.assertRaises(ValueError):
                            palace(n)

    def test_smallest_accepted_size_always_builds(self):
        for palace in (LogicPalace, BeliefPalace):
            for seed in range(200):
                random.seed(seed)
                palace(3)

    def test_default_layouts_are_unchanged_for_seed_42(self):
        # Expected values were taken from the unmodified source, so valid sizes keep their historical layouts.
        random.seed(42)
        logic = LogicPalace()
        self.assertEqual((logic.exit, sorted(logic.cliffs), sorted(logic.soldiers), sorted(logic.colonels)),
                         ((5, 1), [(1, 6), (3, 2), (6, 1)], [(2, 2)], [(6, 6)]))
        random.seed(42)
        beliefs = BeliefPalace()
        self.assertEqual((beliefs.traps, beliefs.soldier, beliefs.colonel, beliefs.exit),
                         ({'F': (6, 1), 'P': (1, 6), 'D': (3, 2)}, (3, 6), (2, 5), (2, 3)))


if __name__ == '__main__':
    unittest.main()
