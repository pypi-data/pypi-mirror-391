"""Data cleaning and preparation for Playbook content."""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PlaybookCleaner:
    """Clean and normalize scraped Playbook data."""
    
    def __init__(self, raw_data_dir: str, cleaned_data_dir: str):
        self.raw_data_dir = Path(raw_data_dir)
        self.cleaned_data_dir = Path(cleaned_data_dir)
        self.cleaned_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Track statistics
        self.stats = {
            'total_pages': 0,
            'cleaned_pages': 0,
            'documents': 0,
            'folders': 0,
            'errors': 0
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common UI patterns
        ui_patterns = [
            r'No elements found\. Consider changing the search query\.',
            r'List is empty\.',
            r'Recent changes',
            r'Your subscriptions',
        ]
        for pattern in ui_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def filter_links(self, links: List[Dict]) -> List[Dict]:
        """Filter out UI/navigation links, keep only content links."""
        if not links:
            return []
        
        # UI patterns to filter out (more conservative - only obvious UI elements)
        ui_patterns = [
            'angle-', 'arrow-', 'caret-', 'chevron-', 'circle-',
            'accessible', 'sign language', 'wheelchair', 'volume',
            'no elements', 'list is empty', 'recent changes',
            'your subscriptions'
        ]
        
        cleaned_links = []
        seen_urls = set()
        
        for link in links:
            url = link.get('url', '')
            text = link.get('text', '').lower()
            link_type = link.get('type', '')
            
            # Skip if obvious UI icon pattern (with hyphen to be specific)
            if any(pattern in text for pattern in ui_patterns):
                continue
            
            # Skip if too short or empty
            if len(text) < 3:
                continue
            
            # Skip if duplicate URL
            if url in seen_urls:
                continue
            
            # Only keep folder or document types
            if link_type not in ['folder', 'document']:
                continue
            
            seen_urls.add(url)
            cleaned_links.append({
                'url': url,
                'text': text,
                'type': link_type
            })
        
        return cleaned_links
    
    def extract_key_content(self, page_data: Dict) -> Dict:
        """Extract and clean key content from a page."""
        content = page_data.get('content', {})
        
        # Extract clean text
        main_text = self.clean_text(content.get('text', ''))
        
        # Extract headings
        headings = []
        for heading in content.get('headings', []):
            heading_text = self.clean_text(heading.get('text', ''))
            if heading_text and len(heading_text) > 2:
                headings.append({
                    'level': heading.get('level', 'h1'),
                    'text': heading_text
                })
        
        # Filter links
        links = self.filter_links(page_data.get('links', []))
        
        # Extract metadata
        metadata = page_data.get('metadata', {})
        breadcrumb = page_data.get('breadcrumb', [])
        
        return {
            'url': page_data.get('url', ''),
            'title': self.clean_text(page_data.get('title', '')),
            'type': page_data.get('type', 'unknown'),
            'scraped_at': page_data.get('scraped_at', ''),
            'breadcrumb': breadcrumb,
            'path': ' > '.join(breadcrumb),
            'text': main_text,
            'headings': headings,
            'links': links,
            'metadata': {
                'created': metadata.get('created'),
                'updated': metadata.get('updated'),
                'owner': metadata.get('owner')
            },
            'stats': {
                'text_length': len(main_text),
                'num_headings': len(headings),
                'num_links': len(links)
            }
        }
    
    def clean_page(self, page_file: Path) -> Optional[Dict]:
        """Clean a single page file."""
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
            
            cleaned = self.extract_key_content(page_data)
            
            # Skip if no meaningful content
            if cleaned['stats']['text_length'] < 10 and cleaned['stats']['num_headings'] == 0:
                logger.debug(f"Skipping page with no content: {cleaned['url']}")
                return None
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning {page_file}: {e}")
            self.stats['errors'] += 1
            return None
    
    def clean_all_pages(self) -> Dict[str, Dict]:
        """Clean all pages in the raw data directory."""
        logger.info(f"Cleaning pages from {self.raw_data_dir}")
        
        cleaned_pages = {}
        page_files = list(self.raw_data_dir.glob('*.json'))
        
        self.stats['total_pages'] = len(page_files)
        
        for page_file in page_files:
            cleaned = self.clean_page(page_file)
            
            if cleaned:
                url = cleaned['url']
                cleaned_pages[url] = cleaned
                
                self.stats['cleaned_pages'] += 1
                if cleaned['type'] == 'document':
                    self.stats['documents'] += 1
                elif cleaned['type'] == 'folder':
                    self.stats['folders'] += 1
                
                # Log progress
                if self.stats['cleaned_pages'] % 50 == 0:
                    logger.info(f"Cleaned {self.stats['cleaned_pages']}/{self.stats['total_pages']} pages")
        
        logger.info(f"Cleaning complete: {self.stats}")
        return cleaned_pages
    
    def save_cleaned_data(self, cleaned_pages: Dict[str, Dict]):
        """Save cleaned pages to disk."""
        output_file = self.cleaned_data_dir / 'cleaned_pages.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_pages, f, indent=2, ensure_ascii=False)
        
        # Save index for quick lookup
        index = {
            url: {
                'title': page['title'],
                'type': page['type'],
                'path': page['path'],
                'text_length': page['stats']['text_length']
            }
            for url, page in cleaned_pages.items()
        }
        
        index_file = self.cleaned_data_dir / 'index.json'
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        # Save stats
        stats_file = self.cleaned_data_dir / 'stats.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
        
        logger.info(f"Saved cleaned data to {output_file}")
        logger.info(f"Saved index to {index_file}")
    
    def run(self):
        """Run the complete cleaning process."""
        logger.info("Starting data cleaning process")
        cleaned_pages = self.clean_all_pages()
        self.save_cleaned_data(cleaned_pages)
        logger.info("Data cleaning complete!")
        return cleaned_pages


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Clean the data
    raw_dir = "/Users/kirtijha/Downloads/playbook_data/pages"
    cleaned_dir = "../data/cleaned"
    
    cleaner = PlaybookCleaner(raw_dir, cleaned_dir)
    cleaner.run()
