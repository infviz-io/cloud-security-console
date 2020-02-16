import json
import boto3
from boto3.dynamodb.conditions import Key
import os
import stdFn


def request_get(event,context):
    status=200
    dynamoName=os.environ['DBEnv']
    client=boto3.resource('dynamodb')
    table=client.Table(dynamoName)
    body={}
    body['Envs']=table.scan()['Items']

    response = {
        "statusCode": status,
        "headers": {
        "Access-Control-Allow-Origin" : "*",
        "Access-Control-Allow-Credentials" : True
        },
        "body": json.dumps(body)
    }
    return response

def request_post(event,context):
    try:
        eventInput=json.loads(event['body'])
    except:
        eventInput=event
    proceed=True

    reqKeys=['Cloud','EnvId']
    for key in reqKeys:
        if key not in eventInput:
            status=400
            body={"Success":False,"message":"Missing required key %s" %(key)}
            proceed=False

    if proceed:
        Cloud = eventInput['Cloud']
        EnvId = eventInput['EnvId']
        dynamoName=os.environ['DBEnv']
        client=boto3.resource('dynamodb')
        table=client.Table(dynamoName)
        lambdaJob=os.environ['FetchLambda']
        eventBridge=os.environ['AwsBridge']

        stdFn.envStatus(os.environ['DBEnv'],'PENDING',EnvId,'Added via API')

    if Cloud=='Azure' and proceed:
        clientLambda=boto3.client('lambda')
        resp=clientLambda.invoke(
            FunctionName=lambdaJob,
            InvocationType='Event',
            Payload=json.dumps({'subscription':EnvId}).encode()
        )
        status=201
        body={"Success":True}
    elif Cloud=='AWS' and proceed:
        clientEvent=boto3.client('events')
        resp=clientEvent.put_permission(
            EventBusName=eventBridge,
            Action='events:PutEvents',
            Principal=EnvId,
            StatementId='csc%s' %(EnvId)
        )
        status=201
        body={"Success":True}
    elif proceed:
        status=400
        body={"Success":False}

    response = {
        "statusCode": status,
        "headers": {
        "Access-Control-Allow-Origin" : "*",
        "Access-Control-Allow-Credentials" : True
        },
        "body": json.dumps(body)
    }
    return response

def request_delete(event,context):
    proceed=True
    try:
        eventInput=event['pathParameters']
    except:
        eventInput=event
    
    EnvId=eventInput['envid']
    dynamoName=os.environ['DBEnv']
    client=boto3.resource('dynamodb')
    table=client.Table(dynamoName)
    eventBridge=os.environ['AwsBridge']
    dbAws=os.environ['DBAWSFindings']
    dbAzure=os.environ['DBAzureAssess']

    if len(EnvId)==12:
        print("Deleting AWS %s" %(EnvId))
        table.delete_item(Key={'Cloud':'AWS','EnvId':EnvId})
        clientEvent=boto3.client('events')
        resp=clientEvent.remove_permission(
            EventBusName=eventBridge,
            StatementId='csc%s' %(EnvId)
        )
        cloudTable=client.Table(dbAws)
        i=spitDelete(cloudTable,EnvId)
        print("Deleted %s items" %(i))
    else:
        print("Deleting Azure %s" %(EnvId))
        table.delete_item(Key={'Cloud':'Azure','EnvId':EnvId})
        cloudTable=client.Table(dbAzure)
        i=spitDelete(cloudTable,EnvId)
        print("Deleted %s items" %(i))

    status=200
    body={'success':True}
    response = {
        "statusCode": status,
        "headers": {
        "Access-Control-Allow-Origin" : "*",
        "Access-Control-Allow-Credentials" : True
        },
        "body": json.dumps(body)
    }
    return response

def spitDelete(table,envId):
    if len(envId)==12:
        attribute='AwsAccountId'
    else:
        attribute='SubscriptionId'
    response=table.query(
        KeyConditionExpression=Key(attribute).eq(envId)
    )
    scanItems=response['Items']

    grpItems=list(stdFn.divide_chunks(scanItems,25))
    i=0
    for items in grpItems:
        with table.batch_writer() as batch:
            for item in items:
                try:
                    batch.delete_item(Key={attribute:envId,'Id':item['Id']})
                    i+=1
                except Exception as e:
                    print("Issue processing event (%s)" %(e))
                    raise("Issue")
    return i