import json
import os

def load_and_fill_template(template_file, partition, record_counter, legal_tag_name):
    """
    Load a JSON template file and fill in the variables programmatically.
    
    Args:
        template_file (str): Path to the template JSON file
        partition (str): OSDU partition name
        record_counter (int): Record counter for unique ID
        legal_tag_name (str): Legal tag name
    
    Returns:
        dict: JSON object with filled variables
    """
    
    # Read the template file
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Replace template variables
    filled_content = template_content.format(
        partition=partition,
        record_counter=record_counter,
        legal_tag_name=legal_tag_name
    )
    
    # Parse as JSON and return
    return json.loads(filled_content)

def create_large_payload_from_template(template_file="storage_record_100KB_template.json", 
                                     partition="opendes", 
                                     record_counter=1, 
                                     legal_tag_name="performance-test-legal-tag"):
    """
    Create a large payload from template that matches locustfile.py format.
    
    Usage example in your test:
        payload = create_large_payload_from_template(
            partition=self.partition,
            record_counter=self.record_counter,
            legal_tag_name=self.legal_tag_name
        )
    """
    return load_and_fill_template(template_file, partition, record_counter, legal_tag_name)

# Example usage:
if __name__ == "__main__":
    # Test the template loading
    payload = create_large_payload_from_template(
        partition="testpartition",
        record_counter=123,
        legal_tag_name="test-legal-tag"
    )
    
    print("Template filled successfully!")
    print(f"ID: {payload['id']}")
    print(f"Kind: {payload['kind']}")
    print(f"Legal tags: {payload['legal']['legaltags']}")
    print(f"ACL owners: {payload['acl']['owners']}")
    print(f"Data logs count: {len(payload['data']['logs'])}")
    
    # Calculate approximate size
    json_str = json.dumps(payload)
    size_kb = len(json_str.encode('utf-8')) / 1024
    print(f"Approximate size: {size_kb:.1f} KB")