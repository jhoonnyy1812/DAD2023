import json
import boto3

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def s3():
    return boto3.resource(
        service_name="s3",
        region_name="us-east-2",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def lambda_handler(event, context):
    document = event["queryStringParameters"]["document"]
    s3().Object("mybycketdad", "{0}.jpeg".format(document)).delete()

    return {
        "statusCode": 200,
        "body": json.dumps("Deleted document for {0}!".format(document)),
    }
