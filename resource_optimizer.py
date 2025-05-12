def parse_input_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse input file (CSV or JSON) into task data structure."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file {file_path} not found")
    
    if path.suffix == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    
    elif path.suffix == '.csv':
        tasks = []
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse resources JSON string into a dictionary
                if 'resources' in row and row['resources']:
                    try:
                        row['resources'] = json.loads(row['resources'].replace("'", '"'))
                    except json.JSONDecodeError:
                        raise ValueError(f"Invalid JSON in resources field: {row['resources']}")
                else:
                    row['resources'] = {}

                # Convert duration to int
                if 'duration' in row:
                    row['duration'] = int(row['duration'])

                # Clean dependencies field if present
                if 'dependencies' in row and not row['dependencies']:
                    row['dependencies'] = []
                
                tasks.append(row)
        return tasks

    else:
        raise ValueError("Unsupported file format. Please provide CSV or JSON")
