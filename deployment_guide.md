# Deployment Guide: Titan LLM Wrapper on AWS EC2

This guide will walk you through deploying the FastAPI-based Titan LLM wrapper on an Amazon EC2 instance using Amazon Bedrock.

---

## Prerequisites
- AWS account with access to Bedrock (Titan model enabled)
- IAM user or EC2 instance role with Bedrock permissions
- EC2 Security Group allowing inbound traffic on port `8000`

---

## Step-by-Step Setup

### 1. Launch EC2 Instance
- **AMI**: Ubuntu 22.04 LTS
- **Instance Type**: `t3.medium` or higher
- **Storage**: 16 GB or more
- **Security Group**:
  - Inbound Rule: TCP port 8000 open to your IP or 0.0.0.0/0 for testing (not recommended long-term)

---

### 2. Connect to EC2
```bash
ssh -i <your-key.pem> ubuntu@<EC2_PUBLIC_IP>
```

---

### 3. Install Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip
pip3 install fastapi uvicorn boto3 python-multipart
```

---

### 4. Create and Upload Files
Upload the following project files to the EC2 instance:
```
main.py
requirements.txt
```

You can use `scp` or copy/paste.

---

### 5. Configure AWS Credentials
If not using an EC2 role, configure manually:
```bash
aws configure
```
Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Region: `us-east-1`

Ensure that the IAM user or instance role has these permissions:
```json
{
  "Effect": "Allow",
  "Action": ["bedrock:*"],
  "Resource": "*"
}
```

---

### 6. Run the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

To run in background:
```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
```

---

### 7. Test the API

#### Generate Prompt:
```bash
curl -X POST http://<EC2_PUBLIC_IP>:8000/generate \
     -F 'prompt=Summarize the concept of entropy'
```

#### View Metrics:
```bash
curl http://<EC2_PUBLIC_IP>:8000/metrics
```

---

## Security Notes
- Do **not** expose port `8000` to the public in production.
- Use an API Gateway + Lambda proxy for production use if needed.
- uvicorn main:app --reload
---


