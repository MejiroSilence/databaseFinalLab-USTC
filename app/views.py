import json
import traceback
from flask import render_template, flash, redirect,jsonify,request
from matplotlib import dviread
from app import app
import pymysql
import datetime ,time
from checks import *

@app.route('/customer/list', methods = ['GET'])
def customerList():
    db = pymysql.connect(host='localhost',user='root',password='114514',database='banksys')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from customer")
    dataList=cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('customerList.html',dataList=dataList)

@app.route('/customer/search',methods=["GET"])
def customerSearch():
    return render_template('customerSearch.html')

@app.route('/api/customer/search',methods=["POST"])#TODO:
def apiCustomerSearch():
    return 114

@app.route("/customer/edit/<string:ID>", methods=["GET"])
def customerEdit(ID):
    if request.method == "GET":
        db = pymysql.connect(host='localhost',user='root',password='114514',database='banksys')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select * from customer where customerID = '{0}'".format(ID))
        data=cursor.fetchall()
        cursor.close()
        db.close()
        return render_template('customerEdit.html',customer=data)

@app.route("/api/customer/edit/<string:ID>",methods=["POST"])
def apiCustomerEdit(ID):
    error=customerCheck(request.form)
    if error!='':
        flash(error)
        return redirect('/customer/edit/'+ID)
    db = pymysql.connect(host='localhost',user='root',password='114514',database='banksys')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    sql='update customer set customerName=%s , customerPhone=%s , customerAdress=%s , contactName=%s , contactPhone=%s , contactMail=%s , userContactRelation=%s where customerID=%s'
    cursor.execute(sql,(request.form['customerName'],request.form['customerPhone'],request.form['customerAdress'],request.form['contactName'],request.form['contactPhone'],request.form['contactMail'],request.form['userContactRelation'],ID))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/customer/list')

@app.route('/api/customer/add/',methods=["POST"])
def apiCustomerAdd():
    error=customerIDcheck(request.form['customerID'])
    if error!='':
        flash(error)
        return redirect('/customer/list')
    error=customerCheck(request.form)
    if error!='':
        flash(error)
        return redirect('/customer/list')    
    db = pymysql.connect(host='localhost',user='root',password='114514',database='banksys')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('select * from customer where customerID=%s',(request.form['customerID']))
    if cursor.fetchall():
        cursor.close()
        db.close()
        flash('ID already exists')
        return redirect('/customer/list')
    sql='insert into customer (customerID,customerName,customerPhone,customerAdress,contactName,contactPhone,contactMail,userContactRelation) values (%s,%s,%s,%s,%s,%s,%s,%s)'
    cursor.execute(sql,(request.form['customerID'],request.form['customerName'],request.form['customerPhone'],request.form['customerAdress'],request.form['contactName'],request.form['contactPhone'],request.form['contactMail'],request.form['userContactRelation']))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/customer/list')

@app.route("/account/addCustomer/<string:ID>",methods=["GET"])
def accountAddCustomer(ID):#TODO:
    return 114514

