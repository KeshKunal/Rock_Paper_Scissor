import time
import os

def keep_vscode_active(file_path):
    # Ensure the file exists
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("# Keep VS Code active\n")
    
    while True:
        try:
            # Append a comment to the file
            with open(file_path, "a") as f:
                f.write(f" # Activity comment at {time.ctime()}\n")
            print(f"Appended comment to {file_path} at {time.ctime()}")
            time.sleep(300)  # Wait 5 minutes (300 seconds)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    # Specify the path to a file open in VS Code
    target_file = "path/to/your/file.py"  # Replace with your file path
    print(f"Starting to keep VS Code active by modifying {target_file}...")
    time.sleep(5)  # Initial delay to allow setup
    keep_vscode_active(target_file)