import boto3
from boto3.dynamodb.conditions import Key
import json
import time
import os

def request_handler(context,event):
    dynamoName=os.environ['DBEnv']
    client=boto3.resource('dynamodb')
    table=client.Table(dynamoName)
    lambdaJob=os.environ['FetchLambda']

    response=table.query(
        KeyConditionExpression=Key('Cloud').eq('Azure')
    )
    items=response['Items']
    i=0
    for item in items:
        time.sleep(0.2)
        print("TRIGGER subscription %s" %(item['EnvId']))
        i+=1
        clientLambda=boto3.client('lambda')
        clientLambda.invoke(
            FunctionName=lambdaJob,
            InvocationType='Event',
            Payload=json.dumps({'subscription':item['EnvId']}).encode()
        )
        
    return {"Triggered":i}