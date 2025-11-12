"""
EnhancedSpider.py - Research V4
Multi-domain research spider with API credit monitoring
Domain-agnostic web scraping system
"""

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
from typing import List, Dict, Optional
import json
from datetime import datetime
import logging

try:
    from .ConfigManager import ConfigManager
    from .ApiMonitor import SerpAPIMonitor
except ImportError:
    from FlaskApp.services.v4.ConfigManager import ConfigManager
    from FlaskApp.services.v4.ApiMonitor import SerpAPIMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversalResearchSpider:
    """
    Domain-agnostic research spider with API monitoring.
    Supports any research domain configured in domains.json
    """

    def __init__(self, config: ConfigManager, check_credits: bool = True):
        """
        Initialize spider with configuration and API monitoring.
        
        Args:
            config: ConfigManager instance
            check_credits: Whether to check API credits before operations
        """
        self.config = config
        self.domain = config.get_current_domain()
        self.domain_info = config.get_domain_info()
        
        # API Monitoring
        self.api_monitor = SerpAPIMonitor(config) if check_credits else None
        self.check_credits = check_credits
        
        # Configuration
        self.serpapi_key = config.get_api_key()
        self.delay = config.get_search_delay()
        self.max_sources = config.get_max_sources()
        self.request_timeout = config.get_request_timeout()
        
        # Session setup
        self.session = requests.Session()
        self.session.headers.update(config.get_request_headers())
        
        # Domain-specific settings
        self.domain_reliability = self._build_domain_reliability()
        self.skip_domains = set(config.get_skip_domains())
        self.keywords = self.domain_info.get('keywords', [])
        
        search_cfg = config.get_search_config()
        self.supported_extensions = set(search_cfg.get('supported_extensions', []))
        self.unsupported_extensions = set(search_cfg.get('unsupported_extensions', []))
        
        logger.info(f"Initialized {self.domain} research spider")
    
    def _build_domain_reliability(self) -> Dict[str, float]:
        """Build flat domain reliability dictionary."""
        domain_reliability = {}
        config_domains = self.config.get_domain_reliability()
        
        for category, domains in config_domains.items():
            domain_reliability.update(domains)
        
        return domain_reliability
    
    def check_api_status(self, required_searches: int = 7) -> bool:
        """
        Check API status before starting research.
        
        Args:
            required_searches: Estimated number of searches needed
            
        Returns:
            True if can proceed, False otherwise
        """
        if not self.check_credits or not self.api_monitor:
            return True
        
        logger.info("Checking SerpAPI credit status...")
        
        status = self.api_monitor.check_credits(verbose=True)
        
        if not status['can_proceed']:
            logger.error("Insufficient API credits. Research blocked.")
            return False
        
        if status['searches_remaining'] < required_searches:
            logger.warning(f"Low credits: {status['searches_remaining']} remaining, need ~{required_searches}")
            
            if self.config.should_auto_stop_on_critical():
                logger.error("Auto-stop enabled. Halting research.")
                return False
            else:
                response = input(f"⚠️  Only {status['searches_remaining']} searches left. Continue? (y/n): ")
                return response.lower() == 'y'
        
        logger.info(f"✓ API credits OK: {status['searches_remaining']} searches available")
        return True
    
    def search_serpapi(self, query_term: str, domain_hint: str = None) -> List[Dict[str, str]]:
        """
        Search for information using SerpAPI with domain-specific targeting.
        
        Args:
            query_term: Main search term (e.g., plant name, disease, math concept)
            domain_hint: Optional hint about content type
            
        Returns:
            List of search results
        """
        try:
            logger.info(f"Searching SerpAPI for: {query_term} ({self.domain})")
            
            results = []
            
            # Build domain-specific queries
            queries = self._build_search_queries(query_term, domain_hint)
            
            for priority, query in queries:
                logger.info(f"  [{priority}] {query}")
                
                params = {
                    "q": query,
                    "api_key": self.serpapi_key,
                    "num": 30,
                    "engine": "google"
                }
                
                response = requests.get(
                    "https://serpapi.com/search", 
                    params=params, 
                    timeout=self.request_timeout
                )
                response.raise_for_status()
                data = response.json()
                
                organic_results = data.get("organic_results", [])
                logger.info(f"    → {len(organic_results)} results")
                
                for result in organic_results:
                    url = result.get('link', '')
                    
                    if url in [r['url'] for r in results]:
                        continue
                    
                    is_supported, doc_type = self._is_supported_document(url)
                    
                    if is_supported:
                        results.append({
                            'url': url,
                            'title': result.get('title', ''),
                            'snippet': result.get('snippet', ''),
                            'doc_type': doc_type,
                            'priority': priority,
                            'query': query
                        })
                
                # Stop if we have enough results
                if len(results) >= self.max_sources:
                    break
                
                time.sleep(1)  # Be polite
            
            filtered_results = self._filter_relevant_results(results, query_term)
            logger.info(f"✓ Found {len(filtered_results)} relevant results")
            
            return filtered_results[:self.max_sources + 10]
            
        except Exception as e:
            logger.error(f"Error searching SerpAPI: {str(e)}")
            return []
    
    def _build_search_queries(self, term: str, hint: str = None) -> List[tuple]:
        """
        Build domain-specific search queries.
        
        Returns:
            List of (priority, query) tuples
        """
        queries = []
        keywords = self.keywords[:3]  # Top 3 domain keywords
        
        # Priority 1: Academic/University sources
        for keyword in keywords:
            queries.append(('high', f'{term} {keyword} site:edu'))
            queries.append(('high', f'{term} {keyword} site:ac.uk'))
            queries.append(('high', f'{term} {keyword} site:ac.za'))
        
        # Priority 2: Research institutes and organizations
        for keyword in keywords:
            queries.append(('medium', f'{term} {keyword} research'))
            queries.append(('medium', f'{term} {keyword} institute'))
        
        # Priority 3: General scholarly content
        queries.append(('medium', f'{term} {" ".join(keywords[:2])}'))
        
        # Priority 4: Wikipedia and encyclopedic sources
        queries.append(('low', f'{term} site:wikipedia.org'))
        queries.append(('low', f'{term} site:britannica.com'))
        
        return queries
    
    def _is_supported_document(self, url: str) -> tuple:
        """Check if URL points to supported document type."""
        url_lower = url.lower()
        
        if url_lower.endswith('.pdf') or 'pdf' in url_lower:
            return True, 'pdf'
        
        if url_lower.endswith('.txt'):
            return True, 'text'
        
        for ext in self.unsupported_extensions:
            if url_lower.endswith(ext):
                return False, 'unsupported'
        
        return True, 'html'
    
    def _filter_relevant_results(self, results: List[Dict], term: str) -> List[Dict]:
        """Filter and rank results by relevance to domain."""
        term_words = term.lower().split()
        main_term = term_words[0] if term_words else ""
        
        scored_results = []
        seen_urls = set()
        
        for result in results:
            url = result['url']
            title = result['title'].lower()
            snippet = result.get('snippet', '').lower()
            priority = result.get('priority', 'low')
            
            if url in seen_urls:
                continue
            
            if any(skip in url.lower() for skip in self.skip_domains):
                continue
            
            seen_urls.add(url)
            score = 0
            
            # Priority scoring
            if priority == 'high':
                score += 30
            elif priority == 'medium':
                score += 20
            else:
                score += 10
            
            # Term matching
            if term.lower() in title:
                score += 15
            if term.lower() in snippet:
                score += 10
            
            if main_term and (main_term in title or main_term in snippet):
                score += 8
            
            # Domain keyword matching
            for keyword in self.keywords[:5]:
                if keyword in title:
                    score += 5
                if keyword in snippet:
                    score += 3
            
            # Domain reliability
            domain = urlparse(url).netloc
            if domain in self.domain_reliability:
                score += int(self.domain_reliability[domain] * 20)
            
            # Educational domains
            if any(edu in domain for edu in ['.edu', '.ac.', 'university', 'institute']):
                score += 15
            
            # Document type bonus
            if result.get('doc_type') == 'pdf':
                score += 8
            
            scored_results.append((score, result))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [result for score, result in scored_results if score > 15]
    
    def extract_content(self, url: str, doc_type: str = 'html') -> Optional[Dict]:
        """
        Extract content from URL.
        
        Args:
            url: URL to extract from
            doc_type: Document type (html, pdf, text)
            
        Returns:
            Dictionary with text and metadata
        """
        try:
            if doc_type == 'pdf':
                # Use existing PDF extraction
                content = self._extract_pdf_content(url)
                title = url.split('/')[-1].replace('.pdf', '').title()
            elif doc_type == 'text':
                content = self._extract_text_file(url)
                title = url.split('/')[-1].replace('.txt', '').title()
            else:
                response = self.session.get(url, timeout=self.request_timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                    element.decompose()
                
                title = self._extract_title(soup, url)
                content = self._extract_html_content(soup)
            
            if not content or len(content.strip()) < 150:
                return None
            
            domain = urlparse(url).netloc
            reliability_score = self._calculate_reliability(domain, content)
            
            metadata = {
                'source': self._get_source_name(domain, title),
                'reliability': self._get_reliability_level(reliability_score),
                'url': url,
                'domain': domain,
                'title': title,
                'scraped_date': datetime.now().strftime('%Y-%m-%d'),
                'research_domain': self.domain,
                'document_type': doc_type
            }
            
            return {
                'text': content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error extracting from {url}: {str(e)}")
            return None
    
    def _extract_pdf_content(self, url: str) -> Optional[str]:
        """Extract text from PDF."""
        # Implementation from original Spider.py
        import io
        import PyPDF2
        
        try:
            response = self.session.get(url, timeout=self.request_timeout)
            response.raise_for_status()
            
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page_num in range(min(len(pdf_reader.pages), 50)):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        text_parts.append(text.strip())
                except Exception:
                    continue
            
            return "\n\n".join(text_parts) if text_parts else None
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return None
    
    def _extract_text_file(self, url: str) -> Optional[str]:
        """Extract content from text file."""
        try:
            response = self.session.get(url, timeout=self.request_timeout)
            response.raise_for_status()
            
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    text = response.content.decode(encoding)
                    if text and len(text.strip()) > 50:
                        return text.strip()
                except UnicodeDecodeError:
                    continue
            
            return None
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract page title."""
        for selector in ['h1', 'title', '.page-title', '.entry-title']:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                if title and len(title) > 3:
                    return title
        return "Document"
    
    def _extract_html_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML."""
        content_parts = []
        
        # Try common content selectors
        selectors = [
            'article', 
            '.content', 
            '.entry-content', 
            'main',
            '#content',
            '.post-content'
        ]
        
        for selector in selectors:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all('p')
                for p in paragraphs[:15]:
                    text = p.get_text(strip=True)
                    if text and len(text) > 40:
                        content_parts.append(text)
                if len(content_parts) >= 5:
                    break
        
        # Fallback to all paragraphs
        if len(content_parts) < 3:
            paragraphs = soup.find_all('p')
            for p in paragraphs[:20]:
                text = p.get_text(strip=True)
                if text and len(text) > 40:
                    content_parts.append(text)
                if len(content_parts) >= 8:
                    break
        
        return "\n\n".join(content_parts[:10])
    
    def _calculate_reliability(self, domain: str, content: str) -> float:
        """Calculate source reliability score."""
        base_score = self.domain_reliability.get(domain, 0.5)
        
        # Boost for domain keywords
        content_lower = content.lower()
        keyword_matches = sum(1 for kw in self.keywords if kw in content_lower)
        base_score += min(0.1, keyword_matches * 0.02)
        
        # Boost for content length
        if len(content) > 1000:
            base_score += 0.05
        
        return min(1.0, base_score)
    
    def _get_reliability_level(self, score: float) -> str:
        """Convert score to reliability level."""
        if score >= 0.95:
            return "very_high"
        elif score >= 0.85:
            return "high"
        elif score >= 0.75:
            return "medium"
        else:
            return "low"
    
    def _get_source_name(self, domain: str, title: str) -> str:
        """Get clean source name."""
        # Try to get a nice name for the source
        if 'wikipedia' in domain:
            return 'Wikipedia'
        elif 'britannica' in domain:
            return 'Encyclopædia Britannica'
        elif 'edu' in domain:
            return domain.replace('.edu', '').replace('www.', '').title() + ' University'
        else:
            return title.split(' - ')[0] if ' - ' in title else domain
    
    def research(self, query_term: str, estimate_first: bool = True) -> List[Dict]:
        """
        Main research method with API monitoring.
        
        Args:
            query_term: Term to research
            estimate_first: Show cost estimate before proceeding
            
        Returns:
            List of sources
        """
        print(f"\n{'='*80}")
        print(f"🔬 UNIVERSAL RESEARCH SYSTEM V4")
        print(f"{'='*80}")
        print(f"Domain: {self.domain.upper()} - {self.domain_info.get('name', '')}")
        print(f"Query: {query_term}")
        print(f"{'='*80}\n")
        
        # Estimate cost
        if estimate_first and self.api_monitor:
            estimate = self.api_monitor.estimate_research_cost(query_term, questions=4)
            self.api_monitor.print_estimate(estimate)
            
            if not estimate['can_afford']:
                logger.error("Insufficient API credits for research")
                return []
        
        # Check API status
        if not self.check_api_status(required_searches=7):
            logger.error("API check failed. Aborting research.")
            return []
        
        # Perform search
        print("📚 Step 1: Searching for sources...")
        search_results = self.search_serpapi(query_term)
        print(f"✓ Found {len(search_results)} potential sources\n")
        
        # Extract content
        print("📄 Step 2: Extracting content...")
        sources = []
        processed_domains = {}
        
        for i, result in enumerate(search_results[:self.max_sources], 1):
            url = result['url']
            domain = urlparse(url).netloc
            doc_type = result.get('doc_type', 'html')
            
            # Limit per domain
            max_per_domain = 5 if 'edu' in domain or 'ac.' in domain else 3
            processed_domains[domain] = processed_domains.get(domain, 0)
            
            if processed_domains[domain] >= max_per_domain:
                continue
            
            print(f"  [{i}/{len(search_results)}] {result['title'][:60]}...")
            
            source = self.extract_content(url, doc_type)
            
            if source and len(source['text']) > 150:
                sources.append(source)
                processed_domains[domain] += 1
                print(f"    ✓ Extracted from {domain}")
            
            time.sleep(self.delay)
        
        print(f"\n✓ Successfully extracted {len(sources)} sources")
        
        # Sort by reliability
        sources.sort(
            key=lambda x: self.domain_reliability.get(x['metadata']['domain'], 0.5),
            reverse=True
        )
        
        # Save results
        filename = f"{query_term.replace(' ', '_')}_{self.domain}_research.json"
        self._save_results(sources, filename, query_term)
        
        print(f"\n💾 Results saved to: {filename}")
        self._print_summary(sources, query_term)
        
        return sources
    
    def _save_results(self, sources: List[Dict], filename: str, query_term: str):
        """Save research results to JSON."""
        output = {
            "query": query_term,
            "domain": self.domain,
            "domain_info": self.domain_info,
            "collection_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_sources": len(sources),
            "sources": sources
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    
    def _print_summary(self, sources: List[Dict], query_term: str):
        """Print research summary."""
        print(f"\n{'='*80}")
        print(f"📊 RESEARCH SUMMARY: {query_term}")
        print(f"{'='*80}")
        print(f"Domain: {self.domain}")
        print(f"Total Sources: {len(sources)}")
        print()
        
        # Group by reliability
        by_reliability = {}
        for source in sources:
            level = source['metadata']['reliability']
            by_reliability[level] = by_reliability.get(level, 0) + 1
        
        print("Reliability Distribution:")
        for level in ['very_high', 'high', 'medium', 'low']:
            count = by_reliability.get(level, 0)
            if count > 0:
                print(f"  • {level}: {count}")
        
        print(f"\n{'='*80}\n")


def research(query: str, domain: str = "botany", config: ConfigManager = None) -> List[Dict]:
    """
    Convenience function for quick research.
    
    Args:
        query: Search term
        domain: Research domain
        config: Optional config manager
        
    Returns:
        List of sources
    """
    if config is None:
        config = ConfigManager(domain=domain)
    else:
        config.switch_domain(domain)
    
    spider = UniversalResearchSpider(config)
    return spider.research(query)


if __name__ == "__main__":
    # Demo: Research in different domains
    config = ConfigManager(domain="mathematics", verbose=True)
    config.print_summary()
    
    spider = UniversalResearchSpider(config)
    results = spider.research("Pythagorean theorem")
