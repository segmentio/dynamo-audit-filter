import json
import boto3
from io import BytesIO
from gzip import GzipFile
import re


print('Loading function')

s3_client = boto3.client('s3')
kinesis_client = boto3.client('kinesis')

stream_name = "p8t-incoming-dynamodb-dataplane-audit"
# Dev stream name:
# stream_name = "dynamo-filtered-output"

def send_event_kinesis(data):
    response = kinesis_client.put_record(
        StreamName=stream_name,
        Data=data,
        PartitionKey='PartitionKey' # TODO: make unique
    )
    return response['ResponseMetadata']['HTTPStatusCode'] == 200

def lambda_handler(event, context):
    bucket_name=event['Records'][0]['s3']['bucket']['name']
    key_name=event['Records'][0]['s3']['object']['key']

    if not "CloudTrail-Digest" in key_name:
        obj = s3_client.get_object(Bucket=bucket_name,Key=key_name)
        bytestream = BytesIO(obj['Body'].read())
        decompressed = GzipFile(None, 'rb', fileobj=bytestream).read().decode('utf-8')
        extracted = json.loads(decompressed)

        # Look for actions done by a human user.
        for record in extracted['Records']:
            if re.search("^.*@segment.com", record["userIdentity"]["principalId"]):
                print(record)
                if send_event_kinesis(bytes(json.dumps(record), 'UTF-8')):
                    print("data sent to kinesis: {}".format(record))
                else:
                    print("Error sending event to kinesis {}".format(record))
