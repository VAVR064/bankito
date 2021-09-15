import mysql.connector
import re

#Required for de/encryption 
the_key = '0123456789'

dbuser = 'admin'
#dbuser = 'root'
dbpswd = 'sakapuku123!'
dbhost = 'db-interbanks.c3ebzwhrotdf.us-east-2.rds.amazonaws.com'
#dbhost = 'localhost'
dbschema = 'bank_zeus'

def main():

    try:
        cnx = mysql.connector.connect(user=dbuser, password=dbpswd, host=dbhost, database=dbschema)

        commands(cnx)

        cnx.close()
        
        #cursor = cnx.cursor()

        #insert_sql = ("INSERT INTO bnkz_clients (client_id, client_name, client_phone, client_addr, client_pswd) VALUES (%s, %s, %s, %s, aes_encrypt(%s,%s))")
        #insert_data = ('0987654321', 'Daniela', '0980000003', 'Av. Panamerica, Cuenca, N3-53', 'Dannyyy10_@', the_key)

        #cursor.execute(insert_sql, insert_data)
        #cnx.commit()

        #cursor.close()


    except mysql.connector.Error as err:
        print(err)

    cnx.close()


def commands(conn):
    while(True):
        command = input("Enter command: ")
        cmd_syntax = command.split(" ")

        if(len(cmd_syntax) == 0):
            continue
        else:
            inst = cmd_syntax[0]
            if (inst == "cuser"):
                createUser(conn, cmd_syntax[1:])
            elif (inst == "cacc"):
                createAcc(conn, cmd_syntax[1:])
            elif (inst == "ccard"):
                createCard(conn, cmd_syntax[1:])
            elif (inst == "wacc"):
                showAcc(conn, cmd_syntax[1:])
            elif (inst == "wcard"):
                showCard(conn, cmd_syntax[1:])
            elif (inst == "adda"):
                addFunds(conn, cmd_syntax[1:])
            elif (inst == "rma"):
                rmFunds(conn, cmd_syntax[1:])
            elif (inst == "addc"):
                addQuota(conn, cmd_syntax[1:])
            elif (inst == "rmc"):
                rmQuota(conn, cmd_syntax[1:])
            elif (inst == "trans"):
                transFunds(conn, cmd_syntax[1:])
            elif (inst == "list"):
                showCmd()
            elif (inst == "exit"):
                break
            else:
                print("Invalid command")

def showCmd():
    print("cuser <id> <nombre> <celular> <direccion sin espacios> <contraseña>")
    print("cacc <no cuenta> <id cliente> <tipo cuenta> <fondos> <id banco>")
    print("ccard <no tarjeta> <id cliente> <pin> <fondos>")
    print("wacc -all | <no cuenta>")
    print("wcard -all | <no tarjeta>")
    print("adda <no cuenta> <fondos>")
    print("rma <no cuenta> <fondos>")
    print("addc <no tarjeta> <fondos>")
    print("rmc <no tarjeta> <fondos>")
    print("trans <no cuenta envio> <no cuenta recibo> <fondos>")
    print("list")
    print("exit")

def showAcc(conn, args):
    if (len(args) != 1):
        print("Invalid number of arguments")
    else:
        if(args[0] == "-all"):
            try:
                cursor1 = conn.cursor()
                check_sql = ("select acc_number, acc_client, acc_funds, acc_bid from bnkz_accounts")
                cursor1.execute(check_sql)
                results = cursor1.fetchall()

                if(len(results) == 0):
                    print("No existen cuentas en la base")
                else:
                    print("No cuenta | ID cliente | Fondos | ID Banco")
                    for rowr in results:
                        print( str(rowr[0]) + " | " + str(rowr[1]) + " | " + str(rowr[2]) + " | " +  str(rowr[3]))

            except mysql.connector.Error as err:
                print(err)

            cursor1.close()

        else:
            try:
                acc_match = bool(re.match("^\d{10}$",args[0]))

                if (not acc_match):
                    print("Invalid arguments")
                    return

                cursor1 = conn.cursor()
                check_sql = ("select acc_number, acc_client, acc_funds, acc_bid from bnkz_accounts where acc_number = %s")
                cursor1.execute(check_sql,(args[0],))
                results = cursor1.fetchall()

                if(len(results) == 0):
                    print("Cuenta " + args[0] + " no existe")
                else:
                    print("No cuenta | ID cliente | Fondos | ID Banco")
                    rowr = results[0]
                    print( str(rowr[0]) + " | " + str(rowr[1]) + " | " + str(rowr[2]) + " | " +  str(rowr[3]))
                
            except mysql.connector.Error as err:
                print(err)

            cursor1.close()

