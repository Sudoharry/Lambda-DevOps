# EBS Snapshot Management and Email Notification

This Python script is designed to manage Amazon EC2 EBS snapshots, automate the deletion of old snapshots, and send email notifications via Amazon SES whenever new snapshots are created.

## Requirements:
- `boto3` library for interacting with AWS services.
- AWS SES for sending emails.
- AWS EC2 for managing EBS snapshots.

## Prerequisites:
1. AWS CLI configured with access to EC2 and SES.
2. Amazon SES email addresses for both sending and receiving emails must be verified.
3. EC2 Instances and EBS Volumes to create snapshots.

## Setup:
1. Install `boto3` if it's not already installed:
   ```bash
   pip install boto3
   ```
2. Replace the placeholders in the script:
   - **`SENDER`**: Your verified SES email address.
   - **`RECIPIENT`**: The recipient's email address.
   - **Region**: Specify your EC2 instance's region as required.

## Script Overview:
- **Create Snapshots**: For each EC2 instance's EBS volume, a snapshot is created.
- **Delete Old Snapshots**: The script ensures that no more than 5 snapshots are kept for each volume, deleting older snapshots.
- **Email Notification**: Once the snapshots are created and old ones are deleted, an email is sent via SES with the details of the created snapshots.

## Script Functions:

### `send_email()`
- Sends an email notification via SES with details of the created snapshots.

### `delete_old_snapshots()`
- Retrieves snapshots for a given volume ID and deletes the older ones if there are more than 5.

### `lambda_handler()`
- The main function that creates snapshots for all EC2 volumes, manages old snapshots, and sends email notifications.

## Example Usage:

```python
import boto3
import datetime

# Initialize clients for EC2 and SES
ec2_client = boto3.client('ec2')
ses_client = boto3.client('ses', region_name='ap-south-1')  # Change to your SES region

# Email details
SENDER = "example-sender@example.com"  # Replace with your verified SES email
RECIPIENT = "example-recipient@example.com"  # Replace with the recipient email address

# Functions for creating snapshots, deleting old snapshots, and sending notifications...
# Refer to the complete script for details.
```

## Steps to Run:
1. Modify the script with your SES and EC2 details.
2. Deploy the script as a Lambda function or run it directly from your environment.
3. The script will create snapshots, delete old ones if necessary, and send an email with the snapshot details.

## Additional Notes:
- **SES Region**: Ensure the region in the `boto3.client()` call for SES matches the region where your SES is verified (e.g., `ap-south-1` for Mumbai).
- **IAM Permissions**: Ensure the IAM role associated with the script has the following permissions:
  - `ec2:DescribeInstances`
  - `ec2:CreateSnapshot`
  - `ec2:DeleteSnapshot`
  - `ses:SendEmail`
