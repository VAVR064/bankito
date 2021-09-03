from flask import Flask
from flask_restful import Resource, Api, reqparse
import re
import mysql.connector
import secrets

from mysql.connector import cursor

#iv should always be different, but to avoid trouble it is fixed here
#key = b'0123456789ABCDEF'
#the_key = '0123456789'
#ivd = b'0000000000000000'

dbuser = 'admin'
#dbuser = 'root'
dbpswd = 'sakapuku123!'
dbhost = 'db-interbanks.c3ebzwhrotdf.us-east-2.rds.amazonaws.com'
#dbhost = 'localhost'
dbschema = 'bank_zeus'

sm_accs = ["3847563921", "9855748371", "7733987112", "9843282828"]

app = Flask(__name__)
#app.debug = True
api = Api(app)

class Users(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('token', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        flag, token = verifyu(args['token'])

        if(flag == 1):
            return {'message': "Usuario o cuenta no encontrados" }, 404
        elif(flag == 2):
            return {'message': "Solicitud erronea" }, 400
        else:
            return {"token" : token} , 200

    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('token', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        flag, token = verifyu(args['token'])

        if(flag == 1):
            return {'message': "Usuario o cuenta no encontrados" }, 404
        elif(flag == 2):
            return {'message': "Solicitud erronea" }, 400
        else:
            return {"token" : token} , 200

class Payments(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('token', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        code = verifyt(args['token'])

        if(code == 0):
            return {'code' : 0 , 'message': "OK"}, 200
        elif (code == 1):
            return {'code' : 1 , 'message': "Fondos Insuficientes" }, 404
        elif (code == 2):
            return {'code' : 2 , 'message': "Cuentas inexistentes" }, 404
        elif (code == 3):
            return {'code' : 3 , 'message': "Token no válido" }, 404
        elif (code == 4):
            return {'code' : 4 , 'message': "Solicitud erronea" }, 400
        else:
            return {'code' : 5 , 'message': "Ha ocurrido un error, intente más tarde" }, 404

    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('token', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        code = verifyt(args['token'])

        if(code == 0):
            return {'code' : 0 , 'message': "OK"}, 200
        elif (code == 1):
            return {'code' : 1 , 'message': "Fondos Insuficientes" }, 404
        elif (code == 2):
            return {'code' : 2 , 'message': "Cuentas inexistentes" }, 404
        elif (code == 3):
            return {'code' : 3 , 'message': "Token no válido" }, 404
        elif (code == 4):
            return {'code' : 4 , 'message': "solicitud erronea" }, 400
        else:
            return {'code' : 5 , 'message': "Ha ocurrido un error, intente más tarde" }, 404


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
        conn = mysql.connector.connect(user=dbuser, password=dbpswd, host=dbhost, database=dbschema)
        
        cursor1 = conn.cursor()

        if (header[1] == "0"):

            epsw_sql = ("select acc_number from bnkz_accounts where acc_client = %s and acc_bid = %s and acc_number = %s")
            epsw_data = (userid, header[2], accnum)

            cursor1.execute(epsw_sql,epsw_data)
            result = cursor1.fetchall()

            if(len(result) == 0):
                valid = 1
            else:
                accver = (result[0][0])
                
                if (accver == accnum):
                    valid = 0
                    
                    epsw_sql = ("select hex_tok from bnkz_atokens where acc_num = %s")
                    cursor1.execute(epsw_sql,(accnum, ))
                    resultt = cursor1.fetchall()
                    if(len(resultt) == 0):
                        ntoken = None
                        while (ntoken is None):
                            ntoken = secrets.token_hex(16)
                            epsw_sql = ("select * from bnkz_atokens where hex_tok = %s")
                            cursor1.execute(epsw_sql,(ntoken, ))
                            result = cursor1.fetchall()
                            if(len(result) == 0):
                                epsw_sql = ("insert into bnkz_atokens (acc_num, hex_tok) values (%s, %s)")
                                epsw_sql_data = (accnum, ntoken)
                                cursor1.execute(epsw_sql,epsw_sql_data)
                                conn.commit()
                                gtoken = ntoken
                                break
                            else:
                                ntoken = None
                    else:
                        gtoken = resultt[0][0]
                else:
                    valid = 1
        
        else:
            print("Checking for card")
            epsw_sql = ("select card_num from bnkz_cards where card_own = %s and card_num = %s")
            epsw_data = (userid, accnum)

            cursor1.execute(epsw_sql,epsw_data)
            result = cursor1.fetchall()

            if(len(result) == 0):
                valid = 1
            else:
                accver = (result[0][0])
                
                if (accver == accnum):
                    valid = 0
                    
                    epsw_sql = ("select hex_tok from bnkz_ctokens where card_num = %s")
                    cursor1.execute(epsw_sql,(accnum, ))
                    resultt = cursor1.fetchall()
                    if(len(resultt) == 0):
                        ntoken = None
                        while (ntoken is None):
                            ntoken = secrets.token_hex(16)
                            epsw_sql = ("select * from bnkz_ctokens where hex_tok = %s")
                            cursor1.execute(epsw_sql,(ntoken, ))
                            result = cursor1.fetchall()
                            if(len(result) == 0):
                                epsw_sql = ("insert into bnkz_ctokens (card_num, hex_tok) values (%s, %s)")
                                epsw_sql_data = (accnum, ntoken)
                                cursor1.execute(epsw_sql,epsw_sql_data)
                                conn.commit()
                                gtoken = ntoken
                                break
                            else:
                                ntoken = None
                    else:
                        gtoken = resultt[0][0]
                else:
                    valid = 1
                   
    except mysql.connector.Error as err:
        valid = 1
        gtoken = err
    finally:
        cursor1.close()
        conn.close()
    
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
        conn = mysql.connector.connect(user=dbuser, password=dbpswd, host=dbhost, database=dbschema)
        
        cursor1 = conn.cursor()
        epsw_sql = ("select acc_num from bnkz_atokens where hex_tok = %s")

        if (header[1] == "1"):
            epsw_sql = ("select card_num from bnkz_ctokens where hex_tok = %s")

        cursor1.execute(epsw_sql,(tokenv,))
        result = cursor1.fetchall()
        if (len(result) == 0):
            return 3

        accpayer = result[0][0]

        outcode = transFunds(conn, (header[1], accpayer, sm_accs[int(header[0])], money))
                   
    except mysql.connector.Error as err:
        outcode = 5
    finally:
        cursor1.close()
        conn.close()
    
    return outcode

def transFunds(conn, args):
    exitc = 5

    try:
        cursor1 = conn.cursor()
        check_sql = ("select acc_funds from bnkz_accounts where acc_number = %s")
        
        if (args[0] == "1"):
            check_sql = ("select card_funds from bnkz_cards where card_num = %s")

        cursor1.execute(check_sql,(args[1],))
        results1 = cursor1.fetchall()

        check_sql = ("select acc_number from bnkz_accounts where acc_number = %s")
        cursor1.execute(check_sql,(args[2],))
        results2 = cursor1.fetchall()

        if(len(results1) == 0):
            exitc = 2
        elif(len(results2) == 0):
            exitc = 2
        else:
            #print(results[0][0])

            if (float(results1[0][0]) - float(args[3]) < 0):
                exitc = 1
            else:
                upd_sql = ("update bnkz_accounts set acc_funds = acc_funds - %s where acc_number = %s")
                if (args[0] == "1"):
                    upd_sql = ("update bnkz_cards set card_funds = card_funds - %s where card_num = %s")

                upd_sql_data = (args[3], args[1])
                cursor1.execute(upd_sql,upd_sql_data)
                conn.commit()

                upd_sql = ("update bnkz_accounts set acc_funds = acc_funds + %s where acc_number = %s")
                upd_sql_data = (args[3], args[2])
                cursor1.execute(upd_sql,upd_sql_data)
                conn.commit()

                exitc = 0
                
                # print("Transferido $" + args[2] + " desde cuenta" + args[0] + " a la cuenta " + args[1] + " exitosamente")
            
    except mysql.connector.Error as err:
        exitc = 3

    cursor1.close()
    return exitc

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)  # run our Flask app