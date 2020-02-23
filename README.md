# Cloud Security Console (CSC)
> NOTE : This is built mainly for demostration purposes. Feel free to download and see how you can stitch together cloud native security tool findings into a custom layout.
## Overview
The Cloud Security Console (CSC) aggregates AWS security hub & Azure security center & GCP Security Command Center into a single console, built in angular. The main advantage of using this console is that:
* Provides visbility across both AWS, Azure and GCP.
* You can workaround the AWS Security Hub single master limitation within AWS security hub console.
* You can easily grant access to security findings without having access to the cloud consoles.
* You can customise it with anything else you want.
* All security information is kept in accounts you control.

This was built for mainly demostration purposes and therefore has some limitations when compared to the native AWS security hub & Azure security center & GCP security command center. These include:
* It only shows AWS Security Hub findings
* It collects Azure assessments and alert events
* It collects GCP Security Health Analytics & Event Threat Detection findings 
* It is a read only console
* Instructions at the moment are to run the website locally using 'ng serve'

## Architecture
![Cloud Security Console Architecture](https://infviz.io/samples/csc3a.png)

## Requirements
In order to build and deploy the source files will need:
* aws cli (pip install aws-cli)
* sam cli (pip install aws-sam-cli)
* angular cli (npm install -g @angular/cli)

## Setup
### (Optional) Create Azure AD application registration
This is if you want to connect to Azure subscriptions. It will save time if you do this first as you will need the azure credentials as part of the setup of Cloud Security Console.
1. In Azure console create a new app registration
2. In Azure console Obtain a secret key

For more detailed steps follow : https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app

### (Optional) Create GCP service account
This is if you want to connect to GCP Organisation. It will save if you do this first as you will need the GCP service account credentials as part of the setup of Cloud Security Console.
1. Login the GCP console as Org Admin. Switch to a project.
2. In 'APIs & Services' under 'Credentials' create a Service Account
3. Download key file and open in text editor
4. Collect the 'client_email'
5. Collect the 'private_key'. Transform this key into base64. This can be done using python.

`python3`

`import base64`

`a='(privatekey)'`

`b=base64.b64encode(a.encode('utf-8')).decode('utf-8)`

`print(b)`

5. In GCP console switch to your organisation. In 'Security Command Center' click 'Settings'.
6. In'Permissions' grant the service account the following role 'Security Center Admin Viewer'
7. In 'APIs & Services' under 'Dashboard' click 'Enable APIs and Services'
8. Enable 'Cloud Security Command Center API'

### CSC Hub AWS Account
This is the account which will store all the data collected. Steps to setup:

1. Run the command below to setup a deployment bucket

`aws s3 mb s3://(bucketname) --region (region) --profile (aws profile)`

2. In the aws-hub-account folder run the command below to package sam deployment

`sam package --template-file .template.yaml --output-template-file package.yaml --s3-bucket (bucketname) --region (region)`

3. In the aws-hub-account folder run the command below to deploy the configuation. 
* If you do not have azure credentials to can run without Azure parameter-overrides.
* If you do not have gcp credentials to can run without Google parameter-overrides.

`sam deploy --template-file package.yaml --stack-name (existing stackname) --region (region) --capabilities CAPABILITY_IAM --parameter-overrides AzureTenant=(tenant) AzureClientId=(clientid) AzureSecret=(secret) GoogleOrgId=(orgId) GoogleClientEmail=(clientEmail) GoogleSecret=(privateKey base64)`

4. At the end of the deployment collect the output parameters.
* Api
* CognitoClientId
* CognitoDomain
* CognitoPool
* CognitoRedirect
* CognitoRegion

5. In the AWS management console run the following lambdas to load initial data.
* AwsFetchFinding - This will load inital data from your master AWS account
* GcpFetchFinding - This will load inital data from GCP organisation. *This is only available if you've specified Google parameters as part of the deployment.*

6. Create a user in Cognito so that you can login the UI

### Angular UI
This will build all the files local on your pc so you can run the website locally. If you want to host on the server you will need to ng build and setup your own hosting solution.
1. In the aws-hub-account/ui/csc folder run the command below pull the node packages.

`npm -i`

2. In the aws-hub-account/ui/csc/src/environments folder copy environment.template.ts to environment.ts
3. Update environment.ts with the values from the output of the cloud formation stack (Api, CognitoClientId, CognitoDomain, CognitoPool, CognitoRedirect, CognitoRegion)
4. Start the website locally using the command below

`ng serve`

5. Below screenshots show the 'Dashboard' and 'Environments' pages.

![Cloud Security Console Dashboard](https://infviz.io/samples/csc2b.PNG)

![Cloud Security Console Environments](https://infviz.io/samples/csc2a.PNG)


