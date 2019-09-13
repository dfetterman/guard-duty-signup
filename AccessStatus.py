import boto3
import botocore
from botocore.exceptions import ClientError, ParamValidationError
import json
import os

# Written by Dane Fetterman September 2019
# This lambda function runs against the Master Account Env.


env=os.environ['env']
memberRoleName=os.environ['memberRoleName'] #ex. CrossAccountManageGuardDutyRole"


def fn_get_cross_account_role_creds(RoleArn):
    try:
        sts_connection = boto3.client('sts')
        acct_b = sts_connection.assume_role(
            RoleArn = RoleArn,
            RoleSessionName="cross_acct_lambda"
        )
        ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
        SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
        SESSION_TOKEN = acct_b['Credentials']['SessionToken']
        output = [ACCESS_KEY, SECRET_KEY, SESSION_TOKEN]
        return output
    except ClientError as e:
        print("Unexpected error: %s" % e) 
        return 'AccessDenied'


def lambda_handler(event, context):

    myevent = json.dumps(event)
    myevent = json.loads(myevent)

    #Validate input params
    try:
        MasterDetectorId = myevent['MasterDetectorId']
    except:
        print('No MasterDetectorId param found')
        MasterDetectorId = 0
    try:
        MemberId = myevent['MemberId']
    except:
        print('No MemberId param found')
        MemberId = 0
    try:
        Email = myevent['Email']
    except:
        print('No Email param found')
        Email = 0
    #I only need MasterDetectorId, MemberId, and Email at this point
    if MasterDetectorId == 0 or MemberId == 0 or Email == 0:
        finalstatusoutput = {"Status": "failure", "Message": "A parameter is missing", "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email}
        return finalstatusoutput


    RoleArn="arn:aws:iam::{}:role/{}".format(MemberId, memberRoleName)
    print('The target cross account roleARN:', RoleArn)
    #get aws_access_key_id, aws_secret_access_key, and aws_session_token as an array from target cross AWS account.
    cross_account_role_creds=fn_get_cross_account_role_creds(RoleArn) 
    if cross_account_role_creds == 'Error' or cross_account_role_creds == 'AccessDenied':
        finalstatusoutput = {"Status": "failure", "Message": "Cannot get access to target account (MemberId)"}
        print(finalstatusoutput)
        return finalstatusoutput
    else:
        finalstatusoutput = {"Status": "success", "Message": "Member created in master account", "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email}
        print(finalstatusoutput)
        return finalstatusoutput