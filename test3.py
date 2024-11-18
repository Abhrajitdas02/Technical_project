
import logging
import csv
import json
def compare(file_list, log_file="change.log", json_file="change.json"):
    try:
        print("Comparing files for changes...")
        added_rows = []
        deleted_rows = []
        modified_rows = []

        # Read CSV files as lists of dictionaries
        with open(file_list[0], 'r', encoding='utf-8') as f1, open(file_list[1], 'r', encoding='utf-8') as f2:
            csv1 = list(csv.DictReader(f1))
            csv2 = list(csv.DictReader(f2))

        # Convert rows to sets of frozensets for detecting added and deleted rows
        csv1_set = {frozenset(row.items()) for row in csv1}
        csv2_set = {frozenset(row.items()) for row in csv2}

        # Detect added and deleted rows
        added_rows = [dict(row) for row in (csv2_set - csv1_set)]
        deleted_rows = [dict(row) for row in (csv1_set - csv2_set)]

        # Create dictionaries for rows indexed by Tag for modification comparison
        csv1_dict = {row["Tag"]: row for row in csv1 if "Tag" in row}
        csv2_dict = {row["Tag"]: row for row in csv2 if "Tag" in row}

        # Detect modified rows
        common_tags = set(csv1_dict.keys()) & set(csv2_dict.keys())
        for tag in common_tags:
            row1 = csv1_dict[tag]
            row2 = csv2_dict[tag]

            # Compare specific columns for modifications
            changes = {}
            for field in ["Title", "Class", "ID"]:
                if row1.get(field) != row2.get(field):
                    changes[field] = {"Old": row1.get(field, ""), "New": row2.get(field, "")}

            if changes:  # If any field is modified, add to modified rows
                modified_rows.append({"Tag": tag, "Changes": changes})

        # Save changes to log file
        print("Logging changes to file...")
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write("===== CHANGE LOG =====\n\n")

            log.write(f"Added Rows ({len(added_rows)}):\n")
            for row in added_rows:
                log.write(f"  - {row}\n")
            log.write("\n")

            log.write(f"Deleted Rows ({len(deleted_rows)}):\n")
            for row in deleted_rows:
                log.write(f"  - {row}\n")
            log.write("\n")

            log.write(f"Modified Rows ({len(modified_rows)}):\n")
            for row in modified_rows:
                log.write(f"  - Tag: {row['Tag']}\n")
                for field, change in row["Changes"].items():
                    log.write(f"    {field}: Old: '{change['Old']}', New: '{change['New']}'\n")
            log.write("\n")

            log.write("===== SUMMARY =====\n")
            log.write(f"Total rows added: {len(added_rows)}\n")
            log.write(f"Total rows deleted: {len(deleted_rows)}\n")
            log.write(f"Total rows modified: {len(modified_rows)}\n")

        # Save changes to JSON file
        print("Saving changes to JSON file...")
        changes_summary = {
            "AddedRows": added_rows,
            "DeletedRows": deleted_rows,
            "ModifiedRows": modified_rows,
            "Summary": {
                "TotalAdded": len(added_rows),
                "TotalDeleted": len(deleted_rows),
                "TotalModified": len(modified_rows),
            }
        }
        with open(json_file, 'w', encoding='utf-8') as json_out:
            json.dump(changes_summary, json_out, indent=4)

        logging.info(f"Comparison complete. Check {log_file} and {json_file} for details.")

    except Exception as e:
        logging.error(f"Error in compare function: {e}")

compare(["data/test0.csv", "data/test1.csv"])