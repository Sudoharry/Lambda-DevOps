## 1) Import and libraries

```
import boto3
import datetime
import logging
import os
```

- boto3: AWS SDK for python. It allows interaction with AWS services like EC2, S3, CloudWatch and SES

- datetime: Provides classes for manipulating the dates and times. It's used to handle timestamps, calculate the age of EC2 instances and S3 buckets, and set timeframe for CloudWatch metrics.

- logging: Used for logging runtime information (like task status, error, etc)

- os: Used to interact with the operating system. Here,it's used to retrieve environment variables


## 2) Logging Setup

 logger  = logging.getLogger()
 logger = setLevel(logging.INFO)

  - logging.getLogger() : Initialize a logger object
  - logger.setLevel(logging.INFO): Sets the logging level to INFO, meaning it will capture the informational messages  annd higher severity messages(like errors) 


## 3)  AWS Client Initialization

```
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
cloutwatch_client = boto3.client('cloudwatch')
ses_client = boto3.client('ses')

```

- boto3.client('service_name') : Creates a client for interacting with AWS Services (EC2, S3, CloudWatch,SES in this case)

   - ec2_client:Interacts with the EC2 (for EC2 instance management)
   - s3_client: Interacts with the S3 (for bucket management)
   - cloudwatch_client: Interacts with CloudWatch (for monitoring EC2 performance)
   - ses_client: Interacts with SES (for sending emails)


## 4) Environment variables for SES

SES_TO_EMAIL: os.environ.get('SES_TO_EMAIL')
SES_FROM_EMAIL:os.environ.get('SES_FRMO_EMAIL')


- os.environ.get(): Retrieves environment variables.In this case, it fetches:
 - SES_TO_EMAIL: The email address used to send notification(must be verified in SES)
 - SES_FROM_EMAIL: The recipient's email address for receiving notifications.


 ## 5) Define Tags for Compliance


```
DEFAULT_TAGS = [
    {"Key": "Owner", "Value": "default-owner"},
    {"Key": "Project", "Value": "default-project"},
    {"Key": "Environment", "Value": "default-environment"},
    {"Key": "Testing", "Value": "default-testing"}
]
```   

- A list of dictionaries that define default tags to be applied to EC2 instances. Each dictionary has a Key (tag name) and a Value (tag value).


## 6) Sending Emails via SES

```
def send_email(subject,body):
   try: 
       response = ses_client.send_email(
        Source=SES_FROM_EMAIL,
        Destination={'ToAddress': [SES_TO_EMAIL]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Text' : {'Data': body}
            }
        }    
       ) 

       logger.info(f"Email sent: {response['MessageId']}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
```

- This function sends an email using SES(send_email) method
- It takes subject and body as parameters to send the email
- If successful,it logs the email messages ID; otherwise, it logs an error message

## 7) Tagging Compliance
```
def enforce_compliance_tags(resource_id, existing_tags):
    existing_keys = {tag['Key'] for tag in existing_tags}
    missing_tags = [tag for tag in DEFAULT_TAGS if tag['Key'] not in existing_keys]
    
    if missing_tags:
        ec2_client.create_tags(Resources=[resource_id], Tags=missing_tags)
        logger.info(f"Applied missing tags {missing_tags} to resource {resource_id}")
        message = f"Tags {missing_tags} were applied to resource {resource_id}."
        send_email("Tagging Compliance Update", message)
    else:
        logger.info(f"Resource {resource_id} already compliant.")
```

- enforce_compliance_tags ensures that EC2 instances have the required tags.
- It compares the existing tags with the DEFAULT_TAGS and applies missing tags using create_tags.
- If missing tags are applied, an email is sent with the update.

## 8) Auto-Tagging EC2 Instances

```
def auto_tag_resources():
    response = ec2_client.describe_instances()
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            tags = instance.get('Tags', [])
            enforce_compliance_tags(instance_id, tags)
```

- auto_tag_resources retrieves all EC2 instances and checks their tags.
- If any instance is missing the required tags, it calls enforce_compliance_tags to apply them.

## 9 )  Scheduled Cleanup Tasks

```
def scheduled_cleanup():
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

    response = ec2_client.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
    for volume in response['Volumes']:
        volume_id = volume['VolumeId']
        ec2_client.delete_volume(VolumeId=volume_id)
        logger.info(f"Deleted unused volume {volume_id}")
        message = f"Deleted unused EBS volume {volume_id}."
        send_email("Scheduled Cleanup Update", message)

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

```

- This function performs cleanup tasks:
  - Terminates EC2 instances that are stopped for more than 7 days.
  - Deletes unused EBS volumes.
  - Deletes old S3 buckets (older than 30 days).
- Each task sends an email notification.

## 10)  Dynamic Scaling

```
def dynamic_scaling():
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

```

- This function monitors CPU utilization for a specific EC2 instance.
- It fetches CPU metrics from CloudWatch and checks if the average CPU utilization exceeds 80%. If it does, it sends an email and logs the event.

## 11) Lambda Handler

```
def lambda_handler(event, context):
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

```

- The lambda_handler function is the entry point for the Lambda function.
- It orchestrates the entire workflow by calling auto_tag_resources, scheduled_cleanup, and dynamic_scaling.
- After completing the tasks, it logs a success message and sends a final email notification.
- The function returns a 200 HTTP status code, indicating the tasks were successfully executed.