import json
import os
import boto3
import stdFn

def request_handler(event,context):
    #print(event)
    try:
        # Get security hub findings
        shClient=boto3.client('securityhub')
        findings=shClient.get_findings(MaxResults=100)['Findings']

        # Setup connection with Findings DB
        dynamoName=os.environ['DBAWSFindings']
        client=boto3.resource('dynamodb')
        table=client.Table(dynamoName)
        
    except Exception as e:
        print("Issue getting findings (%s)" %(e))
        return False

    grpFindings=list(stdFn.divide_chunks(findings,25))
    i=0
    for grpFinding in grpFindings:
         i+=stdFn.store_dynamo(table,grpFinding)

    accountId=boto3.client('sts').get_caller_identity().get('Account')
    stdFn.envStatus(os.environ['DBEnv'],'MASTER',accountId,'Processed %s events' %(i))

    return {"Processed":i}

