"""
examples/evaluate_all_events.py - Batch Evaluation of All 35 Events
"""

import sys
from pathlib import Path

# Ensure imports work from examples directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.event_database import event_db
from examples.real_world_evaluator import RealWorldEvaluator
import statistics


def evaluate_all_events():
    """Evaluate all events and generate comprehensive report."""
    
    print("="*70)
    print("SERAA EVALUATION: 35 MAJOR REAL-WORLD DECISIONS")
    print("="*70)
    
    # Get all events
    events = event_db.get_all()
    
    print(f"\nTotal Events in Database: {len(events)}")
    
    # Count by domain
    gov_count = len([e for e in events if any(x in e.actor for x in ['President', 'Congress', 'Court', 'Parliament', 'EU'])])
    corp_count = len([e for e in events if any(x in e.actor for x in ['Company', 'Corporation', 'Inc.', 'AG', 'LLC'])])
    tech_count = len([e for e in events if any(x in e.actor for x in ['Facebook', 'Google', 'Apple', 'Twitter', 'Amazon', 'Microsoft', 'ByteDance', 'Signal'])])
    health_count = len([e for e in events if any(x in e.actor for x in ['Hospital', 'Pharma', 'Health', 'CDC', 'FDA', 'Medical'])])
    
    print(f"\nDomains:")
    print(f"  • Government/Policy: {gov_count}")
    print(f"  • Corporate: {corp_count}")
    print(f"  • Technology: {tech_count}")
    print(f"  • Healthcare: {health_count}")
    
    # Evaluate each event
    results = []
    
    for i, event in enumerate(events, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(events)}] {event.title}")
        print(f"{'='*70}")
        
        # Determine domain
        if any(x in event.actor for x in ['President', 'Congress', 'Court', 'Government', 'Parliament', 'EU']):
            domain = 'government'
        elif any(x in event.actor for x in ['Facebook', 'Google', 'Apple', 'Twitter', 'Amazon', 'Microsoft', 'ByteDance', 'Signal']):
            domain = 'tech'
        elif any(x in event.actor for x in ['Hospital', 'Pharma', 'CDC', 'FDA', 'Health', 'Medical']):
            domain = 'healthcare'
        else:
            domain = 'corporate'
        
        try:
            evaluator = RealWorldEvaluator(domain=domain)
            result = evaluator.evaluate_event(event)
            results.append(result)
        except Exception as e:
            print(f"ERROR evaluating {event.title}: {e}")
            # Add placeholder result
            results.append({
                'event': event,
                'pac_score': event.outcomes.get('pac_score', 0.5),
                'approved': False,
                'verdict': 'ERROR'
            })
    
    # Generate summary statistics
    print(f"\n\n{'='*70}")
    print("SUMMARY STATISTICS")
    print(f"{'='*70}")
    
    pac_scores = [r['pac_score'] for r in results]
    approved_count = sum(1 for r in results if r['approved'])
    
    print(f"\nPAC Score Statistics:")
    print(f"  Mean: {statistics.mean(pac_scores):.3f}")
    print(f"  Median: {statistics.median(pac_scores):.3f}")
    if len(pac_scores) > 1:
        print(f"  Std Dev: {statistics.stdev(pac_scores):.3f}")
    print(f"  Min: {min(pac_scores):.3f} ({min(results, key=lambda x: x['pac_score'])['event'].title})")
    print(f"  Max: {max(pac_scores):.3f} ({max(results, key=lambda x: x['pac_score'])['event'].title})")
    
    print(f"\nEthical Approval:")
    print(f"  Approved: {approved_count} ({approved_count/len(results)*100:.1f}%)")
    print(f"  Rejected: {len(results) - approved_count} ({(len(results)-approved_count)/len(results)*100:.1f}%)")
    
    # Categorize by PAC score
    excellent = [r for r in results if r['pac_score'] >= 0.8]
    acceptable = [r for r in results if 0.6 <= r['pac_score'] < 0.8]
    problematic = [r for r in results if 0.4 <= r['pac_score'] < 0.6]
    violations = [r for r in results if r['pac_score'] < 0.4]
    
    print(f"\nPAC Score Distribution:")
    print(f"  Excellent (≥0.8):      {len(excellent)} events")
    print(f"  Acceptable (0.6-0.8):  {len(acceptable)} events")
    print(f"  Problematic (0.4-0.6): {len(problematic)} events")
    print(f"  Violations (<0.4):     {len(violations)} events")
    
    # Top 5 and Bottom 5
    print(f"\n{'='*70}")
    print("TOP 5: Highest PAC Preservation")
    print(f"{'='*70}")
    top5 = sorted(results, key=lambda x: x['pac_score'], reverse=True)[:5]
    for i, r in enumerate(top5, 1):
        print(f"  {i}. {r['event'].title}")
        print(f"      PAC Score: {r['pac_score']:.2f} | Actor: {r['event'].actor}")
    
    print(f"\n{'='*70}")
    print("BOTTOM 5: Lowest PAC Preservation")
    print(f"{'='*70}")
    bottom5 = sorted(results, key=lambda x: x['pac_score'])[:5]
    for i, r in enumerate(bottom5, 1):
        print(f"  {i}. {r['event'].title}")
        print(f"      PAC Score: {r['pac_score']:.2f} | Actor: {r['event'].actor}")
    
    print(f"\n{'='*70}")
    print("EVALUATION COMPLETE")
    print(f"{'='*70}")
    
    return results


if __name__ == "__main__":
    results = evaluate_all_events()
