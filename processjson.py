#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import MySQLdb
import traceback
import time
import pprint

class ProcessJSON():

    def __init__(self, config):
        self.myDB = config["myDB"]
        self.dirPath = config["dirPath"]
        self.httpHost = config["httpHost"]

    def getJSONResponse(self):
        with open(self.dirPath+'response.json', 'r') as myfile:
            data = myfile.read()

        return data

    def dataOutput(self, data, parameterData):

        jsonText = self.getJSONResponse()
        jsonText = jsonText.replace("%FULFILLMENT_TEXT%",parameterData["fulfillmentText"])
        jsonData = json.loads(jsonText)
        jsonData["source"] = self.httpHost

        jsonData["outputContexts"][0]["name"] = data["queryResult"]["intent"]["name"]
        jsonData["outputContexts"][0]["parameters"] = data["queryResult"]["parameters"]

        return jsonData


    def addTwoNumbers(self,data):

        number = int(data["queryResult"]["parameters"]["number"])
        number1 = int(data["queryResult"]["parameters"]["number1"])

        outSum = number + number1

        params = { "fulfillmentText" : "the sum of {} and {} is {}".format(number, number1, outSum) }
        return self.dataOutput(data,params)


    def processJSONdata(self, data):

        pp = pprint.PrettyPrinter(indent=4)

        try:
            displayName = data["queryResult"]["intent"]["displayName"]
        except:
            print (traceback.format_exc())
            return data

        dataOut = ""
        if displayName == "add two numbers":
            dataOut = self.addTwoNumbers(data)

#        print ("displayName: %s" % (displayName))
#        print (type(dataOut))

#        print (pp.pprint(data))

        return dataOut


if __name__ == "__main__":
    print ("Hello World")
