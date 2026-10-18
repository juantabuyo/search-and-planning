"""Focused checks for inference, paths and MDP boundaries."""
import contextlib
import io
import random
import unittest
from unittest.mock import patch

import numpy as np

from logic_search.agents import bfs_find_path, run_bfs_agent, run_manual_agent
from logic_search.knowledge_base import KnowledgeBase
from logic_search.palace import Palace as LogicalPalace
from beliefs.agents import run_bayesian_agent
from beliefs.bayesian import Bayesian
from beliefs.palace import Palace as BeliefPalace
from river_mdp.config import GAMMA, THETA
from river_mdp.main import run_test
from river_mdp.river import River
from river_mdp.value_iteration import ValueIteration


class LogicalTests(unittest.TestCase):
    def test_bfs_shortest_safe_path_and_unreachable_cell(self):
        safe = {(1, 1), (1, 2), (1, 3), (2, 3)}
        self.assertEqual(bfs_find_path((1, 1), (2, 3), safe, 3),
                         ['moveR', 'moveR', 'moveD'])
        self.assertIsNone(bfs_find_path((1, 1), (3, 3), safe, 3))

    def test_no_perceptions_certify_adjacent_cells(self):
        kb = KnowledgeBase(6)
        kb.watch((1, 1), [0, 0, 0, 1, 0, 1, 0, 0])
        self.assertEqual(kb.safe_positions(), {(1, 1), (1, 2), (2, 1)})

    def test_singleton_clause_and_intersection(self):
        kb = KnowledgeBase(6)
        kb.soldier_clauses = [{(2, 1), (1, 2)}]
        kb.no_soldier.add((2, 1))
        kb.inference()
        self.assertEqual(kb.soldier_certain, {(1, 2)})
        kb.no_cliff.update({(1, 1), (1, 2)})
        self.assertEqual(kb.safe_positions(), {(1, 1)})

    @staticmethod
    def rescue_fixture():
        random.seed(3)
        palace = LogicalPalace()
        palace.cliffs = set()
        palace.soldiers = set()
        palace.colonels = {(1, 2)}
        palace.exit = (1, 2)
        return palace

    def test_manual_rescue_and_translated_exit_contract(self):
        palace = self.rescue_fixture()
        with patch('builtins.input', side_effect=['moveR', 'exit']), contextlib.redirect_stdout(io.StringIO()):
            run_manual_agent(palace, show=False)
        self.assertTrue(palace.with_colonel)
        self.assertEqual(palace.apply_action('exit'), 'EXITED')

    def test_automatic_agent_completes_safe_fixture(self):
        palace = self.rescue_fixture()
        success, path = run_bfs_agent(palace, show=False)
        self.assertTrue(success)
        self.assertIn('moveR', path)


class BeliefTests(unittest.TestCase):
    def test_binary_masks_keep_uniform_compatible_support(self):
        beliefs = Bayesian(6)
        beliefs.update((1, 1), [1, 0, 0, 0, 0, 1, 0, 1, 0, 0])
        self.assertAlmostEqual(beliefs.prob_F[0, 1], 0.5)
        self.assertAlmostEqual(beliefs.prob_F[1, 0], 0.5)
        self.assertEqual(np.count_nonzero(beliefs.prob_F), 2)
        for grid in [beliefs.prob_F, beliefs.prob_P, beliefs.prob_D, beliefs.prob_M, beliefs.prob_S]:
            self.assertAlmostEqual(grid.sum(), 1)
            nonzero = grid[grid > 0]
            self.assertTrue(np.allclose(nonzero, nonzero[0]))

    def test_score_can_exceed_one_and_dead_soldier_is_removed(self):
        beliefs = Bayesian(6)
        for grid in [beliefs.prob_F, beliefs.prob_P, beliefs.prob_D, beliefs.prob_M]:
            grid.fill(0)
            grid[0, 1] = 1
        self.assertEqual(beliefs.get_risk_score((1, 2)), 4)
        self.assertNotIn((1, 2), beliefs.get_low_risk_neighbours((1, 1)))
        beliefs.soldier_dead()
        self.assertEqual(beliefs.get_risk_score((1, 2)), 3)

    def test_manual_agent_rescue_with_simulated_input(self):
        random.seed(3)
        palace = BeliefPalace()
        palace.traps = {'F': (6, 6), 'P': (6, 5), 'D': (5, 6)}
        palace.soldier = (5, 5)
        palace.colonel = (1, 2)
        palace.exit = (1, 2)
        with patch('builtins.input', side_effect=['moveR', 'exit']), contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(run_bayesian_agent(palace, show=False))

    def test_grenade_perception_removes_soldier(self):
        random.seed(3)
        palace = BeliefPalace()
        palace.soldier = (1, 2)
        palace.apply_action('grenadeR')
        self.assertIsNone(palace.soldier)
        self.assertTrue(palace.get_percepts()[9])
        self.assertFalse(palace.grenade)


class OneStepRiver:
    """An isolated transition boundary fixture, not a replacement river model."""
    initial_state = (0, 0)
    exit_col = 1
    terminal_states = {(0, 1)}
    islands = set()

    def get_states(self):
        return [(0, 0), (0, 1)]

    def transition_probabilities(self, state, action, destination):
        return float(destination == (0, 1))

    def get_reward(self, state, action, destination):
        return 100


class RiverTests(unittest.TestCase):
    def test_exit_on_final_allowed_transition(self):
        self.assertEqual(run_test(OneStepRiver(), {(0, 0): 'right'}, max_steps=1, show=False),
                         (True, 100, 1))

    def test_zero_budget_and_missing_action_do_not_invent_steps(self):
        self.assertEqual(run_test(OneStepRiver(), {(0, 0): 'right'}, max_steps=0, show=False),
                         (False, 0, 0))
        self.assertEqual(run_test(OneStepRiver(), {}, max_steps=5, show=False), (False, 0, 0))

    def test_transition_rows_are_probability_distributions(self):
        for seed in [5121111, 1500, 37, 51211]:
            river = River(seed=seed)
            for state in river.get_states():
                for action in river.get_actions(state):
                    row = [river.transition_probabilities(state, action, other)
                           for other in river.get_states()]
                    self.assertTrue(all(0 <= probability <= 1 for probability in row))
                    self.assertAlmostEqual(sum(row), 1)

    def test_small_river_uses_its_actual_last_column(self):
        river = River(rows=3, cols=3, num_islands=0, seed=1)
        self.assertEqual(river.exit_col, 2)
        self.assertEqual(river.terminal_states, {(0, 2), (1, 2), (2, 2)})
        self.assertEqual(river.get_reward((0, 1), 'right', (0, 2)), 100)

    def test_bellman_residual_and_policy_for_default_layout(self):
        river = River(seed=5121111)
        solver = ValueIteration(river)
        values, policy = solver.execute(show=False)
        self.assertTrue(solver.converged)
        self.assertLess(solver.max_update, THETA)
        residual = 0
        for state in river.get_states():
            if state in river.terminal_states:
                self.assertEqual(values[state], 0)
                self.assertIsNone(policy[state])
                continue
            action_values = {
                action: sum(river.transition_probabilities(state, action, other) *
                            (river.get_reward(state, action, other) + GAMMA * values[other])
                            for other in river.get_states())
                for action in river.get_actions(state)
            }
            best = max(action_values.values())
            self.assertAlmostEqual(action_values[policy[state]], best)
            residual = max(residual, abs(best - values[state]))
        self.assertLess(residual, THETA)


if __name__ == '__main__':
    unittest.main()
