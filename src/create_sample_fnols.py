"""
Generate sample FNOL documents for testing
Run this to create test data
"""

import os
from datetime import datetime, timedelta
import random

# Sample templates for different scenarios
SAMPLE_FNOLS = [
    {
        "filename": "fnol_fast_track_01.txt",
        "content": """
FIRST NOTICE OF LOSS - AUTOMOBILE CLAIM

POLICY INFORMATION
Policy Number: AUTO-2025-123456
Policyholder Name: Sarah Johnson
Effective Dates: 01/01/2025 - 12/31/2025
Line of Business: Personal Auto

INCIDENT INFORMATION
Date of Loss: 01/15/2025
Time: 2:30 PM
Location: 456 Oak Street, San Francisco, CA 94102

Description of Accident:
Minor rear-end collision at stoplight. I was stopped at red light when vehicle behind 
failed to brake in time. Low-speed impact, minimal damage to rear bumper.

INVOLVED PARTIES
Claimant: Sarah Johnson
Phone: (415) 555-0123
Email: sarah.johnson@email.com

Third Party Driver: Michael Chen
Phone: (415) 555-0456
Insurance: State Farm, Policy #SF-789012

ASSET DETAILS
Asset Type: Vehicle
VIN: 1HGCM82633A004352
Year: 2023
Make: Honda
Model: Civic
License Plate: 7ABC123 (CA)

Estimated Damage: $8,500
Initial Estimate: $8,500

CLAIM TYPE: Auto
Attachments: photos_rear_bumper.zip

Report Filed: Yes
Police Report #: SFPD-2025-0115
"""
    },
    {
        "filename": "fnol_injury_specialist_02.txt",
        "content": """
FIRST NOTICE OF LOSS - INJURY CLAIM

POLICY INFORMATION
Policy Number: AUTO-2025-789012
Policyholder Name: Robert Martinez
Effective Dates: 06/01/2024 - 06/01/2025

INCIDENT INFORMATION
Date of Loss: 01/20/2025
Time: 8:15 AM
Location: Intersection of Main St and 5th Ave, Austin, TX 78701

Description of Accident:
T-bone collision at intersection. Other driver ran red light and struck passenger side 
at moderate speed. Driver experienced neck pain and was transported to hospital for 
evaluation. Passenger (spouse) also complained of back pain.

INVOLVED PARTIES
Claimant: Robert Martinez
Phone: (512) 555-0789
Email: r.martinez@email.com

Injured Parties:
- Robert Martinez (driver) - neck pain, whiplash suspected
- Maria Martinez (passenger) - lower back pain

Third Party Driver: James Wilson
Phone: (512) 555-0321

ASSET DETAILS
Asset Type: Vehicle
VIN: 5YJSA1E14HF123456
Year: 2020
Make: Tesla
Model: Model S
License Plate: TX-ABC-789

Estimated Damage: $22,000

CLAIM TYPE: Injury
Medical Treatment: Yes - Austin Regional Medical Center
Attachments: medical_records.pdf, scene_photos.zip

Police Report: APD-2025-0120
"""
    },
    {
        "filename": "fnol_fraud_investigation_03.txt",
        "content": """
FIRST NOTICE OF LOSS - SUSPICIOUS CLAIM

POLICY INFORMATION
Policy Number: AUTO-2025-456789
Policyholder Name: David Thompson

INCIDENT INFORMATION
Date of Loss: 01/18/2025
Time: 11:45 PM
Location: Remote area off Highway 101, approximately 20 miles north of city limits

Description of Accident:
Vehicle allegedly struck by unknown hit-and-run driver in remote location. Claimant 
states they were forced off road by aggressive driver who fled scene. Extensive damage 
to multiple panels. Story seems inconsistent with damage pattern. No witnesses present. 
Claimant delayed reporting by 36 hours. Vehicle has pre-existing damage that appears 
staged to match claim narrative.

INVOLVED PARTIES
Claimant: David Thompson
Phone: (555) 123-4567
Email: d.thompson@email.com

Third Party: Unknown/fled scene (alleged)

ASSET DETAILS
Asset Type: Vehicle
VIN: 1G1ZD5ST8LF123456
Year: 2015
Make: Chevrolet
Model: Malibu
License Plate: XYZ-9876

Estimated Damage: $18,500

CLAIM TYPE: Auto
Attachments: delayed_photos.zip

Police Report: Not filed (claimant states they forgot)

NOTES: Multiple red flags - delayed reporting, inconsistent story, suspicious damage 
pattern, no police report, remote location with no witnesses.
"""
    },
    {
        "filename": "fnol_missing_fields_04.txt",
        "content": """
FIRST NOTICE OF LOSS - INCOMPLETE SUBMISSION

POLICY INFORMATION
Policy Number: [MISSING]
Policyholder Name: Jennifer Lee

INCIDENT INFORMATION
Date of Loss: 01/22/2025
Time: [NOT PROVIDED]
Location: Parking lot, Shopping Center

Description of Accident:
Vehicle damaged in parking lot while I was shopping. Returned to find dent and scratches 
on driver side door. No note left by other party.

INVOLVED PARTIES
Claimant: Jennifer Lee
Phone: [MISSING]
Email: [MISSING]

Third Party: Unknown

ASSET DETAILS
Asset Type: Vehicle
Year: 2022
Make: Toyota
Model: [MISSING]
License Plate: [MISSING]

Estimated Damage: [NOT PROVIDED]

CLAIM TYPE: [MISSING]
Attachments: None

Police Report: No
"""
    },
    {
        "filename": "fnol_high_value_manual_05.txt",
        "content": """
FIRST NOTICE OF LOSS - HIGH VALUE CLAIM

POLICY INFORMATION
Policy Number: AUTO-2025-PREMIUM-001
Policyholder Name: Alexander Vanderbilt III
Effective Dates: 01/01/2025 - 12/31/2025
Line of Business: Luxury Auto

INCIDENT INFORMATION
Date of Loss: 01/25/2025
Time: 3:45 PM
Location: 1200 Sunset Boulevard, Beverly Hills, CA 90210

Description of Accident:
Multi-vehicle collision on boulevard. Traffic suddenly stopped due to pedestrian 
crossing. Driver of commercial truck failed to stop in time, causing chain reaction 
involving 4 vehicles. Significant structural damage to luxury vehicle. Airbags deployed. 
All occupants safe but vehicle likely total loss.

INVOLVED PARTIES
Claimant: Alexander Vanderbilt III
Phone: (310) 555-9999
Email: avanderbilt@email.com

Third Party 1: Commercial Trucking Co.
Driver: Thomas Rodriguez
Phone: (310) 555-8888
Insurance: Commercial Auto Policy #TRUCK-45678

ASSET DETAILS
Asset Type: Vehicle
VIN: WDD2222221A123456
Year: 2024
Make: Mercedes-Benz
Model: S-Class S580
License Plate: CA-LUXURY-1

Estimated Damage: $75,000 (Likely Total Loss)
Vehicle Value: $125,000

CLAIM TYPE: Auto
Attachments: scene_photos.zip, police_report.pdf, witness_statements.pdf

Police Report: BHPD-2025-0125
Witnesses: 3 independent witnesses
Tow Location: Beverly Hills Auto Body - Secure Storage
"""
    }
]


