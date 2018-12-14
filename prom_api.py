#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from flask_restful import Resource, Api
from json import dumps
#from flask.ext.jsonpify import jsonify
import xmlrpclib
import os

# dict = {'Empty default list for ProdNd!': u'Пустой список НД для выбранного НД продукта!'}
#
# def _(t):
#     return dict.get(t, t)

srv = 'http://localhost:8069'
db = 'pm'
login = 'dom333122@yandex.ru'
pwd = '1'
key =  '51cd18aaa30ca5d1397581f9fed6a747' # md5 for ts '1517433199'


# --- Test
# db = 'lab-test'
# db = 'gn3'
# login = 'kinder001@gmail.com'
# pwd = 'klen97klen97'
# -------------------------


common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % srv)
print(common.version())

uid = common.authenticate(db, login, pwd, {})

print ('uid: %s' % str(uid))

app = Flask(__name__)
api = Api(app)


def required_fields(data):
    print "data:",data
    fields = (
        "CompanyINN",
        "AvCounterpartyINN",
        "AvNumberContract",
        "AvNumberSpecification",
        "AvDateContract",
        "AvTypeTransactionContract",
        # "AvNumberDocument",
        # "AvNumberDate",
        "AvSumContract",
        "AvCostItemContract",
        # "AvNumberPaymentContract ",
        # "AvPurposePaymentContract",
        # "AvCommentContract",
    )
    res = []
    for f in fields:
        if data.get(f) == None:
            # res[f] = "Field is required!")
            res.append(f)
    return res

class finn_transaction(Resource):
    def post(self):
        global db
        global uid
        global pwd
        global key

        try:
            

            data = request.form
            
            if not data :
                data = request.get_json() 

            if not data:
                return {"status":"error", "message" : str("I cant read your data."),"code":501}, 200

            if data.get('key') != key :
                return {"status":"error", "message" : str("Wrong key!"),"code":502}, 200

            req = required_fields(data)
            if req:
                return {"status":"error", "message" : str("Not all required fields is come!"), "fields":req ,"code":503}, 200

            del data['key'] # remove key
            api = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % srv)
            res = api.execute_kw(db, uid, pwd, 'prom.finn_transaction', 'api_create_line', [data])
            # if not res: 
            # print res
            # if res.get('error'): raise Exception(res['error'])
            if res == "":
                return {"status":"error", "message" : str("record is create, but in server was deep error! Call to administrator"),"code":504}, 200
            return res # Fetches first column that is Employee ID
        except Exception as ex:
            return {"status":"error", "message" : str(ex)}, 500

# class Tracks(Resource):
#     def get(self):
#         conn = db_connect.connect()
#         query = conn.execute("select trackid, name, composer, unitprice from tracks;")
#         result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
#         return jsonify(result)
#
# class Employees_Name(Resource):
#     def get(self, employee_id):
#         conn = db_connect.connect()
#         query = conn.execute("select * from employees where EmployeeId =%d "  %int(employee_id))
#         result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
#         return jsonify(result)


# api.add_resource( Labs, '/labs' ) # Route_1
api.add_resource( finn_transaction, '/finn_transaction/new', methods=['POST'] )
# api.add_resource(Tracks, '/tracks') # Route_2
# api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3


if __name__ == '__main__':
     app.run(host='0.0.0.0',port=5002)
