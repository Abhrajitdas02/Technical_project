import csv
import json
import logging

# Configure logging
logging.basicConfig(filename='change.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def compare_csv(file1, file2):
    def read_csv_to_dict(filepath):
        """Helper function to read a CSV file into a dictionary keyed by the 'Tag' column."""
        data = {}
        with open(filepath, 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                tag = row[0]  # Assuming Tag column is at index 0
                data[tag] = row
        return data

    # Read both files into dictionaries keyed by 'Tag'
    f1_data = read_csv_to_dict(file1)
    f2_data = read_csv_to_dict(file2)

    # Lists to store added, removed, and modified rows
    added_rows = []
    removed_rows = []
    modified_rows = []

    # Check for added and modified rows
    for tag, row2 in f2_data.items():
        if tag not in f1_data:
            added_rows.append(row2)  # Row only in file2 (added)
        else:
            row1 = f1_data[tag]
            # Check if Title, Class, or ID columns have changed
            title_index, class_index, id_index = 1, 2, 3
            if (
                row1[title_index] != row2[title_index] or
                row1[class_index] != row2[class_index] or
                row1[id_index] != row2[id_index]
            ):
                modified_rows.append((row1, row2))  # Row present in both, but with changes

    # Check for removed rows (present in file1 but not in file2)
    for tag, row1 in f1_data.items():
        if tag not in f2_data:
            removed_rows.append(row1)

    # Log the changes in the change.log file with clear sections and formatting
    logging.info("=====================================================")
    logging.info("                 CSV COMPARISON RESULT               ")
    logging.info("=====================================================")

    # Added Rows Section
    logging.info("\n# Added Rows")
    logging.info("-----------------------------------------------------")
    logging.info(f"Total Added Rows: {len(added_rows)}")
    for row in added_rows:
        logging.info(f"Added Row: {row}")

    # Removed Rows Section
    logging.info("\n# Removed Rows")
    logging.info("-----------------------------------------------------")
    logging.info(f"Total Removed Rows: {len(removed_rows)}")
    for row in removed_rows:
        logging.info(f"Removed Row: {row}")

    # Modified Rows Section
    logging.info("\n# Modified Rows")
    logging.info("-----------------------------------------------------")
    logging.info(f"Total Modified Rows: {len(modified_rows)}")
    for row1, row2 in modified_rows:
        logging.info(f"Modified Row: From {row1} -> To {row2}")

    # Save the changes to a JSON file with proper indentation
    changes = {
        "added_rows": len(added_rows),
        "removed_rows": len(removed_rows),
        "modified_rows": len(modified_rows),
        "added_rows_details": added_rows,
        "removed_rows_details": removed_rows,
        "modified_rows_details": modified_rows
    }

    with open('changes.json', 'w', encoding='utf-8') as json_file:
        json.dump(changes, json_file, indent=4)

# Example usage
compare_csv("data/test0.csv", "data/test1.csv")

print("done")
