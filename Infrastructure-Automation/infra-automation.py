import boto3
import datetime
import logging
import os

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
cloudwatch_client = boto3.client('cloudwatch')
ses_client = boto3.client('ses')

# Environment variables for SES
SES_FROM_EMAIL = os.environ.get('SES_FROM_EMAIL')  # Verified email in SES
SES_TO_EMAIL = os.environ.get('SES_TO_EMAIL')      # Recipient email address

# Define tags to be applied
DEFAULT_TAGS = [
    {"Key": "Owner", "Value": "default-owner"},
    {"Key": "Project", "Value": "default-project"},
    {"Key": "Environment", "Value": "default-environment"},
    {"Key": "Testing", "Value": "default-testing"}
]

def send_email(subject, body):
    """Send an email via SES."""
    try:
        response = ses_client.send_email(
            Source=SES_FROM_EMAIL,
            Destination={'ToAddresses': [SES_TO_EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body}
                }
            }
        )
        logger.info(f"Email sent: {response['MessageId']}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")

def enforce_compliance_tags(resource_id, existing_tags):
    """Ensure all required tags are applied to the resource."""
    existing_keys = {tag['Key'] for tag in existing_tags}
    missing_tags = [tag for tag in DEFAULT_TAGS if tag['Key'] not in existing_keys]
    
    if missing_tags:
        ec2_client.create_tags(Resources=[resource_id], Tags=missing_tags)
        logger.info(f"Applied missing tags {missing_tags} to resource {resource_id}")
        message = f"Tags {missing_tags} were applied to resource {resource_id}."
        send_email("Tagging Compliance Update", message)
    else:
        logger.info(f"Resource {resource_id} already compliant.")

def auto_tag_resources():
    """Automatically tag EC2 instances based on compliance standards."""
    response = ec2_client.describe_instances()
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            tags = instance.get('Tags', [])
            
            # Enforce compliance tags
            enforce_compliance_tags(instance_id, tags)

def scheduled_cleanup():
    """Clean up unused EC2 and EBS resources."""
    # Terminate stopped EC2 instances older than 7 days
    response = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            launch_time = instance['LaunchTime']
            age = (datetime.datetime.now(datetime.timezone.utc) - launch_time).days
            if age > 7:
                instance_id = instance['InstanceId']
                ec2_client.terminate_instances(InstanceIds=[instance_id])
                logger.info(f"Terminated instance {instance_id}")
                message = f"Terminated stopped instance {instance_id} older than 7 days."
                send_email("Scheduled Cleanup Update", message)

    # Delete unused EBS volumes
    response = ec2_client.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
    for volume in response['Volumes']:
        volume_id = volume['VolumeId']
        ec2_client.delete_volume(VolumeId=volume_id)
        logger.info(f"Deleted unused volume {volume_id}")
        message = f"Deleted unused EBS volume {volume_id}."
        send_email("Scheduled Cleanup Update", message)

    # Delete old S3 buckets (older than 30 days)
    response = s3_client.list_buckets()
    for bucket in response['Buckets']:
        creation_date = bucket['CreationDate']
        age = (datetime.datetime.now(datetime.timezone.utc) - creation_date).days
        if age > 30:
            bucket_name = bucket['Name']
            try:
                s3_client.delete_bucket(Bucket=bucket_name)
                logger.info(f"Deleted bucket {bucket_name}")
                message = f"Deleted old S3 bucket {bucket_name} older than 30 days."
                send_email("Scheduled Cleanup Update", message)
            except Exception as e:
                logger.error(f"Failed to delete bucket {bucket_name}: {str(e)}")

def dynamic_scaling():
    """Adjust infrastructure dynamically based on metrics."""
    # Check CloudWatch metrics for high CPU utilization
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': 'your-instance-id'}],
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
        EndTime=datetime.datetime.utcnow(),
        Period=300,
        Statistics=['Average']
    )

    if response['Datapoints']:
        avg_cpu = response['Datapoints'][0]['Average']
        if avg_cpu > 80:  # Example threshold
            logger.info("CPU utilization is high. Triggering scaling...")
            message = f"High CPU utilization detected (Average: {avg_cpu}%). Scaling actions initiated."
            send_email("Dynamic Scaling Triggered", message)
            # Perform scaling action (e.g., increase instance count or size)

def lambda_handler(event, context):
    """Main Lambda handler function."""
    logger.info("Starting Infrastructure Automation tasks...")
    auto_tag_resources()
    scheduled_cleanup()
    dynamic_scaling()
    logger.info("Infrastructure Automation tasks completed successfully!")
    message = "All infrastructure automation tasks have been completed successfully."
    send_email("Infrastructure Automation Report", message)
    return {
        'statusCode': 200,
        'body': "Infrastructure Automation tasks completed successfully!"
    }
