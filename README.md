QuotePro to ITC TurboRater Integration
======================================

A Python-based microservice to transform insurance quote data from QuotePro into ACORD XML and prepare it for integration with ITC TurboRater's API.

Deployed on AWS EC2 with logging, data persistence, and production-ready service setup.

---------------------
🔧 Features
---------------------
- Receives JSON quote data via POST endpoint
- Validates input fields (VIN, phone, etc.)
- Converts data into ACORD v3.4 XML
- Stores each quote with status tracking in SQLite (PENDING, PROCESSED, BOUND)
- Logs all activity to /var/log/turborater/integration.log with rotation
- OAuth 2.0-ready for ITC API authentication (pending credentials)
- Production deployment using Gunicorn on Ubuntu EC2 with a static Elastic IP

---------------------
🛠 Technologies
---------------------
Backend   : Python, Flask, Gunicorn
Database  : SQLite
Cloud     : AWS EC2, Elastic IP
Formats   : JSON, ACORD XML
Tools     : Postman, AWS CLI, Git
OS        : Ubuntu

---------------------
⚙️ Prerequisites
---------------------
- Python 3.8+
- AWS EC2 instance (Ubuntu)
- QuotePro API access (push-based)
- ITC TurboRater API credentials
- Git, pip, and SQLite installed

---------------------
🚀 Setup Instructions
---------------------

1. Clone the Repository:
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>

2. Install Dependencies:
   pip install -r requirements.txt

   Example requirements.txt:
   -------------------------
   requests==2.31.0
   gunicorn==20.1.0

3. Configure AWS EC2:
   - Launch EC2 instance (e.g., t2.micro, Ubuntu)
   - Assign an Elastic IP
   - Open ports 22 (SSH) and 8000 (API)
   - SSH into EC2:
     ssh -i <your-key>.pem ubuntu@<elastic-ip>

4. Set Up Directories:
   sudo mkdir -p /var/log/turborater /var/lib/turborater
   sudo chown ubuntu:ubuntu /var/log/turborater /var/lib/turborater
   sudo chmod 755 /var/log/turborater /var/lib/turborater

5. Configure Environment Variables:
   sudo nano /etc/environment

   Add:
   ITC_CLIENT_ID="<your_client_id>"
   ITC_CLIENT_SECRET="<your_client_secret>"
   ITC_TOKEN_URL="<itc_token_endpoint>"
   ITC_API_URL="<itc_quote_endpoint>"

   Apply:
   source /etc/environment

6. Deploy Microservice:
   - Copy files to EC2:
     scp -i <your-key>.pem quotepro_to_itc_turborater_mock.py requirements.txt ubuntu@<elastic-ip>:/home/ubuntu

   - Create systemd service:
     sudo nano /etc/systemd/system/quotepro.service

     Content:
     ----------------------
     [Unit]
     Description=QuotePro TurboRater Microservice
     After=network.target

     [Service]
     User=ubuntu
     WorkingDirectory=/home/ubuntu
     ExecStart=/home/ubuntu/.local/bin/gunicorn -w 4 -b 0.0.0.0:8000 quotepro_to_itc_turborater_mock:application
     Restart=always

     [Install]
     WantedBy=multi-user.target

   - Enable and start service:
     sudo systemctl daemon-reload
     sudo systemctl enable quotepro
     sudo systemctl start quotepro

---------------------
📨 Usage
---------------------
Endpoint: http://<elastic-ip>:8000/quote  
Method: POST  
Headers: Content-Type: application/x-www-form-urlencoded  
Body:

jsonobj={
  "id":"InsuranceNavy_0016866151",
  "location":{
    "firstName":"Maria Piedad",
    "lastName":"Tiviano Tiviano",
    "email":"",
    "phone":"-   -",
    "city":"CHICAGO",
    "state":"IL",
    "zipCode":"60651"
  },
  "vehicles":[
    {
      "year":"1998",
      "makeDescription":"TOYOTA",
      "modelDescription":"CAMRY CE/LE/XLE",
      "vinNumber":"JT2BG22K5W0162187"
    }
  ],
  "quote":{
    "totalAmount":545.0,
    "policyTerm":"6",
    "qProQuoteNo":"427481",
    "effectiveDate":"2025-05-22T00:00:00"
  },
  "drivers":[
    {
      "firstName":"MARIA PIEDAD",
      "lastName":"TIVIANO TIVIANO",
      "dob":"1995-06-10T00:00:00"
    }
  ]
}

Response (201 Created):
-----------------------
{
  "status": "success",
  "quoteId": "<uuid>",
  "message": "Quote processing started"
}

---------------------
📈 Monitoring
---------------------
Logs: /var/log/turborater/integration.log  
Database:  
  sqlite3 /var/lib/turborater/quotes.db  
  > SELECT id, status FROM quotes;

---------------------
🔄 Next Steps
---------------------
- Obtain ITC 2 API credentials (client ID, client secret, endpoints)
- Integrate OAuth 2.0 token generation for quote submission
- Confirm QuotePro data push setup

---------------------
🤝 Contributing
---------------------
Feel free to submit issues or pull requests.

---------------------
📜 License
---------------------
MIT License

---------------------
🔗 Contact
---------------------
www.linkedin.com/in/itsvinop
