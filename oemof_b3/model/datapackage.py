import os

import pandas as pd
from frictionless import Package


class DataFramePackage:
    r"""
    Provides a representation of frictionless datapackages as a collection
    of pandas.DataFrames.
    """
    def __init__(self, basepath, data, rel_paths):

        self.basepath = basepath

        self.rel_paths = rel_paths

        self.data = data

    @classmethod
    def from_csv_dir(cls, dir):
        r"""
        Initialize a DataFramePackage from a csv directory
        """
        rel_paths = cls._get_rel_paths(dir, '.csv')

        data = cls._load_csv(cls, dir, rel_paths)

        return cls(dir, data, rel_paths)

    @classmethod
    def from_metadata(cls, json_file_path):
        r"""
        Initialize a DataFramePackage from the metadata string,
        usually named datapackage.json
        """
        dp = Package(json_file_path)

        dir = os.path.split(json_file_path)[0]

        rel_paths = {r['name']: r['path'] for r in dp.resources}

        data = cls._load_csv(cls, dir, rel_paths)

        return cls(dir, data, rel_paths)

    def to_csv_dir(self, destination):
        r"""
        Save the DataFramePackage to csv files.
        """
        for name, data in self.data.items():
            path = self.rel_paths[name]
            full_path = os.path.join(destination, path)
            self._write_resource(data, full_path)

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
        Load a DataFramePackage from csv files.
        """
        data = {}

        for name, path in rel_paths.items():
            full_path = os.path.join(basepath, path)
            data[name] = self._read_resource(full_path)

        return data

    @staticmethod
    def _read_resource(path):
        return pd.read_csv(path, index_col=0)

    @staticmethod
    def _write_resource(data, path):
        root = os.path.split(path)[0]

        if not os.path.exists(root):
            os.makedirs(root)

        data.to_csv(path)
