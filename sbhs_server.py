from flask import (Flask, flash, redirect, render_template, request, url_for,
                   Response, jsonify)
from sbhs import SbhsServer, Sbhs
app = Flask(__name__)


@app.route('/experiment/get_machine_ids')
def get_machine_ids():
    sbhs_server = SbhsServer()
    all_mac_ids = sbhs_server.map_sbhs_to_usb(sbhs_server.get_usb_devices())
    return jsonify(all_mac_ids)

@app.route('/experiment/set_fan/<int:dev_num>/<int:fan_speed>')
def set_fan(dev_num, fan_speed):
    response = {}
    sbhs_server = Sbhs(dev_num)
    connect = sbhs_server.connect_device()
    response["message"] = "Could not set fan speed"
    response["status"] = False
    if connect:
        status = sbhs_server.set_machine_fan(fan_speed)
        if status:
            response["message"] = "Set fan speed at {}%".format(fan_speed)
            response["status"] = True
    return jsonify(response)

@app.route('/experiment/set_heat/<int:dev_num>/<int:heat>')
def set_heat(dev_num, heat):
    response = {}
    sbhs_server = Sbhs(dev_num)
    connect = sbhs_server.connect_device()
    response["message"] = "Could not set heat"
    response["status"] = False
    if connect:
        status = sbhs_server.set_machine_heat(heat)
        if status:
            response["message"] = "Set heat at {}%".format(heat)
            response["status"] = True
    return jsonify(response)

@app.route('/experiment/get_temp/<int:dev_num>')
def get_temp(dev_num):
    sbhs_server = Sbhs(dev_num)
    connect = sbhs_server.connect_device()
    temp = 0.0
    if connect:
        temp = sbhs_server.get_machine_temp()
    return jsonify({"temp": temp})

@app.route('/experiment/reset/<int:dev_num>')
def reset(dev_num):
    response = {}
    sbhs_server = Sbhs(dev_num)
    connect = sbhs_server.connect_device()
    response["message"] = "Reset Failed"
    response["status"] = False
    if connect:
        status = sbhs_server.reset_board()
        if status:
            response["message"] = "Reset Successful"
            response["status"] = True
    return jsonify(response)

@app.route('/experiment/disconnect/<int:dev_num>')
def disconnect(dev_num):
    response = {}
    sbhs_server = Sbhs(dev_num)
    connect = sbhs_server.connect_device()
    response["message"] = "Disconnect Failed"
    response["status"] = False
    if connect:
        status = sbhs_server.disconnect_machine()
        if status:
            response["message"] = "Disconnected"
            response["status"] = True
    return jsonify(response)

# @app.route('/experiment/shutdown/<int:dev_num>')
# def shutdown(dev_num):
#     sbhs_server = SbhsServer()
#     connect = sbhs_server.connect_device(dev_num)
#     message = "Disconnect Failed"
#     if connect:
#         status = sbhs_server.shutdown_machine()
#         message = "Killed"
#     return Response(message)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=1234)
