from flask import render_template, flash, redirect
from app import app

@app.route('/login', methods = ['GET', 'POST'])
def login():
    d=1#TODO:

