#!/usr/bin/env python3
"""
Test Runner - Execute tests for custom Python scripts
"""

import sys
import json
import unittest
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from boop.config.settings import BoopConfig
from boop.core.script import ScriptManager
from boop.core.utils import run_script_in_subprocess


class TestResult:
    """Test result holder."""
    
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0.0):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration


def run_script_test(script_name: str, input_text: str, expected: str, 
                    script_manager: ScriptManager, config: BoopConfig) -> TestResult:
    """Run a single script test.
    
    Args:
        script_name: Name of the script to test
        input_text: Input text for the script
        expected: Expected output text
        script_manager: Script manager instance
        config: Configuration
        
    Returns:
        TestResult object
    """
    start_time = time.time()
    
    try:
        # Get script
        script = script_manager.get_script(script_name)
        if not script:
            return TestResult(
                script_name, 
                False, 
                f"Script '{script_name}' not found",
                time.time() - start_time
            )
        
        # Run script in subprocess
        result = run_script_in_subprocess(
            script.file_path,
            input_text,
            config.python_path
        )
        
        if not result.get('success', False):
            return TestResult(
                script_name,
                False,
                f"Script execution failed: {result.get('error', 'Unknown error')}",
                time.time() - start_time
            )
        
        actual_output = result.get('output', '')
        
        if actual_output == expected:
            return TestResult(
                script_name,
                True,
                f"Output matches expected",
                time.time() - start_time
            )
        else:
            return TestResult(
                script_name,
                False,
                f"Output mismatch.\nExpected: {repr(expected)}\nActual: {repr(actual_output)}",
                time.time() - start_time
            )
            
    except Exception as e:
        return TestResult(
            script_name,
            False,
            f"Exception: {str(e)}",
            time.time() - start_time
        )


def load_test_cases(test_cases_path: Path) -> Optional[Dict[str, Any]]:
    """Load test cases from JSON file.
    
    Args:
        test_cases_path: Path to test cases file
        
    Returns:
        Test cases dictionary or None
    """
    if not test_cases_path.exists():
        print(f"Test cases file not found: {test_cases_path}")
        return None
    
    try:
        with open(test_cases_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading test cases: {e}")
        return None


def run_all_tests(test_cases: Dict[str, Any], config: BoopConfig, target_script: str = None) -> List[TestResult]:
    """Run all tests from test cases.
    
    Args:
        test_cases: Test cases dictionary
        config: Configuration
        target_script: Optional target script name to test
        
    Returns:
        List of TestResult objects
    """
    results = []
    
    # Create script manager
    script_manager = ScriptManager(config)
    script_manager.load_scripts()
    
    print("=" * 70)
    print("Running Python Script Tests")
    print("=" * 70)
    
    for category in test_cases.get('testCases', []):
        category_name = category.get('category', 'Unknown')
        print(f"\n{'=' * 70}")
        print(f"Category: {category_name}")
        print("=" * 70)
        
        for script_test in category.get('scripts', []):
            script_name = script_test.get('name', '')
            # Run all scripts regardless of file extension
            
            # Skip if target_script is specified and doesn't match
            if target_script and script_name != target_script:
                continue
                
            tests = script_test.get('tests', [])
            
            print(f"\n  Script: {script_name}")
            
            for test in tests:
                input_text = test.get('input', '')
                expected = test.get('expected', '')
                test_name = test.get('name', f"Input: {input_text[:30]}")
                
                result = run_script_test(
                    script_name,
                    input_text,
                    expected,
                    script_manager,
                    config
                )
                
                status = "✓ PASS" if result.passed else "✗ FAIL"
                print(f"    {status}: {test_name}")
                if not result.passed:
                    print(f"      {result.message}")
                
                results.append(result)
    
    return results


def run_unit_tests() -> unittest.TestResult:
    """Run unit tests using unittest framework.
    
    Returns:
        TestResult from unittest
    """
    print("\n" + "=" * 70)
    print("Running Unit Tests")
    print("=" * 70)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(Path(__file__).parent),
        pattern='test_*.py'
    )
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def generate_report(results: List[TestResult], unit_test_result: Optional[unittest.TestResult] = None) -> str:
    """Generate test report.
    
    Args:
        results: List of test results
        unit_test_result: Optional unittest result
        
    Returns:
        Report string
    """
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    
    report = []
    report.append("\n" + "=" * 70)
    report.append("TEST REPORT")
    report.append("=" * 70)
    report.append(f"\nPython Script Tests:")
    report.append(f"  Total:  {total}")
    report.append(f"  Passed: {passed}")
    report.append(f"  Failed: {failed}")
    report.append(f"  Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
    
    if unit_test_result:
        report.append(f"\nUnit Tests:")
        report.append(f"  Tests Run: {unit_test_result.testsRun}")
        report.append(f"  Failures: {len(unit_test_result.failures)}")
        report.append(f"  Errors: {len(unit_test_result.errors)}")
        report.append(f"  Skipped: {len(unit_test_result.skipped)}")
    
    if failed > 0:
        report.append(f"\nFailed Tests:")
        for result in results:
            if not result.passed:
                report.append(f"  - {result.name}: {result.message}")
    
    report.append("\n" + "=" * 70)
    
    return "\n".join(report)


def main():
    """Main test runner entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run tests for Boop scripts')
    parser.add_argument('script', nargs='?', help='Name of the script to test (optional)')
    args = parser.parse_args()
    target_script = args.script
    
    print("=" * 70)
    print("BoopPython Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if target_script:
        print(f"Testing specific script: {target_script}")
    print("=" * 70)
    
    # Load configuration
    config_path = project_root / 'boop' / 'config.json'
    config = BoopConfig.from_file(config_path)
    
    # Load test cases
    test_cases_path = Path(__file__).parent / 'test_cases.json'
    test_cases = load_test_cases(test_cases_path)
    
    # Load format test cases
    format_test_cases_path = Path(__file__).parent / 'test_cases_format.json'
    format_test_cases = load_test_cases(format_test_cases_path)
    
    # Combine test cases
    if format_test_cases:
        if test_cases:
            test_cases['testCases'].extend(format_test_cases['testCases'])
        else:
            test_cases = format_test_cases
    
    all_results = []
    unit_test_result = None
    
    # Run script tests if test cases loaded
    if test_cases:
        script_results = run_all_tests(test_cases, config, target_script)
        all_results.extend(script_results)
    
    # Run unit tests
    unit_test_result = run_unit_tests()
    
    # Generate report
    report = generate_report(all_results, unit_test_result)
    print(report)
    
    # Save report to file
    report_path = Path(__file__).parent / 'test_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        f.write(f"\n\nReport saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\nReport saved to: {report_path}")
    
    # Exit with appropriate code
    failed_count = sum(1 for r in all_results if not r.passed)
    if unit_test_result:
        failed_count += len(unit_test_result.failures) + len(unit_test_result.errors)
    
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == '__main__':
    main()
