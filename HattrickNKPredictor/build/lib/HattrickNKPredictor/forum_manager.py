"""A fórum információt leszedi és átírja csv-re"""

import re
from datetime import datetime
from typing import List, Tuple
from bs4 import BeautifulSoup
from .auth_manager import AuthManager


class ForumFetcher:
    """A Hattrick fórum adatainak letöltéséért felelős osztály."""

    def __init__(self, username, password, forum_url, kezdo, utolso):
        """Inicializálja a lekérdezéshez szükséges adatokat."""
        self.username = username
        self.password = password
        self.forum_url = forum_url
        self.kezdo = kezdo
        self.utolso = utolso
        self.login = AuthManager(self.username, self.password, self.forum_url)
        self.session = None

    def fetch_forum_data(self):
        """Letölti és feldolgozza a fórum hozzászólásokat."""
        self.login.login_forum()
        self.session = self.login.convert_cookies_to_requests()

        forum_data = []
        current_url = f"{self.forum_url}n={self.kezdo}&t=17632450&v=4"
        reached_last = False

        while not reached_last and current_url:
            response = self.session.get(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            for wrapper in soup.select('.cfWrapper'):
                post_data = self.parse_post(wrapper)
                if post_data is None:
                    continue
                if post_data:
                    msg_num = post_data["sorszam"]
                    if msg_num > self.utolso:
                        reached_last = True
                        break
                    forum_data.append(post_data)

            if not reached_last:
                next_link = soup.select_one('a[title="Következő"],'
                                            ' a[accesskey="N"]')
                if next_link and 'href' in next_link.attrs:
                    current_url = (f"https://www.hattrick.org"
                                   f"{next_link['href']}")
                else:
                    break
        self.login.driver.quit()
        return forum_data

    def parse_post(self, wrapper):
        """Kinyeri a szükséges adatokat egy bejegyzésből."""
        msg_number = self.get_msg_number(wrapper)
        username = self.get_referenced_msg(wrapper)
        result = self.extract_match_info(wrapper, int(msg_number.lstrip('#')
                                                      ) == self.utolso)
        if result is None:
            return None
        matches, tuti_indices, replay, bonus, team_names = result

        return {
            "sorszam": int(msg_number.lstrip('#')),
            "felhasznalonev": username,
            "meccsek": matches,
            "tuti": tuti_indices,
            "replay": replay,
            "bonusz": bonus,
            "csapatok": team_names
        }

    def get_msg_number(self, wrapper):
        """Visszaadja a hozzászólás sorszámát."""
        tag = wrapper.select_one('.cfHeader a[id]')
        return tag.text.strip() if tag else None

    def get_referenced_msg(self, wrapper):
        """Visszaadja a hozzászólás írójának nevét."""
        title_links = wrapper.select('.cfHeader a[title]')
        if len(title_links) >= 2:
            return title_links[1]['title']
        return None

    def extract_match_info(self, wrapper, is_last_post=False):
        """Kinyeri az eredményekhez kapcsolódó adatokat egy bejegyzésből."""
        matches = []
        tuti_indices = []
        replay = None
        bonus = None
        team_names = []
        rows = wrapper.select('.htMlTable tr')

        if rows:
            for row_idx, row in enumerate(rows, start=1):
                cols = row.find_all('td')
                if len(cols) == 3:
                    result = cols[2].text.strip()
                    score_match = re.search(r'(\d+\s*-\s*\d+)', result)
                    if score_match:
                        score = score_match.group(1).split("-")
                        matches.append(score[0])
                        matches.append(score[1])
                        if is_last_post:
                            teams = cols[0].text.strip().split(" - ")
                            if len(teams) == 2:
                                team_names.append(teams[0])
                                team_names.append(teams[1])
                        if 't' in result.lower():
                            tuti_indices = row_idx - 1
                elif len(cols) == 2:
                    value = cols[1].text.strip()
                    if re.fullmatch(r'\d{1,3}-\d{1,3}-\d{1,3}', value):
                        replay = value
                    else:
                        bonus = value
        else:
            message_div = wrapper.select_one('.message .hattrick-ml')
            if message_div:
                lines = [line.strip() for line in
                         message_div.get_text('\n')
                         .split('\n') if line.strip()]
                start_processing = False

                for line_idx, line in enumerate(lines, start=1):
                    if not start_processing:
                        if line.lower().startswith("nk "):
                            start_processing = True
                        continue

                    if re.search(r'\bT\b', line, re.IGNORECASE):
                        tuti_indices = line_idx - 2

                    match = re.match(r'^.+? - .+? (?:\(\d+\))?\s*(\d{1}[-:]\d'
                                     r'{1})(?!-)(.*)$', line)
                    if match:
                        score = re.split("[-:]", match.group(1))
                        matches.append(score[0])
                        matches.append(score[1])
                        if 't' in match.group(2).lower():
                            tuti_indices = line_idx - 1
                    elif line.upper().startswith('REPLAY'):
                        if line_idx + 1 < len(lines):
                            replay = lines[line_idx].strip().split(" ")[-1]
                    elif (line.upper().startswith('B\u00d3NUSZ')
                          or line.upper().startswith('BONUS')):
                        bonus = lines[line_idx].strip().split(" ")[-1]

        if len(matches) != 10:
            return None

        return matches, tuti_indices, replay, bonus, team_names

    def save_to_csv(self, forum_data, filename=None):
        """Elmenti a fórum adatait CSV fájlba."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"forum_data_{timestamp}.csv"
        csapatok = ""
        with (open(filename, 'w', encoding='utf-8') as f):
            for post in forum_data:
                meccsek = ','.join(post['meccsek']) if post['meccsek'] else ''
                replay = post['replay'].replace('-', ','
                                                ) if post['replay'] else ''
                bonus = post['bonusz'] if post['bonusz'] else ''
                line = (f"{post['sorszam']},{post['felhasznalonev']},"
                        f"{meccsek},{post['tuti']},{replay},{bonus}\n")
                f.write(line)
                if forum_data[-1] == post:
                    csapatok = ','.join(post['csapatok'])
            f.write(f"{csapatok}\n")


class ForumDateAnalyzer:
    """A Hattrick fórum hozzászólásait dátum szerint csoportosító osztály."""

    def __init__(self, username: str, password: str, forum_url: str):
        self.username = username
        self.password = password
        self.forum_url = forum_url
        self.login = AuthManager(self.username, self.password, self.forum_url)
        self.session = None

    def get_date_ranges(self) -> List[Tuple[int, int]]:
        """
        Visszaadja a dátum szerint csoportosított hozzászólások tartományait,
        de csak azokat, ahol az utolsó hozzászólás Cacci-tól van.
        """
        self.login.login_forum()
        self.session = self.login.convert_cookies_to_requests()

        date_dict = {}
        last_post_authors = {}
        current_url = f"{self.forum_url}n=1"
        has_next_page = True

        while has_next_page:
            response = self.session.get(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            for wrapper in soup.select('.cfWrapper'):
                post_number, date, author = self._extract_post_data(wrapper)
                if post_number is None or date is None:
                    continue

                post_num = int(post_number.lstrip('#'))

                if date not in date_dict:
                    date_dict[date] = (post_num+1, post_num)
                    last_post_authors[date] = author
                else:
                    first, _ = date_dict[date]
                    date_dict[date] = (first, post_num)
                    last_post_authors[date] = author

            next_link = soup.select_one('a[title="Következő"],'
                                        ' a[accesskey="N"]')
            if next_link and 'href' in next_link.attrs:
                current_url = f"https://www.hattrick.org{next_link['href']}"
            else:
                has_next_page = False

        self.login.driver.quit()

        filtered_dates = []
        sorted_dates = sorted(date_dict.keys())
        for date in sorted_dates:
            if last_post_authors.get(date) == "Cacci":
                filtered_dates.append(date_dict[date])

        return filtered_dates

    def _extract_post_data(self, wrapper) -> Tuple[str, str, str]:
        """Kinyeri a hozzászólás számát, dátumát és szerzőjét."""
        post_number_tag = wrapper.select_one('.cfHeader a[id]')
        if not post_number_tag:
            return (None, None, None)
        post_number = post_number_tag.text.strip()

        date_th = wrapper.select_one('.htMlTable th')
        if not date_th:
            return (post_number, None, None)

        date_text = date_th.text.strip()
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_text)
        if not date_match:
            return (post_number, None, None)

        author_links = wrapper.select('.cfHeader a[title]')
        author = author_links[1]['title'] if len(author_links) >= 2 else None

        return (post_number, date_match.group(0), author)
