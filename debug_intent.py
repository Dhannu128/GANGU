#!/usr/bin/env python3
"""Debug intent extraction for urgent order"""

import sys
sys.path.append('.')
from agents.intent_extraction_agent import simple_fallback_parser

test_input = "5 cadbury bournville order kar do urgent"
print(f"Testing input: '{test_input}'")

result = simple_fallback_parser(test_input)
print(f"Fallback parser result:")
for key, value in result.items():
    print(f"  {key}: {value}")

# Test urgency keywords
text_lower = test_input.lower()
urgent_keywords = ["urgent", "jaldi", "abhi", "turant", "emergency", "zaruri"]
urgent_found = [kw for kw in urgent_keywords if kw in text_lower]
print(f"\nUrgent keywords found: {urgent_found}")

# Test quantity detection
import re
quantity_match = re.search(r'\b(\d+)\s*(?:piece|pieces|pc|pcs|kg|kilogram|litre|liter|pack|packs|box|boxes)?\b', text_lower)
if quantity_match:
    print(f"Quantity match: {quantity_match.groups()}")
else:
    print("No quantity match found")

# Test simpler quantity regex
quantity_match2 = re.search(r'\b(\d+)\b', text_lower)
if quantity_match2:
    print(f"Simple quantity match: {quantity_match2.group(1)}")