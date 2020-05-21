import json
import boto3
#from io import BytesIO
from io import StringIO
from gzip import GzipFile
import re


print('Loading function')

s3_client = boto3.client('s3')
kinesis_client = boto3.client('kinesis')
# This is the prod stream.
# stream_name = "p8t-incoming-dynamodb-dataplane-audit"
# This is the current dev stream.
stream_name = "dynamo-filtered-output"

def send_event_kinesis(data):
    response = kinesis_client.put_record(
        StreamName=stream_name,
        Data=data,
        # This should actually be unique to shard correctly.
        PartitionKey='PartitionKey'
    )
    return response['ResponseMetadata']['HTTPStatusCode'] == 200

def lambda_handler(event, context):
    bucket_name=event['Records'][0]['s3']['bucket']['name']
    key_name=event['Records'][0]['s3']['object']['key']

    if not "CloudTrail-Digest" in key_name:
        obj = s3.get_object(Bucket=bucket_name,Key=key_name)
        compressed = StringIO(obj['Body'].read())
        decompressed = gzip.GzipFile(fileobj=compressed,mode='rb')
        extracted = json.loads(decompressed.read())

        combined_events = []

        # Look for actions done by a human user.
        for record in extracted['Records']:
            if re.search("^.*@segment.com", record["userIdentity"]["principalId"]):
                print(entry)
                combined_events.append(entry)
                
        # Send matching events to p8t.
        if send_event_kinesis(combined_events):
            print("data sent to kinesis: {}".format(combined_events))
        else:
            print("Error sending event to kinesis {}".format(combined_events))
