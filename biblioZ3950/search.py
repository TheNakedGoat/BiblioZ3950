import json
import csv
from typing import Dict, List
from PyZ3950-ccl import zoom

def load_config(file_path: str) -> Dict:
    with open(file_path, 'r') as f:
        return json.load(f)

def parse_input(input_str: str) -> Dict[str, List[str]]:
    parsed = {}
    reader = csv.reader([input_str])
    for row in reader:
        for item in row:
            key, value = item.split('=')
            parsed[key.strip()] = [v.strip() for v in value.split(',')]
    return parsed

def generate_ccl_query(mapping: Dict, params: Dict[str, List[str]]) -> str:
    query_parts = []
    for key, values in params.items():
        if key in mapping:
            use = mapping[key]['use']
            term_parts = [f'@attr 1={use} "{value}"' for value in values]
            if len(term_parts) > 1:
                query_parts.append(f"({' or '.join(term_parts)})")
            else:
                query_parts.append(term_parts[0])
    return ' and '.join(query_parts)

def query_z3950_server(config: Dict, query: str) -> List[Dict]:
    conn = zoom.Connection(config['server']['host'], config['server']['port'])
    conn.databaseName = config['server']['database']
    conn.preferredRecordSyntax = 'UNIMARC'

    query = zoom.Query('CCL', query)
    results = conn.search(query)

    records = []
    for result in results:
        record = result.data.decode('utf-8', errors='ignore')
        parsed_record = parse_unimarc(record)
        records.append(parsed_record)

    conn.close()
    return records

def parse_unimarc(record: str) -> Dict:
    parsed = {}
    lines = record.split('\n')
    for line in lines:
        if line.startswith('2'):  # Descriptive fields
            tag = line[:3]
            if tag == '200':  # Title and statement of responsibility area
                parsed['title'] = line[11:].strip()
            elif tag == '210':  # Publication, distribution, etc. area
                parsed['publisher'] = line[11:].strip()
            elif tag == '700':  # Personal name - primary responsibility
                parsed['author'] = line[11:].strip()
    return parsed

def main():
    config = load_config('assets/config.json')
    
    user_input = input("Enter search parameters (key=value, separated by commas): ")
    params = parse_input(user_input)
    
    ccl_query = generate_ccl_query(config['search_mapping'], params)
    print(f"Generated CCL Query: {ccl_query}")

    results = query_z3950_server(config, ccl_query)
    
    print(f"\nFound {len(results)} results:")
    for i, record in enumerate(results, 1):
        print(f"\nResult {i}:")
        for key, value in record.items():
            print(f"{key.capitalize()}: {value}")

if __name__ == "__main__":
    main()
