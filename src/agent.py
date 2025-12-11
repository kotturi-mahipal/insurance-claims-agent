"""
Autonomous Insurance Claims Processing Agent
Author: Mahipal Kotturi
"""

import os
import json
import re
from typing import Dict, List, Any
from datetime import datetime
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class InsuranceClaimsAgent:
    """Main agent for processing FNOL documents"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model = genai.GenerativeModel(model_name)
        self.mandatory_fields = [
            'policyNumber', 'policyholderName', 'incidentDate', 
            'incidentLocation', 'description', 'claimantName',
            'assetType', 'claimType'
        ]
        self.fraud_keywords = ['fraud', 'staged', 'inconsistent', 'suspicious', 'fake']
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_text_from_txt(self, txt_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    def extract_fields(self, document_text: str) -> Dict[str, Any]:
        """Extract structured fields using Gemini"""
        
        prompt = f"""
You are an expert insurance claims processor. Extract structured information from this FNOL document.

DOCUMENT TEXT:
{document_text}

Extract these fields in JSON format. Use null if not found:

{{
  "policyInformation": {{
    "policyNumber": "string or null",
    "policyholderName": "string or null",
    "effectiveDates": "string or null"
  }},
  "incidentInformation": {{
    "date": "MM/DD/YYYY or null",
    "time": "HH:MM AM/PM or null",
    "location": {{
      "street": "string or null",
      "city": "string or null",
      "state": "string or null",
      "zip": "string or null"
    }},
    "description": "string or null"
  }},
  "involvedParties": {{
    "claimant": {{
      "name": "string or null",
      "phone": "string or null",
      "email": "string or null"
    }},
    "thirdParties": []
  }},
  "assetDetails": {{
    "assetType": "vehicle/property/other or null",
    "assetId": "string or null",
    "vehicleInfo": {{
      "year": "string or null",
      "make": "string or null",
      "model": "string or null"
    }},
    "estimatedDamage": "number or null"
  }},
  "otherMandatoryFields": {{
    "claimType": "auto/property/injury/other or null",
    "attachments": "string or null",
    "initialEstimate": "number or null"
  }}
}}

RULES:
1. Extract exact values - don't infer
2. Dates in MM/DD/YYYY format
3. Currency as numbers only
4. Infer claimType from context
5. Return ONLY valid JSON
"""
        
        try:
            response = self.model.generate_content(prompt)
            json_str = self._extract_json(response.text)
            return json.loads(json_str)
        except Exception as e:
            raise Exception(f"Extraction failed: {str(e)}")
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from markdown or mixed text"""
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text
    
    def validate_fields(self, extracted_data: Dict) -> List[str]:
        """Identify missing mandatory fields"""
        missing = []
        
        if not extracted_data.get('policyInformation', {}).get('policyNumber'):
            missing.append('policyNumber')
        if not extracted_data.get('policyInformation', {}).get('policyholderName'):
            missing.append('policyholderName')
        
        incident = extracted_data.get('incidentInformation', {})
        if not incident.get('date'):
            missing.append('incidentDate')
        if not incident.get('location', {}).get('city'):
            missing.append('incidentLocation')
        if not incident.get('description'):
            missing.append('description')
        
        if not extracted_data.get('involvedParties', {}).get('claimant', {}).get('name'):
            missing.append('claimantName')
        
        if not extracted_data.get('assetDetails', {}).get('assetType'):
            missing.append('assetType')
        
        if not extracted_data.get('otherMandatoryFields', {}).get('claimType'):
            missing.append('claimType')
        
        return missing
    
    def route_claim(self, extracted_data: Dict, missing_fields: List[str]) -> Dict[str, Any]:
        """Determine routing based on rules"""
        
        description = extracted_data.get('incidentInformation', {}).get('description', '').lower()
        claim_type = extracted_data.get('otherMandatoryFields', {}).get('claimType', '').lower()
        estimated_damage = extracted_data.get('assetDetails', {}).get('estimatedDamage')
        initial_estimate = extracted_data.get('otherMandatoryFields', {}).get('initialEstimate')
        
        damage_amount = estimated_damage or initial_estimate or 0
        
        fraud_indicators = [word for word in self.fraud_keywords if word in description]
        
        route = None
        reasoning = ""
        
        if fraud_indicators:
            route = "investigation"
            reasoning = f"Fraud indicators detected: {', '.join(fraud_indicators)}"
        elif missing_fields:
            route = "manual-review"
            reasoning = f"Missing mandatory fields: {', '.join(missing_fields)}"
        elif 'injury' in claim_type:
            route = "specialist-queue"
            reasoning = "Claim involves injury - requires specialist review"
        elif damage_amount and damage_amount < 25000:
            route = "fast-track"
            reasoning = f"Low damage amount (${damage_amount:,.2f}) with all required fields present"
        else:
            route = "manual-review"
            reasoning = "Standard review required - damage exceeds fast-track threshold or estimate unavailable"
        
        return {
            "recommendedRoute": route,
            "reasoning": reasoning,
            "missingFields": missing_fields,
            "fraudIndicators": fraud_indicators,
            "estimatedDamage": damage_amount
        }
    
    def process_claim(self, file_path: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        
        print(f"Processing: {file_path}")
        
        # Extract text based on file type
        print("  → Extracting text...")
        if file_path.endswith('.pdf'):
            document_text = self.extract_text_from_pdf(file_path)
        else:
            document_text = self.extract_text_from_txt(file_path)
        
        # Extract fields
        print("  → Extracting structured fields...")
        extracted_fields = self.extract_fields(document_text)
        
        # Validate
        print("  → Validating mandatory fields...")
        missing_fields = self.validate_fields(extracted_fields)
        
        # Route
        print("  → Determining routing...")
        routing_info = self.route_claim(extracted_fields, missing_fields)
        
        result = {
            "documentName": os.path.basename(file_path),
            "processedAt": datetime.now().isoformat(),
            "extractedFields": extracted_fields,
            "missingFields": missing_fields,
            "recommendedRoute": routing_info["recommendedRoute"],
            "reasoning": routing_info["reasoning"],
            "fraudIndicators": routing_info.get("fraudIndicators", []),
            "estimatedDamage": routing_info.get("estimatedDamage")
        }
        
        print(f"  ✓ Routed to: {routing_info['recommendedRoute']}")
        
        return result
    
    def save_result(self, result: Dict, output_dir: str = "data/output"):
        """Save processing result to JSON"""
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"claim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"  ✓ Saved to: {filepath}")
        return filepath


if __name__ == "__main__":
    agent = InsuranceClaimsAgent()
    
    # Process the first sample FNOL
    pdf_path = "data/sample_fnols/fnol_fast_track_01.txt"
    
    try:
        result = agent.process_claim(pdf_path)
        agent.save_result(result)
        
        print("\n" + "="*60)
        print("PROCESSING SUMMARY")
        print("="*60)
        print(f"Route: {result['recommendedRoute']}")
        print(f"Reason: {result['reasoning']}")
        if result['missingFields']:
            print(f"Missing: {', '.join(result['missingFields'])}")
        if result['fraudIndicators']:
            print(f"⚠️  Fraud indicators: {', '.join(result['fraudIndicators'])}")
        
    except Exception as e:
        print(f"Error: {str(e)}")