# Guard-Duty-Signup

Guard duty signup is a handful of easily deployed python scripts to enroll a member account in [AWS Guard Duty](https://aws.amazon.com/guardduty/) on a master account. The scripts run as Lambda functions, kicked off by a Step Function that lives behind API Gateway. So, with a single API command, you can enroll a new member AWS account into Guard Duty on a master account.

Why: AWS Account sprawl is a major issue in many organziations. By joining member AWS accounts to a master AWS account's GuardDuty, information about multiple accounts can be aggregated into a single pane of glass.

## Architecture

SEE DIAGRAM

## Requirements

#### Software

[Serverless Framework](https://serverless.com/) is used to deploy. It must be installed on the workstation used to deploy to AWS.

Tested using the following versions:

Serverless Framework Core: 1.51.0
Plugin: 1.3.11
SDK: 2.1.0

aws-cli/1.15.49 Darwin/15.6.0 botocore/1.10.48

#### Configuration

Guard Duty must be enabled on the Master AWS account. You will need the Guard Duty detectorId that you want to associated a Member AWS account with. Guard duty does not need to be enabled on a member account.

A role called "CrossAccountManageGuardDutyRole" must exist on the member account with permissions that permit the master account to assume the role and allow the role to perform guardduty actions. ex. guardduty:\*
While it's assumed that you will create a cloud formation template that the owner of the member account will run in order to grant the master account access, an example of what the permissions look like can be fore in ./memberaccountexample in this project.

## Installation

With AWS CLI configured and using credentials for the master account:

```
serverless deploy --stage dev
```

## Usage

MasterDetectorId - The Guard Duty DetectorId on your Master Account
MemberId - The AWS account number of the member account
Email - The E-mail address associated with the AWS account number of the member account.

```
curl -H "x-api-key: r2wu9P2RnNrSwTv8K8hj54RA8sbGbg" https://1lj82agbb.execute-api.us-east-1.amazonaws.com/dev/guarddutysignup/MasterDetectorId/bab350a4691f29910b874fb1f33459c9/MemberId/123456789123/Email/bob@bobsmith.com
```

## Author

Created by Dane Fetterman in Philadelphia in September 2019.

## License

[MIT](https://choosealicense.com/licenses/mit/)
