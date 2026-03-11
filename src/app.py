from flask import Flask, render_template, request, jsonify
import subprocess
import ollama
import re

app = Flask(__name__)


def detect_language(code):

    if "#include" in code:
        return "c"

    elif "public class" in code:
        return "java"

    else:
        return "python"


def analyze_error(error_text):

    cause = ""
    fix = ""

    if "IndexError" in error_text:
        cause = "You tried to access a list index that does not exist."
        fix = "Use an index between 0 and list length - 1."

    elif "TypeError" in error_text:
        cause = "You used incompatible data types in an operation."
        fix = "Convert variables to the same data type."

    elif "NameError" in error_text:
        cause = "A variable was used before it was defined."
        fix = "Make sure the variable is declared before using it."

    elif "SyntaxError" in error_text:
        cause = "Python cannot understand the syntax of your code."
        fix = "Check missing brackets, quotes, or colons."

    elif "ModuleNotFoundError" in error_text:
        cause = "Python cannot find the imported module."
        fix = "Install the module using pip."

    else:
        cause = "An unknown error occurred."
        fix = "Check your code carefully."

    return cause, fix


@app.route("/", methods=["GET", "POST"])
def index():

    code = ""
    explanation = ""
    cause = ""
    fix = ""
    error_line = None
    language = ""

    if request.method == "POST":

        code = request.form["code"]

        # Detect language
        language = detect_language(code)

        error_text = ""

        # -------- PYTHON EXECUTION --------
        if language == "python":

            with open("../temp/temp_code.py", "w") as f:
                f.write(code)

            result = subprocess.run(
                ["python", "../temp/temp_code.py"],
                capture_output=True,
                text=True
            )

            error_text = result.stderr

        # -------- C EXECUTION --------
        elif language == "c":

            try:
                with open("../temp/temp_code.c", "w") as f:
                    f.write(code)

                compile_result = subprocess.run(
                    ["gcc", "../temp/temp_code.c"],
                    capture_output=True,
                    text=True
                )

                error_text = compile_result.stderr

            except Exception as e:
                error_text = str(e)

        # -------- JAVA EXECUTION --------
        elif language == "java":

            try:
                with open("../temp/Test.java", "w") as f:
                    f.write(code)

                compile_result = subprocess.run(
                    ["javac", "../temp/Test.java"],
                    capture_output=True,
                    text=True
                )

                error_text = compile_result.stderr

            except FileNotFoundError:
                error_text = "Java compiler (javac) not found. Please install JDK."

        # -------- FIND ERROR LINE --------
        match = re.search(r'line (\d+)', error_text)
        if match:
            error_line = int(match.group(1))

        # -------- ANALYZE ERROR --------
        if error_text:

            cause, fix = analyze_error(error_text)

            response = ollama.chat(
                model="phi3",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
Explain this {language} programming error in 3 short points.

Error:
{error_text}

1. Meaning
2. Why it happened
3. How to fix

Keep answer under 80 words.
"""
                    }
                ],
                options={"num_predict":120}
            )

            explanation = response["message"]["content"]

        else:
            explanation = "No error found. Your code ran successfully."

    return render_template(
        "index.html",
        code=code,
        cause=cause,
        fix=fix,
        explanation=explanation,
        error_line=error_line,
        language=language
    )


# -------- CORRECTED CODE FEATURE --------

@app.route("/fix", methods=["POST"])
def fix_code():

    data = request.get_json()
    code = data["code"]

    response = ollama.chat(
        model="phi3",
        messages=[
            {
                "role": "user",
                "content": f"""
Fix the following code and return ONLY the corrected code.

Code:
{code}
"""
            }
        ],
        options={"num_predict":200}
    )

    corrected = response["message"]["content"]

    return jsonify({"fix": corrected})


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
