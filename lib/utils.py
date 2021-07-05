# ------ Imports

import json
import logging
from datetime import datetime

from pymongo import MongoClient
import pymongo

# Reading config.json

def get_config():
    """
    READ /config.json and return it's content as a dictionary
    """
    with open("config.json", "r") as f:
        data = f.read()
    return json.loads(data)

def get_discord_config():
    """
    Returns discord configs in /config.json as (PREFIX, TOKEN)
    """
    config = get_config()

    try:
        discord_configs = config["discord"]
        return discord_configs["prefix"], discord_configs["token"]
    except:
        # TODO: add option to create config.json
        raise Exception("Couldn't find discord configs in /config.json")

# MongoDB

mongoConfig = get_config()["mongo"]
CONNECTION_STRING = mongoConfig["connectionString"]
database = mongoConfig["database"]

client = MongoClient(CONNECTION_STRING)

showcasesCol = client[database]["showcases"]
channelsCol = client[database]["channels"]

def addShowcase(
    originalMsgID: int, 
    approvalMsgID: int, 
    content: str, 
    attachments: list, 
    author: int
    ):

    dbEntry = {
        "originalMessage": originalMsgID,
        "approvalMessage": approvalMsgID,
        "content": content,
        "attachments": attachments,
        "author": author
    }

    showcasesCol.insert_one(dbEntry)

def getShowcase(approvalMsgID: int):
    results = showcasesCol.find({"approvalMessage": approvalMsgID})
    if(results.count() == 1):
        for result in results:
            return result
    elif(results.count() > 1):
        return 0
    else:
        return None

def addChannel(channel: str, reaction: str):
    # Check whether the reaction already exists
    results = channelsCol.find({"reaction": reaction}).count()
    if(results > 0):
        return False

    dbEntry = {
        "channel": channel,
        "reaction": reaction
    }
    channelsCol.insert_one(dbEntry)

def getChannel(reaction=None):
    # Return all channels and it's corresponding reaction
    if(reaction == None):
        results = channelsCol.find()
        channels = []
        for result in results:
            channels.append(result)
        return channels
    
    # Find channel related to reaction
    results = channelsCol.find({"reaction": reaction})

    # If reaction does not exist
    if(results.count() < 1):
        return None
    
    for result in results:
        return result
    

    