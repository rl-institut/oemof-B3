import os

import pandas as pd

from frictionless import steps, transform


class VariationGen:

    def __init__(self, dp):

        self.datapackage = dp

    def create_variations(self, variations, destination):

        for id, row in variations.iterrows():

            _dp = self.datapackage.to_copy()

            _dp = self.set_values(_dp, row)
            print('saving')
            _dp.to_json('~/Desktop/pack.json')

    @staticmethod
    def set_values(_dp, row):
        from pprint import pprint
        # evtl https: // github.com / frictionlessdata / datapackage - pipelines - pandas - driver
        element, variable = row.index.item()

        value = row.item()

        print(element)
        print(variable)
        print(value)

        e = _dp.get_resource(element)
        print(e.name)
        dd = e.read_data()

        # https://frictionlessdata.io/tooling/python/transforming-data/#set-cells
        e = transform(
            e,
            steps=[
                steps.cell_set(field_name=variable, value=100),
            ]
        )
        dd = e.read_data()

        return _dp


class DataDict:
    def __init__(self, dict):
        self.dict = dict

    @classmethod
    def from_csv_dir(cls, dir):

        file_dict = cls.get_file_dict(dir, '.csv')

        data_dict = cls.load_csv(cls, file_dict)

        return cls(data_dict)

    @staticmethod
    def get_file_dict(dir, file_ext):

        file_dict = {}
        for root, dirs, files in os.walk(dir):
            print(dirs)
            for file in files:
                if file.endswith(file_ext):
                    name = file.strip(file_ext)
                    file_dict[name] = os.path.join(root, file)

        return file_dict

    def load_csv(self, file_dict):
        data_dict = {}
        for name, path in file_dict.items():
            data_dict[name] = self.read_data(path)

        return data_dict

    @staticmethod
    def read_data(path):
        return pd.read_csv(path)