def showCard(conn, args):
    if (len(args) != 1):
        print("Invalid number of arguments")
    else:
        if(args[0] == "-all"):
            try:
                cursor1 = conn.cursor()
                check_sql = ("select card_num, card_own, card_funds from bnkz_cards")
                cursor1.execute(check_sql)
                results = cursor1.fetchall()

                if(len(results) == 0):
                    print("No existen tarjetas en la base")
                else:
                    print("No tarjeta | ID cliente | Cupo")
                    for rowr in results:
                        print( str(rowr[0]) + " | " + str(rowr[1]) + " | " + str(rowr[2]))

            except mysql.connector.Error as err:
                print(err)

            cursor1.close()

        else:
            try:
                acc_match = bool(re.match("^\d{16}$",args[0]))

                if (not acc_match):
                    print("Invalid arguments")
                    return
                
                cursor1 = conn.cursor()
                check_sql = ("select card_num, card_own, card_funds from bnkz_cards where card_num = %s")
                cursor1.execute(check_sql,(args[0],))
                results = cursor1.fetchall()

                if(len(results) == 0):
                    print("Tarjeta " + args[0] + " no existe")
                else:
                    print("No tarjeta | ID cliente | Cupo")
                    rowr = results[0]
                    print(str(rowr[0]) + " | " + str(rowr[1]) + " | " + str(rowr[2]))


            except mysql.connector.Error as err:
                print(err)

            cursor1.close()

def addFunds(conn, args):
    if (len(args) != 2):
        print("Invalid number of arguments")
    else:
        try:
            acc_match = bool(re.match("^\d{10}$",args[0]))
            fun_match = bool(re.match("^\d{1,13}\.\d{2}$",args[1]))

            if (not acc_match or not fun_match):
                print("Invalid arguments")
                return

            cursor1 = conn.cursor()
            check_sql = ("select acc_number from bnkz_accounts where acc_number = %s")
            cursor1.execute(check_sql,(args[0],))

            results = cursor1.fetchall()

            if(len(results) == 0):
                print("Cuenta " + args[0] + " no existe")
            else:
                upd_sql = ("update bnkz_accounts set acc_funds = acc_funds + %s where acc_number = %s")
                upd_sql_data = (args[1], args[0])
                cursor1.execute(upd_sql,upd_sql_data)
                conn.commit()

                print("Añadido " + args[1] + " a la cuenta " + args[0] + " exitosamente")
                
        except mysql.connector.Error as err:
            print(err)

        cursor1.close()

def addQuota(conn, args):
    if (len(args) != 2):
        print("Invalid number of arguments")
    else:
        try:
            acc_match = bool(re.match("^\d{16}$",args[0]))
            fun_match = bool(re.match("^\d{1,13}\.\d{2}$",args[1]))

            if (not acc_match or not fun_match):
                print("Invalid arguments")
                return

            cursor1 = conn.cursor()
            check_sql = ("select card_num from bnkz_cards where card_num = %s")
            cursor1.execute(check_sql,(args[0],))

            results = cursor1.fetchall()

            if(len(results) == 0):
                print("Tarjeta " + args[0] + " no existe")
            else:
                upd_sql = ("update bnkz_cards set card_funds = card_funds + %s where card_num = %s")
                upd_sql_data = (args[1], args[0])
                cursor1.execute(upd_sql,upd_sql_data)
                conn.commit()

                print("Añadido " + args[1] + " a la tarjeta " + args[0] + " exitosamente")
                
        except mysql.connector.Error as err:
            print(err)

        cursor1.close()

def rmFunds(conn, args):
    if (len(args) != 2):
        print("Invalid number of arguments")
    else:
        try:
            acc_match = bool(re.match("^\d{10}$",args[0]))
            fun_match = bool(re.match("^\d{1,13}\.\d{2}$",args[1]))

            if (not acc_match or not fun_match):
                print("Invalid arguments")
                return

            cursor1 = conn.cursor()
            check_sql = ("select acc_funds from bnkz_accounts where acc_number = %s")
            cursor1.execute(check_sql,(args[0],))

            results = cursor1.fetchall()

            if(len(results) == 0):
                print("Cuenta " + args[0] + " no existe")
            else:
                #print(results[0][0])

                if (float(results[0][0]) - float(args[1]) < 0):
                    print("No hay suficientes fondos")
                else:
                    upd_sql = ("update bnkz_accounts set acc_funds = acc_funds - %s where acc_number = %s")
                    upd_sql_data = (args[1], args[0])
                    cursor1.execute(upd_sql,upd_sql_data)
                    conn.commit()
                    
                    print("Removido " + args[1] + " de la cuenta " + args[0] + " exitosamente")
                
        except mysql.connector.Error as err:
            print(err)

        cursor1.close()

def rmQuota(conn, args):
    if (len(args) != 2):
        print("Invalid number of arguments")
    else:
        try:
            acc_match = bool(re.match("^\d{16}$",args[0]))
            fun_match = bool(re.match("^\d{1,13}\.\d{2}$",args[1]))

            if (not acc_match or not fun_match):
                print("Invalid arguments")
                return

            cursor1 = conn.cursor()
            check_sql = ("select card_funds from bnkz_cards where card_num = %s")
            cursor1.execute(check_sql,(args[0],))

            results = cursor1.fetchall()

            if(len(results) == 0):
                print("Tarjeta " + args[0] + " no existe")
            else:
                #print(results[0][0])

                if (float(results[0][0]) - float(args[1]) < 0):
                    print("No hay suficiente cupo")
                else:
                    upd_sql = ("update bnkz_cards set card_funds = card_funds - %s where card_num = %s")
                    upd_sql_data = (args[1], args[0])
                    cursor1.execute(upd_sql,upd_sql_data)
                    conn.commit()
                    
                    print("Removido " + args[1] + " de la tarjeta " + args[0] + " exitosamente")
                
        except mysql.connector.Error as err:
            print(err)

        cursor1.close()

