import os
import re
import shutil
import config
import file_utils
import latex_utils
import ai_service
import logic

def main():
    """Main function to orchestrate the job application automation."""
    # 1. Initial Setup and Checks
    if not latex_utils.check_dependencies():
        return
    
    model = ai_service.configure_ai()
    if not model:
        return

    # 2. Get all pending jobs from the CSV
    pending_jobs = file_utils.get_all_pending_jobs(config.JOBS_CSV_FILE)
    if not pending_jobs:
        print("\nNo new jobs to process. All applications are up to date!")
        return
    
    total_jobs = len(pending_jobs)
    print(f"\nFound {total_jobs} pending job applications to process.")
    print("-" * 40)

    # 3. Loop through each pending job and process it
    for i, job_info in enumerate(pending_jobs):
        print(f"Processing Job {i+1} of {total_jobs}: {job_info.get('JobTitle')} at {job_info.get('CompanyName')}")
        
        # Load language-specific files based on the job's language
        lang = job_info.get("Language", "EN").upper()
        if lang == "DE":
            profile_path, prompts_path, cv_source_dir = config.PROFILE_DE_FILE, config.PROMPTS_DE_FILE, config.CV_PROJECT_DE_DIR
        else:
            profile_path, prompts_path, cv_source_dir = config.PROFILE_EN_FILE, config.PROMPTS_EN_FILE, config.CV_PROJECT_EN_DIR

        if not os.path.isdir(cv_source_dir):
            print(f"Error: The CV project directory was not found at '{cv_source_dir}'")
            continue # Skip to the next job

        my_profile = file_utils.load_text_file(profile_path)
        prompts = file_utils.load_json_file(prompts_path)
        if not my_profile or not prompts:
            print("Could not load profile or prompt files. Exiting.")
            return

        # Generate AI Content
        print(f"Generating content in {lang}...")
        
        summary_example = logic.extract_section(my_profile, "Example of Desired Summary", "Beispiel für die gewünschte Zusammenfassung")
        summary_context = { "summary_example": summary_example, "my_profile": my_profile, "job_description": job_info["JobDescription"] }
        custom_summary = ai_service.generate_content(model, prompts["profile_summary"]["system_instruction"], prompts["profile_summary"]["template"], summary_context)

        cover_letter_body = logic.process_cover_letter_paragraphs(model, prompts, my_profile, job_info)

        if not custom_summary or not cover_letter_body:
            print("Failed to generate all required AI content. Skipping to next job.")
            continue
        
        print("✅ AI content generated successfully.")

        # Prepare Temporary Directory for this Application
        company_name = job_info['CompanyName']
        # temp_app_dir = os.path.join(config.APPLICATIONS_DIR, f"_{company_name.replace(' ', '_')}_temp")
        # final_app_dir = os.path.join(config.APPLICATIONS_DIR, company_name.replace(" ", "_"))
        job_title_sanitized = re.sub(r'[\W_]+', '', job_info.get('JobTitle', '')) 
        
        folder_name = f"{company_name.replace(' ', '_')}_{job_title_sanitized}"
        final_app_dir = os.path.join(config.APPLICATIONS_DIR, folder_name)
        temp_app_dir = os.path.join(config.APPLICATIONS_DIR, f"_{folder_name}_temp")
        
        if os.path.exists(temp_app_dir): shutil.rmtree(temp_app_dir)
        shutil.copytree(cv_source_dir, temp_app_dir)

        # Update CV with AI Content
        sanitized_summary = file_utils.sanitize_for_latex(custom_summary)
        file_utils.find_and_replace(temp_app_dir, config.PROFILE_SUMMARY_PLACEHOLDER, sanitized_summary)
        logic.process_experience_blocks(model, prompts, my_profile, job_info, temp_app_dir)

        # Compile Final PDF
        if latex_utils.compile_to_pdf(temp_app_dir):
            logic.handle_successful_compilation(job_info, lang, cover_letter_body, temp_app_dir, final_app_dir)
        else:
            print("\n--- Compilation Failed ---")
            print(f"The temporary folder has been kept for debugging at: '{temp_app_dir}'")
            print("Please check the .log file inside that folder to find the specific LaTeX error.")
        
        print("-" * 40)
    
    print("All pending jobs have been processed.")