def create_sample_fnols(output_dir: str = "data/sample_fnols"):
    """Create sample FNOL text files for testing"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'='*70}")
    print("GENERATING SAMPLE FNOL DOCUMENTS")
    print(f"{'='*70}\n")
    
    for sample in SAMPLE_FNOLS:
        filepath = os.path.join(output_dir, sample["filename"])
        
        with open(filepath, 'w') as f:
            f.write(sample["content"])
        
        print(f"✅ Created: {sample['filename']}")
    
    print(f"\n📁 Total files created: {len(SAMPLE_FNOLS)}")
    print(f"📂 Location: {output_dir}")
    print(f"{'='*70}\n")
    
    # Print routing predictions
    print("📊 EXPECTED ROUTING:")
    print("-" * 70)
    print("1. fnol_fast_track_01.txt       → 🟢 fast-track")
    print("2. fnol_injury_specialist_02.txt → 🟣 specialist-queue")
    print("3. fnol_fraud_investigation_03.txt → 🔴 investigation")
    print("4. fnol_missing_fields_04.txt    → 🟡 manual-review")
    print("5. fnol_high_value_manual_05.txt → 🟡 manual-review")
    print("-" * 70)


if __name__ == "__main__":
    create_sample_fnols()
    
    print("\n💡 Next steps:")
    print("   1. Run: python src/agent.py")
    print("   2. Or batch process: python src/batch_process.py data/sample_fnols")