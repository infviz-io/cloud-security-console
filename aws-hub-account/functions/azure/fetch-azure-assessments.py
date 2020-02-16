import os
import json
import urllib3
import boto3
import stdFn
import datetime

AUTH_URL='https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token'
ASSESSMENTS_URL="https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Security/assessments?api-version=2020-01-01"
ALERTS_URL="https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Security/alerts?api-version=2019-01-01"

def request_handler(event,context):
    # Subscription to get details from
    subscription_id = event['subscription']

    # Tenant ID for your Azure subscription
    TENANT_ID = os.environ['Tenant']

    # Your service principal App ID
    CLIENT = os.environ['ClientId']

    # Your service principal password
    KEY = os.environ['Secret']

    # Http session
    http = urllib3.PoolManager()
    
    # Environment DB
    dbEnv=os.environ['DBEnv']

    # Get Access Token
    data={
        'grant_type':'client_credentials',
        'client_id': CLIENT,
        'client_secret': KEY,
        'scope':'https://management.azure.com/.default'
    }
    url=AUTH_URL.replace('{tenant}',TENANT_ID)
    r = http.request('POST', url, fields=data)
    authToken=json.loads(r.data.decode('utf-8'))
    accessToken=authToken['access_token']

    print("Getting Assessments")
    # Get Assessments
    try:
        url=ASSESSMENTS_URL.replace('{subscriptionId}',subscription_id)
        header={'Authorization':'Bearer %s' %(accessToken)}
        r = http.request('GET', url, headers=header)
        respJson=json.loads(r.data.decode('utf-8'))
        assessments=respJson['value']
    except Exception as e:
        stdFn.envStatus(dbEnv,'ERROR',subscription_id,"%s" %(e))

 
    # Store asssessments
    print("Storing Assessments")
    i=storeItems(os.environ['DBAzureAssess'], subscription_id, assessments)

    # Get Alerts
    try:
        url=ALERTS_URL.replace('{subscriptionId}',subscription_id)
        header={'Authorization':'Bearer %s' %(accessToken)}
        r = http.request('GET', url, headers=header)
        respJson=json.loads(r.data.decode('utf-8'))
        alerts=respJson['value']
    except Exception as e:
        stdFn.envStatus(dbEnv,'ERROR',subscription_id,"%s" %(e))

    # Store Alerts
    i+=storeItems(os.environ['DBAzureAssess'], subscription_id, alerts)

    print("Processed %s" %(i))
    stdFn.envStatus(dbEnv,'VERIFED',subscription_id,'Processed %s events' %(i))
    return {"Processed":i}

def storeItems(dynamoName, subscription_id, events):
    # Setup DynamoDB
    try:
        client=boto3.resource('dynamodb')
        table=client.Table(dynamoName)
    except Exception as e:
        print(e)
        return False
    
    nowTime=datetime.datetime.now().isoformat()
    i=0
    grpEvents=list(stdFn.divide_chunks(events,25))
    for items in grpEvents:
    # Write into DynamoDB
        with table.batch_writer() as batch:
            for item in items:
                try:
                    item['SubscriptionId']=subscription_id
                    item['Id']=item['id']
                    item['FirstObservedAt']=nowTime

                    # Get alert or assessment
                    try:
                        if item['type']=='Microsoft.Security/assessments':
                            item['RecordState']=item['properties']['status']['code']
                            item['LastObservedAt']=nowTime
                            item['Title']=item['properties']['displayName']
                            item['Description']=item['properties']['resourceDetails']['Id']
                        elif item['type']=='Microsoft.Security/Locations/alerts':
                            item['RecordState']=item['properties']['state']
                            if 'detectedTimeUtc' in item['properties']:
                                item['LastObservedAt']=item['properties']['detectedTimeUtc']
                            else:
                                item['LastObservedAt']=nowTime
                            item['Title']=item['properties']['alertDisplayName']
                            item['Description']=item['properties']['associatedResource']
                        else:
                            item['RecordState']='Unknown'
                            item['LastObservedAt']=nowTime
                            item['Title']='Unknown'
                            item['Description']='Unknown'
                    except Exception as e:
                        print("Issue getting details from assessment or alert: %s" %(e))
                        print(item)

                    batch.put_item(Item=item)
                    i+=1
                except Exception as e:
                    print("Issue processing event (%s)" %(e))

    return i 