if __name__ == "__main__":
    main()


# import os
# import shutil
# import config
# import file_utils
# import latex_utils
# import ai_service
# import logic # <-- NEW: Import the logic module

# def main():
#     """Main function to orchestrate the job application automation."""
#     # 1. Initial Setup and Checks
#     if not latex_utils.check_dependencies():
#         return
    
#     model = ai_service.configure_ai()
#     if not model:
#         return

#     # 2. Get the next job from the CSV
#     job_info = file_utils.get_next_job(config.JOBS_CSV_FILE)
#     if not job_info:
#         print("\nNo new jobs to process. All applications are up to date!")
#         return

#     # 3. Load language-specific files based on the job's language
#     lang = job_info.get("Language", "EN").upper()
#     if lang == "DE":
#         profile_path, prompts_path, cv_source_dir = config.PROFILE_DE_FILE, config.PROMPTS_DE_FILE, config.CV_PROJECT_DE_DIR
#     else:
#         profile_path, prompts_path, cv_source_dir = config.PROFILE_EN_FILE, config.PROMPTS_EN_FILE, config.CV_PROJECT_EN_DIR

#     if not os.path.isdir(cv_source_dir):
#         print(f"Error: The CV project directory was not found at '{cv_source_dir}'")
#         return

#     my_profile = file_utils.load_text_file(profile_path)
#     prompts = file_utils.load_json_file(prompts_path)
#     if not my_profile or not prompts:
#         print("Could not load profile or prompt files. Exiting.")
#         return

#     # 4. Generate AI Content
#     print(f"\nGenerating content in {lang}...")
    
#     summary_example = logic.extract_section(my_profile, "Example of Desired Summary", "Beispiel für die gewünschte Zusammenfassung")
#     summary_context = { "summary_example": summary_example, "my_profile": my_profile, "job_description": job_info["JobDescription"] }
#     custom_summary = ai_service.generate_content(model, prompts["profile_summary"]["system_instruction"], prompts["profile_summary"]["template"], summary_context)

#     cover_letter_body = logic.process_cover_letter_paragraphs(model, prompts, my_profile, job_info)

#     if not custom_summary or not cover_letter_body:
#         print("Failed to generate all required AI content. Exiting.")
#         return
    
#     print("✅ AI content generated successfully.")

#     # 5. Prepare Temporary Directory for this Application
#     company_name = job_info['CompanyName']
#     temp_app_dir = os.path.join(config.APPLICATIONS_DIR, f"_{company_name.replace(' ', '_')}_temp")
#     final_app_dir = os.path.join(config.APPLICATIONS_DIR, company_name.replace(" ", "_"))
    
#     if os.path.exists(temp_app_dir): shutil.rmtree(temp_app_dir)
#     shutil.copytree(cv_source_dir, temp_app_dir)

#     # 6. Update CV with AI Content
#     sanitized_summary = file_utils.sanitize_for_latex(custom_summary)
#     file_utils.find_and_replace(temp_app_dir, config.PROFILE_SUMMARY_PLACEHOLDER, sanitized_summary)
#     logic.process_experience_blocks(model, prompts, my_profile, job_info, temp_app_dir)

#     # 7. Compile Final PDF
#     if latex_utils.compile_to_pdf(temp_app_dir):
#         logic.handle_successful_compilation(job_info, lang, cover_letter_body, temp_app_dir, final_app_dir)
#     else:
#         print("\n--- Compilation Failed ---")
#         print(f"The temporary folder has been kept for debugging at: '{temp_app_dir}'")
#         print("Please check the .log file inside that folder to find the specific LaTeX error.")

# if __name__ == "__main__":
#     main()
