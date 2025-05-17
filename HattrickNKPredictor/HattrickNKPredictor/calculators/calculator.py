"""A PredictionGame osztály kezeli az NK
játék résztvevőit és kiszámolja az eredményeket."""
from typing import List
from HattrickNKPredictor.calculators.models import Participant


class PredictionGame:
    """NK játékhoz tartozó pontszámítási
    és rangsorolási logikát tartalmazza."""

    def __init__(self, csv_data: List[List[str]]):
        """Inicializálja a játékot a CSV adatok alapján."""
        self.participants = []
        self.correct_results = None
        self.correct_replay = None
        self.correct_bonus = None
        self.countrys = None
        self._parse_csv(csv_data)

    def _parse_csv(self, csv_data: List[List[str]]):
        """Feldolgozza a CSV adatokat és inicializálja a játék állapotát."""
        *participant_rows, correct_row, country_row = csv_data
        self.countrys = list(country_row)

        self.correct_results = []
        for i in range(2, 12, 2):
            if i + 1 < len(correct_row):
                try:
                    home = int(correct_row[i])
                    away = int(correct_row[i + 1])
                    self.correct_results.append((home, away))
                except (ValueError, IndexError):
                    self.correct_results.append((0, 0))

        try:
            self.correct_replay = (
                int(correct_row[13]),
                int(correct_row[14]),
                int(correct_row[15])
            )
        except (ValueError, IndexError):
            self.correct_replay = (0, 0, 0)

        self.correct_bonus = correct_row[16] if len(correct_row) > 16 else ""

        for row in participant_rows:
            try:
                participant_id = int(row[0])
                name = row[1]

                predictions = []
                for i in range(2, 12, 2):
                    if (i + 1 < len(row) and row[i] != '[]'
                            and row[i + 1] != '[]'):
                        try:
                            home = int(row[i])
                            away = int(row[i + 1])
                            predictions.append((home, away))
                        except (ValueError, IndexError):
                            predictions.append((0, 0))
                    else:
                        predictions.append((0, 0))

                if len(predictions) != 5:
                    print(f"Skipping participant {name}"
                          f" (ID: {participant_id}) due "
                          f"to incomplete predictions.")
                    continue

                tuti_match = int(row[12]) if (len(row) > 12
                                              and row[12] != '[]') else 0

                try:
                    replay = (
                        int(row[13]) if (len(row) > 13 and
                                         row[13] != '[]') else 0,
                        int(row[14]) if (len(row) > 14 and
                                         row[14] != '[]') else 0,
                        int(row[15]) if (len(row) > 15 and
                                         row[15] != '[]') else 0
                    )
                except ValueError:
                    replay = (0, 0, 0)

                bonus = row[16] if len(row) > 16 else ""
                match_data = {
                    "tuti_match": tuti_match,
                    "replay": replay,
                    "bonus": bonus
                }
                self.participants.append(
                    Participant(participant_id, name, predictions, match_data)
                )
            except (ValueError, IndexError) as e:
                print(f"Error parsing row {row}: {e}")

    def calculate_all_scores(self):
        """Kiszámítja minden résztvevő pontszámait."""
        for participant in self.participants:
            participant.calculate_scores(
                self.correct_results,
                self.correct_replay,
                self.correct_bonus
            )

    def get_rankings(self) -> List[Participant]:
        """Visszaadja a résztvevőket pontszám szerint csökkenő sorrendben."""
        return sorted(self.participants, key=lambda p: p.total_score,
                      reverse=True)

    def print_results(self):
        """Kiírja a rangsort a konzolra."""
        rankings = self.get_rankings()
        print("Rank\tID\tName\tTotal\tMatches\tReplay\tBonus")
        for rank, participant in enumerate(rankings, 1):
            print(f"{rank}\t{participant.id}"
                  f"\t{participant.name}"
                  f"\t{participant.total_score}\t"
                  f"{sum(participant.match_scores)}"
                  f"\t{participant.replay_score}\t"
                  f"{participant.bonus_score}")
