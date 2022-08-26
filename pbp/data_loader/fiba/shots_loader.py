import json
import os

from file_loader import FibaFileLoader
from pbp.resources.shots.fiba_shot import FibaShot
from pbp_loader import FibaPbpLoader
from web_loader import FibaWebLoader


class FibaShotsLoader(FibaFileLoader, FibaWebLoader):
    """
    Loads FIBA Live Stats pbp data for game
    :param str game_id: FIBA Live Stats Game ID
    :param str source: Where the data should be loaded from - file or web
    :param lst competition: List that contains the name of competition, season and phase in season.
    """
    base_directory = 'C:/Users/alons/PBP Database/'

    def __init__(self, game_id, source, competition):
        self.game_id = game_id
        self.source = source
        self.competition = competition
        self.file_directory = self.base_directory + f'{competition[0]}/{competition[1]}/{game_id}'
        self._load_data()

    def _load_data(self):
        source_method = getattr(self, f'_from_{self.source}')
        source_method()

    def _from_file(self):
        """
        Loads shots data from local file system
        """
        if not self.file_directory:
            raise ValueError('file_directory cannot be None when data source if file')
        self.file_path = f'{self.file_directory}/shots.json'
        self._load_data_from_file()
        self._make_shot_items()

    def _from_web(self):
        """
        Loads shots data from web
        """
        pbp_loader = FibaPbpLoader(self.game_id, self.source, self.competition)
        self.source_data = [s for s in pbp_loader.data if 'x' in s]
        self._save_data_to_file()

    def _save_data_to_file(self):
        self._make_shot_items()
        if self.file_directory:
            if not os.path.isdir(self.file_directory):
                os.makedirs(self.file_directory)
            file_path = f'{self.file_directory}/shots.json'
            with open(file_path, 'w') as outfile:
                json.dump(self.data, outfile, indent=4)

    def _make_shot_items(self):
        self.items = [FibaShot(item) for item in self.source_data]

    @property
    def data(self):
        return [item.data for item in self.items]



game_id = '1758418'
competition = ['Champions League', '2020', 'Qualifiers']
pbp_loader = FibaShotsLoader(game_id, 'web', competition)
print(pbp_loader.data)
