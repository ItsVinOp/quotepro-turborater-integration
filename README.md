QuotePro to ITC TurboRater Integration


This project implements a Python microservice to process insurance quote data from QuotePro, convert it to ACORD XML, and prepare it for submission to ITC TurboRater's API. The service is deployed on AWS EC2 with a stable Elastic IP, using SQLite for data persistence and Gunicorn for API performance.
Features

Receives JSON quote data pushed from QuotePro to an API endpoint.
Validates input (e.g., VIN, phone) and converts to ACORD v3.4 XML.
Stores quotes in SQLite with status tracking (PENDING, PROCESSED, BOUND).
Configures logging with rotation to /var/log/turborater/integration.log.
Prepares for ITC 2 API integration using OAuth 2.0 authentication (pending credentials).
Deployed on AWS EC2 with secure endpoint configuration.

Technologies

Backend: Python, Gunicorn, SQLite
Cloud: AWS EC2, Elastic IP
Data Formats: JSON, ACORD XML
Tools: Postman, AWS CLI, VS Code, Git
OS: Ubuntu

Prerequisites

Python 3.8+
AWS EC2 instance with Ubuntu
QuotePro API access (push-based)
ITC TurboRater API credentials (client ID, client secret, token/quote endpoints)
Git, pip, and SQLite installed

Setup Instructions

Clone the Repository:
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>


Install Dependencies:
pip install -r requirements.txt

Example requirements.txt:
requests==2.31.0
gunicorn==20.1.0


Configure AWS EC2:

Launch an EC2 instance (Ubuntu, e.g., t2.micro).
Assign an Elastic IP for a static endpoint.
Open ports 22 (SSH) and 8000 (API) in the security group.
SSH into the instance:ssh -i <your-key>.pem ubuntu@<elastic-ip>




Set Up Directories:
sudo mkdir -p /var/log/turborater /var/lib/turborater
sudo chown ubuntu:ubuntu /var/log/turborater /var/lib/turborater
sudo chmod 755 /var/log/turborater /var/lib/turborater


Configure Environment Variables:
sudo nano /etc/environment

Add:
ITC_CLIENT_ID="<your_client_id>"
ITC_CLIENT_SECRET="<your_client_secret>"
ITC_TOKEN_URL="<itc_token_endpoint>"
ITC_API_URL="<itc_quote_endpoint>"

Apply:
source /etc/environment


Deploy Microservice:

Copy files to EC2:scp -i <your-key>.pem quotepro_to_itc_turborater_mock.py requirements.txt ubuntu@<elastic-ip>:/home/ubuntu


Set up systemd service:sudo nano /etc/systemd/system/quotepro.service

Add:[Unit]
Description=QuotePro TurboRater Microservice
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/home/ubuntu/.local/bin/gunicorn -w 4 -b 0.0.0.0:8000 quotepro_to_itc_turborater_mock:application
Restart=always

[Install]
WantedBy=multi-user.target


Enable and start:sudo systemctl daemon-reload
sudo systemctl enable quotepro
sudo systemctl start quotepro





Usage

Endpoint: http://<elastic-ip>:8000/quote
Method: POST
Headers: Content-Type: application/x-www-form-urlencoded
Body:jsonobj={"id":"InsuranceNavy_0016866151","location":{"firstName":"Maria Piedad","lastName":"Tiviano Tiviano","email":"","phone":"-   -","city":"CHICAGO","state":"IL","zipCode":"60651"},"vehicles":[{"year":"1998","makeDescription":"TOYOTA","modelDescription":"CAMRY CE/LE/XLE","vinNumber":"JT2BG22K5W0162187"}],"quote":{"totalAmount":545.0,"policyTerm":"6","qProQuoteNo":"427481","effectiveDate":"2025-05-22T00:00:00"},"drivers":[{"firstName":"MARIA PIEDAD","lastName":"TIVIANO TIVIANO","dob":"1995-06-10T00:00:00"}]}


Response (201 Created):{
    "status": "success",
    "quoteId": "<uuid>",
    "message": "Quote processing started"
}



Monitoring

Logs: Check /var/log/turborater/integration.log for quote processing and ITC API status.
Database: Query SQLite:sqlite3 /var/lib/turborater/quotes.db "SELECT id, status FROM quotes;"



Next Steps

Obtain ITC 2 API credentials (client ID, client secret, endpoints) from ITC support.
Integrate OAuth 2.0 token generation for ITC API submission.
Confirm QuotePro data push with support.

Contributing
Feel free to submit issues or pull requests for enhancements or bug fixes.
License
MIT License
Contact - www.linkedin.com/in/itsvinop
