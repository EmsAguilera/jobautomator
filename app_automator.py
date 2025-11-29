import os
import csv
import shutil
import subprocess
import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
JOBS_CSV_FILE = "jobs.csv"
CV_PROJECT_DIR = os.path.join("templates", "cv_project")
COVER_LETTER_TEMPLATE = os.path.join("templates", "cover_letter_template.md")
APPLICATIONS_DIR = "applications"
# From your error log, it seems your main file is 'cv.tex'.
# Change this if it's different.
MAIN_TEX_FILE = "cv.tex" 
LATEX_COMPILER = "xelatex" # We've switched to xelatex!

# --- PLACEHOLDERS ---
PROFILE_SUMMARY_PLACEHOLDER = "[---PROFILE_SUMMARY_PLACEHOLDER---]"
COVER_LETTER_BODY_PLACEHOLDER = "[---COVER_LETTER_BODY_PLACEHOLDER---]"

def check_dependencies():
    """Checks if the required LaTeX compiler is installed and in the PATH."""
    if shutil.which(LATEX_COMPILER) is None:
        print("--- Dependency Error ---")
        print(f"Error: The '{LATEX_COMPILER}' command was not found in your system's PATH.")
        print("This script requires a LaTeX distribution to be installed.")
        print("\nFor Windows, please install MiKTeX: https://miktex.org/download")
        print("For macOS, please install MacTeX: https://www.tug.org/mactex/")
        print("For Linux, please install TeX Live (e.g., 'sudo apt-get install texlive-full')")
        print("\nIMPORTANT: During installation, ensure you select the option to 'Add to system PATH'.")
        print("After installing, you MUST restart your terminal before running this script again.")
        exit()
    print(f"✅ Dependency check passed: '{LATEX_COMPILER}' is available.")

def get_api_key():
    """Prompts the user for their API key and validates it."""
    api_key = "AIzaSyDRBveTWuyI7bth4KWDTNZldJil-WBbqTU" # input("Please enter your Google AI API key: ").strip()
    if not api_key:
        print("API key cannot be empty.")
        exit()
    return api_key

def configure_ai(api_key):
    """Configures the generative AI model."""
    try:
        genai.configure(api_key=api_key)
        print("✅ Successfully configured Google AI.")
    except Exception as e:
        print(f"Error configuring Google AI: {e}")
        exit()

def get_next_job(csv_file):
    """Reads the CSV and returns the first job with an empty 'Status'."""
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get('Status'):
                    print(f"Found next job: {row['JobTitle']} at {row['CompanyName']}")
                    return row
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        exit()
    return None

def generate_ai_content(job_description):
    """Generates tailored content for the CV and cover letter using the AI."""
    print("Asking AI to generate tailored content... (this may take a moment)")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        profile_prompt = f"""
        Analyze the language of the following job description. Your entire response MUST be in the same language.
        Based on the job description, write a professional and concise 2-3 sentence 'Profile Summary' (in German: 'Profil' or 'Zusammenfassung') for a CV.
        Focus on the key requirements and skills mentioned. The output must be plain text only, suitable for a LaTeX document. Do not include a title like "Profile Summary".

        Job Description:
        ---
        {job_description}
        ---
        """
        profile_response = model.generate_content(profile_prompt)
        custom_profile = profile_response.text.strip()

        cover_letter_prompt = f"""
        Analyze the language of the following job description. Your entire response MUST be in the same language.
        Based on the job description, write 2-3 compelling paragraphs for the main body of a cover letter.
        Connect the candidate's potential skills to the company's needs as described in the job post.
        The tone should be professional and enthusiastic. The output must be plain text only. Do not include a title or greeting.

        Job Description:
        ---
        {job_description}
        ---
        """
        cover_letter_response = model.generate_content(cover_letter_prompt)
        custom_cover_letter_body = cover_letter_response.text.strip()
        
        print("✅ AI content generated successfully.")
        return custom_profile, custom_cover_letter_body

    except Exception as e:
        print(f"An error occurred while generating AI content: {e}")
        exit()

def find_and_replace_in_cv(directory, placeholder, replacement):
    """Searches all .tex files in a directory and replaces the placeholder."""
    found_and_replaced = False
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".tex"):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if placeholder in content:
                    print(f"Found placeholder in: {file_path}")
                    content = content.replace(placeholder, replacement)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    found_and_replaced = True
    if not found_and_replaced:
        print(f"Warning: Could not find the placeholder '{placeholder}' in any .tex file.")


