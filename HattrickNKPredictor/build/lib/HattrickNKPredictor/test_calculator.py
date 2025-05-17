"""
Egységtesztek a PredictionGame osztályhoz.
"""
import unittest
from unittest.mock import patch, mock_open
from .calculator import PredictionGame


class TestPredictionGame(unittest.TestCase):
    """
    Egységtesztek a PredictionGame osztályhoz.
    """

    def setUp(self):
        """
        Minta bemeneti adatok beállítása minden teszteset előtt.
        """
        self.sample_csv_data = [
            ["1", "User1", "1", "0", "2", "1",
             "0", "0", "1", "1", "3", "2", "2", "50", "60", "70", "A"],
            ["2", "User2", "0", "1", "1",
             "1", "2", "1", "0", "0", "1", "2", "3", "55", "65", "75", "B"],
            ["3", "User3", "1", "1", "0",
             "0", "1", "0", "2", "1", "0", "1", "1", "60", "70", "80", "C"],
            ["", "", "1", "0", "2", "1", "1",
             "1", "3", "2", "1", "2", [], "50", "60", "70", "A"],
            ["TeamA", "TeamB", "TeamC", "TeamD", "TeamE",
             "TeamF", "TeamG", "TeamH", "TeamI", "TeamJ"]
        ]

    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.reader')
    def test_parse_csv(self, mock_csv_reader):
        """
        Teszteli a PredictionGame osztály
        konstruktorában történő CSV-feldolgozást.
        """
        mock_csv_reader.return_value = self.sample_csv_data
        game = PredictionGame(self.sample_csv_data)

        self.assertEqual(len(game.participants), 3)
        self.assertEqual(game.correct_results, [(1, 0), (2, 1),
                                                (1, 1), (3, 2), (1, 2)])
        self.assertEqual(game.correct_replay, (50, 60, 70))
        self.assertEqual(game.correct_bonus, "A")
        self.assertEqual(game.countrys,
                         ["TeamA", "TeamB", "TeamC", "TeamD", "TeamE",
                          "TeamF", "TeamG", "TeamH", "TeamI", "TeamJ"])

    def test_calculate_all_scores(self):
        """
        Teszteli a pontszámítás működését.

        """
        game = PredictionGame(self.sample_csv_data)
        game.calculate_all_scores()

        self.assertEqual(game.participants[0].match_scores[1], 10)

        rankings = game.get_rankings()
        self.assertEqual(rankings[0].name, "User1")

    def test_print_results(self):
        """
        Teszteli, hogy a print_results metódus hibamentesen lefut-e.
        """
        game = PredictionGame(self.sample_csv_data)
        game.calculate_all_scores()

        try:
            game.print_results()
        except TimeoutError as e:
            self.fail(f"print_results() raised "
                      f"{type(e).__name__} unexpectedly")


if __name__ == '__main__':
    unittest.main()
