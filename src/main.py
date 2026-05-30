import time
import traceback
from pipeline import run


def main():
    start_time = time.time()

    try:
        print("=" * 60)
        print("AI LinkedIn Growth Engine")
        print("=" * 60)

        result = run(dry_run=False)

        if result.get("ok"):

            print("\nSUCCESS")

            print(f"Topic: {result.get('topic')}")
            print(f"Score: {result.get('final_score')}")
            print(f"Published: {result.get('published')}")

            if result.get("image_path"):
                print(f"Image: {result.get('image_path')}")

        else:

            print("\nFAILED")
            print(result.get("reason", "Unknown error"))

    except Exception as e:

        print("\nCRITICAL ERROR")
        print(str(e))
        traceback.print_exc()

        raise

    finally:

        elapsed = round(time.time() - start_time, 2)

        print("\nExecution Time:", elapsed, "seconds")
        print("=" * 60)


if __name__ == "__main__":
    main()