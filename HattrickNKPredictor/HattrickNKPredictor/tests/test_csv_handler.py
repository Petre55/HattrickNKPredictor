"""
Egységtesztek a CSVhandler osztályhoz, amely CSV fájlok kezelését végzi.
"""
import unittest
import os
import tempfile
from unittest.mock import patch
import pandas as pd
from HattrickNKPredictor.forum.csv_handler import CSVhandler


class TestCSVHandler(unittest.TestCase):
    """
    Egységtesztek a CSVhandler osztályhoz, amely CSV fájlok kezelését végzi.
    """

    def setUp(self):
        """Minden teszthez új CSVhandler példányt hozunk létre."""
        self.handler = CSVhandler()

    @patch('os.listdir')
    @patch('os.path.getmtime')
    def test_get_latest_file(self, mock_mtime, mock_listdir):
        """
        Teszteli, hogy a get_latest_file metódus helyesen választja ki
        a legutoljára módosított CSV fájlt.
        """
        mock_listdir.return_value = [
            "forum_data_20230101_120000.csv",
            "forum_data_20230102_120000.csv",
            "other_file.txt"  # ezt figyelmen kívül kell hagynia
        ]
        mock_mtime.side_effect = [100, 200, 300]  # fájlok módosítási ideje

        latest = self.handler.get_latest_file()
        self.assertIn("forum_data_20230102_120000.csv", latest)

    @patch('HattrickNKPredictor.forum.csv_handler.CSVhandler.get_latest_file')
    @patch('pandas.read_csv')
    def test_read_latest_forum_csv(self, mock_read_csv, mock_get_latest):
        """
        Teszteli, hogy a read_latest_forum_csv metódus helyesen hívja meg
        a pandas.read_csv függvényt a legfrissebb fájl nevével.

        """
        mock_get_latest.return_value = "test.csv"
        mock_read_csv.return_value = (pd.DataFrame
                                      ({'col1': [1, 2], 'col2': [3, 4]}))

        df = self.handler.read_latest_forum_csv()
        self.assertEqual(len(df), 2)
        mock_read_csv.assert_called_with("test.csv")

    def test_csv_reader(self):
        """
        Teszteli a csv_reader metódust,
        amely fájlból soronként olvassa be az adatokat.
        """
        test_data = "1,User1,1,0,2,1\n2,User2,0,1,1,1\n"
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(test_data)
            temp_path = temp_file.name

        try:
            result = self.handler.csv_reader(temp_path)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], ["1", "User1", "1", "0", "2", "1"])
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
