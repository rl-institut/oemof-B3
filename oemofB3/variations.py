import os

import pandas as pd


class VariationGen:

    def __init__(self, path_basis_dp):

        self.FILE_EXT = ".csv"

        self.path_basis_dp = path_basis_dp

        self.path_elements = os.path.join(self.path_basis_dp, 'elements')

        self.basis_dp = self.read_elements()

        print(self.basis_dp)

    def get_element_list(self):

        element_list = os.listdir(self.path_elements)

        element_list = [
            os.path.splitext(el)[0] for el in element_list if el.endswith(self.FILE_EXT)
        ]

        return element_list

    def read_elements(self):

        element_list = self.get_element_list()

        elements = {}

        for e in element_list:

            path = os.path.join(self.path_elements, e + self.FILE_EXT)

            df = self.read_element(path)

            elements[e] = df

        return elements

    @staticmethod
    def read_element(element):
        return pd.read_csv(element)

    @staticmethod
    def read_variations(path_variations):
        pd.read_csv(path_variations)

    def create_variations(self, variations, destination):

        for id, row in variations.iterrows():

            dp = self.basis_dp.copy()

            print(id, row)





