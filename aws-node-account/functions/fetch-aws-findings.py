import json
import os
import boto3
import stdFn

def request_handler(event,context):
    #print(event)
    try:
        shClient=boto3.client('securityhub')
        findings=shClient.get_findings(MaxResults=100)['Findings']
    except Exception as e:
        print("Issue getting findings (%s)" %(e))
        return False

    cloudwatch_events = boto3.client('events')
    currentSet=[]
    responses=[]

    grpFindings=list(stdFn.divide_chunks(findings,10))
    i=0
    for grpFinding in grpFindings:
        response = cloudwatch_events.put_events(
            Entries=[
                {
                    'Detail': json.dumps({"findings":grpFinding}),
                    'DetailType': 'Security Hub Findings - Imported',
                    'Resources': [],
                    'Source': 'custom.securityconsole'
                }
            ]
        )
        responses.append(response)
        i+=len(grpFinding)

    response={"Processed":i,"zEventMsgs":responses}

    return response