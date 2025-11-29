import os
import shutil
import datetime
import re
import config
import file_utils
import latex_utils
import ai_service
import locale

def extract_section(profile_text, title_en, title_de):
    """A robust function to extract content under a specific ## heading in either language."""
    content = None
    for title in [title_en, title_de]:
        try:
            start_marker = f"## {title}"
            parts = profile_text.split(start_marker)
            if len(parts) > 1:
                content_after_marker = parts[1]
                end_parts = content_after_marker.split("\n## ")
                content = end_parts[0].strip()
                break
        except Exception:
            continue
    if not content:
        print(f"Warning: Could not find section '{title_en}' or '{title_de}' in profile file.")
    return content or ""

def parse_experience_from_profile(profile_text):
    """Parses the profile text to reliably extract experience blocks."""
    experience_data = {}
    current_placeholder = None
    lines = profile_text.split('\n')
    for line in lines:
        placeholder_match = re.search(r"(---EXPERIENCE-BLOCK-.*?---)", line)
        if placeholder_match:
            current_placeholder = placeholder_match.group(1)
            if current_placeholder not in experience_data:
                experience_data[current_placeholder] = []
            continue
        if current_placeholder:
            if line.strip() and not re.search(r"---EXPERIENCE-BLOCK-.*?---", line) and not line.strip().startswith("## "):
                experience_data[current_placeholder].append(line.strip())
    return experience_data

def process_experience_blocks(model, prompts, my_profile, job_info, temp_app_dir):
    """Finds, rewrites, and replaces all dynamic experience blocks."""
    print("\nProcessing dynamic experience blocks...")
    experience_blocks = parse_experience_from_profile(my_profile)
    if not experience_blocks or all(not items for items in experience_blocks.values()):
        print("Warning: No dynamic experience blocks were found. Skipping.")
        return
    for placeholder, items in experience_blocks.items():
        if not items: continue
        base_experience_description = "\n".join(items)
        print(f"Rewriting experience for placeholder: {placeholder}")
        experience_context = { "my_profile": my_profile, "job_description": job_info["JobDescription"], "base_experience_description": base_experience_description }
        rewritten_text_block = ai_service.generate_content(model, prompts["experience_block"]["system_instruction"], prompts["experience_block"]["template"], experience_context)
        if rewritten_text_block:
            bullet_points = [line.strip() for line in rewritten_text_block.strip().split('\n') if line.strip()]
            latex_items = [f"    \\item{{{file_utils.sanitize_for_latex(point)}}}" for point in bullet_points]
            final_block = "\\begin{cvitems}\n" + "\n".join(latex_items) + "\n\\end{cvitems}"
            file_utils.find_and_replace(temp_app_dir, placeholder, final_block)

def process_cover_letter_paragraphs(model, prompts, my_profile, job_info):
    """
    Parses the profile, generates AI content, sanitizes ALL paragraphs, 
    and assembles the full cover letter body.
    """
    print("\nAssembling cover letter paragraphs...")
    paragraph_pattern = re.compile(r"## (?:Cover Letter Paragraph|Anschreiben Absatz) \((.*?)\)\s*\n(.*?)(?=\n## |\Z)", re.DOTALL)
    found_paragraphs = paragraph_pattern.findall(my_profile)
    if not found_paragraphs:
        print("Warning: No 'Cover Letter Paragraph' or 'Anschreiben Absatz' sections found in profile. Body will be empty.")
        return ""
    
    final_body_parts = []
    for tag, content in found_paragraphs:
        tag = tag.strip().lower()
        content = content.strip()
        
        paragraph_to_add = ""
        if tag.startswith("ai:"):
            ai_type = tag.split(":")[1].strip()
            prompt_key = f"cover_letter_{ai_type}"
            if prompt_key in prompts:
                print(f"Generating AI paragraph for: {ai_type}")
                context = { 
                    "my_profile": my_profile, 
                    "job_description": job_info["JobDescription"], 
                    f"{ai_type}_example": content,
                    "target_company_name": job_info.get("CompanyName", "") 
                }
                ai_paragraph = ai_service.generate_content(model, prompts[prompt_key]["system_instruction"], prompts[prompt_key]["template"], context)
                paragraph_to_add = ai_paragraph or ""
        elif tag == "static":
            print("Adding static paragraph.")
            paragraph_to_add = content
        
        if paragraph_to_add:
            sanitized_paragraph = file_utils.sanitize_for_latex(paragraph_to_add)
            final_body_parts.append(sanitized_paragraph)

    return "\n\n".join(final_body_parts)


