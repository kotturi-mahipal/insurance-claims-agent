"""
Batch processor for multiple FNOL documents
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from agent import InsuranceClaimsAgent


class BatchProcessor:
    """Process multiple FNOL documents in batch"""
    
    def __init__(self):
        self.agent = InsuranceClaimsAgent()
        self.results = []
        self.stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "routes": {
                "fast-track": 0,
                "manual-review": 0,
                "investigation": 0,
                "specialist-queue": 0
            }
        }
    
    def process_directory(self, input_dir: str, output_dir: str = "data/output"):
        """Process all files in a directory"""
        
        input_path = Path(input_dir)
        
        # Get both PDF and TXT files
        pdf_files = list(input_path.glob("*.pdf"))
        txt_files = list(input_path.glob("*.txt"))
        all_files = pdf_files + txt_files
        
        if not all_files:
            print(f"⚠️  No files found in {input_dir}")
            return
        
        print(f"\n{'='*70}")
        print(f"BATCH PROCESSING: {len(all_files)} documents")
        print(f"{'='*70}\n")
        
        for idx, file in enumerate(all_files, 1):
            print(f"\n[{idx}/{len(all_files)}] Processing: {file.name}")
            print("-" * 70)
            
            try:
                # Process claim
                result = self.agent.process_claim(str(file))
                
                # Save individual result
                self.agent.save_result(result, output_dir)
                
                # Track statistics
                self.stats["total"] += 1
                self.stats["successful"] += 1
                self.stats["routes"][result["recommendedRoute"]] += 1
                
                # Store result
                self.results.append({
                    "filename": file.name,
                    "route": result["recommendedRoute"],
                    "status": "success"
                })
                
                print(f"✅ Successfully processed - Route: {result['recommendedRoute']}")
                
            except Exception as e:
                self.stats["total"] += 1
                self.stats["failed"] += 1
                
                self.results.append({
                    "filename": file.name,
                    "route": None,
                    "status": "failed",
                    "error": str(e)
                })
                
                print(f"❌ Failed: {str(e)}")
        
        # Generate summary report
        self._generate_summary_report(output_dir)
    
    def _generate_summary_report(self, output_dir: str):
        """Generate batch processing summary report"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = Path(output_dir) / f"batch_summary_{timestamp}.json"
        
        summary = {
            "processedAt": datetime.now().isoformat(),
            "statistics": self.stats,
            "results": self.results
        }
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary to console
        print(f"\n{'='*70}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*70}")
        print(f"\n📊 Statistics:")
        print(f"   Total Processed: {self.stats['total']}")
        print(f"   ✅ Successful: {self.stats['successful']}")
        print(f"   ❌ Failed: {self.stats['failed']}")
        
        print(f"\n📈 Routing Distribution:")
        for route, count in self.stats['routes'].items():
            if count > 0:
                percentage = (count / self.stats['total']) * 100
                print(f"   {route}: {count} ({percentage:.1f}%)")
        
        print(f"\n💾 Summary saved to: {report_file}")
        print(f"{'='*70}\n")
        
        # Generate visual chart
        self._print_route_chart()
    
    def _print_route_chart(self):
        """Print ASCII bar chart of routes"""
        
        print("\n📊 Route Distribution Chart:")
        print("-" * 70)
        
        max_count = max(self.stats['routes'].values()) if any(self.stats['routes'].values()) else 1
        
        route_symbols = {
            "fast-track": "🟢",
            "manual-review": "🟡",
            "investigation": "🔴",
            "specialist-queue": "🟣"
        }
        
        for route, count in self.stats['routes'].items():
            if count > 0:
                bar_length = int((count / max_count) * 40)
                bar = "█" * bar_length
                symbol = route_symbols.get(route, "⚪")
                print(f"{symbol} {route:20s} | {bar} {count}")
        
        print("-" * 70)


def main():
    """Main entry point for batch processing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Batch process FNOL documents"
    )
    parser.add_argument(
        "input_dir",
        help="Directory containing files to process"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="data/output",
        help="Output directory for results (default: data/output)"
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.exists(args.input_dir):
        print(f"❌ Error: Directory not found: {args.input_dir}")
        return
    
    # Process batch
    processor = BatchProcessor()
    processor.process_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()