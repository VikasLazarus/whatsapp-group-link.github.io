import csv

def process_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Read the header
        try:
            header = next(reader)
            writer.writerow(header) # Write the header to output exactly as is
        except StopIteration:
            return # Empty file

        processed_count = 0
        skipped_count = 0
        
        for row in reader:
            if not row: continue
            
            # Identify the group name column
            # Adjust index if your CSV structure is different. 
            # Assuming standard structure: category, group_name, whatsapp_link, status
            # group_name is likely at index 1
            if len(row) > 1:
                group_name = row[1]
            else:
                group_name = row[0]

            # FILTER LOGIC ONLY: Remove "Features"
            if "features" in group_name.lower():
                skipped_count += 1
                continue
            
            # Write the row exactly as it was in the input (preserving original category)
            writer.writerow(row)
            processed_count += 1

    print(f"Done! Processed {processed_count} groups.")
    print(f"Removed {skipped_count} groups named 'Features'.")
    print(f"Saved to: {output_file}")

# --- Execution ---
if __name__ == "__main__":
    # Replace with your actual file names
    input_filename = "input_groups.csv"
    output_filename = "filtered_groups.csv"
    
    process_csv(input_filename, output_filename)