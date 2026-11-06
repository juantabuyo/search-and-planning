from collections import deque
from .knowledge_base import KnowledgeBase
from .functions import get_action, get_grenade_action, kb_neighbours, print_knowledge_base
from .config import MAX_STEPS

def run_manual_agent(palace, show=True):
    """Navigate interactively using the logical knowledge base."""
    kb = KnowledgeBase(palace.n)
    print('USER-GUIDED LOGICAL AGENT')
    print('\nCommands (case-insensitive):')
    print('  Move: moveU, moveD, moveL, moveR')
    print('  Grenade: grenadeU, grenadeD, grenadeL, grenadeR')
    print('  Leave with the colonel: exit')
    print('\nMap legend:')
    print('  CW    = Captain Willard (B=breeze, R=snoring, L=glow, G=scream)')
    print('  ✓     = Visited cell')
    print('  o     = Known safe cell (unvisited)')
    print('  P!    = Confirmed cliff')
    print('  S!    = Confirmed soldier')
    print('  E!    = Confirmed exit')
    print('  P?    = Possible cliff')
    print('  S?    = Possible soldier')
    print('  PS?   = Possible cliff AND soldier')
    print('  E?    = Possible exit')
    print('  .     = Unknown cell')
    print('=' * 70)
    step = 0
    while True:
        step += 1
        percepts = palace.get_percepts()
        kb.watch(palace.captain, percepts)
        if show:
            print('\n')
            print('=' * 70)
            print(f'STEP {step}')
            print('=' * 70)
            print_knowledge_base(palace, kb, percepts)
        print(f'\nCurrent position: {palace.captain}')
        print(f"Colonel rescued: {('YES' if palace.with_colonel else 'NO')}")
        print(f"Grenade available: {('YES' if palace.grenade else 'NO')}")
        safe = kb.safe_neighbours(palace.captain)
        if safe:
            unvisited = [pos for pos in safe if pos not in kb.visited]
            if unvisited:
                print(f'Unvisited safe neighbouring cells: {unvisited}')
            else:
                print(f'All safe neighbouring cells have been visited: {safe}')
        else:
            print(f'No known safe neighbouring cells (a move may be risky)')
        if kb.exit_certain:
            print(f'Confirmed exit: {list(kb.exit_certain)}')
        if kb.soldier_certain and kb.soldier_alive:
            print(f'Confirmed soldier: {list(kb.soldier_certain)}')
        if kb.cliff_certain:
            print(f'Confirmed cliffs: {list(kb.cliff_certain)}')
        print('\n')
        print('=' * 70)
        inp = input('Your action: ').strip().lower()
        actions = {'moveu': 'moveU', 'moved': 'moveD', 'movel': 'moveL', 'mover': 'moveR', 'grenadeu': 'grenadeU', 'grenaded': 'grenadeD', 'grenadel': 'grenadeL', 'grenader': 'grenadeR', 'exit': 'exit'}
        if inp not in actions:
            print(f"Invalid action: '{inp}'")
            print(f'Valid commands: moveu, moved, movel, mover, grenadeu, grenaded, grenadel, grenader, exit')
            continue
        action = actions[inp]
        try:
            result = palace.apply_action(action)
            if result == 'EXITED':
                print('\n')
                print('=' * 70)
                print(f'\nMISSION COMPLETED IN {step} STEPS')
                print('=' * 70)
                print('Captain Willard has rescued Colonel Kurtz.')
                return
        except Exception as e:
            print('\n')
            print('=' * 70)
            print(f'GAME OVER (step {step})')
            print('=' * 70)
            print(f'Cause: {e}')
            print('The captain could not complete the mission.')
            return

def run_bfs_agent(palace, show=True):
    """Explore safe cells with BFS, then use the original risk heuristic if stuck.

    This heuristic can enter an unknown dangerous cell; success is not guaranteed.
    """
    kb = KnowledgeBase(palace.n)
    path = []
    counter = 0
    last_positions = deque(maxlen=10)
    if show:
        print('AUTONOMOUS BFS AGENT')
        print('=' * 70)
    step = 0
    while step < MAX_STEPS:
        step += 1
        percepts = palace.get_percepts()
        kb.watch(palace.captain, percepts)
        if show:
            print('\n')
            print('=' * 70)
            print(f'STEP {step} - Position: {palace.captain}')
            print('=' * 70)
            print_knowledge_base(palace, kb, percepts)
        last_positions.append(palace.captain)
        if len(last_positions) == 10 and len(set(last_positions)) <= 3:
            counter += 1
            if show:
                print(f'Loop detected (counter = {counter})')
        else:
            counter = max(0, counter - 1)
        if palace.captain in kb.exit_certain and palace.with_colonel:
            result = palace.apply_action('exit')
            if result == 'EXITED':
                if show:
                    print(f'\nMISSION COMPLETED IN {step} STEPS')
                return (True, path)
        if palace.grenade and kb.soldier_alive and (len(kb.soldier_certain) == 1):
            soldier_pos = list(kb.soldier_certain)[0]
            action = use_grenade(palace, kb, soldier_pos, show)
            if action:
                palace.apply_action(action)
                path.append(action)
                continue
        action = None
        if counter >= 5:
            if show:
                print(f'FORCING A RISKY MOVE (counter={counter})')
            action = risky_move(palace, kb, show, force=True)
            counter = 0
        else:
            action = bfs_find_best_action(palace, kb, show)
        if action is None:
            if show:
                print(f'No BFS route; trying the risk heuristic...')
            action = risky_move(palace, kb, show, force=False)
        if action is None:
            if show:
                print(f'LAST RESORT: trying a cell without a confirmed hazard')
            action = last_move(palace, kb, show)
        if action is None:
            if show:
                print(f'\nGAME OVER - No available move')
            return (False, path)
        try:
            palace.apply_action(action)
            path.append(action)
            if show:
                print(f'Action: {action}')
        except Exception as e:
            if show:
                print(f'\nGAME OVER: {e}')
            return (False, path)
    if show:
        print(f'\nLimit of {MAX_STEPS} steps reached')
    return (False, path)

