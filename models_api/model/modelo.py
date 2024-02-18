class ModeloModel:
    def __init__(self, model):
        self.variables = model['models']['var']
        self.model_type = model['method']

    def json(self):
        return {
            'model_type': self.model_type,
            'variables': self.variables,
        }