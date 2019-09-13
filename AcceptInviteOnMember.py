import boto3
import botocore
from botocore.exceptions import ClientError, ParamValidationError
import json
import os

# Written by Dane Fetterman September 2019
# This lambda function runs against the Member Account Env.

env=os.environ['env']
MasterId=os.environ['MasterId'] #AWS Account ID of master account
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


def fn_list_invitations(cross_account_role_creds):
    try:
        # print("create_detector using the followingparams: {}".format (cross_account_role_creds))
        client = boto3.client(
            'guardduty', 
            aws_access_key_id=cross_account_role_creds[0],
            aws_secret_access_key=cross_account_role_creds[1],
            aws_session_token=cross_account_role_creds[2],
        )    
        response = client.list_invitations(
            MaxResults=20
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

def fn_accept_invitation(DetectorId, MasterId, InvitationId, cross_account_role_creds):
    try:
        # print("create_detector using the followingparams: {}".format (cross_account_role_creds))
        client = boto3.client(
            'guardduty', 
            aws_access_key_id=cross_account_role_creds[0],
            aws_secret_access_key=cross_account_role_creds[1],
            aws_session_token=cross_account_role_creds[2],
        )    
        response = client.accept_invitation(
            DetectorId=DetectorId,
            MasterId=MasterId,
            InvitationId=InvitationId
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
    try:
        MemberDetectorId = myevent['MemberDetectorId']
    except:
        print('no MemberDetectorId param found')
        MemberDetectorId = 0
    if MasterDetectorId == 0 or MemberId == 0 or Email == 0 or MemberDetectorId == 0:
        finalstatusoutput = {"Status": "failure", "Message": "A parameter is missing", "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email, "MemberDetectorId": MemberDetectorId}
        return finalstatusoutput



    RoleArn="arn:aws:iam::{}:role/{}".format(MemberId, memberRoleName)
    print('The target cross account roleARN:', RoleArn)
    #get aws_access_key_id, aws_secret_access_key, and aws_session_token as an array from target cross AWS account.
    cross_account_role_creds=fn_get_cross_account_role_creds(RoleArn) 
    if cross_account_role_creds == 'Error' or cross_account_role_creds == 'AccessDenied':
        finalstatusoutput = {"Status": "failure", "Message": "Cannot get access to target account (MemberId)"}
        print(finalstatusoutput)
        return finalstatusoutput


    list_invitations = fn_list_invitations(cross_account_role_creds)
    #Lets pull the invitation ID from the list_invitations function
    invitations = list_invitations['Invitations']
    print(invitations)
    for i in invitations:
        if i['AccountId'] == MasterId: #Only look at invites from Master AWS account
            print('InvitationId:', i['InvitationId'])
            InvitationId = i['InvitationId']


    #Let's accept the invitation using the InvitationId
    accept_invitation = fn_accept_invitation(MemberDetectorId, MasterId, InvitationId, cross_account_role_creds)
    print('Printing accept_invitation output:', accept_invitation)

    finalstatusoutput = {"Status": "success", "Message": "Guard Duty Invite Accepted in member account", "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email, "MemberDetectorId": MemberDetectorId, "InvitationId": InvitationId}        
    return finalstatusoutput    