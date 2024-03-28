#!/bin/bash

# Define the path to the template and the output file
template_path="images.py.template"
output_path="images.py"

# Start with copying the template to the output
cp "$template_path" "$output_path"

# Placeholder in the template to be replaced
placeholder="# IMAGES_PLACEHOLDER"

# Initialize an empty string to hold the dictionary entries
map_entries=""

# Process each SVG file
for svg in *.svg; do
    # Minify the SVG file using svgo and encode it to base64
    encoded=$(svgo "$svg" -o - | base64 -w 0)

    # Extract the file name without extension for the Python dictionary key
    name=$(basename "$svg" .svg)

    # Append the dictionary entry to the map entries string
    map_entries+="    \"$name\": \"data:image/svg+xml;base64,$encoded\",\n"
done

# Remove the last newline and comma from the map entries
map_entries=${map_entries%$'\n',}

# Replace the placeholder in the output file with the map entries
awk -v placeholder="$placeholder" -v replacement="$map_entries" '{sub(placeholder,replacement)}1' "$output_path" > "${output_path}.tmp" && mv "${output_path}.tmp" "$output_path"
