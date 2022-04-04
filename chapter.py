from flask import Flask, json, request
from flask_restful import Resource, Api

app = Flask(__name__)
app.debug = False
api = Api(app)

ACCOUNTS = [{"name": "admin", "account": 9999999999, "balance": 1000.00}]

def add(name = "admin", account = 9999999999, balance = 1000.00):
    ACCOUNTS.append({"name": name, "account": account, "balance": balance})

class Users(Resource):
    def get(self):
        try:
            result = app.response_class( response = json.dumps({'data' : ACCOUNTS}), status=200, mimetype='application/json')
            result.headers.add('Access-Control-Allow-Origin', '*')
            return result
        except Exception as e:
            result = app.response_class( response = json.dumps({'errorMsg' : "Ha ocurrido un error en el sitema. Por favor, intente más tarde."}), status=500, mimetype='application/json')
            result.headers.add('Access-Control-Allow-Origin', '*')
            print(e)
            return result

    def post(self):
        try:
            data = request.get_json()
            isError = False
            missFields = []
            
            if "name" not in data:
                isError = True
                missFields.append("name")
            
            if "account" not in data:
                isError = True
                missFields.append("account")

            if "balance" not in data:
                isError = True
                missFields.append("balance"),

            if isError:
                result = app.response_class( response = json.dumps({'errorMsg' : "El cuerpo no contiene el(los) campo(s): " + str(missFields)}), status=400, mimetype='application/json')
            else:
                add(data["name"],data["account"],data["balance"])
                result = app.response_class( response = json.dumps({'errorMsg' : "Usuario creado exitosamente"}), status=201, mimetype='application/json')
            
            result.headers.add('Access-Control-Allow-Origin', '*')
            return result
        except Exception as e:
            result = app.response_class( response = json.dumps({'errorMsg' : "Ha ocurrido un error en el sitema. Por favor, intente más tarde."}), status=500, mimetype='application/json')
            result.headers.add('Access-Control-Allow-Origin', '*')
            print(e)
            return result
                

api.add_resource(Users, '/users')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)  # run our Flask app