import json

# The name of the map data file you downloaded.
INPUT_FILENAME = "countries-110m.json"
# The name of the structured output file we will create.
OUTPUT_FILENAME = "countries.txt"

# This dictionary maps abbreviations from the map data to their full names.
ABBREVIATION_MAP = {
    "dem. rep. congo": "democratic republic of the congo",
    "dominican rep.": "dominican republic",
    "central african rep.": "central african republic",
    "eq. guinea": "equatorial guinea",
    "solomon is.": "solomon islands",
    "bosnia and herz.": "bosnia and herzegovina",
    "w. sahara": "western sahara",
}

# Add any custom or common abbreviations you want to recognize.
CUSTOM_ABBREVIATIONS = {
    "usa": "united states of america",
    "uk": "united kingdom",
    "uae": "united arab emirates",
}

def generate_country_file():
    """
    Reads a TopoJSON file, extracts country names, and writes them to a
    structured text file with separate sections for names and abbreviations.
    """
    try:
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
            world_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{INPUT_FILENAME}' was not found.")
        return

    geometries = world_data['objects']['countries']['geometries']
    country_names = set()
    all_abbreviations = ABBREVIATION_MAP.copy()
    all_abbreviations.update(CUSTOM_ABBREVIATIONS)

    for country_data in geometries:
        name_from_map = country_data['properties']['name'].lower()
        full_name = all_abbreviations.get(name_from_map, name_from_map)
        if full_name not in ["antarctica", "greenland"]:
            country_names.add(full_name)

    # --- Write the structured file ---
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            # Write the [COUNTRIES] section
            f.write("[COUNTRIES]\n")
            for name in sorted(list(country_names)):
                f.write(f"{name}\n")
            
            # Write a separator and the [ABBREVIATIONS] section
            f.write("\n[ALTERNATES]\n")
            for abbr, full_name in sorted(all_abbreviations.items()):
                f.write(f"{abbr} -> {full_name}\n")
                
        print(f"Successfully wrote {len(country_names)} countries and "
              f"{len(all_abbreviations)} abbreviations to '{OUTPUT_FILENAME}'.")
    except IOError as e:
        print(f"Error writing to file '{OUTPUT_FILENAME}': {e}")

if __name__ == "__main__":
    generate_country_file()
