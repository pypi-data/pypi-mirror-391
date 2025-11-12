#!/usr/bin/env python3
"""
test_v4.py - Comprehensive test suite for Research V4
Can be run locally or in CI/CD pipeline
"""

import sys
import os
from pathlib import Path
import traceback


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_test(name, passed=True):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} - {name}")


class TestRunner:
    """Test runner for V4 components"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def run_test(self, name, test_func):
        """Run a single test"""
        try:
            test_func()
            self.passed += 1
            print_test(name, passed=True)
            return True
        except AssertionError as e:
            self.failed += 1
            error_msg = f"{name}: {str(e)}"
            self.errors.append(error_msg)
            print_test(name, passed=False)
            print(f"      Error: {str(e)}")
            return False
        except Exception as e:
            self.failed += 1
            error_msg = f"{name}: {type(e).__name__}: {str(e)}"
            self.errors.append(error_msg)
            print_test(name, passed=False)
            print(f"      Exception: {str(e)}")
            if '--verbose' in sys.argv:
                traceback.print_exc()
            return False
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print_header("Test Summary")
        print(f"\n  Total Tests: {total}")
        print(f"  Passed: {self.passed} ({'green' if self.passed == total else 'yellow'})")
        print(f"  Failed: {self.failed}")
        
        if self.failed > 0:
            print("\n  Failed Tests:")
            for error in self.errors:
                print(f"    • {error}")
        
        print("\n" + "="*80)
        
        return self.failed == 0


def test_imports():
    """Test 1: Verify all imports work"""
    print_header("Test 1: Module Imports")
    
    runner = TestRunner()
    
    def test_config_manager():
        from V4.ConfigManager import ConfigManager
        assert ConfigManager is not None
    
    def test_flora_database():
        from V4.FloraDatabase import FloraDatabase
        assert FloraDatabase is not None
    
    def test_rag_system():
        from V4.RagSys import RAGSystem
        assert RAGSystem is not None
    
    def test_art_gen():
        from V4.UniversalArticleGenerator import UniversalArticleGenerator
        assert UniversalArticleGenerator is not None
    
    def test_api_monitor():
        from V4.ApiMonitor import SerpAPIMonitor
        assert SerpAPIMonitor is not None
    
    runner.run_test("ConfigManager import", test_config_manager)
    runner.run_test("FloraDatabase import", test_flora_database)
    runner.run_test("RAGSystem import", test_rag_system)
    runner.run_test("ArticleGenerator import", test_art_gen)
    runner.run_test("ApiMonitor import", test_api_monitor)
    
    return runner.passed, runner.failed


def test_config_manager():
    """Test 2: ConfigManager functionality"""
    print_header("Test 2: ConfigManager")
    
    from V4.ConfigManager import ConfigManager
    runner = TestRunner()
    
    def test_initialization():
        config = ConfigManager(verbose=False)
        assert config is not None
        assert config.domain == 'botany'
    
    def test_get_domains():
        config = ConfigManager(verbose=False)
        domains = config.get_available_domains()
        assert len(domains) > 0
        assert 'botany' in domains
        assert 'medical' in domains
    
    def test_switch_domain():
        config = ConfigManager(verbose=False)
        success = config.switch_domain('medical')
        assert success == True
        assert config.get_current_domain() == 'medical'
    
    def test_get_questions():
        config = ConfigManager(verbose=False)
        questions = config.get_domain_questions()
        assert isinstance(questions, list)
        assert len(questions) > 0
    
    def test_api_settings():
        config = ConfigManager(verbose=False)
        threshold = config.get_api_warning_threshold()
        assert threshold == 100
        critical = config.get_api_critical_threshold()
        assert critical == 20
    
    def test_llm_model():
        config = ConfigManager(verbose=False)
        model = config.get_llm_model()
        assert 'LiquidAI' in model or 'Liquid' in model
    
    runner.run_test("Initialization", test_initialization)
    runner.run_test("Get domains", test_get_domains)
    runner.run_test("Switch domain", test_switch_domain)
    runner.run_test("Get questions", test_get_questions)
    runner.run_test("API settings", test_api_settings)
    runner.run_test("LLM model", test_llm_model)
    
    return runner.passed, runner.failed


def test_flora_database():
    """Test 3: FloraDatabase functionality"""
    print_header("Test 3: FloraDatabase")
    
    from V4.FloraDatabase import FloraDatabase
    from V4.ConfigManager import ConfigManager
    runner = TestRunner()
    
    def test_initialization():
        config = ConfigManager(verbose=False)
        db = FloraDatabase(config)
        assert db is not None
    
    def test_create_schema():
        config = ConfigManager(verbose=False)
        db = FloraDatabase(config)
        result = db.create_default_schema()
        assert result == True
    
    def test_get_statistics():
        config = ConfigManager(verbose=False)
        db = FloraDatabase(config)
        db.create_default_schema()
        stats = db.get_statistics()
        assert isinstance(stats, dict)
        assert 'total_entries' in stats
    
    runner.run_test("Initialization", test_initialization)
    runner.run_test("Create schema", test_create_schema)
    runner.run_test("Get statistics", test_get_statistics)
    
    return runner.passed, runner.failed


def test_rag_system():
    """Test 4: RAG System"""
    print_header("Test 4: RAG System")
    
    from V4.RagSys import RAGSystem
    from V4.ConfigManager import ConfigManager
    runner = TestRunner()
    
    def test_initialization():
        config = ConfigManager(verbose=False)
        rag = RAGSystem(config)
        assert rag is not None
        assert rag.embedding_model is not None
    
    def test_statistics():
        config = ConfigManager(verbose=False)
        rag = RAGSystem(config)
        stats = rag.get_statistics()
        assert isinstance(stats, dict)
        assert stats['index_size'] == 0
    
    def test_build_index():
        config = ConfigManager(verbose=False)
        rag = RAGSystem(config)
        texts = ["This is a test document.", "Another test document."]
        metadata = [{"source": "test1"}, {"source": "test2"}]
        rag.build_index(texts, metadata)
        assert rag.index is not None
        assert rag.index.ntotal == 2
    
    def test_retrieve():
        config = ConfigManager(verbose=False)
        rag = RAGSystem(config)
        texts = ["Plants need water and sunlight.", "Medical treatments vary."]
        metadata = [{"source": "botany"}, {"source": "medicine"}]
        rag.build_index(texts, metadata)
        results = rag.retrieve("plants", k=1)
        assert len(results) == 1
        assert 'text' in results[0]
    
    runner.run_test("Initialization", test_initialization)
    runner.run_test("Get statistics", test_statistics)
    runner.run_test("Build index", test_build_index)
    runner.run_test("Retrieve documents", test_retrieve)
    
    return runner.passed, runner.failed


def test_api_monitor():
    """Test 5: API Monitor"""
    print_header("Test 5: API Monitor")
    
    from V4.ApiMonitor import SerpAPIMonitor
    from V4.ConfigManager import ConfigManager
    runner = TestRunner()
    
    def test_initialization():
        config = ConfigManager(verbose=False)
        monitor = SerpAPIMonitor(config)
        assert monitor is not None
        assert monitor.warning_threshold == 100
        assert monitor.critical_threshold == 20
    
    def test_estimate():
        config = ConfigManager(verbose=False)
        monitor = SerpAPIMonitor(config)
        estimate = monitor.estimate_research_cost("Test Plant", questions=4)
        assert isinstance(estimate, dict)
        assert 'total_searches_needed' in estimate
        assert estimate['total_searches_needed'] == 7  # 3 web + 4 AI
    
    runner.run_test("Initialization", test_initialization)
    runner.run_test("Cost estimation", test_estimate)
    
    return runner.passed, runner.failed


def test_article_generator():
    """Test 6: Article Generator"""
    print_header("Test 6: Universal Article Generator")
    
    from V4.UniversalArticleGenerator import ContentCleaner, UniversalArticleGenerator
    from V4.ConfigManager import ConfigManager
    runner = TestRunner()
    
    def test_content_cleaner():
        config = ConfigManager(verbose=False)
        cleaning_settings = config.get_content_cleaning_settings()
        cleaner = ContentCleaner(cleaning_settings)
        assert cleaner is not None
    
    def test_remove_citations():
        config = ConfigManager(verbose=False)
        cleaning_settings = config.get_content_cleaning_settings()
        cleaner = ContentCleaner(cleaning_settings)
        text = "This is a test [1] with citations [2]"
        cleaned = cleaner.remove_citations(text)
        assert '[1]' not in cleaned
        assert '[2]' not in cleaned
    
    def test_markdown_conversion():
        config = ConfigManager(verbose=False)
        cleaning_settings = config.get_content_cleaning_settings()
        cleaner = ContentCleaner(cleaning_settings)
        text = "**Bold text** and *italic text*"
        converted = cleaner.convert_markdown_to_html(text)
        assert '<strong>' in converted or '<em>' in converted
    
    def test_generator_init():
        config = ConfigManager(verbose=False)
        generator = UniversalArticleGenerator(config, fetch_images=False)
        assert generator is not None
        assert generator.domain in ['botany', 'medical', 'mathematics', 'carpentry']
    
    def test_domain_sections():
        config = ConfigManager(domain='medical', verbose=False)
        generator = UniversalArticleGenerator(config, fetch_images=False)
        sections = generator.get_domain_sections("Test Topic")
        assert len(sections) > 0
        assert all('name' in s and 'query' in s for s in sections)
    
    runner.run_test("ContentCleaner initialization", test_content_cleaner)
    runner.run_test("Remove citations", test_remove_citations)
    runner.run_test("Markdown conversion", test_markdown_conversion)
    runner.run_test("Generator initialization", test_generator_init)
    runner.run_test("Domain sections", test_domain_sections)
    
    return runner.passed, runner.failed


def test_config_files():
    """Test 7: Configuration files"""
    print_header("Test 7: Configuration Files")
    
    from V4.ConfigManager import ConfigManager
    import json
    runner = TestRunner()
    
    config = ConfigManager(verbose=False)
    config_dir = Path(config.config_dir)
    
    required_configs = [
        'ai_settings.json',
        'api_monitor.json',
        'config.json',
        'domain_reliability.json',
        'domains.json',
        'search_config.json'
    ]
    
    for cfg_file in required_configs:
        def test_config_exists(filename=cfg_file):
            cfg_path = config_dir / filename
            assert cfg_path.exists(), f"Config file not found: {filename}"
            
            # Validate JSON
            with open(cfg_path) as f:
                data = json.load(f)
                assert isinstance(data, dict), f"Invalid JSON in {filename}"
        
        runner.run_test(f"Config file: {cfg_file}", test_config_exists)
    
    return runner.passed, runner.failed


def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("  RESEARCH V4 - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\n  Running all tests...")
    
    total_passed = 0
    total_failed = 0
    
    # Run all test suites
    test_suites = [
        ("Imports", test_imports),
        ("ConfigManager", test_config_manager),
        ("FloraDatabase", test_flora_database),
        ("RAGSystem", test_rag_system),
        ("ApiMonitor", test_api_monitor),
        ("ArticleGenerator", test_article_generator),
        ("ConfigFiles", test_config_files)
    ]
    
    results = []
    
    for name, test_func in test_suites:
        try:
            passed, failed = test_func()
            total_passed += passed
            total_failed += failed
            results.append((name, passed, failed))
        except Exception as e:
            print(f"\n❌ Test suite '{name}' crashed: {str(e)}")
            if '--verbose' in sys.argv:
                traceback.print_exc()
            total_failed += 1
            results.append((name, 0, 1))
    
    # Print final summary
    print_header("FINAL RESULTS")
    print("\n  Test Suite Results:")
    for name, passed, failed in results:
        status = "✅" if failed == 0 else "❌"
        print(f"    {status} {name}: {passed} passed, {failed} failed")
    
    print(f"\n  {'='*76}")
    print(f"  Total: {total_passed} passed, {total_failed} failed")
    print(f"  {'='*76}\n")
    
    if total_failed == 0:
        print("  ✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"  ❌ {total_failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
