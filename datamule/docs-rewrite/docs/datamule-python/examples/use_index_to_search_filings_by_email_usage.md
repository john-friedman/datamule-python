# Using Index() to search filings by email usage

Construct data using `Index()`.

```
import csv
from datamule import Index

index = Index()

common_email_domains = [
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "icloud.com",
    "aol.com",
    "protonmail.com",
    "mail.com",
    "zoho.com",
    "yandex.com",
    "gmx.com",
    "inbox.com",
    "live.com",
    "msn.com",
    "me.com",
    "mac.com",
    "yahoo.co.uk",
    "yahoo.co.in",
    "fastmail.com",
    "tutanota.com"
]

# Open CSV file for writing
with open('sec_email_findings.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['accession', 'filing_date', 'filename', 'domain']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write header
    writer.writeheader()
    
    # Search for each domain
    for domain in common_email_domains:
        print(f"\nSearching for @{domain}...")
        
        results = index.search_submissions(
            text_query=f'"@{domain}"',
            requests_per_second=5.0,
            quiet=False,
        )
        
        # Write each result to CSV
        for result in results:
            # Extract the _id and split at colon
            doc_id = result['_id']
            accession, filename = doc_id.split(':', 1)
            
            # Extract filing date from _source
            filing_date = result['_source'].get('file_date', '')
            
            # Write row to CSV
            writer.writerow({
                'accession': accession,
                'filing_date': filing_date,
                'filename': filename,
                'domain': domain
            })
        
        print(f"Found {len(results)} results for @{domain}")

print("\nCSV file created successfully!")
```

## Plots
![Email Domain Race](../images/email_domain_race_lines.gif)
![Email Domain Race Cumulative](../images/email_domain_race_cumulative.gif)


## Plotting code

Plot email popularity
```
import csv
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
import matplotlib.animation as animation
import numpy as np

# Dictionary to store counts by domain and year
domain_year_counts = defaultdict(lambda: defaultdict(int))

def extract_base_domain(full_domain):
    """Extract base domain name (e.g., 'yahoo' from 'yahoo.com' or 'yahoo.co.uk')"""
    return full_domain.split('.')[0]

# Read the existing CSV file
with open('sec_email_findings.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        filing_date = row['filing_date']
        full_domain = row['domain']
        
        # Extract base domain
        base_domain = extract_base_domain(full_domain)
        
        # Count by year for plotting
        if filing_date:
            try:
                year = datetime.strptime(filing_date, '%Y-%m-%d').year
                if year != 2026:  # Exclude 2026
                    domain_year_counts[base_domain][year] += 1
            except ValueError:
                pass

# Get all years and sort them
all_years = sorted(set(year for domain_data in domain_year_counts.values() for year in domain_data.keys()))

def get_top_5_domains_up_to_year(end_year):
    """Get top 5 domains based on count at a specific year"""
    year_counts = {}
    for domain, year_data in domain_year_counts.items():
        year_counts[domain] = year_data[end_year]
    
    # Sort by count and get top 5
    top_5 = sorted(year_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return [domain for domain, count in top_5 if count > 0]

# Prepare figure
fig, ax = plt.subplots(figsize=(14, 8))

# Color map for domains
all_domains = list(domain_year_counts.keys())
colors = plt.cm.tab10(np.linspace(0, 1, len(all_domains)))
domain_colors = {domain: colors[i] for i, domain in enumerate(all_domains)}

# Store line objects for each domain
lines = {}
for domain in all_domains:
    line, = ax.plot([], [], marker='o', linewidth=2.5, markersize=6, 
                    label=domain, color=domain_colors[domain], alpha=0)
    lines[domain] = line

# Number of intermediate frames between years
FRAMES_PER_YEAR = 10
total_frames = (len(all_years) - 1) * FRAMES_PER_YEAR + 1

def interpolate_counts(domain, year_idx, progress):
    """Interpolate count values between two years"""
    if year_idx >= len(all_years) - 1:
        return domain_year_counts[domain][all_years[year_idx]]
    
    year1 = all_years[year_idx]
    year2 = all_years[year_idx + 1]
    count1 = domain_year_counts[domain][year1]
    count2 = domain_year_counts[domain][year2]
    
    # Linear interpolation
    return count1 + (count2 - count1) * progress

def animate(frame):
    # Calculate which year we're in and progress through that year
    year_idx = frame // FRAMES_PER_YEAR
    progress = (frame % FRAMES_PER_YEAR) / FRAMES_PER_YEAR
    
    if year_idx >= len(all_years):
        year_idx = len(all_years) - 1
        progress = 1.0
    
    current_year = all_years[year_idx]
    
    # Get top 5 domains for current year
    top_5_domains = get_top_5_domains_up_to_year(current_year)
    
    # Get years and interpolated current position
    years_so_far = all_years[:year_idx + 1]
    if progress > 0 and year_idx < len(all_years) - 1:
        current_x = current_year + progress
        years_display = years_so_far + [current_x]
    else:
        years_display = years_so_far
    
    # Update each domain's line
    for domain in all_domains:
        counts = [domain_year_counts[domain][year] for year in years_so_far]
        
        # Add interpolated point if we're between years
        if progress > 0 and year_idx < len(all_years) - 1:
            interpolated_count = interpolate_counts(domain, year_idx, progress)
            counts_display = counts + [interpolated_count]
        else:
            counts_display = counts
        
        # Only show if domain is in top 5 for current year
        if domain in top_5_domains:
            lines[domain].set_data(years_display, counts_display)
            lines[domain].set_alpha(1.0)  # Fully visible
        else:
            lines[domain].set_data(years_display, counts_display)
            lines[domain].set_alpha(0.15)  # Faded out
    
    # Update axes limits
    if progress > 0 and year_idx < len(all_years) - 1:
        ax.set_xlim(all_years[0] - 0.5, current_year + progress + 0.5)
    else:
        ax.set_xlim(all_years[0] - 0.5, current_year + 0.5)
    
    # Get max count for scaling
    max_count = 1
    for domain in top_5_domains:
        for year in years_so_far:
            count = domain_year_counts[domain][year]
            max_count = max(max_count, count)
    
    ax.set_ylim(0.5, max_count * 1.15)
    
    # Update title - just show current year as integer
    ax.set_title(f'Top 5 Email Domains in SEC Filings - {current_year}', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Update legend to only show top 5
    handles = [lines[domain] for domain in top_5_domains]
    labels = top_5_domains
    ax.legend(handles, labels, loc='upper left', fontsize=11, framealpha=0.9)
    
    return list(lines.values())

# Set up the plot
ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Number of Occurrences (log scale)', fontsize=13, fontweight='bold')
ax.set_yscale('log')
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
ax.set_facecolor('#f8f9fa')

# Create animation - 2x slower: changed fps from 20 to 10
print(f"Creating animated racing line chart with {total_frames} frames... this may take a moment...")
anim = animation.FuncAnimation(fig, animate, frames=total_frames, 
                              interval=50, repeat=True, blit=False)

# Save as gif - 2x slower: fps changed from 20 to 10
anim.save('email_domain_race_lines.gif', writer='pillow', fps=10, dpi=100)
print("Animation saved as 'email_domain_race_lines.gif'")

plt.close()
```

