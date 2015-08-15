from flask_restful import Resource


class BaseResource(Resource):
    def get(self, **kwargs):
        return 'Not Implemented', 501

    def put(self, **kwargs):
        return 'Not Implemented', 501

    def delete(self, **kwargs):
        return 'Not Implemented', 501


class BaseRepositoryResource(Resource):
    def get(self, **kwargs):
        return 'Not Implemented', 501

    def post(self, **kwargs):
        return 'Not Implemented', 501
