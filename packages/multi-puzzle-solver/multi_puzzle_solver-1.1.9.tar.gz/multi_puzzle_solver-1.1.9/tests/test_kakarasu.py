import numpy as np

from puzzle_solver import kakarasu_solver as solver
from puzzle_solver.core.utils import get_pos

def test_toy():
    top = np.array(['30', '15', '9', '18', '10', '17', '30', '30', '10'])
    side = np.array(['42', '30', '24', ' ', ' ', '17', '8', '14', '21'])
    binst = solver.Board(top=top, side=side)
    solutions = binst.solve_and_print()
    assert len(solutions) == 1, f'unique solutions != 1, == {len(solutions)}'
    solution = solutions[0].assignment


if __name__ == '__main__':
    test_toy()
