import json
from flask import render_template, flash, redirect,jsonify,request
from app import app
import pymysql
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

@app.route("/customer/createAccount/<string:ID>")#TODO:
def customerCreateAccount(ID):
    return '114514'

@app.route("/customer/delete/<string:ID>",methods=["GET"])# TODO:
def customerDelete(ID):
    db = pymysql.connect(host='localhost',user='root',password='114514',database='banksys')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('select')
    return '114514'
