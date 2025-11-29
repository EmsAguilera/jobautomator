import os
import shutil
import subprocess
import config

def check_dependencies():
    # ... (this function remains the same) ...
    required_tools = [config.LATEX_COMPILER, "pandoc"]
    all_found = True
    for tool in required_tools:
        if shutil.which(tool) is None:
            print(f"--- Dependency Error ---")
            print(f"Error: The command '{tool}' was not found in your system's PATH.")
            all_found = False
    if all_found:
        print(f"✅ Dependency checks passed: '{config.LATEX_COMPILER}' and 'pandoc' are available.")
    return all_found

def compile_to_pdf(directory):
    # ... (this function remains the same) ...
    main_file_path = os.path.join(directory, config.MAIN_TEX_FILE)
    if not os.path.exists(main_file_path): return False
    print(f"Compiling {config.MAIN_TEX_FILE} to PDF using {config.LATEX_COMPILER}...")
    for i in range(2):
        try:
            process = subprocess.run(
                [config.LATEX_COMPILER, '-interaction=nonstopmode', config.MAIN_TEX_FILE],
                cwd=directory, capture_output=True, text=True, encoding='utf-8', errors='ignore',
                timeout=config.COMPILER_TIMEOUT
            )
            if process.returncode != 0:
                print(f"--- LaTeX Compilation Error (Attempt {i+1}) ---")
                return False
        except subprocess.TimeoutExpired:
            print("--- LaTeX Compilation Error: Timeout ---")
            return False
    print("✅ PDF compilation successful.")
    return True

def convert_md_to_pdf(md_content, pdf_file_path, metadata):
    """Converts a Markdown string to a PDF using a LaTeX template via Pandoc."""
    print(f"Converting Cover Letter to PDF...")
    
    # Build the command with all the metadata variables
    command = [
        "pandoc",
        "-f", "markdown",  # Input format
        "-o", pdf_file_path,
        "--template", config.COVER_LETTER_LATEX_TEMPLATE,
        "--pdf-engine=xelatex",
        "-V", f"mainfont={config.COVER_LETTER_FONT}" # Set the main font
    ]
    
    # Add all other metadata as variables for the template
    for key, value in metadata.items():
        command.extend(["-V", f"{key}={value}"])

    try:
        # We pass the markdown content directly to the command
        process = subprocess.run(
            command,
            input=md_content,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=120
        )
        if process.returncode != 0:
            print(f"--- Pandoc Conversion Error ---")
            # Print the error to help debug issues with the template or fonts
            print(process.stderr)
            return False
        
        print(f"✅ Cover Letter PDF created at: {pdf_file_path}")
        return True
    except Exception as e:
        print(f"--- Pandoc Conversion Error: {e} ---")
        return False
