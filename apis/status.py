from flask_restx import Namespace, Resource, fields

api = Namespace('status', description="Status of server")

@api.route('/')
class Status(Resource):
    @api.doc('status')
    def get(self):
        #Return {up: true} and a 200 Status code
        return {'up': True}
