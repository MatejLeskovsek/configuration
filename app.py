from flask import Flask
from flask import request
import pymongo
import requests

app = Flask(__name__)

service_name = "configuration_core_service"
service_ip = "192.168.1.121"

microservices = [{"name":"database_core_service", "ip":"34.96.72.77"},{"name":"ecostreet_core_service", "ip": "34.120.106.247"}]

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
        return ms_old
    except Exception as err:
        return err
    
@app.route('/configupdate', methods = ['POST'])
def config_update():
    service_ip = request.form["ip"]
    for ms in microservices:
        url = 'http://' + ms["ip"] + '/config'
        response = requests.post(url, data={"name": service_name, "ip": service_ip})
    return 200

