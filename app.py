from flask import Flask
from flask import request
import pymongo
import requests

app = Flask(__name__)

service_name = "configuration_core_service"
service_ip = "34.141.19.56:5000"

microservices = [{"name":"database_core_service", "ip":"34.159.211.186:5000"},{"name":"ecostreet_core_service", "ip": "34.159.194.58:5000"}]

@app.route("/")
def hello_world():
    return "Configuration server microservice."
    
@app.route('/update', methods = ['POST'])
def update():
    # connect to mongodb and authenticate user, return token
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
        # send info to other microservices about ip change 
        if change:
            for ms in microservices:
                url = 'http://' + ms["ip"] + '/config'
                response = requests.post(url, data=ms)
        return str(request.remote_addr)
    except Exception as err:
        return err
    
@app.route('/configupdate', methods = ['POST'])
def config_update():
    service_ip = request.form["ip"]
    #for ms in microservices:
    #    url = ms["ip"] + '/config'
    #    response = requests.post(url, data=request.form)
    try:
        url = 'http://34.159.194.58:5000/config'
        response = requests.post(url, data=request.form)
        return response.text
    except Exception as err:
        return err

