#!/usr/bin/env python3
"""
V4.cli - Enhanced CLI with Multiple Output Formats
This module is part of the V4 package and provides the command-line interface
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from V4.ConfigManager import ConfigManager
from V4.Spider import UniversalResearchSpider
from V4.ApiMonitor import SerpAPIMonitor
from V4.RagSys import RAGSystem
from V4.UniversalArticleGenerator import UniversalArticleGenerator


class OutputFormatter:
    """Handle multiple output formats"""
    
    def __init__(self, format_type: str = 'html'):
        self.format_type = format_type.lower()
    
    def format_article(self, content: str, metadata: Dict) -> str:
        """Format article based on output type"""
        if self.format_type == 'text':
            return self._to_plain_text(content, metadata)
        elif self.format_type == 'json':
            return self._to_json(content, metadata)
        else:  # html
            return content
    
    def _to_plain_text(self, content: str, metadata: Dict) -> str:
        """Convert HTML to plain text"""
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', content)
        
        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Add metadata header
        header = f"""
{'='*70}
{metadata.get('title', 'Article')}
{'='*70}
Subtitle: {metadata.get('subtitle', '')}
Domain: {metadata.get('domain', 'N/A')}
Generated: {metadata.get('date', datetime.now().strftime('%Y-%m-%d'))}
{'='*70}

"""
        return header + text
    
    def _to_json(self, content: str, metadata: Dict) -> str:
        """Convert to JSON format"""
        import re
        
        # Extract sections
        sections = []
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if '<h2' in line or '<h3' in line:
                # Save previous section
                if current_section:
                    sections.append({
                        'heading': current_section,
                        'content': '\n'.join(current_content).strip()
                    })
                # Start new section
                current_section = re.sub(r'<[^>]+>', '', line).strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_section:
            sections.append({
                'heading': current_section,
                'content': '\n'.join(current_content).strip()
            })
        
        output = {
            'metadata': metadata,
            'sections': sections,
            'full_html': content
        }
        
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def get_file_extension(self) -> str:
        """Get appropriate file extension"""
        extensions = {
            'html': '.html',
            'text': '.txt',
            'json': '.json'
        }
        return extensions.get(self.format_type, '.html')


class CreativeWriter:
    """Generate creative content like poems and essays"""
    
    def __init__(self, config: ConfigManager, rag_system: Optional[RAGSystem] = None):
        self.config = config
        self.rag_system = rag_system
    
    def write_poem(self, topic: str, style: str = "free verse", 
                   research_data: List[Dict] = None) -> str:
        """Generate a poem about a topic"""
        
        if self.rag_system and research_data:
            # Build context from research
            texts = [s['text'] for s in research_data]
            metadata = [s['metadata'] for s in research_data]
            self.rag_system.build_index(texts, metadata)
            
            if not self.rag_system.is_llm_loaded():
                self.rag_system.load_llm()
            
            prompt = f"Write a {style} poem about {topic}. Make it vivid, evocative, and emotionally resonant."
            result = self.rag_system.query(prompt, k=5, max_new_tokens=500, temperature=0.9)
            return result['answer']
        else:
            # Basic template without RAG
            return f"""
A {style} poem about {topic}

[Generated poem would appear here with RAG/LLM]
To generate actual poems, use --rag flag and ensure research data is available.
"""
    
    def write_essay(self, topic: str, essay_type: str = "expository", 
                   research_data: List[Dict] = None, word_count: int = 1000) -> str:
        """Generate an essay"""
        
        if self.rag_system and research_data:
            texts = [s['text'] for s in research_data]
            metadata = [s['metadata'] for s in research_data]
            self.rag_system.build_index(texts, metadata)
            
            if not self.rag_system.is_llm_loaded():
                self.rag_system.load_llm()
            
            sections = []
            
            # Introduction
            intro_prompt = f"Write a compelling introduction for a {essay_type} essay about {topic}."
            intro = self.rag_system.query(intro_prompt, k=5, max_new_tokens=300)
            sections.append(f"<h2>Introduction</h2>\n<p>{intro['answer']}</p>")
            
            # Body paragraphs
            body_prompts = [
                f"Discuss the main aspects and characteristics of {topic}.",
                f"Analyze the significance and implications of {topic}.",
                f"Explore different perspectives or applications related to {topic}."
            ]
            
            for i, prompt in enumerate(body_prompts, 1):
                result = self.rag_system.query(prompt, k=5, max_new_tokens=300)
                sections.append(f"<h2>Body Paragraph {i}</h2>\n<p>{result['answer']}</p>")
            
            # Conclusion
            conclusion_prompt = f"Write a thoughtful conclusion summarizing the key points about {topic}."
            conclusion = self.rag_system.query(conclusion_prompt, k=5, max_new_tokens=250)
            sections.append(f"<h2>Conclusion</h2>\n<p>{conclusion['answer']}</p>")
            
            return "\n\n".join(sections)
        else:
            return f"""
