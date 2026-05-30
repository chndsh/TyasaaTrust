# TyasaaTrust - Psychometric Collaboration Guide

## For Person A and Person C

### Key Responsibilities:
- Administer psychometric assessments using questions.py question bank
- Validate psychometric scores through psych.py routing
- Integrate results into psychometric.py analysis framework

### Understanding the Question Structure:

Each question in questions.py:
1. Four options (A-D) with weighted scores for:
   - Integrity (0-4)
   - Financial Discipline (0-4)
   - Resilience (0-4)

### Cluster Mapping:
C1: Udharo & Khata (Q01-Q04)
C2: Festive Cycle Pressure (Q05-Q08)
C3: Supplier & Inventory Decisions (Q09-Q12)
C4: Business Setbacks & Loss Recovery (Q13-Q16)
C5: Growth Decisions Under Uncertainty (Q17-Q20)

### Collaboration Workflow:
1. Person A/C creates question sets per cluster
2. Person B administers assessments and records responses
3. Person C analyzes results using psychometric.py
4. All outputs stored in /backend/data directory

### Critical Scoring Rules:
- Total score per question = sum of weights across traits
- Cluster performance requires average >3.5 threshold
- Individual trait scores below 2 trigger recomputation

### File Integration:
- Questions.py: Core question bank
- Psychometric.py: Calculation engine
- Psych.py: Result routing

### Risk Mitigation:
- Always validate contradictory answers across traits
- Document any system changes in person_b.md
- Maintain audit trail of all question modifications