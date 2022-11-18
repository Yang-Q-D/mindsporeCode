"""
Beautify the results
"""

import sys
import json

try:
    result_path = sys.argv[1]
except IndexError:
    print("Please enter result file path.")
    exit(1)

with open(result_path, 'r') as f:
    d = json.load(f)
    print("\n================================")
    print(d['title'])
    print("--------------------------------")
    print(d['value'][0]['key'], ": ", d['value'][0]['value'])
    print(d['value'][1]['key'], ": ", d['value'][1]['value'])
    print("--------------------------------")
    for item in d['value'][2:]:
        print(item['key'], ": ", item['value'])
    print("================================\n")
