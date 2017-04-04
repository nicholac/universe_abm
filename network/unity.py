'''
Created on 29 Mar 2017

@author: dusted-ipro
'''
import json
from flask import Flask, render_template, jsonify, g, request, Response, abort

# Flask App configuration
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = ''
app.name = 'universeabm'
print app.name

@app.route('/syspos')
def sysPos():
    out = {'1':{'x': 10.0,
                'y':10.0,
                'z':10.0},
           '2':{'x': 20.0,
                'y':20.0,
                'z':20.0},
           '3':{'x': 20.0,
                'y':20.0,
                'z':20.0},
           '4':{'x': 90.0,
                'y':50.0,
                'z':20.0}
           }
    return Response(json.dumps(out),  mimetype='application/json')


@app.route('/syspopn')
def sysPopn():
    out = {'1':{50.0},
           '2':{10.0},
           '3':{100.0},
           '4':{2000.0}}
    return Response(json.dumps(out),  mimetype='application/json')


if __name__ == '__main__':

    app.run(host='192.168.1.64', port=8080)
