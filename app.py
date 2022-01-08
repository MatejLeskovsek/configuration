from flask import Flask
from flask import request
import pymongo
import requests
import datetime
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from flask_apispec import FlaskApiSpec
from marshmallow import Schema
from flask_cors import CORS, cross_origin
import sys

app = Flask(__name__)
app.config.update({
    'APISPEC_SWAGGER_URL': '/cfopenapi',
    'APISPEC_SWAGGER_UI_URL': '/cfswaggerui'
})
docs = FlaskApiSpec(app, document_options=False)
cors = CORS(app)
service_name = "configuration_core_service"
service_ip = "configuration-core-service"
microservices = [{"name":"database_core_service", "ip":"database-core-service"},{"name":"ecostreet_core_service", "ip": "ecostreet-core-service"},{"name":"admin_core_service", "ip": "admin-core-service"},{"name":"play_core_service", "ip": "play-core-service"}]

class NoneSchema(Schema):
    response = fields.Str()

# FALLBACK
@app.errorhandler(404)
def not_found(e):
    return "The API call destination was not found.", 404

# DEFAULT PAGE 
@app.route("/")
@marshal_with(NoneSchema, description='200 OK', code=200)
def health():
    return {"response": "200"}, 200
docs.register(health)

# HOME PAGE
@app.route("/cf")
@marshal_with(NoneSchema, description='200 OK', code=200)
def hello_world():
    return {"response": "Configuration server microservice."}, 200
docs.register(hello_world)

# FUNCTION TO UPDATE MS IP AND SEND NEW CONFIG TO OTHER MS 
@app.route('/cfupdate', methods = ['POST'])
@use_kwargs({"name": fields.Str(), "ip": fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='INTERNAL SERVER ERROR', code=500)
def update():
    global microservices
    global service_ip
    global service_name
    sys.stdout.write("Configuration microservice: /cfupdate accessed\n")
    try:
        microservice = request.form["name"]
        ms_ip = request.form["ip"]
        change = False
        old_ms = None
        for ms in microservices:
            if str(ms["name"]) == str(microservice):
                old_ms = ms["ip"]
                ms["ip"] = ms_ip
                change = True
                break
        if change:
            for ms in microservices:
                name = str(ms["name"])
                if(name == "database_core_service"):
                    url = 'http://' + str(old_ms) + '/dbconfig'
                    response = requests.post(url, data=request.form)
                elif(name == "admin_core_service"):
                    url = 'http://' + str(ms["ip"]) + '/adconfig'
                    response = requests.post(url, data=request.form)
                elif(name == "play_core_service"):
                    url = 'http://' + str(ms["ip"]) + '/plconfig'
                    response = requests.post(url, data=request.form)
                else:
                    url = 'http://' + str(ms["ip"]) + '/lgconfig'
                    response = requests.post(url, data=ms)
        return {"response": "200 OK"}, 200
    except Exception as err:
        return {"response": str(err)}, 500
docs.register(update)

# FUNCTION TO UPDATE CONFIGURATION MS 
@app.route('/cfconfigupdate', methods = ['POST'])
@use_kwargs({'name': fields.Str(), 'ip': fields.Str()})
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='INTERNAL SERVER ERROR', code=500)
def config_update():
    global service_ip
    global microservices
    global service_name
    sys.stdout.write("Configuration microservice: /cfconfigupdate accessed\n")
    service_ip = request.form["ip"]
    try:
        for ms in microservices:
            name = str(ms["name"])
            if(name == "database_core_service"):
                url = 'http://' + ms["ip"] + '/dbconfig'
                response = requests.post(url, data=request.form)
            elif(name == "admin_core_service"):
                url = 'http://' + ms["ip"] + '/adconfig'
                response = requests.post(url, data=request.form)
            elif(name == "play_core_service"):
                url = 'http://' + ms["ip"] + '/plconfig'
                response = requests.post(url, data=request.form)
            else:
                url = 'http://' + ms["ip"] + '/lgconfig'
                response = requests.post(url, data=request.form)
        return {"response": "200 OK"}, 200
    except Exception as err:
        return {"response": str(err)}, 500
docs.register(config_update)

# FUNCTION TO GET CURRENT CONFIG
@app.route("/cfgetconfig")
@marshal_with(NoneSchema, description='200 OK', code=200)
def get_config():
    global service_ip
    global service_name
    global microservices
    sys.stdout.write("Configuration microservice: /cfgetconfig accessed\n")
    return {"response": str([service_name, service_ip, microservices])}, 200
docs.register(get_config)

# METRICS FUNCTION
@app.route("/cfmetrics")
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='METRIC CHECK FAIL', code=500)
def get_health():
    sys.stdout.write("Configuration microservice: /cfmetrics accessed\n")
    start = datetime.datetime.now()
    for ms in microservices:
        try:
            name = ms["name"]
            if(name == "database_core_service"):
                url = 'http://' + ms["ip"] + '/dbhealthcheck'
                response = requests.get(url)
            else:
                url = 'http://' + ms["ip"] + '/lghealthcheck'
                response = requests.get(url)
        except Exception as err:
            return {"response": "METRIC CHECK FAIL:" + name + " unavailable"}, 500
    end = datetime.datetime.now()
    
    delta = end-start
    crt = delta.total_seconds() * 1000
    health = {"metric check": "successful", "microservices response time (ms)": crt}
    return {"response": str(health)}, 200
docs.register(get_health)

# HEALTH CHECK
@app.route("/cfhealthcheck")
@marshal_with(NoneSchema, description='200 OK', code=200)
def send_health():
    sys.stdout.write("Configuration microservice: /cfhealthcheck accessed\n")
    for ms in microservices:
        try:
            name = ms["name"]
            if(name == "database_core_service"):
                url = 'http://' + ms["ip"] + '/db'
                response = requests.get(url)
            elif(name == "ecostreet_core_service"):
                url = 'http://' + ms["ip"] + '/lg'
                response = requests.get(url)
            elif(name == "admin_core_service"):
                url = 'http://' + ms["ip"] + '/ad'
                response = requests.get(url)
            else:
                url = 'http://' + ms["ip"] + '/pl'
                response = requests.get(url)
        except Exception as err:
            return {"response": "Healthcheck fail: depending services unavailable"}, 500
    return {"response": "200 OK"}, 200
docs.register(send_health)