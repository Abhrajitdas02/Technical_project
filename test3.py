import json
import hashlib

def hash_line(line):
    """Generate hash for a line of text."""
    return hashlib.md5(line.strip().encode('utf-8')).hexdigest()

def compare(file_list, log_file="change.log", json_file="change.json"):
    count = 0
    added_tags = []
    deleted_tags = []
    modified_tags = []
    
    with open(file_list[0], 'r', encoding='utf-8') as f1, open(file_list[1], 'r', encoding='utf-8') as f2:
        f1_lines = [line.strip() for line in f1.readlines()]
        f2_lines = [line.strip() for line in f2.readlines()]
        
    # Use sets to find added and deleted lines
    f1_set = set(f1_lines)
    f2_set = set(f2_lines)

    # Detect added tags
    added_tags = list(f2_set - f1_set)
    # Detect deleted tags
    deleted_tags = list(f1_set - f2_set)

    # Detect modified tags (lines present in both but with different content)
    for line in f1_set & f2_set:  # Set intersection (common lines)
        if f1_lines.count(line) != f2_lines.count(line):  # Ensure line count mismatch
            modified_tags.append(line)
            count += 1

    # Write results to log file
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("===== CHANGE LOG =====\n\n")
        log.write(f"Added Tags ({len(added_tags)}):\n")
        for tag in added_tags:
            log.write(f"  - {tag}\n")
        log.write("\n")
        
        log.write(f"Deleted Tags ({len(deleted_tags)}):\n")
        for tag in deleted_tags:
            log.write(f"  - {tag}\n")
        log.write("\n")
        
        log.write(f"Modified Tags ({len(modified_tags)}):\n")
        for tag in modified_tags:
            log.write(f"  - {tag}\n")
        log.write("\n")
        
        if count == 0:
            log.write("No changes detected.\n")
        log.write("===== SUMMARY =====\n")
        log.write(f"Total tags added: {len(added_tags)}\n")
        log.write(f"Total tags deleted: {len(deleted_tags)}\n")
        log.write(f"Total tags modified: {len(modified_tags)}\n")
        log.write(f"Total changes detected: {count}\n")
        
    # Save change data to JSON file
    change_data = {
        "Added Tags": added_tags,
        "Deleted Tags": deleted_tags,
        "Modified Tags": modified_tags,
        "Summary": {
            "Total tags added": len(added_tags),
            "Total tags deleted": len(deleted_tags),
            "Total tags modified": len(modified_tags),
            "Total changes detected": count
        }
    }

    with open(json_file, "w", encoding="utf-8") as json_output:
        json.dump(change_data, json_output, indent=4, ensure_ascii=False)
    
    print(f"Comparison complete. Check {log_file} and {json_file} for details.")
    
compare(["data/test0.csv", "data/test1.csv"]) 
