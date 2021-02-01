import json
import boto3
import time
import os

ACTIVITY_NAME = os.environ['ACTIVITY_NAME']

sfn = boto3.client('stepfunctions')
sts = boto3.client('sts')
session =  boto3.session.Session()

AccountID = sts.get_caller_identity()['Account']
Region = session.region_name



def lambda_handler(event, context):
    print(event)
    
    while True:
        response = sfn.get_activity_task(
            activityArn='arn:aws:states:{region}:{accountid}:activity:{activity}'.format(region = Region, accountid = AccountID, activity=ACTIVITY_NAME),
            workerName='lambda_activity'
        )
        
        token = response['taskToken'] 
        if token != None:
            try:
                input = json.loads(response['input'])
                print(input['Comment'])
                print(response['taskToken'])
                response = sfn.send_task_success(
                    taskToken=token,
                    output='{"message": "You have sent me <' + input['Comment'] + '>"}'
                )
                return input
            except Exception as e:
                response = sfn.send_task_failure(
                    taskToken=token,
                    error=e.args,
                    cause=e.args
                )
                
        response = sfn.send_task_heartbeat(
            taskToken=token
        )
        time.sleep(1)
    
    
    return "error"


