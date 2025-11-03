#!/bin/bash

# Script to render the Charybdis keymap
# This parses the ZMK keymap and generates an SVG visualization

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "🎨 Rendering Charybdis keymap..."

# Parse the ZMK keymap file
echo "📝 Parsing keymap from config/charybdis.keymap..."
keymap -c "$SCRIPT_DIR/config.yaml" parse -z "$PROJECT_ROOT/config/charybdis.keymap" \
    -b "$SCRIPT_DIR/tim_keymap.yaml" > "$SCRIPT_DIR/tim_keymap_parsed.yaml"

# Draw the SVG using the physical layout JSON
echo "🖼️  Drawing SVG with physical layout..."
keymap -c "$SCRIPT_DIR/config.yaml" draw "$SCRIPT_DIR/tim_keymap_parsed.yaml" \
    -j "$PROJECT_ROOT/config/info.json" > "$SCRIPT_DIR/tim_keymap.svg"
# Remove the parsed YAML file
echo "🧹 Removing parsed YAML file..."
rm "$SCRIPT_DIR/tim_keymap_parsed.yaml"


echo "✅ Done! Output saved to docs/keymap/tim_keymap.svg"

