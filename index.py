#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
CURRENTDIR = os.path.dirname(os.path.abspath(__file__))
if CURRENTDIR not in sys.path:
    sys.path.insert(0,CURRENTDIR)

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
import json
import MySQLdb
import traceback
import time



# def dbConnect(q):
#
#     myDB = MySQLdb.connect(host=_dbHost, user=_dbUser, passwd=_dbPass, db=_dbData,compress=1)
#     _dbA = myDB.cursor(cursorclass=MySQLdb.cursors.DictCursor)
#
#     return

# def saveToJsonLog(data, info, ipAddress):
#     dbA = _myDB.cursor()
#     dbA.execute("INSERT INTO jsonLog SET logDate=NOW(), logData=%s, info=%s, IPaddress=%s",
#                     (data, info, ipAddress))
#     id = dbA.lastrowid
#     _myDB.commit()
#     return id

def jsonError(error, location, errorNo):
    e = {"Error": error, "Location": location, "ErrorNo": errorNo}
    return e

def jsonErrorOut(error, location, errorNo):

    e = {"Error": error, "Location": location, "ErrorNo": errorNo}
    return bytes(json.dumps(e, sort_keys=True, indent=2), encoding='utf-8')

def getClientAddress(environ):
    ip = "0.0.0.0"
    # try:
    #     ip = environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
    # except:
        # ip = environ.get('REMOTE_ADDR')

    ip = environ.get('REMOTE_ADDR')
    return ip

def getProgramDir(environ):

    dir = str(environ.get("DOCUMENT_ROOT",""))
    script = str(environ.get("SCRIPT_NAME",""))
    sc = os.path.dirname(script);
    return dir + os.path.sep + sc + os.path.sep

def application(environ, start_response):

    id = 0

    try:
        requestBodySize = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        requestBodySize = 0

    ip = str(environ.get("REMOTE_ADDR","empty"))

    config = {  "myDB": "no db",
                "dirPath": getProgramDir(environ),
                "ipAddress": ip,
                "httpHost": str(environ.get("HTTP_HOST","")) }

    # if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
    #     _IPaddress = request.environ['REMOTE_ADDR']
    # else:
    #     _IPaddress = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy

    if requestBodySize <=0:
        return jsonErrorOut("body lacks contents", "dataIn", 0)

    requestBody = environ['wsgi.input'].read(requestBodySize)
    d = parse_qs(requestBody)
    #saveToJsonLog(str(d), "parseRequestBody", ip)

    jsonText = ""
    if d.get(b'XMLPost') is not None:
        jsonText = d.get(b'XMLPost', '')[0]
    else:
        jsonText = requestBody


    saveToJsonLog(str(jsonText), "requestBody", ip)

    try:
        dataIn = json.loads(jsonText)
    except:
        er = jsonError("cannot parse json", "dataIn", id)
        start_response('200 OK', [('Content-Type', 'application/json')])
        yield bytes(json.dumps(er, sort_keys=True, indent=2), encoding='utf-8')

    try:
        from processjson import ProcessJSON
        pJSON = ProcessJSON(config)
        dataOut = pJSON.processJSONdata(dataIn)
    except:
        er = jsonError("process data error", "ProcessJSON", id)
        start_response('200 OK', [('Content-Type', 'application/json')])
        yield bytes(json.dumps(er, sort_keys=True, indent=2), encoding='utf-8')

    #saveToJsonLog(json.dumps(dataOut), "dataIn", ip)
    #
    dataOut = json.dumps(dataOut) #, sort_keys=True, indent=2)
    # responseHeaders = [('Content-type', 'text/plain'),
    #                    ('Content-Length', str(len(dataOut)))]

    start_response('200 OK', [('Content-Type', 'application/json')])
    yield bytes(dataOut, encoding='utf-8')
