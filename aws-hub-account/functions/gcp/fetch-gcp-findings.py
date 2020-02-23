from jose import jwt,jws, jwk
import time
import urllib3
import json
import boto3
import stdFn
import base64
import datetime
import os

GOOGLE_OAUTH = 'https://www.googleapis.com/oauth2/v4/token'

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform'
]

SOURCES = {
    "3101809420974206212": "Security Health Analytics",
    "13622691099480362264": "Event Threat Detection"
}

GOOGLE_SEC_FINDINGS='https://securitycenter.googleapis.com/v1/organizations/{org}/sources/{source}/findings'

def request_handler(event,context):
    # Organization Id
    org = os.environ['OrgId']

    # Private Key
    secret = base64.b64decode(os.environ['Secret']).decode('utf-8')

    # Client Email
    client_email = os.environ['ClientEmail']  

    iat = int(time.time())

    exp = int(time.time())+3600

    payload = {
            'aud': GOOGLE_OAUTH,
            'iss': client_email,
            'scope': " ".join(SCOPES),
            'iat': iat,
            'exp': exp,
        }
    
    print(payload)
    
    token=jws.sign(payload,secret,algorithm='RS256')

    # Http session
    http = urllib3.PoolManager()
    
    # Environment DB
    dbEnv=os.environ['DBEnv']

    # Get Access Token
    data={
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': token
    }

    r = http.request('POST', GOOGLE_OAUTH, fields=data)
    authToken=json.loads(r.data.decode('utf-8'))
    accessToken=authToken['access_token']

    i=0
    for k,v in SOURCES.items():
        print ("Getting %s" %(v))

        # Get Assessments
        try:
            url=GOOGLE_SEC_FINDINGS.replace('{org}',org).replace('{source}',k)
            header={'Authorization':'Bearer %s' %(accessToken)}
            #print(accessToken)
            #print(url)
            r = http.request('GET', url, headers=header)
            respJson=json.loads(r.data.decode('utf-8'))
            #print(respJson)
            if 'listFindingsResults' in respJson:
                i+=storeItems(os.environ['DBGcpFinding'], v, respJson['listFindingsResults'])
        except Exception as e:
            print(e)
            stdFn.envStatus(dbEnv,'ERROR',org,"%s" %(e))

    # Store asssessments
    #print("Storing Assessments")
    #i=storeItems(os.environ['DBAzureAssess'], subscription_id, assessments)

    print("Processed %s" %(i))
    stdFn.envStatus(dbEnv,'VERIFED',"G"+org,'Processed %s events' %(i))
    return {"Processed":i}

def storeItems(dynamoName, scanner, events):
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
                    # Setup the mandatory keys for CSC
                    if 'ProjectId' in item['finding']:
                        item['ProjectId']=item['finding']['ProjectId']
                    elif 'projectDisplayName' in item['resource']:
                        item['ProjectId']=item['resource']['projectDisplayName']
                    else:
                        item['ProjectId']='(none)'
                    item['Id']=item['finding']['name']
                    item['FirstObservedAt']=item['finding']['eventTime']

                    # Setup the optional indexed keys for CSC
                    try:
                        item['RecordState']=item['finding']['state']
                        item['LastObservedAt']=item['finding']['eventTime']
                        item['Title']=item['finding']['category']
                        if 'Explanation' in item['finding']['sourceProperties']:
                            item['Description']=item['finding']['sourceProperties']['Explanation']
                        else:
                            item['Description']='N/A'
                    except Exception as e:
                        item['RecordState']='N/A'
                        item['LastObservedAt']='N/A'
                        item['Title']='N/A'
                        item['Description']='N/A'
                        print("Issue getting details from findings or alert: %s" %(e))
                        print(item)

                    # Setup the optional GCP specifc keys
                    item['type ']=scanner
                    if 'resourceName' in item['finding']:
                        item['resourceName']=item['finding']['resourceName']
                    else:
                        item['resourceName']='N/A'

                    batch.put_item(Item=item)
                    i+=1
                except Exception as e:
                    print("Issue processing event (%s)" %(e))

    return i 
