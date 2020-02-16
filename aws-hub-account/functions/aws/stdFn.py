import datetime
import json
import boto3

def divide_chunks(l, n): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def store_dynamo(table,items):
    i=0
    with table.batch_writer() as batch:
        for item in items:
            try:
                batch.put_item(Item=item)
                i+=1
            except Exception as e:
                print("Issue processing event (%s)" %(e))
    return i

def envStatus(tableName,status,envId,message):
    client=boto3.resource('dynamodb')
    table=client.Table(tableName)
    if len(envId)==12:
        cloud='AWS'
    else:
        cloud='Azure'
    item={'Cloud':cloud,'EnvId':envId,'Status':status,'Message':message,'Timestamp':datetime.datetime.now().isoformat()}
    table.put_item(Item=item)