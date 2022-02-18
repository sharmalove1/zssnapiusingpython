from flask import Flask, request, json, Response
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS,cross_origin
from bson.objectid import ObjectId
import logging as log
import requests
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)

class ZssnAPI:
    def __init__(self,data):
        log.basicConfig(level=log.DEBUG,format='%(asctime)s%(levelname)s:\n%(message)s\n')
        self.client = MongoClient("mongodb://localhost:27017/")
        database = data['zssnDB']
        collection = data['survivers']
        cursor = self.client[database]
        self.collection = cursor[collection]
        self.data = data

    def read(self):
        log.info('Reading All data')
        documents = self.collection.find({},{"id":1,"name":1,"gender":1,"location":1,"report":1,"infected":1})
        output = [{item:data[item] for item in data if item !="_id"} for data in documents]
        return output

    def write(self,data):
        log.info("Writing Data")
        new_document = data['Document']
        response = self.collection.insert_one(new_document)
        output = {'Status':'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        return output

    def update(self,id,data):
        log.info("Updating Data")
        filt = self.find({"_id":ObjectId(id)})
        updated_data = {'$set':{'location':{'latitude':data['latitude'],'longitude':data['longitude']}}}
        response = self.collection.update_one(filt,updated_data)
        output = {'Status':'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
        return output

    def get_infected(self):
        log.info("Reading infected and non infected")
        var totalDocument = db.collection.count()
        documents = db.collection.aggregate({"$group":{"_id":"big"},"report":1,"infected":{"$sum":1},"noninfected":{"$sum":1}}},
                    {"$project":{"count":1,"percentage":{"$multiply":[ {"$divide":[100,totalDocument]},"$count"]}}})

        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output

@app.route('/')
def base():
    return Response(response=json.dumps({"Status": "UP"}),
                    status=200,
                    mimetype='application/json')


@app.route('/survivors', methods=['GET'])
def survivers_read():
    data = request.json
    if data is None or data == {}:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.read()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/survivors/reports', methods=['GET'])
def survivers_read():
    data = request.json
    if data is None or data == {}:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.get_infected()
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

@app.route('/survivers', methods=['POST'])
def survivers_write():
    data = request.json
    if data is None or data == {} or 'Document' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.write(data)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')


@app.route('/survivers/:id', methods=['PUT'])
def survivers_update():
    data = request.json
    if data is None or data == {} or 'Filter' not in data:
        return Response(response=json.dumps({"Error": "Please provide connection information"}),
                        status=400,
                        mimetype='application/json')
    obj1 = MongoAPI(data)
    response = obj1.update(id,obj1)
    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
