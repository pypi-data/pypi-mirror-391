"""
V4 Package - Universal Research System
Version 4.0.1
"""

__version__ = "1.0.0"
__author__ = "MrViincciLeRoy"
__email__ = "Viincci@proton.me"
import sys
import os

# Windows encoding fix - MUST BE FIRST
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Core components
from V4.ConfigManager import ConfigManager
from V4.FloraDatabase import FloraDatabase
from V4.RagSys import RAGSystem
from V4.UniversalArticleGenerator import UniversalArticleGenerator
from V4.Spider import UniversalResearchSpider
from V4.ApiMonitor import SerpAPIMonitor

# Optional components (may fail if dependencies not installed)
try:
    from V4.ArtGenSys import EnhancedPlantArticleGenerator
except ImportError:
    EnhancedPlantArticleGenerator = None

try:
    from V4.FloraWikipediaScraper import FloraWikipediaScraper
except ImportError:
    FloraWikipediaScraper = None

__all__ = [
    '__version__',
    'ConfigManager',
    'FloraDatabase',
    'RAGSystem',
    'UniversalArticleGenerator',
    'UniversalResearchSpider',
    'SerpAPIMonitor',
    'EnhancedPlantArticleGenerator',
    'FloraWikipediaScraper',
]
