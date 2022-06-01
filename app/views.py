import traceback
from flask import render_template, flash, redirect, jsonify, request
from app import app
import pymysql
import datetime, time
from checks import *

# TODO: check cursor.close db.close for each branch in each func
# TODO: last visit


@app.route("/", methods=["GET"])
def index():
    return redirect("/customer/list")


@app.route("/customer/list", methods=["GET"])
def customerList():
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from customer")
    dataList = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("customerList.html", dataList=dataList)


@app.route("/customer/search", methods=["GET", "POST"])
def customerSearch():
    if request.method == "GET":
        return render_template("customerSearch.html")
    elif request.method == "POST":
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "select * from customer where customerID like %s and customerName like %s and customerPhone like %s and customerAdress like %s"
        customerID = "%"
        customerName = "%"
        customerPhone = "%"
        customerAdress = "%"
        if request.form["customerID"]:
            customerID = "%" + request.form["customerID"] + "%"
        if request.form["customerName"]:
            customerName = "%" + request.form["customerName"] + "%"
        if request.form["customerPhone"]:
            customerPhone = "%" + request.form["customerPhone"] + "%"
        if request.form["customerAdress"]:
            customerAdress = "%" + request.form["customerAdress"] + "%"
        cursor.execute(sql, (customerID, customerName, customerPhone, customerAdress))
        datalist = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template("customerSearch.html", dataList=datalist)


@app.route("/customer/edit/<string:ID>", methods=["GET"])
def customerEdit(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from customer where customerID = '{0}'".format(ID))
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("customerEdit.html", customer=data)


@app.route("/api/customer/edit/<string:ID>", methods=["POST"])
def apiCustomerEdit(ID):
    error = customerCheck(request.form)
    if error != "":
        flash(error)
        return redirect("/customer/edit/" + ID)
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    sql = "update customer set customerName=%s , customerPhone=%s , customerAdress=%s , contactName=%s , contactPhone=%s , contactMail=%s , userContactRelation=%s where customerID=%s"
    cursor.execute(
        sql,
        (
            request.form["customerName"],
            request.form["customerPhone"],
            request.form["customerAdress"],
            request.form["contactName"],
            request.form["contactPhone"],
            request.form["contactMail"],
            request.form["userContactRelation"],
            ID,
        ),
    )
    db.commit()
    cursor.close()
    db.close()
    return redirect("/customer/list")


@app.route("/api/customer/add/", methods=["POST"])
def apiCustomerAdd():
    error = customerIDcheck(request.form["customerID"])
    if error != "":
        flash(error)
        return redirect("/customer/list")
    error = customerCheck(request.form)
    if error != "":
        flash(error)
        return redirect("/customer/list")
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "select * from customer where customerID=%s", (request.form["customerID"])
    )
    if cursor.fetchall():
        cursor.close()
        db.close()
        flash("ID already exists")
        return redirect("/customer/list")
    sql = "insert into customer (customerID,customerName,customerPhone,customerAdress,contactName,contactPhone,contactMail,userContactRelation) values (%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(
        sql,
        (
            request.form["customerID"],
            request.form["customerName"],
            request.form["customerPhone"],
            request.form["customerAdress"],
            request.form["contactName"],
            request.form["contactPhone"],
            request.form["contactMail"],
            request.form["userContactRelation"],
        ),
    )
    db.commit()
    cursor.close()
    db.close()
    return redirect("/customer/list")


@app.route("/account/list/<string:ID>", methods=["GET"])
def accountList(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "select customerCheck.accountID as accountID, customerCheck.bankName as bankName, lastVisit, accountBalance, accountRegisterDate, overdraft from customerCheck,checkAccount where customerID = %s and customerCheck.accountID = checkAccount.accountID",
        (ID),
    )
    checkData = cursor.fetchall()
    cursor.execute(
        "select customerDeposit.accountID as accountID , customerDeposit.bankName as bankName,lastVisit,accountBalance,accountRegisterDate,interestRate,currencyType from customerDeposit,depositaccount where customerID = %s and customerDeposit.accountID = depositaccount.accountID",
        (ID),
    )
    depositaData = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template(
        "accountList.html", checkList=checkData, depositaList=depositaData, ID=ID
    )


