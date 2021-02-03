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


