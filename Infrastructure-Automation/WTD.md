# AWS Lambda Infrastructure Automation

The provided code is an AWS Lambda function that automates various infrastructure tasks using AWS services like EC2, S3, CloudWatch, and SES. The Lambda function performs actions such as enforcing tagging compliance, cleaning up unused resources, and dynamically scaling infrastructure based on CloudWatch metrics. Additionally, it sends email notifications for each task performed using Amazon SES.

## Table of Contents
1. [Overview](#overview)
2. [Setup](#setup)
3. [Code Breakdown](#code-breakdown)
    - [Logging and AWS Clients Initialization](#logging-and-aws-clients-initialization)
    - [Environment Variables for SES](#environment-variables-for-ses)
    - [Tagging Compliance](#tagging-compliance)
    - [Auto-Tagging EC2 Instances](#auto-tagging-ec2-instances)
    - [Scheduled Cleanup Tasks](#scheduled-cleanup-tasks)
    - [Dynamic Scaling](#dynamic-scaling)
    - [Lambda Handler](#lambda-handler)
    - [Email Notifications](#email-notifications)
4. [AWS Permissions](#aws-permissions)
5. [Environment Variables](#environment-variables)
6. [Usage](#usage)
7. [Summary](#summary)

## Overview

This AWS Lambda function automates cloud resource management tasks. It interacts with the following AWS services:
- **EC2**: Manages EC2 instances (e.g., auto-tagging, terminating stopped instances).
- **S3**: Deletes unused or old S3 buckets.
- **CloudWatch**: Monitors EC2 instances for CPU utilization and triggers scaling actions.
- **SES**: Sends email notifications about task completion and status updates.

The Lambda function runs these tasks:
1. **Enforces tagging compliance on EC2 instances.**
2. **Cleans up unused resources (EC2 instances, EBS volumes, and S3 buckets).**
3. **Dynamically scales EC2 instances based on CloudWatch metrics.**

## Setup

To set up this Lambda function, follow these steps:

1. **Create an AWS Lambda Function**:
   - Go to the AWS Lambda console and create a new function using the Python runtime.

2. **Set Permissions**:
   - Ensure the Lambda function has the necessary IAM roles and permissions to interact with EC2, S3, CloudWatch, and SES services. You can attach a managed policy like `AmazonEC2FullAccess`, `AmazonS3FullAccess`, `CloudWatchReadOnlyAccess`, and `AmazonSESFullAccess` to the Lambda execution role.

3. **Configure Environment Variables**:
   - Set the following environment variables in the Lambda function:
     - `SES_FROM_EMAIL`: The sender's email address verified in AWS SES.
     - `SES_TO_EMAIL`: The recipient's email address where notifications will be sent.

4. **Deploy the Lambda Function**:
   - Deploy the function and schedule it to run on your desired frequency (e.g., via CloudWatch Events).

## Code Breakdown

### Logging and AWS Clients Initialization

- The code uses the `logging` module to log activities.
- AWS clients are initialized for EC2, S3, CloudWatch, and SES using the `boto3` library, which is the AWS SDK for Python.

### Environment Variables for SES

- The `SES_FROM_EMAIL` and `SES_TO_EMAIL` environment variables are fetched to configure email notifications.
- These email addresses are used in the `send_email` function to send task notifications.

### Tagging Compliance

- A set of **default tags** (`DEFAULT_TAGS`) is defined, which must be applied to EC2 instances for compliance.
- The `enforce_compliance_tags` function ensures that all required tags are present. If tags are missing, they are applied, and an email is sent notifying about the applied tags.

### Auto-Tagging EC2 Instances

- The `auto_tag_resources` function retrieves all EC2 instances and checks their tags.
- If any instance is missing the required tags, the function applies them and sends an email notification.

### Scheduled Cleanup Tasks

1. **Terminating Stopped EC2 Instances**:
   - The `scheduled_cleanup` function checks for stopped EC2 instances that have been idle for more than 7 days and terminates them.
   
2. **Deleting Unused EBS Volumes**:
   - It deletes EBS volumes that are in the `available` state, indicating they are not attached to any EC2 instance.
   
3. **Deleting Old S3 Buckets**:
   - It deletes S3 buckets that are older than 30 days, based on their creation date.

Each cleanup action triggers an email notification to inform about the performed action.

### Dynamic Scaling

- The `dynamic_scaling` function checks the CPU utilization of a specific EC2 instance.
- If CPU utilization exceeds the threshold (80% in this case), it sends an email notification. The scaling logic (e.g., increasing instance size or count) is not fully implemented in the code.

### Lambda Handler

- The `lambda_handler` function is the main entry point. It:
  1. Calls `auto_tag_resources` to enforce tagging compliance.
  2. Runs `scheduled_cleanup` to perform resource cleanup tasks.
  3. Triggers `dynamic_scaling` based on CloudWatch CPU metrics.
  4. Sends a final email notification summarizing all tasks completed.

### Email Notifications

- The `send_email` function is used to send email notifications via SES. 
- Notifications include:
  - Tagging compliance updates.
  - Scheduled cleanup actions (e.g., terminated EC2 instances, deleted EBS volumes, deleted S3 buckets).
  - Dynamic scaling triggers.
  - A final report on the overall execution of the infrastructure automation tasks.

## AWS Permissions

Ensure that the Lambda function has the appropriate IAM permissions to interact with the necessary AWS services. These permissions include:
- **EC2**: `DescribeInstances`, `CreateTags`, `TerminateInstances`, etc.
- **S3**: `ListBuckets`, `DeleteBucket`.
- **CloudWatch**: `GetMetricStatistics` for retrieving CPU utilization metrics.
- **SES**: `SendEmail` for sending email notifications.

## Environment Variables

The following environment variables should be configured in your Lambda function:
- `SES_FROM_EMAIL`: A verified email address in Amazon SES from which emails will be sent.
- `SES_TO_EMAIL`: The recipient email address for receiving notifications.

## Usage

After deploying the Lambda function:
1. **Invoke Lambda manually** (for testing) or set a schedule to run it periodically (e.g., once a day or every week) using CloudWatch Events.
2. Monitor the execution and check your recipient email for notifications on the performed tasks.

## Summary

This Lambda function automates the following infrastructure management tasks:
- **Enforcing tagging compliance on EC2 instances**.
- **Cleaning up unused resources** such as stopped EC2 instances, unattached EBS volumes, and old S3 buckets.
- **Dynamically scaling EC2 instances** based on CloudWatch metrics.
- **Sending email notifications** via SES for every action performed, such as tagging compliance, resource cleanup, and scaling triggers.

By using this Lambda function, you can ensure better resource management, cost optimization, and operational efficiency in your AWS infrastructure.