@app.route("/api/customer/createAccount/<string:ID>",methods=["POST"])#TODO: redirect add cus
def apiCustomerCreateAccount(ID):
    db = pymysql.connect(host='localhost',user='root',password='114514',database='banksys')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    bankCheck='select * from bank where bankName = %s'
    if request.form['type']=='check':
        cursor.execute(bankCheck,(request.form['bank']))
        if cursor.fetchall():
            if(checkAccountCheck(request.form)):
                try:
                    getRandID="""SELECT random_num
                                    FROM (
                                    SELECT FLOOR(RAND() * 999999) AS random_num 
                                    FROM checkAccount
                                    UNION
                                    SELECT FLOOR(RAND() * 999999) AS random_num
                                    ) AS ss
                                    WHERE "random_num" NOT IN (SELECT accountID FROM checkAccount)
                                    LIMIT 1"""
                    sql1='insert into checkAccount (accountID , bankName , accountBalance , accountRegisterDate , overdraft) values(%s,%s,%s,%s,%s)'
                    sql2='insert into customerCheck (customerID , bankName , accountID , lastVisit) values(%s,%s,%s,%s)'
                    cursor.execute(getRandID)
                    accountID=str(cursor.fetchall()[0]['random_num'])
                    dt=datetime.datetime.now()
                    date=dt.strftime("""%Y-%m-%d""")
                    cursor.execute(sql1,(accountID,request.form['bank'],'0',date,request.form['overdraft']))
                    cursor.execute(sql2,(ID,request.form['bank'],accountID,date))
                except:
                    db.rollback()
                    cursor.close()
                    db.close()
                    flash('this customer already has an check account in this bank, or other unknown error')
                    return redirect('/customer/createAccount/{0}'.format(ID))
                else:
                    db.commit()
                    cursor.close()
                    db.close()
                    flash('success!')
                    #return redirect('/account/addCustomer/{0}'.format(ID))
                    return redirect('/customer/list')
            else:
                cursor.close()
                db.close()
                flash('overdraft rate must be a digit!')
                return redirect('/customer/createAccount/{0}'.format(ID))
        else:
            traceback.print_exc()
            cursor.close()
            db.close()
            flash('no such bank!')
            return redirect('/customer/createAccount/{0}'.format(ID))
    elif request.form['type']=='deposita':
        cursor.execute(bankCheck,(request.form['bank']))
        if cursor.fetchall():
            if(depositaAccountCheck(request.form)):
                try:
                    getRandID="""SELECT random_num
                                    FROM (
                                    SELECT FLOOR(RAND() * 999999) AS random_num 
                                    FROM depositAccount
                                    UNION
                                    SELECT FLOOR(RAND() * 999999) AS random_num
                                    ) AS ss
                                    WHERE "random_num" NOT IN (SELECT accountID FROM depositAccount)
                                    LIMIT 1"""
                    sql1='insert into depositAccount (accountID , bankName , accountBalance , accountRegisterDate , interestRate , currencyType) values(%s,%s,%s,%s,%s,%s)'
                    sql2='insert into customerDeposit (customerID , bankName , accountID , lastVisit) values(%s,%s,%s,%s)'
                    cursor.execute(getRandID)
                    accountID=cursor.fetchall()[0]['random_num'],
                    dt=datetime.datetime.now()
                    date=dt.strftime("""%Y-%m-%d""")
                    cursor.execute(sql1,(accountID,request.form['bank'],'0',date,request.form['interestRate'],request.form['currencyType']))
                    cursor.execute(sql2,(ID,request.form['bank'],accountID,date))
                except:
                    traceback.print_exc()
                    db.rollback()
                    cursor.close()
                    db.close()
                    flash('this customer already has an check account in this bank, or other unknown error')
                    return redirect('/customer/createAccount/{0}'.format(ID))
                else:
                    db.commit()
                    cursor.close()
                    db.close()
                    flash('success!')
                    #return redirect('/account/addCustomer/{0}'.format(ID))
                    return redirect('/customer/list')
            else:
                cursor.close()
                db.close()
                flash('interest rate must be a digit!')
                return redirect('/customer/createAccount/{0}'.format(ID))
        else:
            cursor.close()
            db.close()
            flash('no such bank!')
            return redirect('/customer/createAccount/{0}'.format(ID))
    else:
        cursor.close()
        db.close()
        flash('account type error!')
        return redirect('/customer/createAccount/{0}'.format(ID))

@app.route("/customer/createAccount/<string:ID>",methods=["POST","GET"])
def customerCreateAccount(ID):
    db = pymysql.connect(host='localhost',user='root',password='114514',database='banksys')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('select bankName from bank')
    banks=cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('createAccount.html',banks=banks,ID=ID)


@app.route("/customer/delete/<string:ID>",methods=["POST","GET"])
def customerDelete(ID):
    db = pymysql.connect(host='localhost',user='root',password='114514',database='banksys')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('select * from belongTo where customerID = %s',(ID))
    if cursor.fetchall():
        flash(u'该用户存在贷款，无法删除')
        cursor.close()
        db.close()
        return redirect('/customer/list')
    cursor.execute('select * from customerCheck where customerID = %s',(ID))
    if cursor.fetchall():
        flash(u'该用户存在支票账户，无法删除')
        cursor.close()
        db.close()
        return redirect('/customer/list')
    cursor.execute('select * from customerDeposit where customerID = %s',(ID))
    if cursor.fetchall():
        flash(u'该用户存在储蓄账户，无法删除')
        cursor.close()
        db.close()
        return redirect('/customer/list')
    try:
        cursor.execute('delete from server where customerID = %s',(ID))
        cursor.execute('delete from customer where customerID = %s',(ID))
    except:
        db.rollback()
        flash(u'未知原因删除失败')
        cursor.close()
        db.close()
        return redirect('/customer/list')
    else:
        db.commit()
    flash(u'删除成功')
    cursor.close()
    db.close()
    return redirect('/customer/list')

