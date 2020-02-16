import json
import os
import boto3
import stdFn

def request_handler(event,context):
    #print(event)
    findings=event['detail']['findings']
    dynamoName=os.environ['DBAWSFindings']
    client=boto3.resource('dynamodb')
    table=client.Table(dynamoName)
    i=stdFn.store_dynamo(table,findings)

    print("Processed %s" %(i))
    if i>0:
        masterId=boto3.client('sts').get_caller_identity().get('Account')
        accountId=findings[0]['AwsAccountId']
        if masterId!=accountId:
            status='VERIFIED'
        else:
            status='MASTER'
        stdFn.envStatus(os.environ['DBEnv'],status,accountId,'Processed %s events' %(i))
    else:
        pass

    return {"Processed":i}