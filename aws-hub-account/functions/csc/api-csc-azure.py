import json
import boto3
from boto3.dynamodb.conditions import Key
import os
import stdFn

def request_get(event,context):
    status=200
    dynamoName=os.environ['DBAzureAssess']
    client=boto3.resource('dynamodb')
    table=client.Table(dynamoName)
    resp=table.query(
        IndexName="DisplayData",
        KeyConditionExpression=Key('RecordState').eq('Unhealthy')
    )


    body={}
    body['Items']=resp['Items']

    response = {
        "statusCode": status,
        "headers": {
        "Access-Control-Allow-Origin" : "*",
        "Access-Control-Allow-Credentials" : True
        },
        "body": json.dumps(body)
    }
    return response