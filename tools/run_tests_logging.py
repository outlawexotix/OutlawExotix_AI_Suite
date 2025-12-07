import subprocess
import sys

def main():
    print("Running tests and capturing output to final_test_output.txt...")
    with open('final_test_output.txt', 'w', encoding='utf-8') as f:
        # Run pytest and redirect both stdout and stderr to the file
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v'],
            stdout=f,
            stderr=subprocess.STDOUT
        )
    print(f"Tests finished with exit code: {result.returncode}")
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
