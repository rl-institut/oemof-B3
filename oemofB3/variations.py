import os

import pandas as pd

from frictionless import steps, transform, Package


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
    def __init__(self, basepath, data, rel_paths):

        self.basepath = basepath

        self.rel_paths = rel_paths

        self.data = data

    @classmethod
    def from_csv_dir(cls, dir):
        r"""
        Initialize a DataDict from a csv directory
        """
        rel_paths = cls._get_rel_paths(dir, '.csv')

        data = cls._load_csv(cls, dir, rel_paths)

        return cls(dir, data, rel_paths)

    @classmethod
    def from_metadata(cls, json_file_path):
        r"""
        Initialize a DataDict from the metadata string,
        usually named datapackage.json
        """
        dp = Package(json_file_path)

        dir = os.path.split(json_file_path)[0]

        rel_paths = {r['name']: r['path'] for r in dp.resources}

        data = cls._load_csv(cls, dir, rel_paths)

        return cls(dir, data, rel_paths)

    @staticmethod
    def _get_rel_paths(dir, file_ext):
        r"""
        Get paths to all files in a given directory relative
        to the root with a given file extension.
        """
        rel_paths = {}
        for root, dirs, files in os.walk(dir):

            rel_path = os.path.relpath(root, dir)

            for file in files:
                if file.endswith(file_ext):
                    name = file.strip(file_ext)
                    rel_paths[name] = os.path.join(rel_path, file)

        return rel_paths

    def _load_csv(self, basepath, rel_paths):
        r"""
        Load a DataDict from csv files.
        """
        data = {}

        for name, path in rel_paths.items():
            full_path = os.path.join(basepath, path)
            data[name] = self._read_resource(full_path)

        return data

    def to_csv_dir(self, destination):
        r"""
        Save the DataDict to csv files.
        """
        for name, data in self.data.items():
            path = self.rel_paths[name]
            full_path = os.path.join(destination, path)
            self._write_resource(data, full_path)

    @staticmethod
    def _read_resource(path):
        return pd.read_csv(path)

    @staticmethod
    def _write_resource(data, path):
        root = os.path.split(path)[0]

        if not os.path.exists(root):
            os.makedirs(root)

        data.to_csv(path)
