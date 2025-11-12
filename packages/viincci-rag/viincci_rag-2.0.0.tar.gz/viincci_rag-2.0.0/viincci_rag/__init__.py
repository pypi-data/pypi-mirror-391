"""
Viincci-RAG: Universal Research & Article Generation System

A professional Python package for multi-domain research, retrieval-augmented
generation (RAG), and article generation.

Usage:
    from viincci_rag import ConfigManager, RAGSystem, UniversalResearchSpider
    config = ConfigManager(domain="botany")
    rag = RAGSystem(config)
    spider = UniversalResearchSpider(config)
"""

__version__ = "2.0.0"
__author__ = "MrViincciLeRoy"
__author_email__ = "Viincci@proton.me"
__license__ = "MIT"


# Import V4 classes and create viincci_rag subclasses (canonical namespace)
try:
    from V4 import (
        ConfigManager as _V4ConfigManager,
        FloraDatabase as _V4FloraDatabase,
        RAGSystem as _V4RAGSystem,
        UniversalArticleGenerator as _V4UniversalArticleGenerator,
        UniversalResearchSpider as _V4UniversalResearchSpider,
        SerpAPIMonitor as _V4SerpAPIMonitor,
    )
    
    # Lightweight subclasses: inherit V4 functionality, show viincci_rag namespace
    class ConfigManager(_V4ConfigManager):
        """ConfigManager — viincci_rag canonical class."""
        pass
    
    class FloraDatabase(_V4FloraDatabase):
        """FloraDatabase — viincci_rag canonical class."""
        pass
    
    class RAGSystem(_V4RAGSystem):
        """RAGSystem — viincci_rag canonical class."""
        pass
    
    class UniversalArticleGenerator(_V4UniversalArticleGenerator):
        """UniversalArticleGenerator — viincci_rag canonical class."""
        pass
    
    class UniversalResearchSpider(_V4UniversalResearchSpider):
        """UniversalResearchSpider — viincci_rag canonical class."""
        pass
    
    class SerpAPIMonitor(_V4SerpAPIMonitor):
        """SerpAPIMonitor — viincci_rag canonical class."""
        pass

except Exception as e:
    # Fallback if V4 not available
    import warnings
    warnings.warn(f"Failed to import V4 classes: {e}")
    ConfigManager = None
    FloraDatabase = None
    RAGSystem = None
    UniversalArticleGenerator = None
    UniversalResearchSpider = None
    SerpAPIMonitor = None


__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "ConfigManager",
    "RAGSystem",
    "UniversalResearchSpider",
    "UniversalArticleGenerator",
    "SerpAPIMonitor",
    "FloraDatabase",
]