@app.route(
    "/api/account/addCustomer/<string:accountType>/<string:ID>", methods=["POST"]
)
def apiAccountAddCustomer(accountType, ID):
    if accountType == "check":
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select bankname from checkAccount where accountID=%s", (ID))
        bank = cursor.fetchall()[0]["bankname"]
        dt = datetime.datetime.now()
        date = dt.strftime("""%Y-%m-%d""")
        try:
            cursor.execute(
                "insert into customerCheck (customerID,bankName,accountID,lastVisit) values(%s,%s,%s,%s)",
                (request.form["newUser"], bank, ID, date),
            )
        except:
            traceback.print_exc()
            db.rollback()
            cursor.close()
            db.close()
            flash("error happened when insert")
            return redirect("/account/addCustomer/{0}/{1}".format(accountType, ID))
        else:
            db.commit()
            flash("successed")
            cursor.close()
            db.close()
            return redirect("/account/addCustomer/{0}/{1}".format(accountType, ID))

    elif accountType == "deposita":
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select bankname from depositAccount where accountID=%s", (ID))
        bank = cursor.fetchall()[0]["bankname"]
        dt = datetime.datetime.now()
        date = dt.strftime("""%Y-%m-%d""")
        try:
            cursor.execute(
                "insert into customerDeposit (customerID,bankName,accountID,lastVisit) values(%s,%s,%s,%s)",
                (request.form["newUser"], bank, ID, date),
            )
        except:
            traceback.print_exc()
            db.rollback()
            cursor.close()
            db.close()
            flash("error happened when insert")
            return redirect("/account/addCustomer/{0}/{1}".format(accountType, ID))
        else:
            db.commit()
            flash("successed")
            cursor.close()
            db.close()
            return redirect("/account/addCustomer/{0}/{1}".format(accountType, ID))

    else:
        flash("accountTypeError")
        return redirect("customer/list")


@app.route("/account/addCustomer/<string:accountType>/<string:ID>", methods=["GET"])
def accountAddCustomer(accountType, ID):
    if accountType == "check":
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "select customerCheck.customerID,customerName from customerCheck,customer where accountID=%s and customerCheck.customerID = customer.customerID",
            (ID),
        )
        accountUsers = cursor.fetchall()
        cursor.execute("select bankname from checkAccount where accountID=%s", (ID))
        bank = cursor.fetchall()[0]["bankname"]
        cursor.execute(
            "select customerID from customer where customerID not in (select customerID from customerCheck where bankName = %s)",
            (bank),
        )
        availableUser = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template(
            "accountAddCustomer.html",
            accountUsers=accountUsers,
            availableUser=availableUser,
            accountType=accountType,
            ID=ID,
        )

    elif accountType == "deposita":
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "select customerdeposit.customerID,customerName from customerdeposit,customer where accountID=%s and customerdeposit.customerID = customer.customerID",
            (ID),
        )
        accountUsers = cursor.fetchall()
        cursor.execute("select bankname from depositAccount where accountID=%s", (ID))
        bank = cursor.fetchall()[0]["bankname"]
        cursor.execute(
            "select customerID from customer where customerID not in (select customerID from customerdeposit where bankName = %s)",
            (bank),
        )
        availableUser = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template(
            "accountAddCustomer.html",
            accountUsers=accountUsers,
            availableUser=availableUser,
            accountType=accountType,
            ID=ID,
        )
    else:
        flash("accountTypeError check your url")
        return redirect("customer/list")


