"""
examples/visualize_results.py - Generate shareable visualizations of SERAA evaluations

Creates social media-ready charts and infographics.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.event_database import event_db
from examples.real_world_evaluator import RealWorldEvaluator


def determine_domain(event):
    """Determine domain for event."""
    actor = event.actor.lower()
    if any(d in actor for d in ['president', 'congress', 'court', 'government', 'parliament', 'eu']):
        return 'government'
    elif any(d in actor for d in ['facebook', 'google', 'apple', 'twitter', 'amazon', 'microsoft', 'bytedance', 'signal']):
        return 'tech'
    elif any(d in actor for d in ['hospital', 'pharma', 'health', 'cdc', 'fda', 'medical']):
        return 'healthcare'
    else:
        return 'corporate'


def evaluate_all_quick():
    """Quick evaluation to get PAC scores."""
    events = event_db.get_all()
    results = []
    
    for event in events:
        domain = determine_domain(event)
        try:
            evaluator = RealWorldEvaluator(domain=domain)
            result = evaluator.evaluate_event(event)
            results.append(result)
        except:
            results.append({
                'event': event,
                'pac_score': event.outcomes.get('pac_score', 0.5),
                'approved': False
            })
    
    return results


def create_pac_score_distribution(results, output_path='pac_distribution.png'):
    """Create PAC score distribution histogram."""
    pac_scores = [r['pac_score'] for r in results]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create histogram
    n, bins, patches = ax.hist(pac_scores, bins=20, edgecolor='black', alpha=0.7)
    
    # Color bars by category
    for i, patch in enumerate(patches):
        bin_center = (bins[i] + bins[i+1]) / 2
        if bin_center >= 0.8:
            patch.set_facecolor('#2ecc71')  # Green - Excellent
        elif bin_center >= 0.6:
            patch.set_facecolor('#3498db')  # Blue - Acceptable
        elif bin_center >= 0.4:
            patch.set_facecolor('#f39c12')  # Orange - Problematic
        else:
            patch.set_facecolor('#e74c3c')  # Red - Violations
    
    ax.set_xlabel('PAC Score', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Decisions', fontsize=14, fontweight='bold')
    ax.set_title('SERAA Evaluation: Distribution of PAC Scores\n35 Major Real-World Decisions', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Add legend
    green_patch = mpatches.Patch(color='#2ecc71', label='Excellent (≥0.8)')
    blue_patch = mpatches.Patch(color='#3498db', label='Acceptable (0.6-0.8)')
    orange_patch = mpatches.Patch(color='#f39c12', label='Problematic (0.4-0.6)')
    red_patch = mpatches.Patch(color='#e74c3c', label='Violations (<0.4)')
    ax.legend(handles=[green_patch, blue_patch, orange_patch, red_patch], 
              loc='upper right', fontsize=11)
    
    # Add statistics text
    mean_pac = np.mean(pac_scores)
    median_pac = np.median(pac_scores)
    stats_text = f'Mean: {mean_pac:.2f}\nMedian: {median_pac:.2f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_domain_comparison(results, output_path='domain_comparison.png'):
    """Create domain-wise PAC score comparison."""
    # Categorize by domain
    domain_scores = {'Government': [], 'Corporate': [], 'Technology': [], 'Healthcare': []}
    
    for r in results:
        domain = determine_domain(r['event'])
        if domain == 'government':
            domain_scores['Government'].append(r['pac_score'])
        elif domain == 'tech':
            domain_scores['Technology'].append(r['pac_score'])
        elif domain == 'healthcare':
            domain_scores['Healthcare'].append(r['pac_score'])
        else:
            domain_scores['Corporate'].append(r['pac_score'])
    
    # Calculate means
    domain_means = {k: np.mean(v) if v else 0 for k, v in domain_scores.items()}
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    domains = list(domain_means.keys())
    means = list(domain_means.values())
    colors = ['#3498db', '#e74c3c', '#9b59b6', '#2ecc71']
    
    bars = ax.bar(domains, means, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('Average PAC Score', fontsize=14, fontweight='bold')
    ax.set_title('SERAA Evaluation: PAC Preservation by Domain\n35 Major Real-World Decisions', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 1.0)
    
    # Add reference line at 0.7 (acceptable threshold)
    ax.axhline(y=0.7, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Acceptable Threshold (0.7)')
    ax.legend(fontsize=11)
    
    # Add count labels
    for i, domain in enumerate(domains):
        count = len(domain_scores[domain])
        ax.text(i, 0.05, f'n={count}', ha='center', fontsize=10, style='italic')
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_top_bottom_comparison(results, output_path='top_bottom_decisions.png'):
    """Create comparison of best and worst decisions."""
    sorted_results = sorted(results, key=lambda x: x['pac_score'])
    
    bottom_5 = sorted_results[:5]
    top_5 = sorted_results[-5:][::-1]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Bottom 5 (Worst)
    titles_bottom = [r['event'].title[:40] + '...' if len(r['event'].title) > 40 else r['event'].title 
                     for r in bottom_5]
    scores_bottom = [r['pac_score'] for r in bottom_5]
    
    ax1.barh(range(5), scores_bottom, color='#e74c3c', alpha=0.7, edgecolor='black')
    ax1.set_yticks(range(5))
    ax1.set_yticklabels(titles_bottom, fontsize=10)
    ax1.set_xlabel('PAC Score', fontsize=12, fontweight='bold')
    ax1.set_title('Bottom 5: Lowest PAC Preservation', fontsize=14, fontweight='bold', color='#e74c3c')
    ax1.set_xlim(0, 1.0)
    ax1.invert_yaxis()
    
    for i, score in enumerate(scores_bottom):
        ax1.text(score + 0.02, i, f'{score:.2f}', va='center', fontsize=10, fontweight='bold')
    
    # Top 5 (Best)
    titles_top = [r['event'].title[:40] + '...' if len(r['event'].title) > 40 else r['event'].title 
                  for r in top_5]
    scores_top = [r['pac_score'] for r in top_5]
    
    ax2.barh(range(5), scores_top, color='#2ecc71', alpha=0.7, edgecolor='black')
    ax2.set_yticks(range(5))
    ax2.set_yticklabels(titles_top, fontsize=10)
    ax2.set_xlabel('PAC Score', fontsize=12, fontweight='bold')
    ax2.set_title('Top 5: Highest PAC Preservation', fontsize=14, fontweight='bold', color='#2ecc71')
    ax2.set_xlim(0, 1.0)
    ax2.invert_yaxis()
    
    for i, score in enumerate(scores_top):
        ax2.text(score - 0.02, i, f'{score:.2f}', va='center', ha='right', fontsize=10, fontweight='bold')
    
    plt.suptitle('SERAA Evaluation: Best vs. Worst Decisions for Agency Preservation', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_timeline_view(results, output_path='timeline.png'):
    """Create timeline of PAC scores over years."""
    # Extract years and scores
    timeline_data = []
    for r in results:
        date_str = r['event'].date
        try:
            # Extract year from various date formats
            if '-' in date_str:
                year = int(date_str.split('-')[0]) if date_str[:4].isdigit() else None
            else:
                year = int(date_str.split()[-1]) if date_str.split()[-1].isdigit() else None
            
            if year:
                timeline_data.append((year, r['pac_score'], r['event'].title))
        except:
            pass
    
    timeline_data.sort()
    
    years = [d[0] for d in timeline_data]
    scores = [d[1] for d in timeline_data]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Color points by score
    colors = ['#2ecc71' if s >= 0.8 else '#3498db' if s >= 0.6 else '#f39c12' if s >= 0.4 else '#e74c3c' 
              for s in scores]
    
    ax.scatter(years, scores, c=colors, s=200, alpha=0.6, edgecolors='black', linewidth=2)
    
    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('PAC Score', fontsize=14, fontweight='bold')
    ax.set_title('SERAA Evaluation: PAC Preservation Over Time\n1932-2024', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(-0.05, 1.05)
    
    # Add threshold line
    ax.axhline(y=0.7, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Acceptable Threshold')
    
    # Add legend
    green_patch = mpatches.Patch(color='#2ecc71', label='Excellent (≥0.8)')
    blue_patch = mpatches.Patch(color='#3498db', label='Acceptable (0.6-0.8)')
    orange_patch = mpatches.Patch(color='#f39c12', label='Problematic (0.4-0.6)')
    red_patch = mpatches.Patch(color='#e74c3c', label='Violations (<0.4)')
    ax.legend(handles=[green_patch, blue_patch, orange_patch, red_patch], 
              loc='lower left', fontsize=11)
    
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_approval_pie(results, output_path='approval_rate.png'):
    """Create pie chart of approval rates."""
    approved = sum(1 for r in results if r['approved'])
    rejected = len(results) - approved
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sizes = [approved, rejected]
    labels = [f'Ethically Approved\n({approved} decisions)', 
              f'Ethically Rejected\n({rejected} decisions)']
    colors = ['#2ecc71', '#e74c3c']
    explode = (0.05, 0.05)
    
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                        autopct='%1.1f%%', startangle=90, textprops={'fontsize': 14})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(16)
    
    ax.set_title('SERAA Evaluation: Ethical Approval Rate\n35 Major Real-World Decisions', 
                 fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def generate_all_visualizations():
    """Generate all visualization assets."""
    print("="*70)
    print("GENERATING SERAA VISUALIZATIONS")
    print("="*70)
    print("\nEvaluating all 35 events (this may take a minute)...")
    
    results = evaluate_all_quick()
    
    print(f"\nGenerating visualizations...\n")
    
    # Create output directory
    output_dir = Path('visualizations')
    output_dir.mkdir(exist_ok=True)
    
    # Generate all charts
    create_pac_score_distribution(results, output_dir / 'pac_distribution.png')
    create_domain_comparison(results, output_dir / 'domain_comparison.png')
    create_top_bottom_comparison(results, output_dir / 'top_bottom_decisions.png')
    create_timeline_view(results, output_dir / 'timeline.png')
    create_approval_pie(results, output_dir / 'approval_rate.png')
    
    print("\n" + "="*70)
    print("✅ ALL VISUALIZATIONS GENERATED")
    print("="*70)
    print(f"\nFind your images in: {output_dir.absolute()}/")
    print("\nFiles created:")
    print("  • pac_distribution.png - PAC score histogram")
    print("  • domain_comparison.png - Average PAC by domain")
    print("  • top_bottom_decisions.png - Best vs worst decisions")
    print("  • timeline.png - PAC scores over time (1932-2024)")
    print("  • approval_rate.png - Ethical approval pie chart")
    print("\n📱 Ready to share on social media!")


if __name__ == "__main__":
    generate_all_visualizations()
