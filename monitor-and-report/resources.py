import boto3
import json
from datetime import datetime

# Initialize AWS SDK clients
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
rds_client = boto3.client('rds')
ses_client = boto3.client('ses')

# Email settings
SENDER_EMAIL = "harendrabarot19@gmail.com"
RECIPIENT_EMAIL = "hrshsonii666@gmail.com"
AWS_REGION = "ap-south-1"

def get_ec2_instances():
    """Get details of all EC2 instances."""
    response = ec2_client.describe_instances()
    instances = []
    for reservation in response.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            instances.append({
                'InstanceId': instance['InstanceId'],
                'State': instance['State']['Name'],
                'Type': instance['InstanceType'],
                'LaunchTime': instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S'),
            })
    return instances

def get_s3_buckets():
    """Get details of all S3 buckets."""
    response = s3_client.list_buckets()
    buckets = [{'Name': bucket['Name'], 'CreationDate': bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S')} for bucket in response.get('Buckets', [])]
    return buckets

def get_rds_instances():
    """Get details of all RDS instances."""
    response = rds_client.describe_db_instances()
    instances = []
    for db_instance in response.get('DBInstances', []):
        instances.append({
            'DBInstanceIdentifier': db_instance['DBInstanceIdentifier'],
            'Status': db_instance['DBInstanceStatus'],
            'Engine': db_instance['Engine'],
            'InstanceCreateTime': db_instance['InstanceCreateTime'].strftime('%Y-%m-%d %H:%M:%S'),
        })
    return instances

def send_email(subject, body):
    """Send an email using Amazon SES."""
    ses_client.send_email(
        Source=SENDER_EMAIL,
        Destination={'ToAddresses': [RECIPIENT_EMAIL]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )

def lambda_handler(event, context):
    # Gather resource details
    ec2_instances = get_ec2_instances()
    s3_buckets = get_s3_buckets()
    rds_instances = get_rds_instances()
    
    # Prepare the report
    report = {
        'EC2 Instances': ec2_instances,
        'S3 Buckets': s3_buckets,
        'RDS Instances': rds_instances,
    }
    report_json = json.dumps(report, indent=4)
    
    # Send the report via email
    subject = f"AWS Resource Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    send_email(subject, report_json)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Resource monitoring and report sent successfully!')
    }