@app.route("/api/customer/createAccount/<string:ID>", methods=["POST"])
def apiCustomerCreateAccount(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    bankCheck = "select * from bank where bankName = %s"
    if request.form["type"] == "check":
        cursor.execute(bankCheck, (request.form["bank"]))
        if cursor.fetchall():
            if checkAccountCheck(request.form):
                try:
                    getRandID = """SELECT random_num
                                    FROM (
                                    SELECT FLOOR(RAND() * 999999) AS random_num 
                                    FROM checkAccount
                                    UNION
                                    SELECT FLOOR(RAND() * 999999) AS random_num
                                    ) AS ss
                                    WHERE "random_num" NOT IN (SELECT accountID FROM checkAccount)
                                    LIMIT 1"""
                    sql1 = "insert into checkAccount (accountID , bankName , accountBalance , accountRegisterDate , overdraft) values(%s,%s,%s,%s,%s)"
                    sql2 = "insert into customerCheck (customerID , bankName , accountID , lastVisit) values(%s,%s,%s,%s)"
                    cursor.execute(getRandID)
                    accountID = cursor.fetchall()[0]["random_num"]
                    dt = datetime.datetime.now()
                    date = dt.strftime("""%Y-%m-%d""")
                    cursor.execute(
                        sql1,
                        (
                            accountID,
                            request.form["bank"],
                            "0",
                            date,
                            request.form["overdraft"],
                        ),
                    )
                    cursor.execute(sql2, (ID, request.form["bank"], accountID, date))
                except:
                    db.rollback()
                    cursor.close()
                    db.close()
                    flash(
                        "this customer already has an check account in this bank, or other unknown error"
                    )
                    return redirect("/customer/createAccount/{0}".format(ID))
                else:
                    db.commit()
                    cursor.close()
                    db.close()
                    flash("success!")
                    # return redirect('/account/addCustomer/{0}'.format(ID))
                    return redirect("/customer/list")
            else:
                cursor.close()
                db.close()
                flash("overdraft rate must be a digit!")
                return redirect("/customer/createAccount/{0}".format(ID))
        else:
            traceback.print_exc()
            cursor.close()
            db.close()
            flash("no such bank!")
            return redirect("/customer/createAccount/{0}".format(ID))

    elif request.form["type"] == "deposita":
        cursor.execute(bankCheck, (request.form["bank"]))
        if cursor.fetchall():
            if depositaAccountCheck(request.form):
                try:
                    getRandID = """SELECT random_num
                                    FROM (
                                    SELECT FLOOR(RAND() * 999999) AS random_num 
                                    FROM depositAccount
                                    UNION
                                    SELECT FLOOR(RAND() * 999999) AS random_num
                                    ) AS ss
                                    WHERE "random_num" NOT IN (SELECT accountID FROM depositAccount)
                                    LIMIT 1"""
                    sql1 = "insert into depositAccount (accountID , bankName , accountBalance , accountRegisterDate , interestRate , currencyType) values(%s,%s,%s,%s,%s,%s)"
                    sql2 = "insert into customerDeposit (customerID , bankName , accountID , lastVisit) values(%s,%s,%s,%s)"
                    cursor.execute(getRandID)
                    accountID = cursor.fetchall()[0]["random_num"]
                    dt = datetime.datetime.now()
                    date = dt.strftime("""%Y-%m-%d""")
                    cursor.execute(
                        sql1,
                        (
                            accountID,
                            request.form["bank"],
                            "0",
                            date,
                            request.form["interestRate"],
                            request.form["currencyType"],
                        ),
                    )
                    cursor.execute(sql2, (ID, request.form["bank"], accountID, date))
                except:
                    traceback.print_exc()
                    db.rollback()
                    cursor.close()
                    db.close()
                    flash(
                        "this customer already has an check account in this bank, or other unknown error"
                    )
                    return redirect("/customer/createAccount/{0}".format(ID))
                else:
                    db.commit()
                    cursor.close()
                    db.close()
                    flash("success!")
                    # return redirect('/account/addCustomer/{0}'.format(ID))
                    return redirect("/customer/list")
            else:
                cursor.close()
                db.close()
                flash("interest rate must be a digit!")
                return redirect("/customer/createAccount/{0}".format(ID))
        else:
            cursor.close()
            db.close()
            flash("no such bank!")
            return redirect("/customer/createAccount/{0}".format(ID))
    else:
        cursor.close()
        db.close()
        flash("account type error!")
        return redirect("/customer/createAccount/{0}".format(ID))


@app.route("/customer/createAccount/<string:ID>", methods=["POST", "GET"])
def customerCreateAccount(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select bankName from bank")
    banks = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("createAccount.html", banks=banks, ID=ID)


@app.route("/customer/delete/<string:ID>", methods=["POST", "GET"])
def customerDelete(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from belongTo where customerID = %s", (ID))
    if cursor.fetchall():
        flash(u"该用户存在贷款，无法删除")
        cursor.close()
        db.close()
        return redirect("/customer/list")
    cursor.execute("select * from customerCheck where customerID = %s", (ID))
    if cursor.fetchall():
        flash(u"该用户存在支票账户，无法删除")
        cursor.close()
        db.close()
        return redirect("/customer/list")
    cursor.execute("select * from customerDeposit where customerID = %s", (ID))
    if cursor.fetchall():
        flash(u"该用户存在储蓄账户，无法删除")
        cursor.close()
        db.close()
        return redirect("/customer/list")
    try:
        cursor.execute("delete from server where customerID = %s", (ID))
        cursor.execute("delete from customer where customerID = %s", (ID))
    except:
        db.rollback()
        flash(u"未知原因删除失败")
        cursor.close()
        db.close()
        return redirect("/customer/list")
    else:
        db.commit()
    flash(u"删除成功")
    cursor.close()
    db.close()
    return redirect("/customer/list")


@app.route("/api/account/deleteCustomer", methods=["POST"])
def apiAccountDelete():
    json = request.get_json()
    type = json["type"]
    if type == "check":
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                "delete from customerCheck where accountID=%s and customerID=%s",
                (json["accountID"], json["customerID"]),
            )
        except:
            traceback.print_exc()
            db.rollback()
            flash("error at line 487")
            return {"code": 487}
        else:
            flash("成功")
            cursor.execute(
                "select * from customerCheck where accountID=%s", (json["accountID"])
            )
            if cursor.fetchall():
                db.commit()
                cursor.close()
                db.close()
                return {"code": 200}
            else:
                cursor.execute(
                    "delete from checkAccount where accountID=%s", (json["accountID"])
                )
                db.commit()
                cursor.close()
                db.close()
                return {"code": 201}

    elif type == "deposita":
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                "delete from customerDeposit where accountID=%s and customerID=%s",
                (json["accountID"], json["customerID"]),
            )
        except:
            traceback.print_exc()
            db.rollback()
            flash("error at line 487")
            return {"code": 487}
        else:
            flash("成功")
            cursor.execute(
                "select * from customerDeposit where accountID=%s", (json["accountID"])
            )
            if cursor.fetchall():
                db.commit()
                cursor.close()
                db.close()
                return {"code": 200}
            else:
                cursor.execute(
                    "delete from depositAccount where accountID=%s", (json["accountID"])
                )
                db.commit()
                cursor.close()
                db.close()
                return {"code": 201}
    else:
        return {"code": 545}


@app.route("/account/edit/check/<string:ID>", methods=["GET"])
def accountEditCheck(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from checkAccount where accountID=%s", (ID))
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("accountEditCheck.html", data=data[0])


@app.route("/account/edit/deposita/<string:ID>", methods=["GET"])
def accountEditDeposita(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from depositAccount where accountID=%s", (ID))
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("accountEditDeposita.html", data=data[0])


@app.route("/api/account/edit/check/<string:ID>", methods=["POST"])
def apiAccountEditCheck(ID):
    if checkAccountEditCheck(request.form):
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        dt = datetime.datetime.now()
        date = dt.strftime("""%Y-%m-%d""")
        try:
            cursor.execute(
                "update checkAccount set accountBalance=%s,overdraft=%s where accountID=%s",
                (request.form["accountBalance"], request.form["overdraft"], ID),
            )
            cursor.execute(
                "update customerCheck set lastVisit=%s where accountID=%s", (date, ID)
            )
        except:
            traceback.print_exc()
            db.rollback()
            cursor.close()
            db.close()
            flash("error 590")
            return redirect("/account/edit/check/{0}".format(ID))
        else:
            flash("成功")
            db.commit()
            cursor.close()
            db.close()
            return redirect("/account/edit/check/{0}".format(ID))
    else:
        flash("error 598")
        return redirect("/account/edit/check/{0}".format(ID))


@app.route("/api/account/edit/deposita/<string:ID>", methods=["POST"])
def apiAccountEditDeposita(ID):
    if depositaAccountEditCheck(request.form):
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        dt = datetime.datetime.now()
        date = dt.strftime("""%Y-%m-%d""")
        try:
            cursor.execute(
                "update depositAccount set accountBalance=%s,interestRate=%s,currencyType=%s where accountID=%s",
                (
                    request.form["accountBalance"],
                    request.form["interestRate"],
                    request.form["currencyType"],
                    ID,
                ),
            )
            cursor.execute(
                "update customerDeposit set lastVisit=%s where accountID=%s", (date, ID)
            )
        except:
            traceback.print_exc()
            db.rollback()
            cursor.close()
            db.close()
            flash("error 634")
            return redirect("/account/edit/deposita/{0}".format(ID))
        else:
            flash("成功")
            db.commit()
            cursor.close()
            db.close()
            return redirect("/account/edit/deposita/{0}".format(ID))
    else:
        flash("error 641")
        return redirect("/account/edit/deposita/{0}".format(ID))


@app.route("/account/search", methods=["GET", "POST"])
def accountSearch():
    if request.method == "GET":
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select * from checkAccount")
        check = cursor.fetchall()
        cursor.execute("select * from depositAccount")
        deposita = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template(
            "accountSearch.html", checkList=check, depositaList=deposita
        )
    elif request.method == "POST":
        db = pymysql.connect(
            host="localhost", user="root", password="114514", database="banksys"
        )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        if request.form["type"] == "check":
            cursor.execute(
                "select * from checkAccount where accountID=%s",
                (request.form["accountID"]),
            )
            check = cursor.fetchall()
            deposita = []
            cursor.close()
            db.close()
            return render_template(
                "accountSearch.html", checkList=check, depositaList=deposita
            )
        elif request.form["type"] == "deposita":
            cursor.execute(
                "select * from depositAccount where accountID=%s",
                (request.form["accountID"]),
            )
            deposita = cursor.fetchall()
            check = []
            cursor.close()
            db.close()
            return render_template(
                "accountSearch.html", checkList=check, depositaList=deposita
            )
        else:
            flash("error 694")
            return redirect("/account/search")


@app.route("/loan/list", methods=["GET"])
def loadList():
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select loanID,sum(payMoney) as payed from pay group by loanID")
    status = cursor.fetchall()
    cursor.execute("select * from loan")
    loan = cursor.fetchall()
    cursor.execute("select bankName from bank")
    banks = cursor.fetchall()
    cursor.execute("select customerID from customer")
    customerList = cursor.fetchall()
    cursor.close()
    db.close()
    loanStatus = {}
    for l in loan:
        loanStatus[l["loanID"]] = {
            "loanID": l["loanID"],
            "bankName": l["bankName"],
            "loanMoney": l["loanMoney"],
            "status": "not issued",
            "payed": 0,
        }
    for s in status:
        loanStatus[s["loanID"]]["payed"] = s["payed"]
        if s["payed"] == loanStatus[s["loanID"]]["loanMoney"]:
            loanStatus[s["loanID"]]["status"] = "finished"
        else:
            loanStatus[s["loanID"]]["status"] = "issuing"

    return render_template(
        "loanList.html",
        loans=list(loanStatus.values()),
        banks=banks,
        customerList=customerList,
    )


@app.route("/api/loan/add/", methods=["POST"])
def apiLoanAdd():
    try:
        number = float(request.form["loanMoney"])
        if number < 0:
            flash("金额错误")
            return redirect("/loan/list")
    except ValueError:
        flash("金额错误")
        return redirect("/loan/list")

    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cusID = request.form["customerID"]
    cursor.execute("select customerID from customer where customerID=%s", (cusID))
    if cursor.fetchall():
        try:
            getRandID = """SELECT random_num
                                        FROM (
                                        SELECT FLOOR(RAND() * 999999) AS random_num 
                                        FROM loan
                                        UNION
                                        SELECT FLOOR(RAND() * 999999) AS random_num
                                        ) AS ss
                                        WHERE "random_num" NOT IN (SELECT loanID FROM loan)
                                        LIMIT 1"""
            cursor.execute(getRandID)
            newID = cursor.fetchall()[0]["random_num"]
            cursor.execute(
                "insert into loan (loanID,bankName,loanMoney) values (%s,%s,%s)",
                (newID, request.form["bank"], request.form["loanMoney"]),
            )
            cursor.execute(
                "insert into belongto (customerID,loanID) values (%s,%s)",
                (cusID, newID),
            )
        except:
            traceback.print_exc()
            db.rollback()
            cursor.close()
            db.close()
            flash("error 772")
            return redirect("/loan/list")
        else:
            db.commit()
            cursor.close()
            db.close()
            flash("success")
            return redirect("/loan/list")
    else:
        cursor.close()
        db.close()
        flash("customer ID not exists")
        return redirect("/loan/list")


@app.route("/loan/<string:ID>", methods=["GET"])
def loanDetail(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from loan where loanID = %s", (ID))
    loan = cursor.fetchall()
    if loan:
        loan = loan[0]
        cursor.execute("select * from pay where loanID=%s", (ID))
        pays = cursor.fetchall()
        cursor.execute("select sum(payMoney) as payed from pay where loanID=%s", (ID))
        payed = cursor.fetchall()[0]["payed"]
        status = "not issued"
        if payed:
            status = "issuing"
            if payed == loan["loanMoney"]:
                status = "finished"
        else:
            payed = "0"
        cursor.execute(
            "select belongto.customerID,customerName from belongto,customer where loanID=%s and belongto.customerID=customer.customerID",
            (ID),
        )
        cus = cursor.fetchall()
        cursor.execute(
            "select customerID,customerName from customer where customerID not in(select customerID from belongto where loanID=%s)",
            (ID),
        )
        availableCus = cursor.fetchall()
        cursor.close()
        db.close()
        left = float(loan["loanMoney"]) - float(payed)
        return render_template(
            "loanDetail.html",
            loan=loan,
            status=status,
            pays=pays,
            payed=payed,
            left=left,
            customerList=cus,
            availableCus=availableCus,
        )
    else:
        flash("loan ID does not exist")
        cursor.close()
        db.close()
        return redirect("/loan/list")


@app.route("/loan/delete/<string:ID>", methods=["GET", "POST"])
def loanDelete(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from loan where loanID = %s", (ID))
    loan = cursor.fetchall()
    if loan:
        loan = loan[0]
        cursor.execute("select sum(payMoney) as payed from pay where loanID=%s", (ID))
        payed = cursor.fetchall()[0]["payed"]
        status = "not issued"
        if payed:
            status = "issuing"
            if payed == loan["loanMoney"]:
                status = "finished"
        if status == "issuing":
            cursor.close()
            db.close()
            flash("this loan is issuing, can not be deleted")
            return redirect("/loan/{0}".format(ID))
        else:
            try:
                cursor.execute("delete from pay where loanID=%s", (ID))
                cursor.execute("delete from belongto where loanID=%s", (ID))
                cursor.execute("delete from loan where loanID=%s", (ID))
            except:
                db.rollback()
                flash("error 846")
                cursor.close()
                db.close()
                return redirect("/loan/list")
            else:
                db.commit()
                cursor.close()
                db.close()
                flash("success")
                return redirect("/loan/list")

    else:
        flash("loan ID does not exist")
        cursor.close()
        db.close()
        return redirect("/loan/list")


@app.route("/api/loan/search", methods=["POST"])
def apiLoanSearch():
    ID = request.form["loanID"]
    if ID:
        return redirect("/loan/{0}".format(ID))
    else:
        flash("ID can be NULL")
        return redirect("/loan/list")


@app.route("/api/loan/createpay/<string:ID>", methods=["POST"])
def apiLoanCreatePay(ID):
    newPay = request.form["payMoney"]
    try:
        newPayNum = float(newPay)
        if newPayNum <= 0:
            flash("金额必须大于0")
            return redirect("/loan/{0}".format(ID))
    except:
        flash("金额必须是数字")
        return redirect("/loan/{0}".format(ID))
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from loan where loanID = %s", (ID))
    loan = cursor.fetchall()
    if loan:
        loan = loan[0]
        cursor.execute("select sum(payMoney) as payed from pay where loanID=%s", (ID))
        payed = cursor.fetchall()[0]["payed"]
        if payed:
            payedNum = float(payed)
        else:
            payedNum = 0.0
        allNum = float(loan["loanMoney"])
        if payedNum + newPayNum > allNum:
            flash("金额溢出")
            return redirect("/loan/{0}".format(ID))
        getRandID = """SELECT random_num
                                    FROM (
                                    SELECT FLOOR(RAND() * 999999) AS random_num 
                                    FROM pay
                                    UNION
                                    SELECT FLOOR(RAND() * 999999) AS random_num
                                    ) AS ss
                                    WHERE "random_num" NOT IN (SELECT payID FROM pay)
                                    LIMIT 1"""
        cursor.execute(getRandID)
        newID = cursor.fetchall()[0]["random_num"]
        dt = datetime.datetime.now()
        date = dt.strftime("""%Y-%m-%d""")
        try:
            cursor.execute(
                "insert into pay (loanID,payID,payDate,payMoney) values(%s,%s,%s,%s)",
                (ID, newID, date, newPay),
            )
        except:
            traceback.print_exc()
            db.rollback()
            cursor.close()
            db.close()
            flash("error 921")
            return redirect("/loan/{0}".format(ID))
        else:
            db.commit()
            cursor.close()
            db.close()
            flash("success")
            return redirect("/loan/{0}".format(ID))
    else:
        flash("no such loan id")
        return redirect("/loan/list")


@app.route("/api/loan/addCustomer/<string:ID>", methods=["POST"])
def loanAddCustomer(ID):
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from loan where loanID=%s", (ID))
    loan = cursor.fetchall()
    if not loan:
        flash("loan id not exist")
        return redirect("/loan/list")
    loan = loan[0]
    cursor.execute("select sum(payMoney) as payed from pay where loanID=%s", (ID))
    payed = cursor.fetchall()[0]["payed"]
    status = "not issued"
    if payed:
        status = "issuing"
        if payed == loan["loanMoney"]:
            status = "finished"
    if status == "issuing" or status == "finished":
        cursor.close()
        db.close()
        flash("this loan is issuing or finished, can not be edited")
        return redirect("/loan/{0}".format(ID))
    try:
        cursor.execute(
            "insert into belongto (customerID,loanID) values (%s,%s)",
            (request.form["newUser"], ID),
        )
    except:
        db.rollback()
        flash(
            "error 1005: maybe this loan had already connected to this customer, or customer not exits"
        )
    else:
        db.commit()
        flash("success")
    cursor.close()
    db.close()
    return redirect("/loan/{0}".format(ID))


@app.route("/api/loan/deleteCustomer/", methods=["POST"])
def apiLoanDeleteCustomer():
    json = request.get_json()
    ID = json["ID"]
    cus = json["cus"]
    db = pymysql.connect(
        host="localhost", user="root", password="114514", database="banksys"
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from loan where loanID=%s", (ID))
    loan = cursor.fetchall()
    if not loan:
        flash("loan id not exist")
        return {"code": 1028}
    loan = loan[0]
    cursor.execute("select sum(payMoney) as payed from pay where loanID=%s", (ID))
    payed = cursor.fetchall()[0]["payed"]
    status = "not issued"
    if payed:
        status = "issuing"
        if payed == loan["loanMoney"]:
            status = "finished"
    if status == "issuing" or status == "finished":
        cursor.close()
        db.close()
        flash("this loan is issuing or finished, can not be edited")
        return {"code": 1041}
    try:
        cursor.execute(
            "delete from belongto where loanID=%s and customerID=%s", (ID, cus)
        )
        cursor.execute("select * from belongto where loanID=%s", (ID))
        if not cursor.fetchall():
            cursor.execute("delete from loan where loanID=%s", (ID))
    except:
        traceback.print_exc()
        flash("error 1047")
        db.rollback()
    else:
        flash("success")
        db.commit()
    cursor.close()
    db.close()
    return {"code": 1057}

