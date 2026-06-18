import unittest

from hnp.sat import parse_dimacs_cnf_text, solve_dimacs_cnf_text


class SatTests(unittest.TestCase):
    def test_parse_dimacs_cnf_text(self):
        formula = parse_dimacs_cnf_text(
            """
            c example
            p cnf 2 2
            1 2 0
            -1 0
            """
        )

        self.assertEqual(2, formula.variables)
        self.assertEqual([(1, 2), (-1,)], formula.clauses)

    def test_solve_dimacs_cnf_text_reports_sat(self):
        result = solve_dimacs_cnf_text("p cnf 1 1\n1 0\n")

        self.assertTrue(result.satisfiable)

    def test_solve_dimacs_cnf_text_reports_unsat(self):
        result = solve_dimacs_cnf_text("p cnf 1 2\n1 0\n-1 0\n")

        self.assertFalse(result.satisfiable)


if __name__ == "__main__":
    unittest.main()
