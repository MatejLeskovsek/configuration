from flask import Flask
from flask import request
import pymongo
import requests
import datetime
from webargs import fields
from flask_apispec import use_kwargs, marshal_with
from flask_apispec import FlaskApiSpec
from marshmallow import Schema

app = Flask(__name__)
app.config.update({
    'APISPEC_SWAGGER_URL': '/cfopenapi',
    'APISPEC_SWAGGER_UI_URL': '/cfswaggerui'
})
docs = FlaskApiSpec(app, document_options=False)
service_name = "configuration_core_service"
service_ip = "34.96.72.77"
microservices = [{"name":"database_core_service", "ip":"34.96.72.77"},{"name":"ecostreet_core_service", "ip": "34.96.72.77"}]

class NoneSchema(Schema):
    response = fields.Str()

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
    print("/cfupdate accessed")
    try:
        microservice = request.form["name"]
        ms_ip = request.form["ip"]
        change = False
        for ms in microservices:
            if ms["name"] == microservice and ms["ip"] == ms_ip:
                skip = True
            elif ms["name"] == microservice:
                ms["ip"] = ms_ip
                change = True
        if change:
            for ms in microservices:
                if(ms["name"] == "database_core_service"):
                    url = 'http://' + ms["ip"] + '/dbconfig'
                    response = requests.post(url, data=ms)
                else:
                    url = 'http://' + ms["ip"] + '/lgconfig'
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
    print("/cfconfigupdate accessed")
    service_ip = request.form["ip"]
    try:
        for ms in microservices:
            if(ms["name"] == "database_core_service"):
                url = 'http://' + ms["ip"] + '/dbconfig'
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
    print("/cfgetconfig accessed")
    return {"response": str([service_name, service_ip, microservices])}, 200
docs.register(get_config)

# METRICS FUNCTION
@app.route("/cfmetrics")
@marshal_with(NoneSchema, description='200 OK', code=200)
@marshal_with(NoneSchema, description='METRIC CHECK FAIL', code=500)
def get_health():
    print("/cfmetrics accessed")
    start = datetime.datetime.now()
    for ms in microservices:
        try:
            if(ms["name"] == "database_core_service"):
                url = 'http://' + ms["ip"] + '/dbhealthcheck'
                response = requests.get(url)
            else:
                url = 'http://' + ms["ip"] + '/lghealthcheck'
                response = requests.get(url)
        except Exception as err:
            return {"response": "METRIC CHECK FAIL:" + ms["name"] + " unavailable"}, 500
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
    print("/cfhealthcheck accessed")
    return {"response": "200 OK"}, 200
docs.register(send_health)