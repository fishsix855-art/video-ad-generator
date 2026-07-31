import re

SENSITIVE_KEYWORDS = ['best', 'first', 'only', '100%', 'absolute']
COMPLIANCE_CHECKS = [(r'unlimited.*data', 'Check: unlimited claims')]

def check_safety(content):
    issues = []
    lower = content.lower()
    for kw in SENSITIVE_KEYWORDS:
        if kw in lower:
            issues.append('Sensitive: ' + kw)
    for pat, adv in COMPLIANCE_CHECKS:
        if re.search(pat, lower):
            issues.append(adv)
    if len(content) < 10:
        issues.append('Content too short')
    passed = len(issues) == 0
    return {'success': True, 'passed': passed, 'issues': issues, 'score': 1.0 if passed else max(0, 1.0 - len(issues) * 0.15)}

def filter_sensitive(content):
    return content
