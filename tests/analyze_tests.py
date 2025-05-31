#!/usr/bin/env python3
"""
Test analysis script to generate reports on test coverage and results.
"""
import os
import sys
import json
import glob
import re
import argparse
import datetime
from collections import defaultdict

# Function to parse test file to extract test functions
def extract_test_functions(test_path):
    """Extract test functions from a test file."""
    functions = []
    with open(test_path, 'r') as f:
        content = f.read()
        # Find all test functions (those that start with "def test_")
        matches = re.finditer(r'def\s+(test_\w+)\s*\(', content)
        for match in matches:
            functions.append(match.group(1))
    return functions

# Function to analyze test coverage
def analyze_coverage():
    """Analyze which functions are tested and which are not."""
    # Find all Python files in the src/functions directory
    function_files = glob.glob('src/functions/*.py')
    # Find all integration test files
    test_files = glob.glob('tests/test_integration_*.py')
    
    # Extract function names from src files
    functions = {}
    for file_path in function_files:
        filename = os.path.basename(file_path)
        function_name = filename.replace('.py', '')
        
        with open(file_path, 'r') as f:
            content = f.read()
            # Look for the main function in the file
            main_function_match = re.search(r'def\s+(\w+)\s*\(', content)
            if main_function_match:
                main_function = main_function_match.group(1)
                functions[function_name] = {
                    'file_path': file_path,
                    'main_function': main_function,
                    'tested': False,
                    'test_files': []
                }
    
    # Check which functions are tested
    for test_path in test_files:
        with open(test_path, 'r') as f:
            content = f.read()
            
            for function_name, function_info in functions.items():
                # Check if the function name appears in imports or is used directly
                if re.search(r'from\s+src\.functions\.{0}\s+import'.format(function_name), content) or \
                   re.search(r'import\s+src\.functions\.{0}'.format(function_name), content):
                    functions[function_name]['tested'] = True
                    functions[function_name]['test_files'].append(test_path)
    
    return functions

# Function to analyze test results
def analyze_results(results_file):
    """Analyze the test results from a JSON file."""
    if not os.path.exists(results_file):
        print(f"Error: Results file '{results_file}' not found.")
        return None
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Calculate statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Group by category
    from batch_test_runner import get_test_category
    categories = defaultdict(list)
    for test_result in results:
        test_path = test_result['path']
        category = get_test_category(test_path)
        categories[category].append(test_result)
    
    # Calculate per-category statistics
    category_stats = {}
    for category, tests in categories.items():
        total = len(tests)
        passed = sum(1 for t in tests if t['success'])
        category_stats[category] = {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': (passed / total) * 100 if total > 0 else 0
        }
    
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'success_rate': success_rate,
        'categories': category_stats,
        'results': results
    }

# Function to generate a test coverage report
def generate_coverage_report(coverage_data, output_file=None):
    """Generate a test coverage report."""
    total_functions = len(coverage_data)
    tested_functions = sum(1 for f in coverage_data.values() if f['tested'])
    coverage_rate = (tested_functions / total_functions) * 100 if total_functions > 0 else 0
    
    report = f"""
TEST COVERAGE REPORT
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Total Functions: {total_functions}
Tested Functions: {tested_functions}
Untested Functions: {total_functions - tested_functions}
Coverage Rate: {coverage_rate:.2f}%

DETAILS
-------
"""
    
    # List tested functions
    report += "\nTESTED FUNCTIONS:\n"
    for name, info in sorted(coverage_data.items()):
        if info['tested']:
            test_files = [os.path.basename(tf) for tf in info['test_files']]
            report += f"- {name} (tested by: {', '.join(test_files)})\n"
    
    # List untested functions
    report += "\nUNTESTED FUNCTIONS:\n"
    for name, info in sorted(coverage_data.items()):
        if not info['tested']:
            report += f"- {name}\n"
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Coverage report saved to {output_file}")
    
    return report

# Function to generate a test results report
def generate_results_report(results_data, output_file=None):
    """Generate a test results report."""
    if not results_data:
        return "No results data available."
    
    report = f"""
TEST RESULTS REPORT
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Total Tests: {results_data['total_tests']}
Passed Tests: {results_data['passed_tests']}
Failed Tests: {results_data['failed_tests']}
Success Rate: {results_data['success_rate']:.2f}%

CATEGORY BREAKDOWN
-----------------
"""
    
    for category, stats in sorted(results_data['categories'].items()):
        report += f"- {category.upper()}: {stats['passed']}/{stats['total']} passed ({stats['success_rate']:.2f}%)\n"
    
    # List failed tests
    if results_data['failed_tests'] > 0:
        report += "\nFAILED TESTS:\n"
        for result in results_data['results']:
            if not result['success']:
                test_path = os.path.basename(result['path'])
                error = result.get('error', 'No error message available')
                report += f"- {test_path}: {error}\n"
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Results report saved to {output_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Analyze test coverage and results.")
    parser.add_argument('--coverage', action='store_true', help="Generate coverage report")
    parser.add_argument('--results', metavar='RESULTS_FILE', help="Generate results report from JSON file")
    parser.add_argument('--output-dir', default='tests/reports', help="Output directory for reports")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Analyze coverage if requested
    if args.coverage:
        coverage_data = analyze_coverage()
        report = generate_coverage_report(coverage_data, f"{args.output_dir}/coverage_report.txt")
        print("\nCOVERAGE REPORT SUMMARY:")
        print("------------------------")
        total_functions = len(coverage_data)
        tested_functions = sum(1 for f in coverage_data.values() if f['tested'])
        print(f"Total Functions: {total_functions}")
        print(f"Tested Functions: {tested_functions}")
        print(f"Untested Functions: {total_functions - tested_functions}")
        print(f"Coverage Rate: {(tested_functions / total_functions) * 100 if total_functions > 0 else 0:.2f}%")
    
    # Analyze results if requested
    if args.results:
        results_data = analyze_results(args.results)
        if results_data:
            report = generate_results_report(results_data, f"{args.output_dir}/results_report.txt")
            print("\nRESULTS REPORT SUMMARY:")
            print("-----------------------")
            print(f"Total Tests: {results_data['total_tests']}")
            print(f"Passed Tests: {results_data['passed_tests']}")
            print(f"Failed Tests: {results_data['failed_tests']}")
            print(f"Success Rate: {results_data['success_rate']:.2f}%")
    
    # If no arguments were provided, show help
    if not (args.coverage or args.results):
        parser.print_help()

if __name__ == "__main__":
    main() 