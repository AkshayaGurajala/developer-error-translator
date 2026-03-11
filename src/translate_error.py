import pandas as pd

# load dataset
data = pd.read_csv("../data/error_dataset.csv")

def translate_error(error_message):
    for i, row in data.iterrows():
        if row["error_message"].split(":")[0] in error_message:
            return {
                "error_type": row["error_type"],
                "explanation": row["explanation"],
                "solution": row["solution"]
            }

    return {
        "error_type": "Unknown",
        "explanation": "Error not found in database",
        "solution": "Search documentation"
    }


# example test
if __name__ == "__main__":
    error = "IndexError: list index out of range"
    result = translate_error(error)

    print("Error Type:", result["error_type"])
    print("Explanation:", result["explanation"])
    print("Solution:", result["solution"])
