import os
import subprocess
from pathlib import Path

try:
    from .logger import logger
except ImportError:
    from logger import logger


def run_semgrep_scan():
    """
    Run semgrep scan with auto-config and save results in SARIF format.
    Creates reports directory if it doesn't exist.

    Returns:
        bool: True if scan completed successfully, False otherwise
    """
    try:
        # Create reports directory if it doesn't exist
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        # Run semgrep scan with real-time output and proper terminal handling
        process = subprocess.Popen(
            [
                "semgrep",
                "--config",
                "auto",
                "--sarif",
                "--output",
                "reports/semgrep.sarif",
                "--verbose",
                "--force-color",  # Force color output
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},  # Ensure unbuffered output
        )

        # Print output in real-time with proper line handling
        output_lines = []
        error_lines = []

        # Function to read and process output
        def read_output(pipe, output_list, is_error=False):
            while True:
                line = pipe.readline()
                if not line:
                    break
                output_list.append(line)
                # Print with appropriate color for errors
                if is_error:
                    print(
                        f"\033[91m{line}\033[0m", end="", flush=True
                    )  # Red for errors
                else:
                    print(line, end="", flush=True)

        # Start reader threads for stdout and stderr
        import threading

        stdout_thread = threading.Thread(
            target=read_output, args=(process.stdout, output_lines, False)
        )
        stderr_thread = threading.Thread(
            target=read_output, args=(process.stderr, error_lines, True)
        )

        stdout_thread.start()
        stderr_thread.start()

        # Wait for process to complete
        return_code = process.wait()

        # Wait for threads to finish
        stdout_thread.join()
        stderr_thread.join()

        # Create result object
        result = subprocess.CompletedProcess(
            process.args,
            return_code,
            stdout="".join(output_lines),
            stderr="".join(error_lines),
        )

        if result.returncode == 0:
            print("✅ Semgrep scan completed successfully")
            return True
        else:
            print(f"❌ Semgrep scan failed with error: {result.stderr}")
            return False

    except FileNotFoundError:
        print(
            "❌ Error: semgrep command not found. Please make sure semgrep is installed."
        )
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}")
        return False
