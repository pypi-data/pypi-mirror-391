import json
import random
import hashlib

# Template variables for programmatic filling
# These will be replaced at execution time:
# {partition} - OSDU partition name
# {record_counter} - Record counter for unique ID  
# {legal_tag_name} - Legal tag name

# Base structure for seismic dataset with template variables
record = {
    "id": "{partition}:dataset--File.Generic:{record_counter}",
    "kind": "{partition}:wks:dataset--File.Generic:1.0.0",
    "acl": {
        "owners": ["data.default.owners@{partition}.dataservices.energy"],
        "viewers": ["data.default.viewers@{partition}.dataservices.energy"]
    },
    "legal": {
        "legaltags": ["{partition}-{legal_tag_name}"],
        "otherRelevantDataCountries": ["US", "GB"],
        "status": "compliant"
    },
    "data": {
        "Name": "Large Seismic Dataset",
        "ResourceSecurityClassification": "Public",
        "FileSourceInfo": {
            "FileSource": "s3://seismic-bucket/NorthSea3D_2024.sgy",
            "PreloadFilePath": "NorthSea3D_2024.sgy"
        },
        "surveyName": "NorthSea3D_2024",
        "operator": "GeoEnergy",
        "acquisitionDate": "2024-02-01",
        "grid": {
            "xlines": 8000,
            "ilines": 4000,
            "binSize": 12.5
        },
        "volumeCount": 50,
        "files": []
    },
    "createTime": "2025-11-10T10:00:00Z",
    "modifyTime": "2025-11-10T10:00:00Z"
}

# File extensions for variety
extensions = [".zgy", ".segy", ".sgy", ".dat", ".bin", ".seg", ".sgz"]

# Generate random checksum
def generate_checksum():
    random_string = str(random.randint(1000000, 9999999))
    return hashlib.sha256(random_string.encode()).hexdigest()[:12] + "..."

# Generate 5000 file entries to reach approximately 1MB
print("Generating file entries...")
for i in range(5000):
    if i % 1000 == 0:
        print(f"Generated {i} entries...")
    
    line_number = str(i + 1).zfill(4)
    extension = random.choice(extensions)
    file_entry = {
        "filename": f"NorthSea3D_line_{line_number}{extension}",
        "uri": f"https://storage.example.com/seismic/{line_number}{extension}",
        "sizeBytes": random.randint(50000000, 200000000),  # 50MB to 200MB file sizes
        "checksum": f"sha256-{generate_checksum()}"
    }
    record["data"]["files"].append(file_entry)

print("Writing to file...")
# Write to file
with open("storage_record_1MB.json", "w") as f:
    json.dump(record, f, indent=2)

# Check file size
import os
file_size = os.path.getsize("storage_record_1MB.json")
print(f"Generated file size: {file_size} bytes ({file_size/1024:.1f} KB, {file_size/(1024*1024):.2f} MB)")
print(f"Number of file entries: {len(record['data']['files'])}")