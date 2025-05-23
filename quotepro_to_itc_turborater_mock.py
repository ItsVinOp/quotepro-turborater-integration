import json
import os
from xml.etree.ElementTree import Element, SubElement, tostring
import logging
import uuid
from datetime import datetime
from urllib.parse import parse_qs

logging.basicConfig(
    level=logging.INFO,
    filename='/home/ubuntu/turborater_integration.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TurboRaterIntegration:
    def __init__(self):
        self.quotes = {}

    def convert_to_acord_xml(self, quote_data):
        root = Element("ACORD", xmlns="http://www.acord.org/standards")
        insurance = SubElement(root, "InsuranceSvcRq")
        quote = SubElement(insurance, "QuoteRq")
        insured = SubElement(quote, "Insured")
        location = quote_data.get("location", {})
        SubElement(insured, "Name").text = location.get("lastName", "Unknown")
        SubElement(insured, "FirstName").text = location.get("firstName", "")
        SubElement(insured, "Email").text = location.get("email", "")
        SubElement(insured, "Phone").text = location.get("phone", "")
        policy = SubElement(quote, "Policy")
        quote_info = quote_data.get("quote", {})
        SubElement(policy, "PolicyType").text = "auto"
        SubElement(policy, "QuoteAmount").text = str(quote_info.get("totalAmount", 0))
        SubElement(policy, "Source").text = "online"
        vehicles = quote_data.get("vehicles", [])
        if vehicles:
            vehicle = SubElement(quote, "Vehicle")
            v = vehicles[0]
            SubElement(vehicle, "VIN").text = v.get("vinNumber", "")
            SubElement(vehicle, "Make").text = v.get("makeDescription", "")
            SubElement(vehicle, "Model").text = v.get("modelDescription", "")
            SubElement(vehicle, "Year").text = v.get("year", "")
        return tostring(root, encoding="unicode", method="xml")

    def store_quote(self, quote_data):
        xml_data = self.convert_to_acord_xml(quote_data)
        quote_id = str(uuid.uuid4())
        self.quotes[quote_id] = {
            "xml": xml_data,
            "timestamp": datetime.now().isoformat(),
            "quote_data": quote_data
        }
        logger.info(f"Stored quote {quote_id}: {xml_data}")
        return {
    "status": "success",
    "quote_id": quote_id,
    "xml": xml_data,  # This shows the ACORD XML as a string
    "message": "Quote stored successfully"
}


def application(environ, start_response):
    turborater = TurboRaterIntegration()
    if environ['PATH_INFO'] == '/quote' and environ['REQUEST_METHOD'] == 'POST':
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
            logger.info(f"Raw POST data: {post_data}")
            parsed_data = parse_qs(post_data)
            jsonobj = parsed_data.get('jsonobj', [''])[0]
            quote_data = json.loads(jsonobj)
            logger.info(f"Parsed quote data: {json.dumps(quote_data, indent=2)}")
            if quote_data.get("location", {}).get("source", "online") == "online":
                result = turborater.store_quote(quote_data)
                if result:
                    status = '200 OK'
                    response = json.dumps({"status": "success", "data": result})
                else:
                    status = '500 Internal Server Error'
                    response = json.dumps({"error": "Failed to store quote"})
            else:
                status = '200 OK'
                response = json.dumps({"status": "ignored", "reason": "Not an online quote"})
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            status = '400 Bad Request'
            response = json.dumps({"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            status = '500 Internal Server Error'
            response = json.dumps({"error": "Internal server error"})
    else:
        status = '404 Not Found'
        response = json.dumps({"error": "Endpoint not found"})
    
    response_headers = [('Content-type', 'application/json')]
    start_response(status, response_headers)
    return [response.encode()]