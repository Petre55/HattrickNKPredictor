"""CSV handler modul: fórumhoz kapcsolódó CSV fájlok betöltése és kezelése."""
import csv
import os
import pandas as pd
DOWNLOAD_DIR = os.path.dirname(os.path.abspath(__file__))


class CSVhandler:
    """CSV fájlok kezelésére szolgáló osztály."""
    def get_latest_file(self):
        """Megkeresi a legutoljára módosított
        'forum_data*.csv' fájlt a letöltési mappában."""
        files = [
            f for f in os.listdir(DOWNLOAD_DIR)
            if f.startswith("forum_data") and f.endswith(".csv")
        ]

        if not files:
            raise FileNotFoundError("No CSV file found for today's date")

        latest_file = max(files, key=lambda f: os.path.
                          getmtime(os.path.join(DOWNLOAD_DIR, f)))
        return os.path.join(DOWNLOAD_DIR, latest_file)

    def read_latest_forum_csv(self):
        """Beolvassa a legutóbbi 'forum_data*.csv'
         fájlt Pandas DataFrame-ként."""
        file_path = self.get_latest_file()
        return pd.read_csv(file_path)

    def csv_reader(self, file):
        """Beolvassa a megadott CSV fájlt soronként listába."""
        csv_data = []
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                csv_data.append(row)
        return csv_data


handler = CSVhandler()
