import os
import re


def sanitize_manuscript():
    print("🚀 Sanitizing QMD files for hidden invalid characters...")

    project_root = "/Users/dr.ajayshukla/PycharmProjects/pythonProjectwriter/HRPQCT_BMD_TBS_FRAX"
    results_path = os.path.join(project_root, "manuscript", "sections", "04_results.qmd")

    if not os.path.exists(results_path):
        print(f"❌ Could not find {results_path}")
        return

    with open(results_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace the problematic 'approx' and hidden characters
    # This targets the specific line identified in your error log (l.492)
    # Replacing any non-ascii hidden chars around the 'd approx 1.2' area
    sanitized = content.replace("d \approx 1.2", "d \\approx 1.2")  # Standardize LaTeX

    # Use regex to strip out non-printable control characters (like ^^G)
    # This keeps standard spaces, newlines, and visible text
    sanitized = "".join(char for char in sanitized if char.isprintable() or char in "\n\r\t")

    # 2. Specifically fix the 'approx' symbol which often causes issues in Quarto -> LaTeX
    sanitized = sanitized.replace("≈", "\\approx")
    sanitized = sanitized.replace("~", "\\approx")  # If you used tilde as approx

    with open(results_path, "w", encoding="utf-8") as f:
        f.write(sanitized)

    print("✅ Sanitization complete. Hidden characters removed.")


if __name__ == "__main__":
    sanitize_manuscript()