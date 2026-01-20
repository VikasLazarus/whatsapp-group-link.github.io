#!/bin/bash
# Loop through all markdown files in _posts
find _posts -name "*.md" | while read filename; do
  # Get the last git commit date for the file
  git_date=$(git log -1 --format="%ad" --date=iso-strict -- "$filename")
  
  # Check if the file already has a last_modified_at field
  if grep -q "last_modified_at:" "$filename"; then
    # Update existing field (MacOS users might need 'sed -i ""')
    sed -i "s/^last_modified_at: .*/last_modified_at: $git_date/" "$filename"
  else
    # Insert new field after the second line (usually after title/layout)
    sed -i "2ilast_modified_at: $git_date" "$filename"
  fi
done