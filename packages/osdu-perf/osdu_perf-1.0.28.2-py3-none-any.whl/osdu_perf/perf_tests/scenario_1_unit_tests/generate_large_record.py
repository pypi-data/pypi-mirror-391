import json
import random

# OSDU partition and legal tag variables (matching locustfile.py pattern)
partition = "opendes"
legal_tag_name = "performance-test-legal-tag"
record_counter = 1

# Base structure matching OSDU locustfile.py pattern
record = {
    "id": f"{partition}:dataset--File.Generic:{record_counter}",
    "kind": f"{partition}:wks:dataset--File.Generic:1.0.0",
    "acl": {
        "owners": [f"data.default.owners@{partition}.dataservices.energy"],
        "viewers": [f"data.default.viewers@{partition}.dataservices.energy"]
    },
    "legal": {
        "legaltags": [f"{partition}-{legal_tag_name}"],
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
    record["data"]["logs"].append(log_entry)

# Write to file
with open("storage_record_100KB.json", "w") as f:
    json.dump(record, f, indent=2)

# Check file size
import os
file_size = os.path.getsize("storage_record_100KB.json")
print(f"Generated file size: {file_size} bytes ({file_size/1024:.1f} KB)")