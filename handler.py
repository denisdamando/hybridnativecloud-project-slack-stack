import sys
sys.path.insert(0,'/opt')
import json
import boto3
import os
import random
import string
from zipfile import ZipFile

grupo = os.environ['GROUP']

s3 = boto3.client('s3',)

from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token="<TOKEN DONTPAD>")

def sendMessageToSlack(message,username):
  try:
    response = client.chat_postMessage(
        channel='#atividade-slack',
        text=message,
        username=username,)        
  except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    print(f"Got an error: {e.response['error']}")

def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def createFolderTmp():
    path = "/tmp/"+ randomString()

    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
        return None
    else:
        print ("Successfully created the directory %s " % path) 
        return path
def readFromS3andWriteUnzipedLocal(bucketName,bucketKey,path):
    with open(path+'/obj', 'wb') as f:
        s3.download_fileobj(bucketName, bucketKey, f)

    with ZipFile(path+'/obj', 'r') as zipObj:
       zipObj.extractall(path)  
       
def returnInformationDeploy(path):
    data = {}
    with open(path+'/elb.txt', 'r') as file:
        data["elb"] = file.read().replace('\n', '')
    
    return data
    
def messageToSlack(data):
    return "O grupo " + str(grupo) + " acabou de disponibilizar o servico nginx na URL: http://" + data['elb']
   

def hello(event, context):
    print(str(event))
    print(str(context))
    
    bucketName = event['Records'][0]['s3']['bucket']['name']
    bucketKey = event['Records'][0]['s3']['object']['key']
    
    print("Bucket name:" + bucketName)
    print("Bucket key:" + bucketKey)
    
    path=createFolderTmp()
    readFromS3andWriteUnzipedLocal(bucketName, bucketKey,path)
    data = returnInformationDeploy(path)
    message = messageToSlack(data)
    
    sendMessageToSlack(message,str(grupo))

    
