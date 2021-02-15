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
    r"""
    Provides a representation of frictionless datapackages in pandas format.
    """
    def __init__(self, basepath, data_dict, file_dict):

        self.basepath = basepath

        self.data_dict = data_dict

        self.file_dict = file_dict

    @classmethod
    def from_csv_dir(cls, dir):

        file_dict = cls.get_file_dict(dir, '.csv')

        data_dict = cls.load_csv(cls, dir, file_dict)

        return cls(dir, data_dict, file_dict)

    @staticmethod
    def get_file_dict(dir, file_ext):

        file_dict = {}
        for root, dirs, files in os.walk(dir):

            rel_path = os.path.relpath(root, dir)

            for file in files:
                if file.endswith(file_ext):
                    name = file.strip(file_ext)
                    file_dict[name] = os.path.join(rel_path, file)

        return file_dict

    def load_csv(self, basepath, file_dict):
        data_dict = {}

        for name, path in file_dict.items():
            full_path = os.path.join(basepath, path)
            data_dict[name] = self.read_data(full_path)

        return data_dict

    def save_csv(self, destination):

        for name, data in self.data_dict.items():
            path = self.file_dict[name]
            full_path = os.path.join(destination, path)
            self.write_data(data, full_path)

    @staticmethod
    def read_data(path):
        return pd.read_csv(path)

    @staticmethod
    def write_data(data, path):
        root = os.path.split(path)[0]

        if not os.path.exists(root):
            os.makedirs(root)

        data.to_csv(path)
