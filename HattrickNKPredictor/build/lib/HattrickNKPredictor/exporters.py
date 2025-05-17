"""Modul az NK játék eredményeinek
exportálásához és összesített pontszámok kiszámításához."""
import os
import re
from collections import defaultdict
from typing import List, Tuple
from .models import Participant


def export_results_to_txt(
    participants: List[Participant],
    round_name: str,
    actual_results: List[Tuple[int, int]],
    actual_replay: Tuple[int, int, int],
    correct_bonus: str,
    countrys: List[str],
    output_file: str
):
    """Exportálja az aktuális forduló eredményeit .txt
    formátumba, Hattrick fórum táblázat formában."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"[table][tr][th colspan=10 "
                f"align=center][q]{round_name}[/q][/th][/tr]\n")
        f.write("[tr][th]Össz[/th][td][/td]")

        for i in range(0, len(countrys), 2):
            f.write(f"[td]{countrys[i]} - {countrys[i + 1]}[/td]\n")

        f.write("[td]Replay[/td][td]Bónusz[/td][/tr]\n")
        f.write("[tr][th]Eredmények[/th][td][/td]")

        for match in actual_results:
            f.write(f"[td]{match[0]} - {match[1]}[/td]")

        replay_str = (f"{actual_replay[0]}-"
                      f"{actual_replay[1]}-{actual_replay[2]}")
        f.write(f"[td]{replay_str}[/td][td]{correct_bonus}[/td][/tr]\n")

        for p in sorted(participants, key=lambda x: x.total_score,
                        reverse=True):
            f.write(f"[tr][th]{p.name}[/th][td]{p.total_score}p[/td]")
            for i, pred in enumerate(p.predictions):
                score = p.match_scores[i]
                f.write(f"[td]{pred[0]}-{pred[1]} ({score} p)[/td]")

            replay_txt = (f"{p.replay[0]}-{p.replay[1]}"
                          f"-{p.replay[2]} ({p.replay_score} p)")
            bonus_txt = f"{p.bonus_score} p" if p.bonus_score else "0 p"
            f.write(f"[td]{replay_txt}[/td][td]{bonus_txt}[/td][/tr]\n")

        f.write("[/table]\n")


class NKScoreAggregator:
    """Összesíti a különböző txt fájlokból származó NK pontszámokat."""

    def __init__(self):
        """Inicializálja az üres ponttáblát."""
        self.scores = defaultdict(int)

    def _extract_scores_from_text(self, text: str) -> List[Tuple[str, int]]:
        """Kinyeri a nevet és pontszámot a Hattrick-formátumú táblázatból."""
        pattern = r"\[tr\]\[th\](.*?)\[/th\]\[td\](\d+)p\[/td\]"
        return re.findall(pattern, text)

    def add_file(self, filepath: str):
        """Hozzáadja egy fájl pontszámait az összesítéshez."""
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        extracted = self._extract_scores_from_text(content)
        for name, pts in extracted:
            self.scores[name.strip()] += int(pts)

    def add_folder(self, folder_path: str):
        """Végigolvassa az összes .txt fájlt
        a mappában és hozzáadja az eredményeket."""
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                self.add_file(os.path.join(folder_path, filename))

    def _format_table(self) -> str:
        """Formázza az összesített eredményeket fórum táblázat formátumban."""
        sorted_scores = sorted(self.scores.items(), key=lambda x: -x[1])
        output = "[table]\n"
        output += ("[tr][th colspan=7 align=center]"
                   "[q]Összesített eredmény[/q][/th][/tr]\n")
        output += "[tr][th][/th][th]Név[/th][th]Pontszám[/th][/tr]\n"
        for i, (name, score) in enumerate(sorted_scores, 1):
            output += f"[tr][td]{i}[/td][td]{name}[/td][td]{score}[/td][/tr]\n"
        output += "[/table]"
        return output

    def save_result(self, output_file: str = "score.txt"):
        """Elmenti az összesített táblázatot a megadott fájlba."""
        result = self._format_table()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
