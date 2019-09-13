import boto3
import botocore
from botocore.exceptions import ClientError, ParamValidationError
import json
import os

# Written by Dane Fetterman September 2019
# This lambda function runs against the Member Account Env.

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



def fn_enable_guard_duty(cross_account_role_creds):
    try:
        # print("create_detector using the followingparams: {}".format (cross_account_role_creds))
        client = boto3.client(
            'guardduty', 
            aws_access_key_id=cross_account_role_creds[0],
            aws_secret_access_key=cross_account_role_creds[1],
            aws_session_token=cross_account_role_creds[2],
        )    
        response = client.create_detector(
            Enable=True,
            # FindingPublishingFrequency='FIFTEEN_MINUTES',
            # Tags={
                # 'mytag': 'mytagvalue-createdinLambda'
            # }
        )
        print(response)
        return response
    except ClientError as e:
        print('Running create_detector caught an error, printing error before processing it:', e)
        # print("create_detector used the following params: {}".format (cross_account_role_creds))
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("Ran into an access denied error")
            output = ['AccessDenied', e]
            return output
        elif 'InternalServerErrorException' == e.__class__.__name__:
            print('Error is a InternalServerErrorException')
            output = ['InternalServerErrorException', e]
            return output
        elif e.response['Error']['Code'] == 'BadRequestException':
            print("Potentially the detector already exists")
            output = ['BadRequestException', e]
            return output            
        else:
            print('Other type of error')
            output = ['error', e]
            return output

def fn_list_detectors(cross_account_role_creds):
    try:
        # print("create_detector using the followingparams: {}".format (cross_account_role_creds))
        client = boto3.client(
            'guardduty', 
            aws_access_key_id=cross_account_role_creds[0],
            aws_secret_access_key=cross_account_role_creds[1],
            aws_session_token=cross_account_role_creds[2],
        )    
        response = client.list_detectors(
            MaxResults=30
        )
        print(response)
        return response
    except ClientError as e:
        print('Running create_detector caught an error, printing error before processing it:', e)
        # print("create_detector used the following params: {}".format (cross_account_role_creds))
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("Ran into an access denied error")
            output = ['AccessDenied', e]
            return output
        elif 'InternalServerErrorException' == e.__class__.__name__:
            print('Error is a InternalServerErrorException')
            output = ['InternalServerErrorException', e]
            return output
        elif e.response['Error']['Code'] == 'BadRequestException':
            print("Potentially the detector already exists")
            output = ['BadRequestException', e]
            return output            
        else:
            print('Other type of error')
            output = ['error', e]
            return output

def lambda_handler(event, context):
    

    finalstatusoutput = {"Status": "unknnown"}

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



    enable_guard_duty = fn_enable_guard_duty(cross_account_role_creds)

    #if it's an error, type will be blah
    print(type(enable_guard_duty))
    print(enable_guard_duty)



    #need to return member detector id

    # Errors are outputted formatted as a list
    if type(enable_guard_duty) == list:
        print('this is a list')
        if enable_guard_duty[0] == 'AccessDenied':
            finalstatusoutput = {"Status": "failure", "Message": "Cannot run CreateDetector operation, probably due to IAM permissions", "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email}
        if enable_guard_duty[0] == 'InternalServerErrorException' or enable_guard_duty[0] == 'error':
            finalstatusoutput = {"Status": "failure", "Message": str(enable_guard_duty[1]), "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email}
        if enable_guard_duty[0] == 'BadRequestException': #We're assuming this failure is due to a DetectorId already existing on the member
            list_detectors = fn_list_detectors(cross_account_role_creds) #Lets get a list of existing DetectorIds on the member
            DetectorIds = list_detectors['DetectorIds']
            MemberDetectorId = DetectorIds[0]
            finalstatusoutput = {"Status": "success", "Message": str(enable_guard_duty[1]), "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email, "MemberDetectorId": MemberDetectorId}
    else: # success is typically NOT formatted as a list
        print('printing output of enable_guard_duty')
        MemberDetectorId = enable_guard_duty['DetectorId']
        finalstatusoutput = {"Status": "success", "Message": "Guard Duty Enabled in member account", "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email, "MemberDetectorId": MemberDetectorId}
        
    return finalstatusoutput    