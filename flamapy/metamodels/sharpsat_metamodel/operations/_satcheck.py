"""Satisfiability pre-check guarding the pyunigen calls.

pyunigen (the UniGen/ApproxMC binding) segfaults the whole interpreter when handed an
unsatisfiable formula (found by the 2.8 calibration runs, where it silently killed worker
pools), so every operation checks the CNF with a plain SAT call first and short-circuits
the trivial answer (count 0 / empty sample) instead of crashing.
"""
from pysat.solvers import Solver


def satisfiable(clauses: list[list[int]]) -> bool:
    solver = Solver(name='glucose3', bootstrap_with=clauses)
    try:
        return bool(solver.solve())
    finally:
        solver.delete()
