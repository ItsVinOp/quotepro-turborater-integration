import json
from xml.etree.ElementTree import Element, SubElement, tostring
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='turborater_integration.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# TurboRater API Integration (Mocked)
class TurboRaterIntegration:
    def __init__(self, api_url, username, password):
        self.api_url = api_url
        self.auth = (username, password)

    def convert_to_acord_xml(self, quote_data):
        root = Element("ACORD", xmlns="http://www.acord.org/standards")
        insurance = SubElement(root, "InsuranceSvcRq")
        quote = SubElement(insurance, "QuoteRq")
        
        # Insured details
        insured = SubElement(quote, "Insured")
        SubElement(insured, "Name").text = quote_data.get("last_name", "Unknown")
        SubElement(insured, "FirstName").text = quote_data.get("first_name", "")
        SubElement(insured, "Email").text = quote_data.get("email", "")
        SubElement(insured, "Phone").text = quote_data.get("phone", "")
        
        # Policy details
        policy = SubElement(quote, "Policy")
        SubElement(policy, "PolicyType").text = quote_data.get("policy_type", "auto")
        SubElement(policy, "QuoteAmount").text = str(quote_data.get("quote_amount", 0))
        SubElement(policy, "Source").text = quote_data.get("source", "online")
        
        # Vehicle details (if provided)
        if "vehicle" in quote_data:
            vehicle = SubElement(quote, "Vehicle")
            SubElement(vehicle, "VIN").text = quote_data["vehicle"].get("vin", "")
            SubElement(vehicle, "Make").text = quote_data["vehicle"].get("make", "")
            SubElement(vehicle, "Model").text = quote_data["vehicle"].get("model", "")
            SubElement(vehicle, "Year").text = str(quote_data["vehicle"].get("year", ""))
        
        return tostring(root, encoding="unicode", method="xml")

    def send_to_turborater(self, quote_data):
        xml_data = self.convert_to_acord_xml(quote_data)
        logger.info(f"Generated ACORD XML: {xml_data}")
        
        # Mock TurboRater API response (bypassing actual API call)
        mock_response = {
            "status": "success",
            "quote_id": "TR123456789",
            "message": "Quote stored successfully"
        }
        logger.info(f"Mock TurboRater API response: {mock_response}")
        return mock_response

# HTTP Server for QuotePro data
class QuoteProHandler(BaseHTTPRequestHandler):
    def __init__(self, turborater_integration, *args, **kwargs):
        self.turborater_integration = turborater_integration
        super().__init__(*args, **kwargs)

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            quote_data = json.loads(post_data)
            
            # Conditional trigger for online quotes
            if quote_data.get("source") == "online":
                result = self.turborater_integration.send_to_turborater(quote_data)
                if result:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "data": result}).encode())
                else:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to send to TurboRater"}).encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ignored", "reason": "Not an online quote"}).encode())
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Internal server error"}).encode())

# Microservice
class QuoteProToTurboRaterService:
    def __init__(self, turborater_api_url, turborater_username, turborater_password, host='localhost', port=8000):
        self.turborater_integration = TurboRaterIntegration(turborater_api_url, turborater_username, turborater_password)
        self.host = host
        self.port = port

    def start_server(self):
        def handler(*args, **kwargs):
            QuoteProHandler(self.turborater_integration, *args, **kwargs)
        
        server = HTTPServer((self.host, self.port), handler)
        logger.info(f"Server started on {self.host}:{self.port} at {datetime.now()}")
        server.serve_forever()

# Test function with sample data
def run_tests():
    turborater = TurboRaterIntegration(
        "https://api.turborater.com/quote",  # Placeholder (not used in mock)
        "username",                          # Placeholder (not used in mock)
        "password"                           # Placeholder (not used in mock)
    )
    
    # Sample QuotePro data for an auto insurance quote
    sample_quote = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "123-456-7890",
        "source": "online",
        "quote_amount": 1500.00,
        "policy_type": "auto",
        "vehicle": {
            "vin": "1HGCM82633A004352",
            "make": "Honda",
            "model": "Accord",
            "year": 2020
        }
    }
    
    # Test with sample data
    result = turborater.send_to_turborater(sample_quote)
    logger.info(f"Sample data test result: {result}")
    
    # Test with invalid data
    invalid_quote = {"invalid": "data"}
    result = turborater.send_to_turborater(invalid_quote)
    logger.info(f"Invalid data test result: {result}")
    
    # Test with incomplete data
    incomplete_quote = {"last_name": "Smith", "source": "online"}
    result = turborater.send_to_turborater(incomplete_quote)
    logger.info(f"Incomplete data test result: {result}")
    
    # Test with in-office quote (should be ignored)
    inoffice_quote = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "987-654-3210",
        "source": "in-office",
        "quote_amount": 2000.00,
        "policy_type": "auto"
    }
    result = turborater.send_to_turborater(inoffice_quote)
    logger.info(f"In-office data test result: {result}")

# Example usage
if __name__ == "__main__":
    service = QuoteProToTurboRaterService(
        turborater_api_url="https://api.turborater.com/quote",
        turborater_username="username",
        turborater_password="password",
        host="localhost",
        port=8000
    )
    
    # Run tests
    run_tests()
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=service.start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Keep main thread running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info(f"Shutting down server at {datetime.now()}")