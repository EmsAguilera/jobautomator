import csv
import json
import os
import re

def sanitize_for_latex(text):
    """
    A robust function to replace special LaTeX characters with their safe equivalents.
    This version correctly handles all special characters, including %.
    """
    # A dictionary of special characters and their LaTeX-safe equivalents.
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    # This regex ensures we only replace the characters we intend to.
    regex = re.compile('|'.join(re.escape(key) for key in replacements.keys()))
    return regex.sub(lambda match: replacements[match.group(0)], text)

# ... (the rest of the file remains the same) ...

def get_all_pending_jobs(csv_file):
    """Reads the CSV and returns a list of all jobs with an empty 'Status'."""
    pending_jobs = []
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check if the 'Status' column is empty or just whitespace
                if not row.get('Status', '').strip():
                    pending_jobs.append(row)
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        return []
    return pending_jobs

def update_csv_status(csv_file, company_name, job_title, new_status):
    """Updates the status for a specific company in the CSV file."""
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            lines = list(csv.reader(f))
        
        header = lines[0]
        # Get the index for each column we need to check/update
        company_idx = header.index('CompanyName')
        title_idx = header.index('JobTitle')
        status_idx = header.index('Status')

        # Loop through the data rows (starting from index 1)
        for i in range(1, len(lines)):
            # --- THIS IS THE KEY CHANGE ---
            # Check if both the company name and job title match the current row
            if lines[i][company_idx] == company_name and lines[i][title_idx] == job_title:
                lines[i][status_idx] = new_status
                break # We found the unique row, so we can stop searching
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(lines)
        print(f"Updated status for '{job_title}' at '{company_name}' to '{new_status}'.")
    except (FileNotFoundError, ValueError, IndexError) as e:
        print(f"An error occurred while updating the CSV: {e}")

def load_text_file(filepath):
    """Loads the content of a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'.")
        return None

def load_json_file(filepath):
    """Loads the content of a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file at '{filepath}': {e}")
        return None

def find_and_replace(directory, placeholder, replacement):
    """
    Searches all .tex files in a directory and replaces a placeholder.
    """
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".tex"):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if placeholder in content:
                    new_content = content.replace(placeholder, replacement)
                    print(f"Found and replaced '{placeholder}' in: {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

def create_cover_letter(template_path, output_path, replacements):
    """Creates the final cover letter from the template."""
    template_content = load_text_file(template_path)
    if template_content:
        for key, value in replacements.items():
            template_content = template_content.replace(key, value)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print(f"Cover letter created at: {output_path}")
