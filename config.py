import os

AUTHOR_INFO = {
    "name": "Emilio Aguilera", # Replace with your actual name
    "street": "Renckstraße 1, ",
    "city": "76133 Karlsruhe",
    "phone": "+49 15737800576",
    "email": "emsaguilera99@gmail.com"
}

# --- File and Directory Paths ---
JOBS_CSV_FILE = "jobs.csv"
APPLICATIONS_DIR = "applications"
TEMPLATES_DIR = "templates"

# CV and Cover Letter Templates
CV_PROJECT_EN_DIR = os.path.join(TEMPLATES_DIR, "cv_project_en")
CV_PROJECT_DE_DIR = os.path.join(TEMPLATES_DIR, "cv_project_de")
COVER_LETTER_TEMPLATE_EN = os.path.join(TEMPLATES_DIR, "cover_letter_template_en.md")
COVER_LETTER_TEMPLATE_DE = os.path.join(TEMPLATES_DIR, "cover_letter_template_de.md")
COVER_LETTER_LATEX_TEMPLATE = "cover_letter_latex_template.tex" # <-- NEW

# --- NEW: Cover Letter Font Configuration ---
# You can change this to any font installed on your system (e.g., "Calibri", "Helvetica", "Times New Roman")
COVER_LETTER_FONT = "Garamond"

# Profile and Prompt files
PROFILE_EN_FILE = "my_profile_en.txt"
PROFILE_DE_FILE = "my_profile_de.txt"
PROMPTS_EN_FILE = "prompts_en.json"
PROMPTS_DE_FILE = "prompts_de.json"

# --- LaTeX Configuration ---
MAIN_TEX_FILE = "cv.tex"  # IMPORTANT: Change if your main .tex file has a different name
LATEX_COMPILER = "xelatex"
COMPILER_TIMEOUT = 300  # seconds (5 minutes)

# --- Placeholders ---
# These must match the placeholders in your template files exactly
PROFILE_SUMMARY_PLACEHOLDER = "[---PROFILE-SUMMARY-PLACEHOLDER---]"
# Example for a dynamic experience block placeholder
# EXPERIENCE_SENIOR_DEV_PLACEHOLDER = "[---EXPERIENCE_BLOCK_SENIOR_DEV---]"
EXPERIENCE_BLOCK_JUNIOR_DEV_PLACEHOLDER = "---EXPERIENCE-BLOCK-JUNIOR-DEV---"
EXPERIENCE_BLOCK_INTERNSHIP_DEV_PLACEHOLDER = "---EXPERIENCE-BLOCK-INTERNSHIP-DEV---"
EXPERIENCE_BLOCK_FULLSTACK_DEV_PLACEHOLDER = "---EXPERIENCE-BLOCK-FULLSTACK-DEV---"
