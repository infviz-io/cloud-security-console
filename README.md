# Cloud Security Console (CSC)
> NOTE : This is built mainly for demostration purposes. Feel free to download and see how you can stitch together cloud native security tool findings into a custom layout.
## Overview
The Cloud Security Console (CSC) aggregates AWS security hub & Azure security center into a single console, built in angular. The main advantage of using this console is that:
* Provides visbility across both AWS and Azure.
* You can workaround the AWS Security Hub single master limitation within AWS security hub console.
* You can easily grant access to security findings without having access to the AWS console or Azure console.
* You can customise it with anything else you want.
* All security information is keep you accounts you control.

This was built for mainly demostration purposes and therefore has some limitations we compared to the native AWS security hub & Azure security cetner. These include:
* It only shows AWS Security Hub findings
* It collects Azure assessments and alert events
* It is a read only console
* Instructions at the moment are to run the website locally using 'ng serve'

## Architecture
![Cloud Security Console Architecture](https://infviz.io/samples/csc3.png)

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
### CSC Hub AWS Account
This is the account which will store all the data collected. Steps to setup:

1. Run the command below to setup a deployment bucket

`aws s3 mb s3://(bucketname) --region (region) --profile (aws profile)`

2. In the aws-hub-account folder run the command below to package sam deployment

`sam package --template-file .template.yaml --output-template-file package.yaml --s3-bucket (bucketname) --region (region)`

3. In the aws-hub-account folder run the command below to deploy the configuation. If you not have azure credentials to can run without the parameter-overrides

`sam deploy --template-file package.yaml --stack-name (existing stackname) --region (region) --capabilities CAPABILITY_IAM --parameter-overrides AzureTenant=(tenant) AzureClientId=(clientid) AzureSecret=(secret)`

4. At the end of the deployment collect the output parameters.
* Api
* CognitoClientId
* CognitoDomain
* CognitoPool
* CognitoRedirect
* CognitoRegion

### Angular UI
This will build all the files local on your pc so you can run the website locally. If you want to host on the server you will need to ng build and setup your own hosting solution.
1. In the aws-hub-account/ui/csc folder run the command below pull the node packages.

`npm -i`

2. In the aws-hub-account/ui/csc/src/environments folder copy environment.template.ts to environment.ts
3. Update environment.ts with the values from the output of the cloud formation stack (Api, CognitoClientId, CognitoDomain, CognitoPool, CognitoRedirect, CognitoRegion)
4. Start the website locally using the command below

`ng serve`

5. Below screenshots show the 'Dashboard' and 'Environments' pages.

![Cloud Security Console Dashboard](https://infviz.io/samples/csc1.png)

![Cloud Security Console Environments](https://infviz.io/samples/csc2.png)


