import os
import sys
import time

# Get the Cloud Run-provided environment variables
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", 0)
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", 0)
# Get the user-defined environment variables
SLEEP_MS = os.getenv("SLEEP_MS", 500)
FAIL_RATE = os.getenv("FAIL_RATE", 0.1)

# Define a main function to run the job
def main():
    print(f"Starting Task #{TASK_INDEX}, Attempt #{TASK_ATTEMPT}...")
    # Simulate a task that takes some time to complete
    time.sleep(int(SLEEP_MS) / 1000)
    # Simulate a task that might fail
    if float(FAIL_RATE) > 0 and float(FAIL_RATE) > float(os.urandom(1)[0]) / 255:
        print(f"Task #{TASK_INDEX}, Attempt #{TASK_ATTEMPT} failed.")
        sys.exit(1)
    else:
        print(f"Completed Task #{TASK_INDEX}, Attempt #{TASK_ATTEMPT}.")

if __name__ == "__main__":
    main()
