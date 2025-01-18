# Step-by-Step Guide: Add Trigger Using EventBridge for EBS Snapshot Every 3 Minutes

## Step 1: Create an IAM Role for Lambda

### Go to the IAM Console
- Navigate to the IAM (Identity and Access Management) console: [IAM Console](https://console.aws.amazon.com/iam).

### Create a New Role
1. In the left panel, click **Roles**.
2. Click **Create role**.
3. Select **Lambda** as the trusted entity type.
4. Click **Next: Permissions**.

### Assign Permissions
- Attach the following policies (or create a custom policy for more fine-grained permissions):
  - `AmazonEC2FullAccess` (for EC2 snapshot creation)
  - `AmazonSESFullAccess` (for sending email notifications via SES)
  - `CloudWatchLogsFullAccess` (for logging in CloudWatch)
- Optionally, limit permissions to only required actions for better security.

### Review and Create
1. Give the role a name, such as `EBS-Snapshot-Creation-Role`.
2. Review the settings and click **Create role**.

---

## Step 2: Create a Lambda Function

### Go to the Lambda Console
- Navigate to the [AWS Lambda Console](https://console.aws.amazon.com/lambda).

### Create a New Lambda Function
1. Click **Create function**.
2. Choose **Author from scratch**.
3. Enter the function name (e.g., `CreateEBSnapshot`).
4. Select the runtime (e.g., `Python 3.x`).
5. Under Permissions, choose **Use an existing role** and select the role you created in Step 1 (`EBS-Snapshot-Creation-Role`).
6. Click **Create function**.
---
![Create-a-function](https://github.com/user-attachments/assets/4641887f-2603-4394-82a8-6573d63d2c06)
---

### Add Code to Lambda
- Add your code for creating the EBS snapshots (similar to the script you developed).
- Edit the code directly in the console or upload it as a `.zip` file if preferred.

### Test Lambda Function
1. Click **Test** and configure a test event.
2. Ensure the Lambda function works as expected by taking snapshots of your EC2 volumes.
---
![manual-test](https://github.com/user-attachments/assets/96e57642-dfef-407c-a719-cc6e43d3b81f)

---

## Step 3: Create an EventBridge Rule

### Go to the EventBridge Console
- Navigate to the [EventBridge Console](https://console.aws.amazon.com/events).

### Create a New Rule
1. In the left sidebar, click **Rules**.
2. Click **Create rule**.

### Set Up Rule Configuration
1. **Name**: Provide a name (e.g., `EBS-Snapshot-Trigger`).
2. **Description**: (Optional) Add a description (e.g., `Trigger Lambda for EBS snapshot every 3 minutes`).
3. **Event Source**: Choose **Schedule**.
4. **Define pattern**:
   - Select **Fixed rate of** and set the interval to `3 minutes`.
   - Alternatively, use a cron expression for more flexibility. For 3-minute intervals, use:
     ```cron
     cron(0/3 * * * ? *)
     ```
---
![Create-a-EBSSnapshot-](https://github.com/user-attachments/assets/2c48e18b-86cb-458c-b8df-b1fb59a54429)

---
### Select Target
1. Under **Select Targets**, choose **Lambda function**.
2. **Function**: Select the Lambda function you created earlier (`CreateEBSnapshot`).

### Create a Permission
- Check the box to **Create a new role for this specific resource** if prompted. This ensures EventBridge can invoke the Lambda function.

### Configure the Rule
- Ensure **State** is set to **Enabled**.
- Click **Create**.

---

## Step 4: Test the Trigger

### Check EventBridge Rule
- Verify that the EventBridge rule is active.

### Check Lambda Execution
1. Go to the Lambda console and check the **Monitoring** tab.
2. Verify that the Lambda function is triggered every 3 minutes.
3. Check **CloudWatch Logs** for any issues or errors.

### Verify Snapshots
- In the EC2 console, navigate to **Snapshots** and confirm that snapshots are being created for your EC2 volumes.

---
![last-5-snapshot](https://github.com/user-attachments/assets/e18bc10f-da88-46a9-aac5-ecd32926496b)

---

### Check Email for verification
---
![email-recevied](https://github.com/user-attachments/assets/8ea7fdce-f9bb-408a-9206-3a1d530b7b29)

---

## Step 5: Monitor and Clean Up

### Monitor Execution
- Use **CloudWatch Logs** to monitor the Lambda execution and troubleshoot any issues.
- Ensure that errors are logged appropriately.

### Clean Up
1. If testing is complete, disable the EventBridge rule.
2. Optionally, delete the Lambda function, EventBridge rule, and IAM role if no longer needed.

---

## Conclusion

You have successfully scheduled the creation of EBS snapshots every 3 minutes using AWS EventBridge and Lambda. This automation ensures that your EC2 volumes are regularly snapshotted without manual intervention. Use the provided steps to monitor and manage the process efficiently.
