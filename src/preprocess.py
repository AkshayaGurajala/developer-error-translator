import re

def clean_error_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    return text


# Example
if __name__ == "__main__":
    error = "IndexError: list index out of range"
    print(clean_error_text(error))
