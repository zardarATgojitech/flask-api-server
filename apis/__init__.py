from flask_restx import Api
from .status import api as ns1
from .stanza import api as ns2

api = Api(
    title='Flask API Server',
    version='1.0',
    description='Contains endpoints for our machine learning skunkworks'
)

api.add_namespace(ns1, path='/status')
api.add_namespace(ns2, path='/stanza')