"""
Security Analyzer - detects prompt injection vulnerabilities and unsafe patterns.
"""

import re
from typing import Dict, List, Tuple
from ..core.models import ParsedPrompt, Issue


class SecurityAnalyzer:
    """Analyzes prompts for security vulnerabilities."""
    
    # High-risk injection patterns
    HIGH_RISK_PATTERNS = [
        (r'\bignore\s+(all\s+)?previous\s+(instructions|commands|prompt)', 'Prompt override attempt'),
        (r'\breveal\s+(the\s+)?system\s+prompt', 'System prompt leakage attempt'),
        (r'\bshow\s+(me\s+)?your\s+(system\s+)?prompt', 'System prompt disclosure attempt'),
        (r'\b(act|pretend|role-play)\s+as\s+.*\s+and\s+(ignore|forget|disregard)', 'Role confusion attack'),
        (r'\bforgot\s+all\s+previous\s+instructions', 'Instruction override attempt'),
        (r'\b(execute|eval|run|compile)\s+.*code', 'Code execution risk'),
    ]
    
    # Medium-risk patterns
    MEDIUM_RISK_PATTERNS = [
        (r'\{[^}]+\}', 'Unvalidated variable placeholder'),
        (r'\$\{[^}]+\}', 'Unvalidated variable placeholder'),
        (r'<[^>]+>', 'Unvalidated variable placeholder'),
        (r'\bexecute\b', 'Potential code execution'),
        (r'\beval\b', 'Potential code execution'),
        (r'\breturn\s+internal', 'Potential information disclosure'),
        (r'\bdebug\s+mode', 'Debug mode reference'),
    ]
    
    # Low-risk patterns (mostly informational)
    LOW_RISK_PATTERNS = [
        (r'\btranslate\b', 'Safe translation operation'),
        (r'\bsummarize\b', 'Safe summarization operation'),
        (r'\bexplain\b', 'Safe explanation operation'),
    ]
    
    @classmethod
    def analyze(cls, parsed: ParsedPrompt) -> Tuple[float, List[Issue], List[str]]:
        """
        Analyze prompt for security issues.
        
        Returns (score, issues, suggestions)
        """
        issues = []
        suggestions = []
        score = 10.0
        
        text_lower = parsed.raw_text.lower()
        text = parsed.raw_text
        lines = text.splitlines()
        
        # Check high-risk patterns
        for pattern, description in cls.HIGH_RISK_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        severity='high',
                        category='security',
                        description=f'HIGH RISK: {description}',
                        location=line_num,
                        suggestion='Remove or rephrase this instruction to prevent prompt injection',
                    ))
                    score -= 3.0
        
        # Check medium-risk patterns
        for pattern, description in cls.MEDIUM_RISK_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append(Issue(
                        severity='medium',
                        category='security',
                        description=f'MEDIUM RISK: {description}',
                        location=line_num,
                        suggestion='Consider adding input validation or sanitization',
                    ))
                    score -= 1.5
        
        # Check for unguarded variables
        unguarded = cls._check_unguarded_variables(parsed)
        for line_num, var_name in unguarded:
            issues.append(Issue(
                severity='medium',
                category='security',
                description=f'Unguarded user input: {var_name}',
                location=line_num,
                suggestion=f'Add validation for {var_name} or document expected input constraints',
            ))
            score -= 1.0
        
        # Normalize score
        score = max(0.0, min(10.0, score))
        
        # Add suggestions
        if len(parsed.variables) > 0:
            suggestions.append('Consider documenting validation rules for all variables')
        
        if score < 5.0:
            suggestions.append('High security risk detected - review and test thoroughly before production use')
        elif score < 7.0:
            suggestions.append('Medium security risk - add input validation to reduce attack surface')
        
        return score, issues, suggestions
    
    @classmethod
    def _check_unguarded_variables(cls, parsed: ParsedPrompt) -> List[Tuple[int, str]]:
        """Identify variables that lack validation."""
        results = []
        
        # Check if variables appear directly without validation context
        for var in parsed.variables:
            # Check surrounding lines for validation keywords
            lines = parsed.raw_text.splitlines()
            
            if var.location > 0 and var.location <= len(lines):
                # Look at context around variable
                context_start = max(0, var.location - 2)
                context_end = min(len(lines), var.location + 2)
                context = ' '.join(lines[context_start:context_end]).lower()
                
                # Check for validation keywords
                has_validation = any(kw in context for kw in [
                    'validate', 'sanitize', 'check', 'verify', 'constraint',
                    'must', 'should', 'required', 'only', 'allowed',
                ])
                
                if not has_validation:
                    results.append((var.location, var.name))
        
        return results
