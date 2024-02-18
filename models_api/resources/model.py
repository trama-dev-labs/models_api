import pickle
import keras.models
from flask_restful import Resource, reqparse, request
from model.modelo import ModeloModel
from model.predict import PredictModel
from security.security import token_required
import pandas as pd
import numpy as np

PATH = "data/models"
StatusCode = {
    'OK':['Success', 200],             
    'NotFound':['ThereIsNoModelForThisComponent', 404]
}

class Model(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('UR_moqa',type=float)
    atributos.add_argument('Temp_moqa',type=float)
    atributos.add_argument('O3_moqa',type=float)
    atributos.add_argument('PM10_moqa',type=float)
    atributos.add_argument('PM2.5_moqa',type=float)
    atributos.add_argument('NO2_moqa',type=float)

    models_ = {'pm25':{"NeedsTreatment":True},
               'pm10':{"NeedsTreatment":True},
               'ur':{"NeedsTreatment":False},
               'temp':{"NeedsTreatment":False},
               'o3':{"NeedsTreatment":False}}
    actual_model = None

    @token_required
    def get(self, model_id):
        model = self.load_model(model_id)
        if model:
            model_json = ModeloModel(model)
            return model_json.json(), StatusCode['OK'][1]
        return StatusCode['NotFound']
    
    @token_required
    def post(self, model_id):
        raw = self.predict(model_id)
        if raw is not None:
           raw =  PredictModel(raw)
           return raw.json(), StatusCode['OK'][1]
        return StatusCode['NotFound']
    
    def get_h5model(path):
        h5_path = str()
        for s in path.split('/')[:-1]:
            h5_path += s+'/'
        h5_path = h5_path + 'h5files/' + path.split('/')[-1]
        return keras.models.load_model(h5_path)

    def load_model(self, model_id, upper = True, is_fix = False):
        if model_id not in self.models_ and not is_fix:
            return None
        file_name = model_id.upper() if upper else model_id
        full_path = PATH + "/" + file_name + "_model.bin"
        model = Model.load_bin_model(full_path)
        return model
    
    def load_bin_model(path):
        model_arq = open(path,'rb')
        model = None
        try:
            model = pickle.load(model_arq)
        except EOFError:
            pass
        model_arq.close()

        if type(model) != dict: return model
        if model['models']['modelo'] == None:
            model['models']['modelo'] = Model.get_h5model(path.replace('bin','h5'))

        return model  

    def round_method(self, predict_value):
        rounded = predict_value.astype('int')
        residual_value = predict_value - rounded
        mask = residual_value <= 0.5
        predict_value[mask] = rounded[mask]
        predict_value[~mask] = rounded[~mask]+1
        return predict_value

    def round_model_method(self, model_id, data):
        id = 'fix/fix_'+model_id
        model = self.load_model(id, upper = False, is_fix = True)
        data['adj'] = model.predict(data[data.columns[:-1]])
        data['prediction'].loc[data['adj']==1] = data['prediction'].loc[data['adj']==1].apply(lambda x : np.ceil(x))
        data['prediction'].loc[data['adj']==0] = data['prediction'].loc[data['adj']==0].apply(lambda x : np.floor(x))
        return data[data.columns[:-1]]

    def predict(self, model_id):
        self.actual_model = self.load_model(model_id)
        request_json = request.get_json()
        raw = None
        if self.actual_model and request_json:
            if isinstance(request_json, list):
                idx = pd.Index(range(len(request_json)))
                raw = pd.DataFrame.from_records(request_json, index = idx)
            else:
                raw = pd.DataFrame( request_json, columns = request_json[0].keys )
            raw = self.regression(model_id, raw)
        return raw
    
    def regression(self, model_id, data):
        predicts = self.actual_model['models']['modelo'].predict(data)
        if Model.models_[model_id]["NeedsTreatment"]:
            if self.actual_model['models']['adjust']:
                data['prediction'] = predicts
                data = self.round_model_method(model_id, data)
                return data
            predicts = Model.round_method(predicts)
        data['prediction'] = predicts
        return data