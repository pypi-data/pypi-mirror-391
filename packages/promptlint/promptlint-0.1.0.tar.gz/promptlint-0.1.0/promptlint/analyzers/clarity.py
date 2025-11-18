"""
Clarity Analyzer - evaluates prompt clarity and specificity.
"""

from typing import List, Tuple
from ..core.models import ParsedPrompt, Issue, ScoreResult
from ..core.parser import PromptParser


class ClarityAnalyzer:
    """Analyzes prompt clarity and provides suggestions."""
    
    # Heuristic weights
    WEIGHTS = {
        'clear_structure': 2.0,
        'has_examples': 1.0,
        'has_output_format': 1.5,
        'step_by_step': 1.0,
        'specific_terms': 0.5,
        'ambiguous_phrases': -0.5,
        'conflicting_instructions': -2.0,
        'vague_quantities': -0.75,
    }
    
    @classmethod
    def analyze(cls, parsed: ParsedPrompt) -> Tuple[float, List[Issue], List[str]]:
        """
        Analyze prompt clarity.
        
        Returns (score, issues, suggestions)
        """
        issues = []
        suggestions = []
        score = 5.0  # Base score
        
        # Check for clear structure
        if len(parsed.instructions) > 0:
            score += cls.WEIGHTS['clear_structure']
        else:
            issues.append(Issue(
                severity='high',
                category='clarity',
                description='No clear instructions detected',
                suggestion='Add explicit imperative instructions (start with action verbs)',
            ))
        
        # Check for examples
        if len(parsed.examples) > 0:
            score += cls.WEIGHTS['has_examples']
        else:
            suggestions.append('Add examples to clarify expected input/output')
        
        # Check for output format
        if parsed.output_format is not None:
            score += cls.WEIGHTS['has_output_format']
        else:
            suggestions.append('Specify expected output format (JSON, markdown, etc.)')
        
        # Check for step-by-step
        has_steps = any('step' in instr.text.lower() for instr in parsed.instructions)
        if has_steps:
            score += cls.WEIGHTS['step_by_step']
        
        # Look for ambiguous phrases
        ambiguous_issues = cls._check_ambiguous_phrases(parsed)
        issues.extend(ambiguous_issues)
        score -= len(ambiguous_issues) * abs(cls.WEIGHTS['ambiguous_phrases'])
        
        # Check for vague quantities
        vague_quantities = cls._check_vague_quantities(parsed)
        if vague_quantities:
            for line_num, phrase, suggestion in vague_quantities:
                issues.append(Issue(
                    severity='medium',
                    category='clarity',
                    description=f'Vague quantity: "{phrase}"',
                    location=line_num,
                    suggestion=suggestion,
                ))
                score += cls.WEIGHTS['vague_quantities']
        
        # Check for conflicting instructions
        conflicts = cls._check_conflicts(parsed)
        if conflicts:
            for conflict_desc in conflicts:
                issues.append(Issue(
                    severity='high',
                    category='clarity',
                    description=conflict_desc,
                    suggestion='Review instructions for contradictions',
                ))
                score += cls.WEIGHTS['conflicting_instructions']
        
        # Check variable usage
        if len(parsed.variables) > 0 and not parsed.metadata.get('has_examples'):
            suggestions.append('Provide example values for variables to improve clarity')
        
        # Normalize score to 0-10
        score = max(0.0, min(10.0, score))
        
        return score, issues, suggestions
    
    @classmethod
    def _check_ambiguous_phrases(cls, parsed: ParsedPrompt) -> List[Issue]:
        """Detect ambiguous and weak phrases."""
        issues = []
        ambiguous_phrases = PromptParser.AMBIGUOUS_PHRASES
        
        lines = parsed.raw_text.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            for phrase, suggestion in ambiguous_phrases.items():
                if phrase in line_lower:
                    issues.append(Issue(
                        severity='medium',
                        category='clarity',
                        description=f'Ambiguous phrase: "{phrase}"',
                        location=line_num,
                        suggestion=suggestion,
                    ))
        
        return issues
    
    @classmethod
    def _check_vague_quantities(cls, parsed: ParsedPrompt) -> List[Tuple[int, str, str]]:
        """Detect vague quantity expressions."""
        results = []
        lines = parsed.raw_text.splitlines()
        
        vague_patterns = [
            ('many', 'Specify exact number instead of "many"'),
            ('few', 'Specify exact number instead of "few"'),
            ('large', 'Define "large" precisely (size, length, etc.)'),
            ('small', 'Define "small" precisely (size, length, etc.)'),
            ('a lot', 'Specify quantity instead of "a lot"'),
            ('some', 'Be more specific than "some"'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            for vague_word, suggestion in vague_patterns:
                if f' {vague_word} ' in f' {line_lower} ':
                    results.append((line_num, vague_word, suggestion))
        
        return results
    
    @classmethod
    def _check_conflicts(cls, parsed: ParsedPrompt) -> List[str]:
        """Detect conflicting instructions."""
        conflicts = []
        
        # Simple conflict detection
        text_lower = parsed.raw_text.lower()
        
        conflict_pairs = [
            (('be brief', 'be detailed'), 'Cannot be both brief and detailed'),
            (('concise', 'elaborate'), 'Cannot be both concise and elaborate'),
            (('include all', 'exclude'), 'Conflicting inclusion/exclusion instructions'),
            (('ignore', 'consider'), 'Conflicting consideration instructions'),
        ]
        
        for (phrase1, phrase2), description in conflict_pairs:
            if phrase1 in text_lower and phrase2 in text_lower:
                conflicts.append(description)
        
        return conflicts
