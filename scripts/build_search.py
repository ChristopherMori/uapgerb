#!/usr/bin/env python3
"""
Build search index for the YouTube wiki
Processes all video pages and creates searchable JSON index
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

def extract_frontmatter_and_content(file_path):
    """Extract YAML frontmatter and content from markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split frontmatter and content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()
        else:
            frontmatter = ""
            body = content
    else:
        frontmatter = ""
        body = content
    
    # Parse frontmatter
    metadata = {}
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"\'')
    
    return metadata, body

def clean_text(text):
    """Clean text for search indexing"""
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # Code
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Links
    text = re.sub(r'#{1,6}\s*', '', text)         # Headers
    text = re.sub(r'\n+', ' ', text)              # Multiple newlines
    text = re.sub(r'\s+', ' ', text)              # Multiple spaces
    return text.strip()

def build_search_index():
    """Build search index from all video pages"""
    pages_dir = Path('pages')
    search_data = []
    recent_videos = []
    
    if not pages_dir.exists():
        print("Pages directory not found. Creating empty search index.")
        # Create empty data files
        os.makedirs('_data', exist_ok=True)
        
        with open('_data/search.json', 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
        
        with open('_data/recent.json', 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
        
        return
    
    print(f"Processing pages from {pages_dir}")
    
    # Process all markdown files in pages directory
    for md_file in pages_dir.glob('*.md'):
        try:
            print(f"Processing {md_file.name}")
            
            metadata, content = extract_frontmatter_and_content(md_file)
            
            # Extract key information
            title = metadata.get('title', md_file.stem)
            date = metadata.get('date', '')
            duration = metadata.get('duration', '')
            video_id = metadata.get('video_id', '')
            youtube_url = metadata.get('youtube_url', '')
            
            # Clean content for search
            clean_content = clean_text(content)
            
            # Create search document
            search_doc = {
                'title': title,
                'url': f"/pages/{md_file.name}",
                'date': date,
                'duration': duration,
                'video_id': video_id,
                'youtube_url': youtube_url,
                'body': clean_content[:2000]  # Limit content length
            }
            
            search_data.append(search_doc)
            
            # Add to recent videos (for homepage)
            recent_video = {
                'title': title,
                'url': f"/pages/{md_file.name}",
                'date': date,
                'duration': duration,
                'youtube_url': youtube_url
            }
            
            recent_videos.append(recent_video)
            
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            continue
    
    # Sort recent videos by date (newest first)
    try:
        recent_videos.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
    except:
        # If date parsing fails, keep original order
        pass
    
    # Create _data directory
    os.makedirs('_data', exist_ok=True)
    
    # Write search index
    with open('_data/search.json', 'w', encoding='utf-8') as f:
        json.dump(search_data, f, indent=2, ensure_ascii=False)
    
    # Write recent videos
    with open('_data/recent.json', 'w', encoding='utf-8') as f:
        json.dump(recent_videos, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Search index built successfully!")
    print(f"   📊 {len(search_data)} videos indexed")
    print(f"   📁 Search data: _data/search.json")
    print(f"   📁 Recent videos: _data/recent.json")

if __name__ == "__main__":
    build_search_index()


