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
@app.route("/")
def hello_world():
    return "Configuration server microservice."

# FUNCTION TO UPDATE MS IP AND SEND NEW CONFIG TO OTHER MS
@app.route('/update', methods = ['POST'])
def update():
    global microservices
    global service_ip
    global service_name
    try:
        microservice = request.form["name"]
        ms_ip = request.form["ip"]
        ms_old = None
        change = False
        for ms in microservices:
            if ms["name"] == microservice and ms["ip"] == ms_ip:
                ms_old = ms
                continue
            elif ms["name"] == microservice:
                ms["ip"] = ms_ip
                ms_old = ms
                change = True
        if change:
            for ms in microservices:
                url = 'http://' + ms["ip"] + '/config'
                response = requests.post(url, data=ms)
        return "200 OK"
    except Exception as err:
        return err

# FUNCTION TO UPDATE CONFIGURATION MS 
@app.route('/configupdate', methods = ['POST'])
def config_update():
    global service_ip
    global microservices
    global service_name
    service_ip = request.form["ip"]
    try:
        for ms in microservices:
            url = 'http://' + ms["ip"] + '/config'
            response = requests.post(url, data=request.form)
        return response.text
    except Exception as err:
        return err

# FUNCTION TO GET CURRENT CONFIG
@app.route("/getconfig")
def get_config():
    global service_ip
    global service_name
    global microservices
    return str([service_name, service_ip, microservices])

# HEALTH CHECK
@app.route("/health")
def get_health():
    start = datetime.datetime.now()
    for ms in microservices:
        try:
            url = 'http://' + ms["ip"] + '/config'
            response = requests.get(url)
        except Exception as err:
            return "HEALTH CHECK FAIL:" + ms["name"] + " unavailable"
    end = datetime.datetime.now()
    
    delta = start-end
    crt = delta.total_seconds() * 1000
    health = {"health check": "successful", "microservices response time (ms)": crt}
    return str(health)

@app.route("/healthcheck")
def send_health():
    return "200 OK"