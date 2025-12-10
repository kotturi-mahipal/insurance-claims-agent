"""
Unit tests for Insurance Claims Agent
"""

import pytest
import json
from src.agent import InsuranceClaimsAgent

class TestInsuranceClaimsAgent:
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return InsuranceClaimsAgent()
    
    @pytest.fixture
    def sample_extracted_data(self):
        """Sample extracted data for testing"""
        return {
            "policyInformation": {
                "policyNumber": "AUTO-12345",
                "policyholderName": "John Doe",
                "effectiveDates": "01/01/2025 - 01/01/2026"
            },
            "incidentInformation": {
                "date": "01/10/2025",
                "time": "2:30 PM",
                "location": {
                    "street": "123 Main St",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zip": "90001"
                },
                "description": "Rear-end collision at intersection"
            },
            "involvedParties": {
                "claimant": {
                    "name": "John Doe",
                    "phone": "555-1234",
                    "email": "john@example.com"
                },
                "thirdParties": []
            },
            "assetDetails": {
                "assetType": "vehicle",
                "assetId": "1HGCM82633A123456",
                "vehicleInfo": {
                    "year": "2023",
                    "make": "Honda",
                    "model": "Accord"
                },
                "estimatedDamage": 15000
            },
            "otherMandatoryFields": {
                "claimType": "auto",
                "attachments": "photos.zip",
                "initialEstimate": 15000
            }
        }
    
    def test_validate_fields_complete(self, agent, sample_extracted_data):
        """Test validation with complete data"""
        missing = agent.validate_fields(sample_extracted_data)
        assert len(missing) == 0, "No fields should be missing"
    
    def test_validate_fields_missing_policy(self, agent, sample_extracted_data):
        """Test validation with missing policy number"""
        sample_extracted_data['policyInformation']['policyNumber'] = None
        missing = agent.validate_fields(sample_extracted_data)
        assert 'policyNumber' in missing
    
    def test_validate_fields_missing_claimant(self, agent, sample_extracted_data):
        """Test validation with missing claimant name"""
        sample_extracted_data['involvedParties']['claimant']['name'] = None
        missing = agent.validate_fields(sample_extracted_data)
        assert 'claimantName' in missing
    
    def test_route_fast_track(self, agent, sample_extracted_data):
        """Test fast-track routing for low damage claims"""
        missing_fields = []
        result = agent.route_claim(sample_extracted_data, missing_fields)
        
        assert result['recommendedRoute'] == 'fast-track'
        assert result['estimatedDamage'] == 15000
        assert len(result['fraudIndicators']) == 0
    
    def test_route_manual_review_high_damage(self, agent, sample_extracted_data):
        """Test manual review for high damage claims"""
        sample_extracted_data['assetDetails']['estimatedDamage'] = 50000
        missing_fields = []
        result = agent.route_claim(sample_extracted_data, missing_fields)
        
        assert result['recommendedRoute'] == 'manual-review'
    
    def test_route_manual_review_missing_fields(self, agent, sample_extracted_data):
        """Test manual review routing when fields are missing"""
        missing_fields = ['policyNumber', 'incidentDate']
        result = agent.route_claim(sample_extracted_data, missing_fields)
        
        assert result['recommendedRoute'] == 'manual-review'
        assert 'Missing mandatory fields' in result['reasoning']
    
    def test_route_investigation_fraud(self, agent, sample_extracted_data):
        """Test investigation routing for fraud indicators"""
        sample_extracted_data['incidentInformation']['description'] = \
            "This seems like a staged accident with inconsistent details"
        
        missing_fields = []
        result = agent.route_claim(sample_extracted_data, missing_fields)
        
        assert result['recommendedRoute'] == 'investigation'
        assert len(result['fraudIndicators']) > 0
        assert 'staged' in result['fraudIndicators'] or 'inconsistent' in result['fraudIndicators']
    
    def test_route_specialist_injury(self, agent, sample_extracted_data):
        """Test specialist routing for injury claims"""
        sample_extracted_data['otherMandatoryFields']['claimType'] = 'injury'
        missing_fields = []
        result = agent.route_claim(sample_extracted_data, missing_fields)
        
        assert result['recommendedRoute'] == 'specialist-queue'
        assert 'injury' in result['reasoning'].lower()
    
    def test_fraud_keywords_detection(self, agent):
        """Test fraud keyword detection"""
        test_descriptions = [
            ("Normal accident description", []),
            ("This looks like fraud to me", ["fraud"]),
            ("Staged accident with suspicious details", ["staged", "suspicious"]),
            ("Inconsistent and fake story", ["inconsistent", "fake"])
        ]
        
        for description, expected_keywords in test_descriptions:
            sample_data = {
                "incidentInformation": {"description": description},
                "otherMandatoryFields": {"claimType": "auto"},
                "assetDetails": {"estimatedDamage": 10000}
            }
            result = agent.route_claim(sample_data, [])
            
            for keyword in expected_keywords:
                assert keyword in result['fraudIndicators'], \
                    f"Expected '{keyword}' in fraud indicators for: {description}"
    
    def test_extract_json_from_markdown(self, agent):
        """Test JSON extraction from markdown code blocks"""
        markdown_json = '```json\n{"test": "value"}\n```'
        result = agent._extract_json(markdown_json)
        assert result == '{"test": "value"}'
        
        plain_json = '{"test": "value"}'
        result = agent._extract_json(plain_json)
        assert result == '{"test": "value"}'
    
    def test_edge_case_zero_damage(self, agent, sample_extracted_data):
        """Test routing with zero damage amount"""
        sample_extracted_data['assetDetails']['estimatedDamage'] = 0
        missing_fields = []
        result = agent.route_claim(sample_extracted_data, missing_fields)
        
        assert result['recommendedRoute'] == 'fast-track'
    
    def test_edge_case_no_damage_estimate(self, agent, sample_extracted_data):
        """Test routing with no damage estimate"""
        sample_extracted_data['assetDetails']['estimatedDamage'] = None
        sample_extracted_data['otherMandatoryFields']['initialEstimate'] = None
        missing_fields = []
        result = agent.route_claim(sample_extracted_data, missing_fields)
        
        assert result['recommendedRoute'] == 'manual-review'
        assert 'estimate unavailable' in result['reasoning'].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])