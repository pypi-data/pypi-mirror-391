import json
import random

# Template variables for programmatic filling
# These will be replaced at execution time:
# {partition} - OSDU partition name
# {record_counter} - Record counter for unique ID  
# {legal_tag_name} - Legal tag name

# Base structure with template variables
record_template = {
    "id": "{partition}:dataset--File.Generic:{record_counter}",
    "kind": "{partition}:wks:dataset--File.Generic:1.0.0",
    "acl": {
        "owners": ["data.default.owners@{partition}.dataservices.energy"],
        "viewers": ["data.default.viewers@{partition}.dataservices.energy"]
    },
    "legal": {
        "legaltags": ["{partition}-{legal_tag_name}"],
        "otherRelevantDataCountries": ["US"],
        "status": "compliant"
    },
    "data": {
        "Name": "Large Test File",
        "ResourceSecurityClassification": "Public",
        "FileSourceInfo": {
            "FileSource": "s3://test-bucket/large-data.csv",
            "PreloadFilePath": "large-data.csv"
        },
        "logs": []
    },
    "createTime": "2025-11-10T10:00:00Z",
    "modifyTime": "2025-11-10T10:00:00Z"
}

# Lithology types for variety
lithologies = ["sandstone", "shale", "limestone", "dolomite", "siltstone", "mudstone", "conglomerate", "anhydrite"]

# Remarks for variety
remarks = [
    "good zone", "high gamma reading", "carbonate zone", "tight formation", "porous zone",
    "mudstone layer", "dense carbonate", "high porosity", "radioactive shale", "medium porosity",
    "tight carbonate", "good reservoir", "excellent porosity", "hot shale", "moderate porosity",
    "reservoir quality", "sealing layer", "high permeability", "dense formation", "fair reservoir",
    "clay rich", "vuggy porosity", "organic rich", "clean sand", "crystalline",
    "unconsolidated", "radioactive zone", "dolomitic", "arkosic sand", "bentonitic",
    "friable sand", "quartz rich", "illitic shale", "oolitic texture", "cemented zone",
    "black shale", "clean reservoir", "micritic", "feldspathic", "pyritic shale",
    "fossiliferous", "glauconitic", "carbonaceous", "high net pay", "anhydritic",
    "bioturbated", "fissile shale", "chalky texture", "cross bedded", "uranium bearing"
]

# Generate ~500 log entries to get closer to 100KB
for i in range(500):
    depth = 1000 + i
    log_entry = {
        "depth": depth,
        "gamma": round(random.uniform(60.0, 120.0), 1),
        "resistivity": round(random.uniform(1.0, 6.0), 1),
        "porosity": round(random.uniform(0.05, 0.30), 2),
        "lithology": random.choice(lithologies),
        "remarks": random.choice(remarks)
    }
    record_template["data"]["logs"].append(log_entry)

# Write template to file with variables intact
with open("storage_record_100KB.json", "w") as f:
    json.dump(record_template, f, indent=2)

# Check file size
import os
file_size = os.path.getsize("storage_record_100KB.json")
print(f"Generated template file size: {file_size} bytes ({file_size/1024:.1f} KB)")
print(f"Template variables included:")
print(f"  - {{partition}} in id, kind, acl, and legal sections")
print(f"  - {{record_counter}} in id")
print(f"  - {{legal_tag_name}} in legal tags")
print(f"Number of log entries: {len(record_template['data']['logs'])}")