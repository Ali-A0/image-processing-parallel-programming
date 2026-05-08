from PIL import Image
import os
import threading

input_folder = "images"
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

NUM_THREADS = 10

image_files = [
    os.path.join(input_folder, f)
    for f in os.listdir(input_folder)
    if f.lower().endswith(".jpg")
]

def process_to_gray(files, thread_num):
    for file in files:
        try:
            #print(f"[Thread {thread_num}] Started: {file}")

            img = Image.open(file).convert("L")

            output_path = os.path.join(
                output_folder,
                "gray_" + os.path.basename(file)
            )

            img.save(output_path)

            print(f"[Thread {thread_num}] Done: {file}")

        except Exception as e:
            print(f"[Thread {thread_num}] Error: {file} -> {e}")


if __name__ == "__main__":
    threads = []

    chunk_size = len(image_files) // NUM_THREADS + 1

    for i in range(NUM_THREADS):
        start = i * chunk_size
        end = start + chunk_size
        chunk = image_files[start:end]

        if not chunk:
            continue

        t = threading.Thread(
            target=process_to_gray,
            args=(chunk, i)
        )

        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("All images processed")