from flask import Flask
from flask_restful import Api
from resources.model import Model
from resources.user import User

def create_app():
    app = Flask( __name__ )
    app.config['SECRET_KEY'] = '42bd04f8-02c6-46ea-bf42-7bd5d8bc0e08'
    return app

def create_api(): 

    api = Api(app)
    api.add_resource(Model, '/predict/<string:model_id>',
                     endpoint='/predict/<string:model_id>')
    api.add_resource(Model, '/variables/<string:model_id>',
                     endpoint='variables/<string:model_id>')
    api.add_resource(User, '/login',
                     endpoint='/login')

app = create_app()
api = create_api()

if __name__ == '__main__':
    app.run(debug = True)