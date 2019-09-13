import boto3
import botocore
from botocore.exceptions import ClientError, ParamValidationError
import json
import os

# Written by Dane Fetterman September 2019
# This lambda function runs against the Master Account Env.

env=os.environ['env']


# def response(message, status_code):
#     return {
#         'statusCode': str(status_code),
#         'body': json.dumps(message),
#         'headers': {
#             'Content-Type': 'application/json',
#             'Access-Control-Allow-Origin': '*',
#             'Access-Control-Allow-Credentials': 'true'
#             },
#         }


def fn_create_members(MasterDetectorId, MemberId, Email):
    try:
        print("create_members using the following params: {} {} {}".format (MasterDetectorId, MemberId, Email))
        client = boto3.client('guardduty')
        response = client.create_members(
            DetectorId=MasterDetectorId,
            AccountDetails=[
                {
                    'AccountId': MemberId,
                    'Email': Email
                },
            ]
        )
        print(response)
        return response
    except ClientError as e:
        print('Running create_members caught an error, printing error before processing it:', e)
        print("create_members used the following params: {} {} {}".format (MasterDetectorId, MemberId, Email))
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("Ran into an access denied error")
            output = ['AccessDenied', e]
            return output
        elif 'InternalServerErrorException' == e.__class__.__name__:
            print('Error is a InternalServerErrorException')
            output = ['InternalServerErrorException', e]
            return output
        else:
            print('Other type of error')
            output = ['error', e]
            return output





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



    create_members = fn_create_members(MasterDetectorId, MemberId, Email)
    

    try:
        if create_members[0] == 'AccessDenied':
            finalstatusoutput = {"Status": "failure", "Message": "Cannot run CreateMembers operation, probably due to IAM permissions however if you submitted an incorrect DetectorId that would also throw an access denied error even if IAM permissions are correct", "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email}
            return finalstatusoutput       
        elif create_members[0] == 'InternalServerErrorException' or create_members[0] == 'error':
            finalstatusoutput = {"Status": "failure", "Message": str(create_members[1]), "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email}
            return finalstatusoutput
    except:
        print('printing output of create_members')
        statusoutput = json.dumps(create_members['UnprocessedAccounts'])
        print(statusoutput)
        if statusoutput == '[]':
            print('status output = [], that is usually a success')
            finalstatusoutput = {"Status": "success", "Message": "Member created in master account", "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email}
            return finalstatusoutput
        else:
            finalstatusoutput = {"Status": "failure", "Message": statusoutput, "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email}
            return finalstatusoutput

