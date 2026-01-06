import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import datetime
import os

# Configuration
# Searching for Quantitative Biology (q-bio) updates
QUERY = 'cat:q-bio.BM OR cat:q-bio.GN OR cat:q-bio.MN'
MAX_RESULTS = 5
README_PATH = 'README.md'

def fetch_arxiv_papers():
    base_url = 'http://export.arxiv.org/api/query?'
    # Sort by submittedDate descending to get latest
    params = {
        'search_query': QUERY,
        'start': 0,
        'max_results': MAX_RESULTS,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    url = base_url + urllib.parse.urlencode(params)
    data = urllib.request.urlopen(url)
    return data.read().decode('utf-8')

def parse_papers(xml_data):
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.replace('\n', ' ').strip()
        link = entry.find('atom:id', ns).text
        published = entry.find('atom:published', ns).text[:10] # YYYY-MM-DD
        summary = entry.find('atom:summary', ns).text.replace('\n', ' ').strip()[:200] + "..."
        
        # Extract categories
        categories = []
        for cat in entry.findall('atom:category', ns):
            categories.append(cat.get('term'))
            
        papers.append({
            'title': title,
            'link': link,
            'published': published,
            'summary': summary,
            'categories': ', '.join(categories[:2])
        })
    return papers

def update_readme(papers):
    if not papers:
        print("No papers found.")
        return

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    new_content = f"\n### 🆕 Latest q-bio Research ({current_date})\n"
    for p in papers:
        new_content += f"- **[{p['title']}]({p['link']})** ({p['published']})\n"
        new_content += f"  > *{p['summary']}*\n"
    
    if not os.path.exists(README_PATH):
        print("README.md not found!")
        return

    with open(README_PATH, 'r') as f:
        content = f.read()

    # Insert before the "Timeline & Milestones" section or append
    marker = "## Timeline & Milestones"
    
    # We want to maintain a "Recent Research" section. 
    # If we already have one, append to it. If not, create it.
    research_header = "## Recent Research Feed"
    
    if research_header in content:
        updated_content = content.replace(research_header, research_header + new_content)
    elif marker in content:
        # Insert before timeline
        updated_content = content.replace(marker, research_header + "\n" + new_content + "\n\n" + marker)
    else:
        # Fallback
        updated_content = content + "\n\n" + research_header + "\n" + new_content

    with open(README_PATH, 'w') as f:
        f.write(updated_content)
    
    print(f"Added {len(papers)} papers to README.md")

if __name__ == "__main__":
    print("Fetching Quantitative Biology papers...")
    xml_data = fetch_arxiv_papers()
    papers = parse_papers(xml_data)
    update_readme(papers)