def handle_successful_compilation(job_info, lang, cover_letter_body, temp_app_dir, final_app_dir):
    """Saves final files, creates the cover letter PDF, updates CSV, and cleans up."""
    # Sanitize ALL text inputs from the CSV file first.
    company_name = file_utils.sanitize_for_latex(job_info.get('CompanyName', ''))
    job_title = file_utils.sanitize_for_latex(job_info.get('JobTitle', ''))
    hr_name = file_utils.sanitize_for_latex(job_info.get('HRManagerName', ''))
    company_street = file_utils.sanitize_for_latex(job_info.get('CompanyStreet', ''))
    company_city = file_utils.sanitize_for_latex(job_info.get('CompanyCity', ''))
    
    os.makedirs(final_app_dir, exist_ok=True)

    author_name_sanitized = config.AUTHOR_INFO["name"].replace(" ", "")
    company_name_sanitized = job_info['CompanyName'].replace(" ", "_")
    
    if lang == 'DE':
        cv_filename = f"Lebenslauf_{author_name_sanitized}_{company_name_sanitized}.pdf"
        cl_filename = f"Anschreiben_{author_name_sanitized}_{company_name_sanitized}.pdf"
    else:
        cv_filename = f"CV_{author_name_sanitized}_{company_name_sanitized}.pdf"
        cl_filename = f"CoverLetter_{author_name_sanitized}_{company_name_sanitized}.pdf"

    shutil.move(
        os.path.join(temp_app_dir, config.MAIN_TEX_FILE.replace('.tex', '.pdf')),
        os.path.join(final_app_dir, cv_filename)
    )
    print(f"✅ CV saved to: {os.path.join(final_app_dir, cv_filename)}")

    hr_gender = job_info.get('HRManagerGender', '').upper()
    
    if lang == 'DE':
        try:
            locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
        except locale.Error:
            print("Warning: German locale not found. Using default date format.")
        
        date_str = datetime.date.today().strftime("%d. %B %Y")
        salutation = "Sehr geehrte Damen und Herren,"
        if hr_name and hr_gender == 'F': salutation = f"Sehr geehrte Frau {hr_name},"
        elif hr_name and hr_gender == 'M': salutation = f"Sehr geehrter Herr {hr_name},"
        application_subject = f"Bewerbung um die Stelle als {job_title}"
        final_body = f"{cover_letter_body}\n\nMit freundlichen Grüßen,\n\n{config.AUTHOR_INFO['name']}"
    else:
        try:
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        except locale.Error:
            print("Warning: English locale not found. Using default date format.")

        date_str = datetime.date.today().strftime("%B %d, %Y")
        salutation = "Dear Hiring Team,"
        if hr_name and hr_gender == 'F': salutation = f"Dear Ms. {hr_name},"
        elif hr_name and hr_gender == 'M': salutation = f"Dear Mr. {hr_name},"
        application_subject = f"Application for the position of {job_title}"
        final_body = f"{cover_letter_body}\n\nSincerely,\n\n{config.AUTHOR_INFO['name']}"

    company_block_lines = []
    if company_name: company_block_lines.append(company_name)
    if hr_name: company_block_lines.append(hr_name)
    if company_street: company_block_lines.append(company_street)
    if company_city: company_block_lines.append(company_city)
    company_block_text = r' \\ '.join(line for line in company_block_lines if line)

    metadata = {
        "title": f"Cover Letter for {job_title}",
        "author-name": config.AUTHOR_INFO["name"],
        "author-street": config.AUTHOR_INFO["street"],
        "author-city": config.AUTHOR_INFO["city"],
        "author-phone": config.AUTHOR_INFO["phone"],
        "author-email": config.AUTHOR_INFO["email"],
        "company-block": company_block_text,
        "date": date_str,
        "application-subject": application_subject,
        "salutation": salutation,
        "body": final_body
    }
    
    pdf_file_path = os.path.join(final_app_dir, cl_filename)
    latex_utils.convert_md_to_pdf("", pdf_file_path, metadata)

    file_utils.update_csv_status(config.JOBS_CSV_FILE, job_info['CompanyName'], job_info['JobTitle'], f"Generated on {datetime.date.today()}")
    print(f"\nSuccessfully processed application for {job_info['JobTitle']} at {job_info['CompanyName']}.")

    if os.path.exists(temp_app_dir):
        shutil.rmtree(temp_app_dir)
        print("Temporary directory cleaned up.")