Cumulative
```
import csv
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
import matplotlib.animation as animation
import numpy as np

# Dictionary to store counts by domain and year
domain_year_counts = defaultdict(lambda: defaultdict(int))

def extract_base_domain(full_domain):
    """Extract base domain name (e.g., 'yahoo' from 'yahoo.com' or 'yahoo.co.uk')"""
    return full_domain.split('.')[0]

# Read the existing CSV file
with open('sec_email_findings.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        filing_date = row['filing_date']
        full_domain = row['domain']
        
        # Extract base domain
        base_domain = extract_base_domain(full_domain)
        
        # Count by year for plotting
        if filing_date:
            try:
                year = datetime.strptime(filing_date, '%Y-%m-%d').year
                if year != 2026:  # Exclude 2026
                    domain_year_counts[base_domain][year] += 1
            except ValueError:
                pass

# Get all years and sort them
all_years = sorted(set(year for domain_data in domain_year_counts.values() for year in domain_data.keys()))

# Calculate cumulative sums for each domain
domain_cumsum = defaultdict(dict)
for domain in domain_year_counts:
    cumsum = 0
    for year in all_years:
        cumsum += domain_year_counts[domain][year]
        domain_cumsum[domain][year] = cumsum

# Calculate the maximum cumulative value across all domains and all years
max_cumsum_overall = 0
for domain in domain_cumsum:
    if all_years:
        final_cumsum = domain_cumsum[domain][all_years[-1]]
        max_cumsum_overall = max(max_cumsum_overall, final_cumsum)

def get_top_5_domains_cumulative(end_year):
    """Get top 5 domains based on cumulative count up to a specific year"""
    cumulative_counts = {}
    for domain in domain_cumsum:
        cumulative_counts[domain] = domain_cumsum[domain].get(end_year, 0)
    
    # Sort by cumulative count and get top 5
    top_5 = sorted(cumulative_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return [domain for domain, count in top_5 if count > 0]

# Prepare figure
fig, ax = plt.subplots(figsize=(14, 8))

# Color map for domains
all_domains = list(domain_year_counts.keys())
colors = plt.cm.tab10(np.linspace(0, 1, len(all_domains)))
domain_colors = {domain: colors[i] for i, domain in enumerate(all_domains)}

# Store line objects for each domain
lines = {}
for domain in all_domains:
    line, = ax.plot([], [], marker='o', linewidth=2.5, markersize=6, 
                    label=domain, color=domain_colors[domain], alpha=0)
    lines[domain] = line

# Number of intermediate frames between years
FRAMES_PER_YEAR = 10
# Add extra frames for the pause at the end (5 seconds at 20fps = 100 frames)
PAUSE_FRAMES = 100
animation_frames = (len(all_years) - 1) * FRAMES_PER_YEAR + 1
total_frames = animation_frames + PAUSE_FRAMES

def interpolate_cumsum(domain, year_idx, progress):
    """Interpolate cumulative count values between two years"""
    if year_idx >= len(all_years) - 1:
        return domain_cumsum[domain][all_years[year_idx]]
    
    year1 = all_years[year_idx]
    year2 = all_years[year_idx + 1]
    cumsum1 = domain_cumsum[domain][year1]
    cumsum2 = domain_cumsum[domain][year2]
    
    # Linear interpolation
    return cumsum1 + (cumsum2 - cumsum1) * progress

def animate(frame):
    # If we're in the pause frames, just keep showing the final state
    if frame >= animation_frames:
        frame = animation_frames - 1
    
    # Calculate which year we're in and progress through that year
    year_idx = frame // FRAMES_PER_YEAR
    progress = (frame % FRAMES_PER_YEAR) / FRAMES_PER_YEAR
    
    if year_idx >= len(all_years):
        year_idx = len(all_years) - 1
        progress = 1.0
    
    current_year = all_years[year_idx]
    
    # Get top 5 domains for current year (based on cumulative)
    top_5_domains = get_top_5_domains_cumulative(current_year)
    
    # Get years and interpolated current position
    years_so_far = all_years[:year_idx + 1]
    if progress > 0 and year_idx < len(all_years) - 1:
        current_x = current_year + progress
        years_display = years_so_far + [current_x]
    else:
        years_display = years_so_far
    
    # Update each domain's line
    for domain in all_domains:
        cumsums = [domain_cumsum[domain][year] for year in years_so_far]
        
        # Add interpolated point if we're between years
        if progress > 0 and year_idx < len(all_years) - 1:
            interpolated_cumsum = interpolate_cumsum(domain, year_idx, progress)
            cumsums_display = cumsums + [interpolated_cumsum]
        else:
            cumsums_display = cumsums
        
        # Only show if domain is in top 5 for current year
        if domain in top_5_domains:
            lines[domain].set_data(years_display, cumsums_display)
            lines[domain].set_alpha(1.0)  # Fully visible
        else:
            lines[domain].set_data(years_display, cumsums_display)
            lines[domain].set_alpha(0.15)  # Faded out
    
    # Update axes limits
    if progress > 0 and year_idx < len(all_years) - 1:
        ax.set_xlim(all_years[0] - 0.5, current_year + progress + 0.5)
    else:
        ax.set_xlim(all_years[0] - 0.5, current_year + 0.5)
    
    # Keep y-axis constant throughout the entire animation
    ax.set_ylim(0, max_cumsum_overall * 1.25)
    
    # Update title
    ax.set_title(f'Top 5 Email Domains in SEC Filings (Cumulative) - {current_year}', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Update legend to only show top 5
    handles = [lines[domain] for domain in top_5_domains]
    labels = top_5_domains
    ax.legend(handles, labels, loc='upper left', fontsize=11, framealpha=0.9)
    
    return list(lines.values())

# Set up the plot
ax.set_xlabel('Year', fontsize=13, fontweight='bold')
ax.set_ylabel('Cumulative Occurrences', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
ax.set_facecolor('#f8f9fa')

# Create animation
print(f"Creating cumulative animated racing line chart with {total_frames} frames (including 5 second pause at end)... this may take a moment...")
anim = animation.FuncAnimation(fig, animate, frames=total_frames, 
                              interval=50, repeat=True, blit=False)

# Save as gif
anim.save('email_domain_race_cumulative.gif', writer='pillow', fps=20, dpi=100)
print("Animation saved as 'email_domain_race_cumulative.gif'")

plt.close()
```