Essay: {topic}
Type: {essay_type}
Target Length: {word_count} words

[Generated essay would appear here with RAG/LLM]
To generate actual essays, use --rag flag and ensure research data is available.
"""


def list_domains(config: ConfigManager):
    """List available research domains."""
    print("\n" + "="*70)
    print("🌐 Available Research Domains")
    print("="*70 + "\n")
    
    for domain in config.get_available_domains():
        info = config.get_domain_info(domain)
        current = " ⭐ (CURRENT)" if domain == config.get_current_domain() else ""
        
        print(f"🔹 {domain}{current}")
        print(f"   {info.get('description', 'No description')}")
        keywords = info.get('keywords', [])
        if keywords:
            print(f"   Keywords: {', '.join(keywords[:5])}")
        print()


def check_credits(config: ConfigManager):
    """Check SerpAPI credits."""
    monitor = SerpAPIMonitor(config)
    status = monitor.check_credits(verbose=True)
    return status['can_proceed']


def show_domain_info(domain: str, config: ConfigManager):
    """Show detailed information about a specific domain."""
    if domain not in config.get_available_domains():
        print(f"\n❌ Domain '{domain}' not found")
        return
    
    info = config.get_domain_info(domain)
    
    print("\n" + "="*70)
    print(f"🔬 Domain: {domain.upper()}")
    print("="*70)
    print(f"\nName: {info.get('name', 'N/A')}")
    print(f"Description: {info.get('description', 'N/A')}")
    
    print("\n📚 Primary Sources:")
    for source in info.get('primary_sources', []):
        print(f"  • {source.replace('_', ' ').title()}")
    
    print("\n❓ Research Questions:")
    for i, question in enumerate(info.get('questions', []), 1):
        print(f"  {i}. {question}")
    
    print("\n🔑 Keywords:")
    keywords = info.get('keywords', [])
    if keywords:
        print(f"  {', '.join(keywords)}")
    else:
        print("  No keywords defined")
    
    print("\n" + "="*70 + "\n")


def perform_research(args, config: ConfigManager):
    """Perform research and generate output"""
    
    print(f"\n🔍 Starting research...")
    print(f"   Query: {args.query}")
    print(f"   Domain: {args.domain}")
    print(f"   Output Format: {args.format}")
    
    if args.content_type in ['poem', 'essay']:
        print(f"   Content Type: {args.content_type}")
    
    # Switch domain
    if not config.switch_domain(args.domain):
        print(f"\n❌ Could not switch to domain: {args.domain}")
        return
    
    # Collect research data
    spider = UniversalResearchSpider(config, check_credits=not args.no_credit_check)
    sources = spider.research(args.query, estimate_first=not args.no_credit_check)
    
    if not sources:
        print("\n❌ No sources found or insufficient API credits")
        return
    
    print(f"\n✅ Research complete! Found {len(sources)} sources")
    
    # Initialize RAG if requested
    rag_system = None
    if args.rag:
        print("\n🤖 Initializing RAG system...")
        try:
            rag_system = RAGSystem(config)
            texts = [s['text'] for s in sources]
            metadata = [s['metadata'] for s in sources]
            rag_system.build_index(texts, metadata)
            rag_system.load_llm()
            print("✅ RAG system ready")
        except Exception as e:
            print(f"⚠️  RAG initialization failed: {e}")
            rag_system = None
    
    # Generate content based on type
    output_formatter = OutputFormatter(args.format)
    
    if args.content_type == 'poem':
        print("\n📝 Generating poem...")
        writer = CreativeWriter(config, rag_system)
        content = writer.write_poem(args.query, args.poem_style, sources)
        
        metadata = {
            'title': f'Poem: {args.query}',
            'subtitle': f'A {args.poem_style} composition',
            'domain': args.domain,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
    elif args.content_type == 'essay':
        print("\n📝 Generating essay...")
        writer = CreativeWriter(config, rag_system)
        content = writer.write_essay(args.query, args.essay_type, sources, args.word_count)
        
        metadata = {
            'title': f'Essay: {args.query}',
            'subtitle': f'A {args.essay_type} analysis',
            'domain': args.domain,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
    else:  # article (default)
        print("\n📝 Generating article...")
        generator = UniversalArticleGenerator(
            config=config,
            rag_system=rag_system,
            fetch_images=args.fetch_images
        )
        content = generator.generate_full_article(args.query, sources)
        
        metadata = {
            'title': f'Article: {args.query}',
            'subtitle': 'Comprehensive research article',
            'domain': args.domain,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
    
    # Format output
    formatted_content = output_formatter.format_article(content, metadata)
    
    # Save to file
    safe_filename = args.query.lower().replace(' ', '-').replace('/', '-')
    date_str = datetime.now().strftime('%Y-%m-%d')
    extension = output_formatter.get_file_extension()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = output_dir / f"{date_str}-{safe_filename}{extension}"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print(f"\n✅ Content generated successfully!")
    print(f"📁 Saved to: {filename}")
    print(f"📊 Size: {len(formatted_content):,} characters")
    
    # Also save metadata separately if JSON format
    if args.format == 'json':
        meta_file = output_dir / f"{date_str}-{safe_filename}-metadata.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f"📁 Metadata: {meta_file}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Universal Research System V4 - Multi-Format Output & Creative Writing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  viincci-research -q "Rosa rubiginosa" -d botany
  viincci-research -q "diabetes" -d medical --format text
  viincci-research -q "Impressionism" -d art_history --content-type essay --rag
  viincci-research --list-domains
        """
    )
    
    # Basic arguments
    parser.add_argument('-q', '--query', type=str, help='Research query/topic')
    parser.add_argument('-d', '--domain', type=str, default='botany', 
                       help='Research domain')
    
    # Output format
    parser.add_argument('--format', type=str, choices=['html', 'text', 'json'],
                       default='html', help='Output format (default: html)')
    
    # Content type
    parser.add_argument('--content-type', type=str, 
                       choices=['article', 'poem', 'essay'],
                       default='article', help='Type of content to generate')
    
    # Creative writing options
    parser.add_argument('--poem-style', type=str, default='free verse',
                       help='Style of poem (e.g., "sonnet", "haiku", "free verse")')
    parser.add_argument('--essay-type', type=str, default='expository',
                       help='Type of essay (e.g., "expository", "argumentative")')
    parser.add_argument('--word-count', type=int, default=1000,
                       help='Target word count for essays')
    
    # Research options
    parser.add_argument('--rag', action='store_true',
                       help='Use RAG for intelligent generation')
    parser.add_argument('--fetch-images', action='store_true', default=True,
                       help='Fetch images from Wikimedia Commons')
    parser.add_argument('--no-credit-check', action='store_true',
                       help='Skip API credit checking')
    
    # Output options
    parser.add_argument('--output-dir', type=str, default='_posts',
                       help='Output directory (default: _posts)')
    
    # Utility commands
    parser.add_argument('--list-domains', action='store_true',
                       help='List all available domains')
    parser.add_argument('--domain-info', type=str, metavar='DOMAIN',
                       help='Show detailed domain information')
    parser.add_argument('--check-credits', action='store_true',
                       help='Check SerpAPI credit status')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize config
    try:
        config = ConfigManager(domain=args.domain, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Error initializing configuration: {e}")
        sys.exit(1)
    
    # Handle utility commands
    if args.list_domains:
        list_domains(config)
        return
    
    if args.domain_info:
        show_domain_info(args.domain_info, config)
        return
    
    if args.check_credits:
        can_proceed = check_credits(config)
        sys.exit(0 if can_proceed else 1)
    
    if not args.query:
        parser.print_help()
        print("\n💡 Tip: Use --list-domains to see all available research domains")
        sys.exit(0)
    
    # Perform research and generate output
    try:
        perform_research(args, config)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
