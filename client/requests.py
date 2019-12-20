import json

import requests

ip_port_local = "http://127.0.0.1:5000"


def process_img(path, filter_id, ngrok=None):
    if ngrok:
        req_path = ngrok + '/transfer/' + str(filter_id)
    else:
        req_path = ip_port_local + '/transfer/' + str(filter_id)
    r = requests.post(req_path, files={'image': open(path, 'rb')})
    return r.json()['res_img']


def request(req, req_path):
    try:
        print(ip_port_local)
        res_str = requests.post(ip_port_local + req_path, json=req, timeout=7).json()
        return res_str
    except:
        print("error in request")
        return json.loads(json.dumps({"result": "Server is unreachable, try again later"}))


def get_flask_transfer(img, style_id):
    # print(img)
    # print(type(img))
    req = json.dumps({
        "img": img,
        "style_id": style_id})
    res = request(req, '/transfer/')

    if res['result'] != 'OK':
        return res['result']

    return res['res_img']
