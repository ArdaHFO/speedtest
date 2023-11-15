from flask import Blueprint, render_template

views =Blueprint(__name__,  "views")

@views.route("/")
def home ():
    return render_template("index.html")

@views.route("/measure")
def result ():
    return render_template("measure.html")