def bfs_find_best_action(palace, kb, show=False):
    """Prefer a known exit after rescue, then the nearest unvisited safe cell.

    Return None when the risk heuristic must choose instead.
    """
    current_pos = palace.captain
    safe_positions = kb.safe_positions()
    if palace.with_colonel and len(kb.exit_certain) > 0:
        exit_pos = list(kb.exit_certain)[0]
        if show:
            print(f'GOAL: reach the exit at {exit_pos}')
        path = bfs_find_path(current_pos, exit_pos, safe_positions, palace.n)
        if path and len(path) > 0:
            return path[0]
    target = find_nearest_unvisited_safe(current_pos, kb, safe_positions, palace.n, show)
    if target:
        path = bfs_find_path(current_pos, target, safe_positions, palace.n)
        if path and len(path) > 0:
            if show:
                print(f'Exploring towards {target}')
            return path[0]
    return None

def bfs_find_path(start, goal, safe_positions, n_grids):
    """Return a shortest action sequence using only known safe cells, or None."""
    if start == goal:
        return []
    queue = deque([(start, [])])
    visited = {start}
    while queue:
        pos, path = queue.popleft()
        for neighbour in kb_neighbours(pos, n_grids):
            if neighbour in visited:
                continue
            if neighbour not in safe_positions:
                continue
            visited.add(neighbour)
            action = get_action(pos, neighbour)
            new_path = path + [action]
            if neighbour == goal:
                return new_path
            queue.append((neighbour, new_path))
    return None

def find_nearest_unvisited_safe(start, kb, safe_positions, n_grids, show=False):
    """Find the nearest unvisited cell reachable through known safe cells."""
    queue = deque([start])
    visited = {start}
    while queue:
        pos = queue.popleft()
        if pos != start and pos not in kb.visited and (pos in safe_positions):
            return pos
        for neighbour in kb_neighbours(pos, n_grids):
            if neighbour in visited:
                continue
            if neighbour not in safe_positions:
                continue
            visited.add(neighbour)
            queue.append(neighbour)
    if show:
        print('No unvisited safe cells')
    return None

def use_grenade(palace, kb, soldier_pos, show=False):
    """Attack an adjacent soldier, or take one safe step towards an attack position."""
    current_pos = palace.captain
    safe_positions = kb.safe_positions()
    action = get_grenade_action(current_pos, soldier_pos)
    if action:
        if show:
            print(f'Throwing a grenade towards {soldier_pos}')
        return action
    soldier_neighbours = kb_neighbours(soldier_pos, kb.n)
    safe_near_soldier = [pos for pos in soldier_neighbours if pos in safe_positions]
    for target in safe_near_soldier:
        path = bfs_find_path(current_pos, target, safe_positions, palace.n)
        if path and len(path) > 0:
            if show:
                print(f'Approaching the soldier')
            return path[0]
    return None

def risky_move(palace, kb, show=False, force=False):
    """Rank neighbours by the original heuristic, not a probability.

    Visited cells add 50; each possible cliff or soldier adds 20. Confirmed
    hazards are excluded. The forced mode permits a previously visited cell.
    """
    current_pos = palace.captain
    neighbours = kb_neighbours(current_pos, palace.n)
    candidates = []
    for neighbour in neighbours:
        if neighbour in kb.cliff_certain or neighbour in kb.soldier_certain:
            continue
        risk = 0
        if neighbour in kb.visited:
            risk += 50
        if neighbour in kb.possible_cliffs():
            risk += 20
        if neighbour in kb.possible_soldier() and kb.soldier_alive:
            risk += 20
        candidates.append((risk, neighbour))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    if force:
        _, best_neighbour = candidates[0]
        if show:
            print(f'FORCED MOVE to {best_neighbour}')
        return get_action(current_pos, best_neighbour)
    risk, best_neighbour = candidates[0]
    if risk < 50:
        if show:
            print(f'Heuristic move to {best_neighbour} (risk score={risk})')
        return get_action(current_pos, best_neighbour)
    return None

def last_move(palace, kb, show=False):
    """Choose a neighbour without a confirmed hazard as a last resort."""
    current_pos = palace.captain
    neighbours = kb_neighbours(current_pos, palace.n)
    for neighbour in neighbours:
        if neighbour not in kb.cliff_certain and neighbour not in kb.soldier_certain:
            if show:
                print(f'LAST RESORT: moving to {neighbour}')
            return get_action(current_pos, neighbour)
    return None
