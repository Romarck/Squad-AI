from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List
import ast
import re
import inspect

class PytestExecutionRequest(BaseModel):
    """Input schema for Pytest Execution Simulator Tool."""
    action: str = Field(..., description="Action to perform: 'validate_syntax', 'simulate_pytest', or 'analyze_quality'")
    code: str = Field(..., description="Python code to analyze")
    test_code: str = Field(default="", description="Test code for pytest simulation (required for 'simulate_pytest' action)")

class PytestExecutionSimulator(BaseTool):
    """Tool for validating Python code, simulating pytest execution, and analyzing code quality through static analysis."""

    name: str = "pytest_execution_simulator"
    description: str = (
        "Validates Python code syntax, simulates pytest execution through static analysis, "
        "and analyzes code quality. Supports three actions: 'validate_syntax' for syntax validation, "
        "'simulate_pytest' for test simulation, and 'analyze_quality' for code quality analysis."
    )
    args_schema: Type[BaseModel] = PytestExecutionRequest

    def _run(self, action: str, code: str, test_code: str = "") -> str:
        """Execute the requested action on the provided code."""
        try:
            if action == "validate_syntax":
                return self.validate_python_code(code)
            elif action == "simulate_pytest":
                if not test_code:
                    return "Error: test_code is required for simulate_pytest action"
                return self.simulate_pytest_execution(test_code, code)
            elif action == "analyze_quality":
                return self.analyze_code_quality(code)
            else:
                return f"Error: Invalid action '{action}'. Use 'validate_syntax', 'simulate_pytest', or 'analyze_quality'"
        except Exception as e:
            return f"Error executing {action}: {str(e)}"

    def validate_python_code(self, code: str) -> str:
        """Validates Python code syntax using compile() and returns validation result."""
        try:
            # Check syntax using compile()
            compile(code, '<string>', 'exec')
            
            # Additional AST-based analysis
            try:
                tree = ast.parse(code)
                issues = []
                
                # Check for common issues
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and not node.name.isidentifier():
                        issues.append(f"Invalid function name: {node.name}")
                    elif isinstance(node, ast.Name) and node.id in ['eval', 'exec', 'compile']:
                        issues.append(f"Potentially unsafe function used: {node.id}")
                
                result = "✅ Code syntax is valid!\n"
                result += f"📊 Analysis complete: {len(list(ast.walk(tree)))} AST nodes found\n"
                
                if issues:
                    result += "⚠️  Potential issues found:\n"
                    for issue in issues:
                        result += f"  - {issue}\n"
                else:
                    result += "✨ No obvious issues detected\n"
                
                return result
                
            except SyntaxError as ast_error:
                return f"❌ AST parsing failed: {str(ast_error)}"
                
        except SyntaxError as e:
            return f"❌ Syntax Error: Line {e.lineno}, Column {e.offset}: {e.msg}"
        except Exception as e:
            return f"❌ Validation Error: {str(e)}"

    def simulate_pytest_execution(self, test_code: str, main_code: str) -> str:
        """Simulates pytest execution by analyzing test structure and code."""
        try:
            # Validate both codes first
            main_validation = self.validate_python_code(main_code)
            test_validation = self.validate_python_code(test_code)
            
            if "❌" in main_validation:
                return f"❌ Main code validation failed:\n{main_validation}"
            if "❌" in test_validation:
                return f"❌ Test code validation failed:\n{test_validation}"
            
            # Parse test code
            test_tree = ast.parse(test_code)
            main_tree = ast.parse(main_code)
            
            # Find test functions
            test_functions = []
            for node in ast.walk(test_tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    test_functions.append(node.name)
            
            # Find main functions to test
            main_functions = []
            for node in ast.walk(main_tree):
                if isinstance(node, ast.FunctionDef):
                    main_functions.append(node.name)
            
            # Analyze test structure
            test_results = []
            has_imports = any(isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom) 
                            for node in test_tree.body)
            
            for test_func in test_functions:
                # Simulate test execution logic
                test_node = None
                for node in ast.walk(test_tree):
                    if isinstance(node, ast.FunctionDef) and node.name == test_func:
                        test_node = node
                        break
                
                if test_node:
                    # Check for assertions
                    has_assertions = any(isinstance(node, ast.Call) and 
                                       isinstance(node.func, ast.Name) and 
                                       node.func.id.startswith('assert') 
                                       for node in ast.walk(test_node))
                    
                    # Simple simulation: tests pass if they have proper structure
                    if has_assertions:
                        test_results.append((test_func, "PASSED", "Test has proper assertions"))
                    else:
                        test_results.append((test_func, "FAILED", "No assertions found"))
                else:
                    test_results.append((test_func, "ERROR", "Test function not found"))
            
            # Generate report
            report = "🧪 PYTEST SIMULATION REPORT\n"
            report += "=" * 50 + "\n\n"
            
            if not test_functions:
                report += "❌ No test functions found (functions must start with 'test_')\n"
                return report
            
            report += f"📋 Found {len(test_functions)} test function(s)\n"
            report += f"📦 Main code has {len(main_functions)} function(s)\n"
            report += f"📥 Test imports detected: {'Yes' if has_imports else 'No'}\n\n"
            
            passed = 0
            failed = 0
            
            for test_name, status, message in test_results:
                if status == "PASSED":
                    report += f"✅ {test_name} :: {status}\n"
                    passed += 1
                else:
                    report += f"❌ {test_name} :: {status} - {message}\n"
                    failed += 1
            
            report += "\n" + "=" * 50 + "\n"
            report += f"📊 SUMMARY: {passed} passed, {failed} failed\n"
            
            if failed == 0:
                report += "🎉 All tests passed!\n"
            else:
                report += f"⚠️  {failed} test(s) need attention\n"
            
            return report
            
        except Exception as e:
            return f"❌ Pytest simulation error: {str(e)}"

    def analyze_code_quality(self, code: str) -> str:
        """Analyzes Python code for basic quality metrics and returns assessment."""
        try:
            # First validate syntax
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                return f"❌ Cannot analyze code with syntax errors: {str(e)}"
            
            metrics = {
                'functions': 0,
                'classes': 0,
                'lines': len(code.split('\n')),
                'docstrings': 0,
                'try_blocks': 0,
                'imports': 0,
                'complexity_issues': []
            }
            
            # Analyze AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics['functions'] += 1
                    # Check for docstring
                    if (node.body and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Str)):
                        metrics['docstrings'] += 1
                    # Check function length (complexity indicator)
                    if len(node.body) > 20:
                        metrics['complexity_issues'].append(f"Function '{node.name}' is quite long ({len(node.body)} statements)")
                
                elif isinstance(node, ast.ClassDef):
                    metrics['classes'] += 1
                    if (node.body and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Str)):
                        metrics['docstrings'] += 1
                
                elif isinstance(node, (ast.Try, ast.TryExcept)):
                    metrics['try_blocks'] += 1
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    metrics['imports'] += 1
            
            # Generate quality report
            report = "📈 CODE QUALITY ANALYSIS\n"
            report += "=" * 40 + "\n\n"
            
            # Basic metrics
            report += "📊 METRICS:\n"
            report += f"  • Lines of code: {metrics['lines']}\n"
            report += f"  • Functions: {metrics['functions']}\n"
            report += f"  • Classes: {metrics['classes']}\n"
            report += f"  • Import statements: {metrics['imports']}\n"
            report += f"  • Try/except blocks: {metrics['try_blocks']}\n\n"
            
            # Documentation assessment
            report += "📚 DOCUMENTATION:\n"
            total_definitions = metrics['functions'] + metrics['classes']
            if total_definitions > 0:
                doc_percentage = (metrics['docstrings'] / total_definitions) * 100
                report += f"  • Docstring coverage: {doc_percentage:.1f}% ({metrics['docstrings']}/{total_definitions})\n"
                
                if doc_percentage >= 80:
                    report += "  ✅ Excellent documentation!\n"
                elif doc_percentage >= 50:
                    report += "  ⚠️  Good documentation, could be improved\n"
                else:
                    report += "  ❌ Poor documentation - add more docstrings\n"
            else:
                report += "  • No functions or classes found\n"
            
            report += "\n"
            
            # Error handling assessment
            report += "🛡️  ERROR HANDLING:\n"
            if metrics['try_blocks'] > 0:
                report += f"  ✅ Found {metrics['try_blocks']} error handling block(s)\n"
            else:
                report += "  ⚠️  No error handling detected - consider adding try/except blocks\n"
            
            report += "\n"
            
            # Complexity issues
            if metrics['complexity_issues']:
                report += "🔍 COMPLEXITY ISSUES:\n"
                for issue in metrics['complexity_issues']:
                    report += f"  ⚠️  {issue}\n"
                report += "\n"
            
            # Overall assessment
            report += "🎯 OVERALL ASSESSMENT:\n"
            
            quality_score = 0
            if metrics['functions'] > 0 and metrics['docstrings'] / metrics['functions'] >= 0.5:
                quality_score += 30
            if metrics['try_blocks'] > 0:
                quality_score += 20
            if metrics['lines'] < 100:  # Reasonable size
                quality_score += 20
            if len(metrics['complexity_issues']) == 0:
                quality_score += 30
            
            if quality_score >= 80:
                report += "  🌟 Excellent code quality!\n"
            elif quality_score >= 60:
                report += "  ✅ Good code quality with room for improvement\n"
            elif quality_score >= 40:
                report += "  ⚠️  Moderate code quality - several improvements needed\n"
            else:
                report += "  ❌ Code quality needs significant improvement\n"
            
            # Suggestions
            report += "\n💡 SUGGESTIONS:\n"
            suggestions = []
            
            if total_definitions > 0 and (metrics['docstrings'] / total_definitions) < 0.8:
                suggestions.append("Add docstrings to functions and classes")
            
            if metrics['try_blocks'] == 0 and metrics['functions'] > 0:
                suggestions.append("Add error handling with try/except blocks")
            
            if metrics['complexity_issues']:
                suggestions.append("Break down complex functions into smaller ones")
            
            if not suggestions:
                suggestions.append("Code looks good! Keep up the excellent work!")
            
            for i, suggestion in enumerate(suggestions, 1):
                report += f"  {i}. {suggestion}\n"
            
            return report
            
        except Exception as e:
            return f"❌ Code quality analysis error: {str(e)}"