import random

def kb_neighbours(pos, n):
    """Return orthogonally adjacent cells inside the one-based grid."""
    x, y = pos
    out = []
    for x_add, y_add in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        x_new, y_new = (x + x_add, y + y_add)
        if 1 <= x_new <= n and 1 <= y_new <= n:
            out.append((x_new, y_new))
    return out

def get_action(from_pos, to_pos):
    """Return the action between adjacent positions."""
    x_from, y_from = from_pos
    x_to, y_to = to_pos
    if x_to < x_from:
        return 'moveU'
    elif x_to > x_from:
        return 'moveD'
    elif y_to < y_from:
        return 'moveL'
    elif y_to > y_from:
        return 'moveR'

def get_grenade_action(captain_pos, target_pos):
    """Return an attack action for an adjacent target, otherwise None."""
    x_from, y_from = captain_pos
    x_to, y_to = target_pos
    if abs(x_from - x_to) + abs(y_from - y_to) != 1:
        return None
    if x_to < x_from:
        return 'grenadeU'
    elif x_to > x_from:
        return 'grenadeD'
    elif y_to < y_from:
        return 'grenadeL'
    elif y_to > y_from:
        return 'grenadeR'

def print_knowledge_base(palace, kb, percepts):
    """Display inferred facts and unresolved possible locations."""
    breeze, snoring, glow, _, _, _, _, scream = percepts
    safe = kb.safe_positions()
    cliff_positions = kb.possible_cliffs()
    soldier_positions = kb.possible_soldier()
    exit_positions = kb.possible_exit()
    width = 7
    print("\nKnowledge map (the captain's current beliefs):")
    for x in range(1, kb.n + 1):
        row_label = []
        row_coords = []
        for y in range(1, kb.n + 1):
            box = (x, y)
            tag = pos_label(box, palace, kb, breeze, snoring, glow, scream, safe, cliff_positions, soldier_positions, exit_positions)
            row_label.append(f'{tag:<{width}}')
            row_coords.append(f'({x},{y})'.ljust(width))
        print(''.join(row_label))
        print(''.join(row_coords))
        print()
    print(f'Known safe cells: {sorted(list(safe))}')
    if kb.cliff_certain:
        print(f'P! inferred: {sorted(list(kb.cliff_certain))}')
    if kb.soldier_alive and kb.soldier_certain:
        print(f'S! inferred: {sorted(list(kb.soldier_certain))}')
    if kb.exit_certain:
        print(f'E! inferred: {sorted(list(kb.exit_certain))}')

def pos_label(pos, palace, kb, breeze, snoring, glow, scream, safe, cliff_positions, soldier_positions, exit_positions):
    """Choose a display symbol from the current knowledge base."""
    if pos == palace.captain:
        suffix = ''
        if breeze:
            suffix += 'B'
        if snoring and kb.soldier_alive:
            suffix += 'R'
        if glow:
            suffix += 'L'
        if scream:
            suffix += 'G'
        return ('CW' + suffix)[:4]
    if pos in kb.cliff_certain:
        return 'P!'
    if kb.soldier_alive and pos in kb.soldier_certain:
        return 'S!'
    if pos in kb.exit_certain:
        return 'E!'
    if pos in kb.visited:
        return '✓'
    if pos in safe:
        return 'o'
    if pos in cliff_positions and pos in soldier_positions:
        return 'PS?'
    if pos in cliff_positions:
        return 'P?'
    if pos in soldier_positions:
        return 'S?'
    if pos in exit_positions:
        return 'E?'
    return '.'

def random_position(n):
    """Draw a one-based grid position."""
    return (random.randint(1, n), random.randint(1, n))
