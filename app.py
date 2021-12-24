from flask import Flask
from flask import request
import pymongo
import requests
import datetime

app = Flask(__name__)

service_name = "configuration_core_service"
service_ip = "34.141.19.56:5000"

microservices = [{"name":"database_core_service", "ip":"34.159.211.186:5000"},{"name":"ecostreet_core_service", "ip": "34.159.194.58:5000"}]

# HOME PAGE
@app.route("/cf")
def hello_world():
    return "Configuration server microservice."

# FUNCTION TO UPDATE MS IP AND SEND NEW CONFIG TO OTHER MS
@app.route('/cfupdate', methods = ['POST'])
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
        return "200 OK"
    except Exception as err:
        return err

# FUNCTION TO UPDATE CONFIGURATION MS 
@app.route('/cfconfigupdate', methods = ['POST'])
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
        return "200 OK"
    except Exception as err:
        return err

# FUNCTION TO GET CURRENT CONFIG
@app.route("/cfgetconfig")
def get_config():
    global service_ip
    global service_name
    global microservices
    print("/cfgetconfig accessed")
    return str([service_name, service_ip, microservices])

# METRICS FUNCTION
@app.route("/cfmetrics")
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
            return "METRIC CHECK FAIL:" + ms["name"] + " unavailable"
    end = datetime.datetime.now()
    
    delta = end-start
    crt = delta.total_seconds() * 1000
    health = {"metric check": "successful", "microservices response time (ms)": crt}
    return str(health)

# HEALTH CHECK
@app.route("/cfhealthcheck")
def send_health():
    print("/cfhealthcheck accessed")
    return "200 OK"