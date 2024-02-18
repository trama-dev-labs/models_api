class PredictModel:
    def __init__(self, data):
        self.data = data
        self.variables = data[data.columns[:-1]]
        self.predict = data['prediction']

    def json(self):
        return self.data.to_dict('records')