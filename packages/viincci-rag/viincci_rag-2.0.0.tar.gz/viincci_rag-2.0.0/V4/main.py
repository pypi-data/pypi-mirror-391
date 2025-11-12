#!/usr/bin/env python3
"""
V4.main - Comprehensive Main Controller for Viincci-RAG
This module is part of the V4 package
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from V4.ConfigManager import ConfigManager
from V4.Spider import UniversalResearchSpider
from V4.RagSys import RAGSystem
from V4.UniversalArticleGenerator import UniversalArticleGenerator
from V4.ApiMonitor import SerpAPIMonitor
from V4.FloraDatabase import FloraDatabase


def main():
    """Main controller entry point"""
    parser = argparse.ArgumentParser(
        description="Viincci-RAG Main Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command', choices=['research', 'workflow', 'list', 'stats'],
                       help='Command to execute')
    parser.add_argument('-q', '--query', type=str, help='Research query')
    parser.add_argument('-d', '--domain', type=str, default='botany',
                       help='Research domain')
    parser.add_argument('--rag', action='store_true', help='Use RAG system')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize config
    config = ConfigManager(domain=args.domain, verbose=args.verbose)
    
    if args.command == 'list':
        print("\nAvailable domains:")
        for domain in config.get_available_domains():
            print(f"  • {domain}")
    
    elif args.command == 'research' and args.query:
        print(f"\n🔍 Researching: {args.query}")
        spider = UniversalResearchSpider(config)
        sources = spider.research(args.query)
        print(f"✅ Found {len(sources)} sources")
    
    elif args.command == 'workflow' and args.query:
        print(f"\n🚀 Full workflow for: {args.query}")
        spider = UniversalResearchSpider(config)
        sources = spider.research(args.query)
        
        generator = UniversalArticleGenerator(config)
        article = generator.generate_full_article(args.query, sources)
        
        # Save output
        filename = f"_posts/{datetime.now().strftime('%Y-%m-%d')}-{args.query.replace(' ', '-')}.html"
        Path("_posts").mkdir(exist_ok=True)
        with open(filename, 'w') as f:
            f.write(article)
        print(f"✅ Saved to: {filename}")
    
    elif args.command == 'stats':
        db = FloraDatabase(config)
        stats = db.get_statistics()
        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
