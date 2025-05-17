"""
Egységtesztek a MatchScorer osztály calculate_score metódusához.
Ez a metódus kiszámítja a pontszámot a tipp és a tényleges eredmény alapján.
"""
import unittest
from HattrickNKPredictor.calculators.models import MatchScorer, Participant


class TestMatchScorer(unittest.TestCase):
    """
    Egységtesztek a MatchScorer osztály calculate_score metódusához.
    Ez a metódus kiszámítja a pontszámot
    a tipp és a tényleges eredmény alapján.
    """

    def test_calculate_score_exact_match(self):
        """Ha a tipp teljesen egyezik az eredménnyel, 5 pont jár."""
        self.assertEqual(MatchScorer.calculate_score((2, 1), (2, 1)), 5)

    def test_calculate_score_correct_outcome_and_diff(self):
        """Ha a tipp győztes és gólkülönbség alapján is helyes, 3 pont jár."""
        self.assertEqual(MatchScorer.calculate_score((3, 1), (2, 0)), 3)

    def test_calculate_score_correct_outcome_only(self):
        """Ha csak a meccs kimenetele
        (győzelem, döntetlen, vereség) stimmel, 2 pont jár."""
        self.assertEqual(MatchScorer.calculate_score((3, 1), (1, 0)), 2)

    def test_calculate_score_correct_home_score(self):
        """Ha csak a hazai csapat gólszáma stimmel, 1 pont jár."""
        self.assertEqual(MatchScorer.calculate_score((0, 1), (0, 0)), 1)

    def test_calculate_score_no_match(self):
        """Ha semmi nem stimmel, 0 pont jár."""
        self.assertEqual(MatchScorer.calculate_score((1, 2), (3, 0)), 0)


class TestParticipant(unittest.TestCase):
    """
    Egységtesztek a Participant osztályhoz, amely a
     játékos tippjeinek és pontszámának kezeléséért felelős.
    """

    def setUp(self):
        """Egy minta résztvevő példány létrehozása a tesztekhez."""
        self.participant = Participant(
            participant_id=1,
            name="Test User",
            predictions=[(1, 0), (2, 1), (0, 0), (1, 1), (3, 2)],
            match_data={
                "tuti_match": 2,  # ez a 3. meccs (index 2)
                "replay": (50, 60, 70),
                "bonus": "A"
            }
        )

    def test_calculate_scores_match_scores(self):
        """
        Teszteli a mérkőzés tipp pontszámítását.
        Ellenőrzi, hogy a 'tuti meccs' duplázva van-e.
        """
        actual_results = [(1, 0), (2, 1), (1, 1), (1, 1), (3, 2)]
        self.participant.calculate_scores(actual_results, (50, 60, 70), "A")
        self.assertEqual(self.participant.match_scores, [5, 10, 3, 5, 5])

    def test_calculate_scores_replay_score(self):
        """
        Teszteli a visszajátszás tipp pontszámítását.
        A különbségek alapján 2 pont/meccs jár, ha 10-en belül van.
        """
        actual_results = [(1, 0), (2, 1), (1, 1), (1, 1), (3, 2)]

        # Pontos találat
        self.participant.calculate_scores(actual_results, (50, 60, 70), "A")
        self.assertEqual(self.participant.replay_score, 6)

        # Mindhárom 5-tel tér el
        self.participant.calculate_scores(actual_results, (55, 65, 75), "A")
        self.assertEqual(self.participant.replay_score, 6)

        # Egyik sem pontos, csak 2
