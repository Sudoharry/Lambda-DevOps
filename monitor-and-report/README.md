# Project: AWS Lambda function to monitor and report on all AWS resources 


## Purpose: The Lambda function will gather details about AWS resources, monitor their status, and generate a report.

## Key Features:
 - Query AWS services like EC2, S3, RDS, etc.
 - Monitor the status (e.g., usage, uptime, health).
 - Generate and send a consolidated report (e.g., via email using Amazon SES).


## Implementation Steps

1. Prerequisites
 - Ensure the AWS Lambda execution role has permissions for all required AWS services (e.g., ec2:DescribeInstances, s3:ListBuckets, etc.).
 - Use the AWS SDK (boto3) in Python for querying services.

2. Python Lambda Function
 - Get code at resources.py a Python Lambda function to gather resource details and send a report: 

3. IAM Role Permissions
  Attach the following permissions to your Lambda execution role:

 - ec2:DescribeInstances
 - s3:ListBuckets
 - rds:DescribeDBInstances
 - ses:SendEmail

4. Deployment Steps
    1. Create a Lambda Function:
    - Go to the AWS Lambda Console.
    - Create a new function and choose Python as the runtime.
    - Paste the function code into the editor.
      
    2.Set Environment Variables (Optional):
    - Configure the sender and recipient email addresses using environment variables. 
    3. Test the Function:
    - Trigger the function manually to test resource monitoring and email reporting.
    4. Schedule Monitoring:
    - Use an Amazon CloudWatch Events rule to trigger the Lambda function periodically (e.g., daily).
---
 5. Output Example
   - Email Report: 
```
      Subject: AWS Resource Report - 2025-01-17 10:00:00

{
    "EC2 Instances": [
        {
            "InstanceId": "i-1234567890abcdef0",
            "State": "running",
            "Type": "t2.micro",
            "LaunchTime": "2025-01-16 12:00:00"
        }
    ],
    "S3 Buckets": [
        {
            "Name": "my-bucket",
            "CreationDate": "2024-12-01 08:00:00"
        }
    ],
    "RDS Instances": [
        {
            "DBInstanceIdentifier": "my-database",
            "Status": "available",
            "Engine": "mysql",
            "InstanceCreateTime": "2024-11-30 14:00:00"
        }
    ]
}
```
