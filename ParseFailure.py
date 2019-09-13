import json

# Written by Dane Fetterman September 2019
# This lambda function runs against the Master Account Env.

def lambda_handler(event, context):
    finalstatusoutput = {"Status": "unknnown"}

    myevent = json.dumps(event)
    myevent = json.loads(myevent)

    #Validate input params
    try:
        Status = myevent['Status']
    except:
        print('No status param found')
        Status = 0
    try:
        Message = myevent['Message']
    except:
        print('No message param found')
        Message = 0
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

    finalstatusoutput = {"Status": Status, "Message": Message, "MasterDetectorId": MasterDetectorId, "MemberId": MemberId, "Email": Email, "MemberDetectorId": MemberDetectorId}
    return finalstatusoutput