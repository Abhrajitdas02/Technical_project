import pandas as pd
import json
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger()

def compare_csv_advanced(file1, file2, log_file="change.log", json_file="change.json"):
    # Read the CSV files into DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Ensure that both DataFrames have the same columns and rows (reindex if needed)
    df1, df2 = df1.align(df2, axis=1, join='outer')  # Align columns
    df1, df2 = df1.align(df2, axis=0, join='outer')  # Align rows

    # Identify added and removed rows (based on index)
    added = pd.concat([df1, df2]).drop_duplicates(keep=False)
    removed = pd.concat([df2, df1]).drop_duplicates(keep=False)

    # Compare the DataFrames to identify modified values
    differences = df1.compare(df2)

    # Flatten multi-level columns for JSON compatibility
    differences.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in differences.columns]

    # Log changes to change.log with formatted output
    with open(log_file, "w", encoding="utf-8") as log:
        log.write("===== CHANGE LOG =====\n\n")
        
        # Log added rows
        log.write(f"\n===== ADDED ROWS ({len(added)}) =====\n")
        if len(added) > 0:
            log.write(f"{added}\n")
        else:
            log.write("No added rows.\n")

        # Log removed rows
        log.write(f"\n===== REMOVED ROWS ({len(removed)}) =====\n")
        if len(removed) > 0:
            log.write(f"{removed}\n")
        else:
            log.write("No removed rows.\n")

        # Log modified values
        log.write(f"\n===== MODIFIED VALUES ({len(differences)}) =====\n")
        if not differences.empty:
            log.write(f"{differences}\n")
        else:
            log.write("No modified values.\n")

        # Log summary
        log.write("\n===== SUMMARY =====\n")
        log.write(f"Total rows added: {len(added)}\n")
        log.write(f"Total rows removed: {len(removed)}\n")
        log.write(f"Total modified: {len(differences)}\n")
        log.write("\n===== END OF LOG =====\n")

    # Log information using log.info()
    logger.info("===== CHANGE LOG =====")
    logger.info(f"Added rows ({len(added)}):\n{added if len(added) > 0 else 'No added rows'}")
    logger.info(f"Removed rows ({len(removed)}):\n{removed if len(removed) > 0 else 'No removed rows'}")
    logger.info(f"Modified values:\n{differences if not differences.empty else 'No modified values'}")
    logger.info(f"Total rows added: {len(added)}")
    logger.info(f"Total rows removed: {len(removed)}")
    logger.info(f"Total modified: {len(differences)}")
    logger.info("===== END OF LOG =====")

    # Store the data in a JSON file
    change_data = {
        "Added Rows": added.to_dict(orient="records"),
        "Removed Rows": removed.to_dict(orient="records"),
        "Modified Values": differences.to_dict(orient="records"),
        "Summary": {
            "Total rows added": len(added),
            "Total rows removed": len(removed),
            "Total modified": len(differences)
        }
    }

    with open(json_file, "w", encoding="utf-8") as json_output:
        json.dump(change_data, json_output, indent=4, ensure_ascii=False)
    
    print(f"Comparison complete. Check {log_file} and {json_file} for details.")
    
compare_csv_advanced(f"data/test0.csv", f"data/test1.csv", log_file="change.log", json_file="change.json")