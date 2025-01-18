# Lambda function to handle Infrastructure Automation tasks: Auto Tagging Resources, Scheduled Cleanup, and Dynamic Scaling.


## Overview
The Lambda function will:

- Automatically tag newly created resources.
- Clean up unused or orphaned resources.
- Adjust infrastructure dynamically based on metrics.


## Key Features
1) Auto Tagging:

 - Identifies untagged EC2 instances and applies default tags.
 - Ensures proper resource tracking and organization.

2) Scheduled Cleanup:

 - Cleans up stopped EC2 instances older than 7 days.
 - Deletes orphaned EBS volumes and old S3 buckets.

3) Dynamic Scaling:

 - Monitors EC2 instances' CPU utilization.
 - Triggers scaling actions if metrics exceed predefined thresholds.

 
## Setup Instructions
1. Create a Lambda Function:

  - Go to the AWS Lambda Console.
  - Create a new function, selecting Python as the runtime.

2) Permissions: Attach the following policies to your Lambda execution role:

 - ec2:DescribeInstances
 - ec2:CreateTags
 - ec2:TerminateInstances
 - ec2:DescribeVolumes
 - ec2:DeleteVolume
 - s3:ListBuckets
 - s3:DeleteBucket
 - cloudwatch:GetMetricStatistics

3) Deploy the Code:

- Write the code into the Lambda function editor.

4) Test and Schedule:

 - Test the function with a manual trigger.
 - Use Amazon CloudWatch Events to schedule the function (e.g., run daily).
