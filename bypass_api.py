from flask import Flask, json
from flask_restful import Resource, Api, reqparse
import re

#iv should always be different, but to avoid trouble it is fixed here
#key = b'0123456789ABCDEF'
#the_key = '0123456789'
#ivd = b'0000000000000000'

#dbuser = 'admin'
#dbuser = 'root'
#dbpswd = 'sakapuku123!'
#dbhost = 'db-interbanks.c3ebzwhrotdf.us-east-2.rds.amazonaws.com'
#dbhost = 'localhost'
#dbschema = 'bank_zeus'

#sm_accs = ["3847563921", "9855748371", "7733987112", "9843282828"]

app = Flask(__name__)
#app.debug = True
api = Api(app)

class Users(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('token', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        flag, rtoken = verifyu(args['token'])

        if(flag == 1):
            result = app.response_class( response = json.dumps({'message' : "Usuario o cuenta no encontrados"}), status=404, mimetype='application/json')
        elif(flag == 2):
            result = app.response_class( response = json.dumps({'message' : "Solicitud erronea"}), status=400, mimetype='application/json')
        else:
            result = app.response_class( response = json.dumps({'token' : rtoken}), status=200, mimetype='application/json')

        result.headers.add('Access-Control-Allow-Origin', '*')
        return result
        

    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('token', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        flag, rtoken = verifyu(args['token'])

        if(flag == 1):
            result = app.response_class( response = json.dumps({'message' : "Usuario o cuenta no encontrados"}), status=404, mimetype='application/json')
        elif(flag == 2):
            result = app.response_class( response = json.dumps({'message' : "Solicitud erronea"}), status=400, mimetype='application/json')
        else:
            result = app.response_class( response = json.dumps({'token' : rtoken}), status=200, mimetype='application/json')

        result.headers.add('Access-Control-Allow-Origin', '*')
        return result


class Payments(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('token', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        code = verifyt(args['token'])

        if(code == 0):
            result = app.response_class( response = json.dumps({'code' : 0 , 'message': "OK"}), status=200, mimetype='application/json')
        elif (code == 1):
            result = app.response_class( response = json.dumps({'code' : 1 , 'message': "Fondos Insuficientes" }), status=404, mimetype='application/json')
        elif (code == 2):
            result = app.response_class( response = json.dumps({'code' : 2 , 'message': "Cuentas inexistentes" }), status=404, mimetype='application/json')
        elif (code == 3):
            result = app.response_class( response = json.dumps({'code' : 3 , 'message': "Token no válido" }), status=404, mimetype='application/json')
        elif (code == 4):
            result = app.response_class( response = json.dumps({'code' : 4 , 'message': "Solicitud erronea" }), status=400, mimetype='application/json')
        else:
            result = app.response_class( response = json.dumps({'code' : 5 , 'message': "Ha ocurrido un error, intente más tarde" }), status=500, mimetype='application/json')

        result.headers.add('Access-Control-Allow-Origin', '*')
        return result

    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('token', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        code = verifyt(args['token'])

        if(code == 0):
            result = app.response_class( response = json.dumps({'code' : 0 , 'message': "OK"}), status=200, mimetype='application/json')
        elif (code == 1):
            result = app.response_class( response = json.dumps({'code' : 1 , 'message': "Fondos Insuficientes" }), status=404, mimetype='application/json')
        elif (code == 2):
            result = app.response_class( response = json.dumps({'code' : 2 , 'message': "Cuentas inexistentes" }), status=404, mimetype='application/json')
        elif (code == 3):
            result = app.response_class( response = json.dumps({'code' : 3 , 'message': "Token no válido" }), status=404, mimetype='application/json')
        elif (code == 4):
            result = app.response_class( response = json.dumps({'code' : 4 , 'message': "Solicitud erronea" }), status=400, mimetype='application/json')
        else:
            result = app.response_class( response = json.dumps({'code' : 5 , 'message': "Ha ocurrido un error, intente más tarde" }), status=500, mimetype='application/json')

        result.headers.add('Access-Control-Allow-Origin', '*')
        return result


api.add_resource(Users, '/users')
api.add_resource(Payments, '/pays')

def verifyu(rtoken):
    valid = 2
    gtoken = ""

    data = rtoken.split("-")
    if (len(data) != 3):
        return valid, gtoken

    header = data[0]
    userid = data[1]
    accnum = data[2]
    #userpw = data[3]

    head_match = bool(re.match("^[0-3]{1}[0|1]{1}[0-2]{1}$",header))
    user_match = bool(re.match("^\d{10}$",userid))
    uacc_match = bool(re.match("^\d{10}$",accnum))
    card_match = bool(re.match("^\d{16}$",accnum))

    if (not head_match or not user_match or (header[1] == "0" and not uacc_match) or (header[1] == "1" and not card_match)):
        return valid, gtoken
 
    try:
        valid = 0
        gtoken = "0123456789abcdef0123456789abcdef"           
    except:
        valid = 1
        gtoken = ""
    
    return valid, gtoken

def verifyt(rtoken):
    outcode = 4

    data = rtoken.split("-")
    if (len(data) != 3):
        return outcode

    header = data[0]
    tokenv = data[1]
    money = data[2]

    head_match = bool(re.match("^[0-3]{1}[0|1]{1}[0-2]{1}$",header))
    tok_match = bool(re.match("^[0-9|a-f]{32}$",tokenv))
    fun_match = bool(re.match("^\d{1,13}\.\d{2}$",money))

    if (not head_match or not tok_match or not fun_match):
        return outcode
 
    try:
        outcode = 0
                   
    except:
        outcode = 5

    return outcode

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)  # run our Flask app