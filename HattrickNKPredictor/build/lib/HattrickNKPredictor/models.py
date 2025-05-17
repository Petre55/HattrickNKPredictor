"""Kiszámítja a tippek pontjait a valós eredmények alapján."""
from typing import List, Tuple


class MatchScorer:
    """Kiszámítja a tippek pontjait a valós eredmények alapján."""
    @staticmethod
    def calculate_score(prediction: Tuple[int, int],
                        actual: Tuple[int, int]) -> int:
        """Kiszámítja a pontot egy adott jóslat és valódi eredmény alapján."""
        pred_home, pred_away = prediction
        actual_home, actual_away = actual

        if prediction == actual:
            return 5

        pred_diff = pred_home - pred_away
        actual_diff = actual_home - actual_away
        pred_outcome = 'H' if pred_diff > 0 else 'D' if pred_diff == 0 else 'A'
        actual_outcome = 'H' if actual_diff > 0 \
            else 'D' if actual_diff == 0 else 'A'

        if pred_outcome == actual_outcome:
            if pred_diff == actual_diff:
                return 3
            return 2

        if pred_home == actual_home or pred_away == actual_away:
            return 1

        return 0


class Participant:
    """A játékos osztálya, amely tárolja az összes jóslatot
    , a válaszokat és a pontokat."""

    def __init__(self, participant_id: int, name: str,
                 predictions: List[Tuple[int, int]], match_data: dict):
        """Inicializálja a játékos adatait."""
        self.id = participant_id
        self.name = name
        self.predictions = predictions
        self.tuti_match = match_data["tuti_match"]
        self.replay = match_data["replay"]
        self.bonus = match_data["bonus"]
        self.match_scores = [0] *len(predictions)
        self.total_score = 0
        self.replay_score = 0
        self.bonus_score = 0

    def calculate_scores(self, actual_results: List[Tuple[int, int]],
                         actual_replay: Tuple[int, int, int],
                         correct_bonus: str):
        """Kiszámítja a játékos összes pontját."""
        for i, (pred, actual) in enumerate(
                zip(self.predictions, actual_results)):
            score = MatchScorer.calculate_score(pred, actual)
            if (i + 1) == self.tuti_match:
                score *= 2
            self.match_scores[i] = score

        self.replay_score = sum(
            2 for p, a in zip(self.replay, actual_replay) if abs(p - a) <= 5
        ) + sum(
            1 for p, a in zip(self.replay, actual_replay)
            if 5 < abs(p - a) <= 10
        )

        self.bonus_score = 1 if self.bonus == correct_bonus else 0

        self.total_score = (sum(self.match_scores)
                            + self.replay_score + self.bonus_score)
