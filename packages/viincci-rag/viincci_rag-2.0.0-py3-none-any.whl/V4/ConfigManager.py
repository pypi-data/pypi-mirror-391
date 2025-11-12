"""
ConfigManager.py - Enhanced with API monitoring and domain customization
Research V4 - Domain-agnostic configuration system
"""
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigManager:
    """
    Enhanced centralized configuration manager.
    Supports multi-domain research with customizable sources and models.
    """
    
    def __init__(self, config_dir: str = None, domain: str = "botany", verbose: bool = False):
        """
        Initialize ConfigManager with domain-specific settings.
        
        Args:
            config_dir: Directory containing configuration files
            domain: Research domain (botany, medical, carpentry, mathematics, etc.)
            verbose: Print debug information
        """
        self.verbose = verbose
        self.domain = domain
        
        # Make config_dir relative to this module's location
        if config_dir is None:
            module_dir = Path(__file__).parent
            self.config_dir = module_dir / "config"
        else:
            self.config_dir = Path(config_dir)
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if self.verbose:
            print(f"📁 Config directory: {self.config_dir.absolute()}")
            print(f"🔬 Research domain: {domain}")
        
        # Initialize all configurations
        self._configs = {}
        self._load_all_configs()
    
    def _load_config(self, filename: str, default: Optional[Dict] = None) -> Dict:
        """Load a JSON configuration file."""
        filepath = self.config_dir / filename
        
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                if self.verbose:
                    print(f"✓ Loaded {filename}")
                return config
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing {filename}: {e}")
                return default or {}
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
                return default or {}
        else:
            if self.verbose:
                print(f"⚠️  {filename} not found, creating with defaults")
            if default:
                self._save_config(filename, default)
            return default or {}
    
    def _save_config(self, filename: str, config: Dict) -> None:
        """Save configuration to JSON file."""
        filepath = self.config_dir / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            if self.verbose:
                print(f"✓ Saved {filename}")
        except Exception as e:
            print(f"❌ Error saving {filename}: {e}")
    
    def _load_all_configs(self) -> None:
        """Load all configuration files with defaults."""
        
        # AI Settings
        ai_settings_default = {
            "include_front_matter": True,
            "fetch_images": True,
            "embedding_model": "all-MiniLM-L6-v2",
            "llm_model": "LiquidAI/LFM-40B-MoE",
            "config_path": "v4/config/article_config.json",
            "database_path": "v4/db/research_data.db",
            "device": "cpu",
            "load_in_8bit": False,
            "max_articles_per_run": 1,
            "search_config_path": "v4/config/search_config.json",
            "alternative_models": {
                "small": "LiquidAI/LFM2-1.2B-RAG",
                "medium": "LiquidAI/LFM-3B",
                "large": "LiquidAI/LFM-40B-MoE"
            }
        }
        self._configs['ai_settings'] = self._load_config('ai_settings.json', ai_settings_default)
        
        # API Monitoring Settings
        api_monitor_default = {
            "check_before_research": True,
            "warning_threshold": 100,
            "critical_threshold": 20,
            "auto_stop_on_critical": True,
            "estimate_cost_before_run": True
        }
        self._configs['api_monitor'] = self._load_config('api_monitor.json', api_monitor_default)
        
        # Domain-specific configurations
        self._load_domain_configs()
        
        # Main Config
        config_default = {
            "app_name": "Universal Research System V4",
            "version": "4.0",
            "debug": False,
            "current_domain": self.domain,
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "api": {
                "serpapi_key_env": "SERP_API_KEY",
                "request_timeout": 40,
                "retry_attempts": 3,
                "retry_delay": 2
            },
            "scraping": {
                "delay_between_requests": 1.5,
                "max_sources": 50,
                "request_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            },
            "output": {
                "posts_directory": "_posts",
                "enable_preview": True,
                "save_json": True
            }
        }
        self._configs['config'] = self._load_config('config.json', config_default)
        
        # Search Config
        search_config_default = {
            "search": {
                "delay": 1.5,
                "max_sources": 50,
                "add_search_terms": False
            },
            "supported_extensions": [".html", ".htm", ".php", ".asp", ".aspx", ".pdf", ".txt"],
            "unsupported_extensions": [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".rar"],
            "skip_domains": ["pinterest.com", "youtube.com", "amazon.com", "ebay.com"]
        }
        self._configs['search_config'] = self._load_config('search_config.json', search_config_default)
        
        # Article Config (with headings and content settings)
        article_config_default = {
            "headings": [
                {
                    "title": "The Complete Guide to {plant_name}",
                    "subtitle": "Discover the facts, care tips, and benefits of this remarkable plant"
                },
                {
                    "title": "Everything You Need to Know About {plant_name}",
                    "subtitle": "A comprehensive guide to growing and caring for this beautiful species"
                }
            ],
            "image_settings": {
                "width": 800,
                "height": 600,
                "default_fallback": "/img/posts/default-plant.jpg"
            },
            "content_cleaning": {
                "remove_source_markers": True,
                "remove_incomplete_paragraphs": True,
                "min_paragraph_length": 50,
                "remove_citations": True
            }
        }
        self._configs['article_config'] = self._load_config('article_config.json', article_config_default)
        
        # Load domain reliability (will be domain-specific)
        self._load_domain_reliability()
    
    def _load_domain_configs(self):
        """Load domain-specific configuration templates."""
        domains_config_default = {
            "botany": {
                "name": "Botanical Research",
                "description": "Plant and flora research",
                "primary_sources": ["university", "research_institute", "botanical_garden"],
                "questions": [
                    "what are the benefits",
                    "interesting facts",
                    "care and cultivation guide",
                    "physical description and characteristics"
                ],
                "keywords": ["plant", "botanical", "species", "cultivation"]
            },
            "medical": {
                "name": "Medical Research",
                "description": "Medical and healthcare research",
                "primary_sources": ["university", "hospital", "research_institute", "medical_journal"],
                "questions": [
                    "what are the symptoms",
                    "what are the treatments",
                    "what causes this condition",
                    "what are the risk factors"
                ],
                "keywords": ["medical", "disease", "treatment", "diagnosis"]
            },
            "carpentry": {
                "name": "Carpentry & Woodworking",
                "description": "Woodworking techniques and materials",
                "primary_sources": ["university", "trade_school", "professional_association"],
                "questions": [
                    "what are the techniques",
                    "what tools are required",
                    "safety considerations",
                    "best practices and tips"
                ],
                "keywords": ["wood", "carpentry", "woodworking", "construction"]
            },
            "mathematics": {
                "name": "Mathematics Research",
                "description": "Mathematical concepts and formulas",
                "primary_sources": ["university", "research_institute", "mathematical_society"],
                "questions": [
                    "what is the theorem or formula",
                    "what are the applications",
                    "proof and derivation",
                    "historical context and development"
                ],
                "keywords": ["mathematics", "theorem", "proof", "formula"]
            }
        }
        self._configs['domains'] = self._load_config('domains.json', domains_config_default)
    
    def _load_domain_reliability(self):
        """Load domain reliability scores based on research domain."""
        # Default botanical domain reliability
        if self.domain == "botany":
            domain_reliability_default = {
                "south_african_academic": {
                    "up.ac.za": 0.98, "uct.ac.za": 0.98, "wits.ac.za": 0.98,
                    "sun.ac.za": 0.98, "ru.ac.za": 0.97, "ukzn.ac.za": 0.97
                },
                "botanical_institutes": {
                    "sanbi.org": 0.98, "plantzafrica.com": 0.97, "kew.org": 0.95
                },
                "international_academic": {
                    "en.wikipedia.org": 0.93, "britannica.com": 0.87
                },
                "gardening_sites": {
                    "thespruce.com": 0.70, "rhs.org.uk": 0.86
                }
            }
        elif self.domain == "medical":
            domain_reliability_default = {
                "academic_medical": {
                    "nih.gov": 0.98, "cdc.gov": 0.98, "who.int": 0.97,
                    "mayo.edu": 0.96, "clevelandclinic.org": 0.95
                },
                "medical_journals": {
                    "nejm.org": 0.98, "thelancet.com": 0.98, "bmj.com": 0.97
                },
                "university_medical": {
                    "harvard.edu": 0.96, "stanford.edu": 0.96, "jhmi.edu": 0.96
                },
                "general_medical": {
                    "webmd.com": 0.75, "healthline.com": 0.75
                }
            }
        elif self.domain == "mathematics":
            domain_reliability_default = {
                "academic": {
                    "mit.edu": 0.98, "stanford.edu": 0.98, "cam.ac.uk": 0.97
                },
                "math_resources": {
                    "mathworld.wolfram.com": 0.95, "brilliant.org": 0.90
                },
                "organizations": {
                    "ams.org": 0.96, "siam.org": 0.95
                }
            }
        else:
            # Generic academic sources
            domain_reliability_default = {
                "academic": {
                    "edu": 0.90, "ac.uk": 0.90, "ac.za": 0.90
                },
                "research": {
                    "researchgate.net": 0.85, "arxiv.org": 0.88
                },
                "general": {
                    "wikipedia.org": 0.80
                }
            }
        
        self._configs['domain_reliability'] = self._load_config(
            'domain_reliability.json', 
            domain_reliability_default
        )
    
    # API Monitoring Methods
    def get_api_warning_threshold(self) -> int:
        """Get warning threshold for API credits."""
        return self._configs['api_monitor'].get('warning_threshold', 100)
    
    def get_api_critical_threshold(self) -> int:
        """Get critical threshold for API credits."""
        return self._configs['api_monitor'].get('critical_threshold', 20)
    
    def should_check_before_research(self) -> bool:
        """Check if API monitoring is enabled."""
        return self._configs['api_monitor'].get('check_before_research', True)
    
    def should_auto_stop_on_critical(self) -> bool:
        """Check if research should auto-stop on critical credits."""
        return self._configs['api_monitor'].get('auto_stop_on_critical', True)
    
    # Domain Methods
    def get_current_domain(self) -> str:
        """Get current research domain."""
        return self.domain
    
    def get_domain_info(self, domain: str = None) -> Dict:
        """Get information about a specific domain."""
        domain = domain or self.domain
        return self._configs['domains'].get(domain, {})
    
    def get_available_domains(self) -> List[str]:
        """Get list of available research domains."""
        return list(self._configs['domains'].keys())
    
    def switch_domain(self, new_domain: str) -> bool:
        """
        Switch to a different research domain.
        
        Args:
            new_domain: New domain to switch to
            
        Returns:
            True if successful, False if domain doesn't exist
        """
        if new_domain in self.get_available_domains():
            self.domain = new_domain
            self._load_domain_reliability()  # Reload domain-specific reliability
            if self.verbose:
                print(f"✓ Switched to domain: {new_domain}")
            return True
        else:
            print(f"❌ Domain '{new_domain}' not found")
            return False
    
    def get_domain_questions(self, domain: str = None) -> List[str]:
        """Get research questions for specific domain."""
        domain = domain or self.domain
        domain_info = self.get_domain_info(domain)
        return domain_info.get('questions', [])
    
    # Article Configuration Methods
    def get_headings(self) -> List[Dict]:
        """Get article heading templates."""
        return self._configs.get('article_config', {}).get('headings', [])
    
    def get_image_settings(self) -> Dict:
        """Get image configuration settings."""
        return self._configs.get('article_config', {}).get('image_settings', {
            "width": 800,
            "height": 600,
            "default_fallback": "/img/posts/default-plant.jpg"
        })
    
    def get_content_cleaning_settings(self) -> Dict:
        """Get content cleaning configuration."""
        return self._configs.get('article_config', {}).get('content_cleaning', {
            "remove_source_markers": True,
            "remove_incomplete_paragraphs": True,
            "min_paragraph_length": 50,
            "remove_citations": True
        })
    
    def get_fetch_images(self) -> bool:
        """Check if image fetching is enabled."""
        return self._configs.get('ai_settings', {}).get('fetch_images', True)
    
    # Existing methods
    def get_ai_settings(self) -> Dict[str, Any]:
        return self._configs['ai_settings']
    
    def get_embedding_model(self) -> str:
        return self._configs['ai_settings'].get('embedding_model', 'all-MiniLM-L6-v2')
    
    def get_llm_model(self) -> str:
        return self._configs['ai_settings'].get('llm_model', 'LiquidAI/LFM-40B-MoE')
    
    def set_llm_model(self, model_name: str):
        """Dynamically change the LLM model."""
        self._configs['ai_settings']['llm_model'] = model_name
        if self.verbose:
            print(f"✓ LLM model changed to: {model_name}")
    
    def get_alternative_models(self) -> Dict[str, str]:
        """Get alternative model options."""
        return self._configs['ai_settings'].get('alternative_models', {})
    
    def get_device(self) -> str:
        return self._configs['ai_settings'].get('device', 'cpu')
    
    def get_load_in_8bit(self) -> bool:
        return self._configs['ai_settings'].get('load_in_8bit', False)
    
    def get_database_path(self) -> str:
        return self._configs['ai_settings'].get('database_path', 'v4/db/research_data.db')
    
    def get_search_delay(self) -> float:
        return self._configs['search_config'].get('search', {}).get('delay', 1.5)
    
    def get_max_sources(self) -> int:
        return self._configs['search_config'].get('search', {}).get('max_sources', 50)
    
    def get_skip_domains(self) -> list:
        return self._configs['search_config'].get('skip_domains', [])
    
    def get_search_questions(self) -> list:
        """Get search questions based on current domain."""
        return self.get_domain_questions()
    
    def get_search_config(self) -> Dict:
        """Get search configuration."""
        return self._configs['search_config']
    
    def get_api_key_env_name(self) -> str:
        return self._configs['config'].get('api', {}).get('serpapi_key_env', 'SERP_API_KEY')
    
    def get_api_key(self) -> Optional[str]:
        env_name = self.get_api_key_env_name()
        return os.getenv(env_name)
    
    def get_request_timeout(self) -> int:
        return self._configs['config'].get('api', {}).get('request_timeout', 40)
    
    def get_domain_reliability(self) -> Dict[str, Dict[str, float]]:
        return self._configs['domain_reliability']
    
    def get_domain_score(self, domain: str) -> Optional[float]:
        for category, domains in self._configs['domain_reliability'].items():
            if domain in domains:
                return domains[domain]
        return None
    
    def get_request_headers(self) -> Dict[str, str]:
        return self._configs['config'].get('scraping', {}).get('request_headers', {})
    
    def print_summary(self) -> None:
        """Print enhanced configuration summary."""
        print("\n" + "="*70)
        print("🔧 Enhanced Research System V4 - Configuration Summary")
        print("="*70)
        
        print(f"\n📊 Application:")
        print(f"  Version: {self._configs['config'].get('version', '4.0')}")
        print(f"  Research Domain: {self.domain.upper()}")
        print(f"  Domain Description: {self.get_domain_info().get('description', 'N/A')}")
        
        print(f"\n🤖 AI Settings:")
        print(f"  Embedding Model: {self.get_embedding_model()}")
        print(f"  LLM Model: {self.get_llm_model()}")
        print(f"  Device: {self.get_device()}")
        
        print(f"\n🔍 Search Settings:")
        print(f"  Max Sources: {self.get_max_sources()}")
        print(f"  Search Delay: {self.get_search_delay()}s")
        
        print(f"\n💰 API Monitoring:")
        print(f"  Check Before Research: {self.should_check_before_research()}")
        print(f"  Warning Threshold: {self.get_api_warning_threshold()}")
        print(f"  Critical Threshold: {self.get_api_critical_threshold()}")
        print(f"  Auto-Stop on Critical: {self.should_auto_stop_on_critical()}")
        
        print(f"\n🌐 Available Domains:")
        for domain in self.get_available_domains():
            current = " (CURRENT)" if domain == self.domain else ""
            print(f"  • {domain}{current}")
        
        print(f"\n📚 Reliability Sources ({len(self._configs['domain_reliability'])} categories):")
        for category, domains in self._configs['domain_reliability'].items():
            print(f"  • {category}: {len(domains)} sources")
        
        print("="*70 + "\n")


if __name__ == "__main__":
    # Demo
    config = ConfigManager(domain="medical", verbose=True)
    config.print_summary()
    
    print("\n🔄 Switching domains...")
    config.switch_domain("mathematics")
    config.print_summary()