def transFunds(conn, args):
    if (len(args) != 3):
        print("Invalid number of arguments")
    else:
        try:
            sacc_match = bool(re.match("^\d{10}$",args[0]))
            racc_match = bool(re.match("^\d{10}$",args[1]))
            fun_match = bool(re.match("^\d{1,13}\.\d{2}$",args[2]))

            if (not sacc_match or not racc_match or not fun_match):
                print("Invalid arguments")
                return

            cursor1 = conn.cursor()
            check_sql = ("select acc_funds from bnkz_accounts where acc_number = %s")
            cursor1.execute(check_sql,(args[0],))
            results1 = cursor1.fetchall()

            check_sql = ("select acc_number from bnkz_accounts where acc_number = %s")
            cursor1.execute(check_sql,(args[1],))
            results2 = cursor1.fetchall()

            if(len(results1) == 0):
                print("Cuenta " + args[0] + " no existe")
            elif(len(results2) == 0):
                print("Cuenta " + args[1] + " no existe")
            else:
                #print(results[0][0])

                if (float(results1[0][0]) - float(args[2]) < 0):
                    print("No hay suficientes fondos")
                else:
                    upd_sql = ("update bnkz_accounts set acc_funds = acc_funds - %s where acc_number = %s")
                    upd_sql_data = (args[2], args[0])
                    cursor1.execute(upd_sql,upd_sql_data)
                    conn.commit()

                    upd_sql = ("update bnkz_accounts set acc_funds = acc_funds + %s where acc_number = %s")
                    upd_sql_data = (args[2], args[1])
                    cursor1.execute(upd_sql,upd_sql_data)
                    conn.commit()
                    
                    print("Transferido $" + args[2] + " desde cuenta" + args[0] + " a la cuenta " + args[1] + " exitosamente")
                
        except mysql.connector.Error as err:
            print(err)

        cursor1.close()

def createUser(conn, args):
    if (len(args) != 5):
        print("Invalid number of arguments")
    else:
        try:
            id_match = bool(re.match("^\d{10}$",args[0]))
            tel_match = bool(re.match("^09\d{8}$", args[2]))

            if (not id_match or not tel_match):
                print("Invalid arguments")
                return

            cursor = conn.cursor()

            insert_sql = ("INSERT INTO bnkz_clients (client_id, client_name, client_phone, client_addr, client_pswd) VALUES (%s, %s, %s, %s, aes_encrypt(%s,%s))")
            insert_data = (args[0], args[1], args[2], args[3], args[4], the_key)

            cursor.execute(insert_sql, insert_data)
            conn.commit()

            print("Usuario creado exitosamente")
                
        except mysql.connector.Error as err:
            print(err)

        cursor.close()

def createAcc(conn, args):
    if (len(args) != 5):
        print("Invalid number of arguments")
    else:
        try:
            acc_match = bool(re.match("^\d{10}$",args[0]))
            usr_match = bool(re.match("^\d{10}$",args[1]))
            type_match = bool(re.match("^[0|1]{1}$",args[2]))
            fun_match = bool(re.match("^\d{1,13}\.\d{2}$",args[3]))
            bid_match = bool(re.match("^\d{1}$",args[4]))

            if (not acc_match or not usr_match or not type_match or not fun_match or not bid_match):
                print("Invalid arguments")
                return

            cursor = conn.cursor()

            insert_sql = ("INSERT INTO bnkz_accounts (acc_number, acc_client, acc_type, acc_funds, acc_bid) VALUES (%s, %s, %s, %s, %s)")
            insert_data = (args[0], args[1], args[2], args[3], args[4])

            cursor.execute(insert_sql, insert_data)
            conn.commit()

            print("Cuenta creada exitosamente")
                
        except mysql.connector.Error as err:
            print(err)

        cursor.close()

def createCard(conn, args):
    if (len(args) != 4):
        print("Invalid number of arguments")
    else:
        try:
            acc_match = bool(re.match("^\d{16}$",args[0]))
            usr_match = bool(re.match("^\d{10}$",args[1]))
            pin_match = bool(re.match("^\d{4}$",args[2]))
            fun_match = bool(re.match("^\d{1,13}\.\d{2}$",args[3]))

            if (not acc_match or not usr_match or not pin_match or not fun_match):
                print("Invalid arguments")
                return

            cursor = conn.cursor()

            insert_sql = ("INSERT INTO bnkz_cards (card_num, card_own, card_pin, card_funds) VALUES (%s, %s, %s, %s)")
            insert_data = (args[0], args[1], args[2], args[3])

            cursor.execute(insert_sql, insert_data)
            conn.commit()

            print("Tarjeta creada exitosamente")
                
        except mysql.connector.Error as err:
            print(err)

        cursor.close()

if __name__ == "__main__":
    main()