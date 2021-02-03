from datapackage import DataPackage


class VariationGen:

    def __init__(self, dp):

        self.datapackage = dp

        print(dp.resources)

    def create_variations(self, variations, destination):

        for id, row in variations.iterrows():

            _dp = self.dp.copy()

            self.set_values(_dp, row)

    @staticmethod
    def set_values(_dp, row):
        pass



