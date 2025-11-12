import json
import os

def load_100kb_template_and_fill(partition, record_counter, legal_tag_name):
    """
    Load the 100KB JSON template and fill in variables programmatically.
    
    This function matches the exact format used in locustfile.py:
    - "id": f"{partition}:dataset--File.Generic:{record_counter}"
    - "kind": f"{partition}:wks:dataset--File.Generic:1.0.0"
    - "acl.owners": f"data.default.owners@{partition}.dataservices.energy"
    - "acl.viewers": f"data.default.viewers@{partition}.dataservices.energy"
    - "legal.legaltags": f"{partition}-{legal_tag_name}"
    
    Args:
        partition (str): OSDU partition name (e.g., self.partition)
        record_counter (int): Record counter for unique ID (e.g., self.record_counter)
        legal_tag_name (str): Legal tag name (e.g., self.legal_tag_name)
    
    Returns:
        dict: JSON object with filled variables, ready for API call
    """
    
    # Get the directory of this script to find the template file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_file = os.path.join(script_dir, "storage_record_100KB.json")
    
    # Read the template file
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Replace template variables with actual values
    filled_content = template_content.format(
        partition=partition,
        record_counter=record_counter,
        legal_tag_name=legal_tag_name
    )
    
    # Parse as JSON and return
    return json.loads(filled_content)

# Example usage for your locustfile.py:
"""
Usage in your test method:

@tag("storage", "record_size_100KB")
@task(6)
def test_create_large_storage_record(self):
    self.logger.info("[Test] [create a large 100KB storage record] API tested: /api/storage/v2/records")
    
    # Generate unique record ID using incrementing counter
    self.record_counter += 1
    
    # Load and fill the 100KB template
    from template_utils import load_100kb_template_and_fill
    large_payload = load_100kb_template_and_fill(
        partition=self.partition,
        record_counter=self.record_counter,
        legal_tag_name=self.legal_tag_name
    )
    
    # Wrap in array format as expected by OSDU Storage API
    payload = [large_payload]
    
    url = self.host + "/api/storage/v2/records"
    response = self.client.put(url, data=json.dumps(payload), headers=self.headers)
    self.logger.info(f"Create large record status: {response.status_code}")
    
    if response.status_code == 201:
        self.logger.info(f"✅ Successfully created large record: {large_payload['id']}")
    else:
        self.logger.error(f"❌ Failed to create large record: {large_payload['id']} Response: {response.text}")
"""

# Test the function if run directly
if __name__ == "__main__":
    # Test with sample values
    test_payload = load_100kb_template_and_fill(
        partition="testpartition",
        record_counter=123,
        legal_tag_name="performance-test-legal-tag"
    )
    
    print("✅ Template loaded and filled successfully!")
    print(f"ID: {test_payload['id']}")
    print(f"Kind: {test_payload['kind']}")  
    print(f"Legal tags: {test_payload['legal']['legaltags']}")
    print(f"ACL owners: {test_payload['acl']['owners'][0]}")
    print(f"ACL viewers: {test_payload['acl']['viewers'][0]}")
    print(f"Data logs count: {len(test_payload['data']['logs'])}")
    
    # Calculate size
    json_str = json.dumps(test_payload)
    size_kb = len(json_str.encode('utf-8')) / 1024
    print(f"Filled payload size: {size_kb:.1f} KB")