def compile_latex_to_pdf(directory, main_file):
    """Compiles a LaTeX project into a PDF using the specified compiler."""
    main_file_path = os.path.join(directory, main_file)
    if not os.path.exists(main_file_path):
        print(f"Error: Main LaTeX file '{main_file}' not found in '{directory}'.")
        return False

    print(f"Compiling {main_file} to PDF using {LATEX_COMPILER}...")
    for i in range(2):
        process = subprocess.run(
            [LATEX_COMPILER, '-interaction=nonstopmode', main_file],
            cwd=directory,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=120
        )
        if process.returncode != 0:
            print(f"--- LaTeX Compilation Error (using {LATEX_COMPILER}) ---")
            print(f"Attempt {i+1} failed. See log file for details: {os.path.join(directory, main_file.replace('.tex', '.log'))}")
            return False
    
    print("✅ PDF compilation successful.")
    return True

def create_cover_letter(template_path, output_path, replacements):
    """Creates the final cover letter from the template."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        for key, value in replacements.items():
            template_content = template_content.replace(key, value)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print(f"Cover letter created at: {output_path}")

    except Exception as e:
        print(f"An error occurred while creating the cover letter: {e}")


def update_csv_status(csv_file, company_name, new_status):
    """Updates the status for a specific company in the CSV file."""
    lines = []
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            lines = list(reader)

        header = lines[0]
        company_idx = header.index('CompanyName')
        status_idx = header.index('Status')

        for i in range(1, len(lines)):
            if lines[i][company_idx] == company_name:
                lines[i][status_idx] = new_status
                break
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(lines)
        print(f"Updated status for {company_name} to '{new_status}'.")

    except Exception as e:
        print(f"An error occurred while updating the CSV: {e}")

def main():
    """Main function to run the application automation process."""
    check_dependencies()
    
    api_key = get_api_key()
    configure_ai(api_key)

    job_to_apply = get_next_job(JOBS_CSV_FILE)

    if not job_to_apply:
        print("\nNo new jobs to process. All applications are up to date!")
        return

    company = job_to_apply['CompanyName']
    title = job_to_apply['JobTitle']
    description = job_to_apply['JobDescription']

    custom_profile, custom_cover_letter_body = generate_ai_content(description)

    temp_app_dir = os.path.join(APPLICATIONS_DIR, f"_{company.replace(' ', '_')}_temp")
    final_app_dir = os.path.join(APPLICATIONS_DIR, company.replace(" ", "_"))
    
    if os.path.exists(temp_app_dir):
        shutil.rmtree(temp_app_dir)
    
    shutil.copytree(CV_PROJECT_DIR, temp_app_dir)

    find_and_replace_in_cv(temp_app_dir, PROFILE_SUMMARY_PLACEHOLDER, custom_profile)
    
    if compile_latex_to_pdf(temp_app_dir, MAIN_TEX_FILE):
        os.makedirs(final_app_dir, exist_ok=True)
        final_cv_name = f"CV_YourName_{company.replace(' ', '_')}.pdf"
        shutil.move(
            os.path.join(temp_app_dir, MAIN_TEX_FILE.replace('.tex', '.pdf')),
            os.path.join(final_app_dir, final_cv_name)
        )
        print(f"✅ CV saved to: {os.path.join(final_app_dir, final_cv_name)}")

        cover_letter_replacements = {
            "{company_name}": company,
            "{job_title}": title,
            "{current_date}": datetime.date.today().strftime("%B %d, %Y"),
            "{source_of_job_posting}": "your website",
            COVER_LETTER_BODY_PLACEHOLDER: custom_cover_letter_body
        }
        final_cl_name = f"CoverLetter_YourName_{company.replace(' ', '_')}.md"
        create_cover_letter(
            COVER_LETTER_TEMPLATE,
            os.path.join(final_app_dir, final_cl_name),
            cover_letter_replacements
        )
        
        update_csv_status(JOBS_CSV_FILE, company, f"Generated on {datetime.date.today()}")
        print(f"\nSuccessfully processed application for {title} at {company}.")

    shutil.rmtree(temp_app_dir)

if __name__ == "__main__":
    main()