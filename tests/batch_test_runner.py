#!/usr/bin/env python3
"""
Batch test runner script for running integration tests in batches.
This helps organize and run tests in a structured way with better error handling.
"""
import os
import sys
import subprocess
import argparse
import glob
import re
from collections import defaultdict
import json
import time

# Define test categories
CATEGORIES = {
    'database': ['mysql', 'db', 'database'],
    'api': ['api', 'onet_api', 'get_occupation'],
    'skills': ['skill', 'gap'],
    'llm': ['llm', 'gemini'],
    'extract': ['extract'],
    'transform': ['transform']
}

def get_test_category(test_path):
    """Determine category for a test file based on keywords in its name."""
    filename = os.path.basename(test_path)
    for category, keywords in CATEGORIES.items():
        if any(keyword in filename.lower() for keyword in keywords):
            return category
    return 'other'

def discover_tests():
    """Find all integration tests and categorize them."""
    tests = glob.glob('tests/test_integration_*.py')
    categorized_tests = defaultdict(list)
    
    for test_path in tests:
        category = get_test_category(test_path)
        categorized_tests[category].append(test_path)
    
    return categorized_tests

def run_test(test_path, env_file='env/env.env'):
    """Run a single test and capture its output and status."""
    print(f"Running test: {test_path}")
    start_time = time.time()
    
    # First check if the test exists
    if not os.path.exists(test_path):
        return {
            'path': test_path,
            'success': False,
            'duration': 0,
            'error': f"Test file not found: {test_path}"
        }
    
    try:
        # Run the test with the environment variables
        if os.path.exists(env_file):
            cmd = f'. {env_file} && python3 -m pytest {test_path} -v'
        else:
            print(f"Warning: Environment file {env_file} not found. Running without environment variables.")
            cmd = f'python3 -m pytest {test_path} -v'
            
        process = subprocess.run(
            cmd, 
            shell=True, 
            check=False, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        duration = time.time() - start_time
        
        # Extract test results from output
        test_passed = process.returncode == 0
        output = process.stdout
        error_output = process.stderr
        
        # Collect information about the test
        test_result = {
            'path': test_path,
            'success': test_passed,
            'duration': duration,
            'output': output,
            'error': error_output if error_output else None
        }
        
        # Print a summary
        status = "PASSED" if test_passed else "FAILED"
        print(f"  {status} in {duration:.2f}s")
        
        return test_result
    
    except Exception as e:
        return {
            'path': test_path,
            'success': False,
            'duration': time.time() - start_time,
            'error': str(e)
        }

def run_batch(test_paths, env_file='env/env.env'):
    """Run a batch of tests and return their results."""
    results = []
    
    for test_path in test_paths:
        result = run_test(test_path, env_file)
        results.append(result)
    
    return results

def print_summary(results):
    """Print a summary of test results."""
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    
    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
    print("=" * 60)
    
    if failed_tests > 0:
        print("\nFAILED TESTS:")
        for result in results:
            if not result['success']:
                print(f"  - {result['path']}")
                if result['error']:
                    error_lines = result['error'].split('\n')
                    # Show just the first few lines of the error
                    print(f"    Error: {error_lines[0]}")
                    if len(error_lines) > 1:
                        print(f"           {error_lines[1]}")
    
    print(f"\nTotal time: {sum(r['duration'] for r in results):.2f}s")

def save_results(results, output_file):
    """Save test results to a JSON file."""
    # Clean up results for JSON serialization (remove large outputs)
    clean_results = []
    for r in results:
        clean_r = {
            'path': r['path'],
            'success': r['success'],
            'duration': r['duration'],
        }
        if not r['success']:
            clean_r['error'] = r['error']
        clean_results.append(clean_r)
    
    with open(output_file, 'w') as f:
        json.dump(clean_results, f, indent=2)
    
    print(f"Results saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Run integration tests in batches.")
    parser.add_argument('--category', help="Run tests in a specific category")
    parser.add_argument('--test', help="Run a specific test")
    parser.add_argument('--list', action='store_true', help="List available tests")
    parser.add_argument('--output', help="Save results to a JSON file")
    parser.add_argument('--env', default='env/env.env', help="Environment file to use")
    args = parser.parse_args()
    
    # Check if environment file exists
    if not os.path.exists(args.env):
        print(f"Warning: Environment file {args.env} not found.")
        print("Tests may fail if they require environment variables.")
    
    # Discover tests
    categorized_tests = discover_tests()
    
    # List tests if requested
    if args.list:
        print("Available tests by category:")
        for category, tests in sorted(categorized_tests.items()):
            print(f"\n{category.upper()} ({len(tests)} tests):")
            for test in sorted(tests):
                print(f"  - {test}")
        return
    
    # Run tests
    if args.test:
        # Run a specific test
        results = [run_test(args.test, args.env)]
    elif args.category:
        # Run tests in a specific category
        if args.category not in categorized_tests:
            print(f"Error: Category '{args.category}' not found.")
            print(f"Available categories: {', '.join(sorted(categorized_tests.keys()))}")
            return
        print(f"Running {len(categorized_tests[args.category])} tests in category '{args.category}'...")
        results = run_batch(categorized_tests[args.category], args.env)
    else:
        # Run all tests
        all_tests = [test for tests in categorized_tests.values() for test in tests]
        print(f"Running all {len(all_tests)} tests...")
        results = run_batch(all_tests, args.env)
    
    # Print summary
    print_summary(results)
    
    # Save results if requested
    if args.output:
        save_results(results, args.output)

if __name__ == "__main__":
    main() 