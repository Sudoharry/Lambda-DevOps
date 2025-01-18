import boto3
import datetime

# Initialize clients for EC2 and SES
ec2_client = boto3.client('ec2')
ses_client = boto3.client('ses', region_name='ap-south-1')  # Change to your SES region

# Email details
SENDER = "barotharendra0@gmail.com"  # Replace with your verified SES email
RECIPIENT = "harendrabarot19@gmail.com"  # Replace with the recipient email address
SUBJECT = "EBS Snapshot Created"
CHARSET = "UTF-8"

def send_email(snapshot_details):
    # Email body
    BODY_TEXT = f"The following EBS snapshots were created:\n\n{snapshot_details}"
    
    # Send the email via SES
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def delete_old_snapshots(volume_id):
    # List snapshots for the volume
    snapshots = ec2_client.describe_snapshots(Filters=[
        {'Name': 'volume-id', 'Values': [volume_id]},
        {'Name': 'status', 'Values': ['completed']}
    ])['Snapshots']
    
    # Check if there are more than 5 snapshots
    if len(snapshots) > 4:
        # Sort snapshots by creation time (newest first)
        snapshots.sort(key=lambda x: x['StartTime'], reverse=True)
        
        # Log sorted snapshot details
        print(f"Snapshots for volume {volume_id}:")
        for snapshot in snapshots:
            print(f"Snapshot ID: {snapshot['SnapshotId']}, Created: {snapshot['StartTime']}")
        
        # Keep the latest 5 snapshots and delete the rest
        snapshots_to_delete = snapshots[4:]
        
        # Log which snapshots will be deleted
        print(f"Snapshots to delete (older than latest 5):")
        for snapshot in snapshots_to_delete:
            print(f"Deleting snapshot: {snapshot['SnapshotId']}")
        
        for snapshot in snapshots_to_delete:
            snapshot_id = snapshot['SnapshotId']
            try:
                # Delete the old snapshot
                ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted snapshot: {snapshot_id}")
            except Exception as e:
                print(f"Error deleting snapshot {snapshot_id}: {str(e)}")
    else:
        print(f"Not enough snapshots to delete. Keeping all {len(snapshots)} snapshots for volume {volume_id}.")

def lambda_handler(event, context):
    snapshot_details = []
    
    # Get all EC2 instances
    instances = ec2_client.describe_instances()
    
    # Loop through all instances to find EBS volumes
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            for block_device in instance['BlockDeviceMappings']:
                volume_id = block_device['Ebs']['VolumeId']
                
                # Create a snapshot for each volume
                snapshot_description = f"Snapshot for {volume_id} created at {datetime.datetime.utcnow()}"
                
                try:
                    # Create the snapshot
                    snapshot = ec2_client.create_snapshot(
                        VolumeId=volume_id,
                        Description=snapshot_description
                    )
                    snapshot_details.append(f"Created snapshot: {snapshot['SnapshotId']} for volume {volume_id}")
                    print(f"Created snapshot: {snapshot['SnapshotId']} for volume {volume_id}")
                    
                    # Call delete_old_snapshots to manage lifecycle
                    delete_old_snapshots(volume_id)
                
                except Exception as e:
                    print(f"Error creating snapshot for volume {volume_id}: {str(e)}")
    
    # Send an email with snapshot details
    if snapshot_details:
        send_email("\n".join(snapshot_details))
    
    return {
        'statusCode': 200,
        'body': 'Snapshots created successfully, email sent, and old snapshots deleted'
    }
