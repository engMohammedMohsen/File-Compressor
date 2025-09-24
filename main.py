import json
import os
from pathlib import Path


def get_unique_filename(filepath):
    """Create unique filename if file exists"""
    path = Path(filepath)
    if not path.exists():
        return filepath

    counter = 1
    while True:
        new_name = f"{path.stem}_{counter}{path.suffix}"
        new_path = path.parent / new_name
        if not new_path.exists():
            return str(new_path)
        counter += 1


def compress_file(file_path):
    """Compress text file with frequency-based optimization"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Split by whitespace while preserving structure
        import re

        tokens = re.split(r"(\s+)", text)

        # Count frequency of each token
        frequency = {}
        for token in tokens:
            frequency[token] = frequency.get(token, 0) + 1

        # Sort by frequency (most frequent first) then by length
        sorted_tokens = sorted(frequency.keys(), key=lambda x: (-frequency[x], len(x)))

        # Create word dictionary with frequency-based IDs
        word_dict = {}
        for i, token in enumerate(sorted_tokens):
            # Only compress if it saves space (token appears multiple times OR is long)
            if frequency[token] > 1 or len(token) > 3:
                word_dict[token] = i + 1

        # Build data array
        data_ids = []
        for token in tokens:
            if token in word_dict:
                data_ids.append(word_dict[token])
            else:
                # Keep original token if not worth compressing
                data_ids.append(token)

        original_extension = Path(file_path).suffix
        compressed_data = {
            "extension": original_extension,
            "words": word_dict,
            "data": data_ids,
        }

        # Check if compression is beneficial
        original_size = len(text.encode("utf-8"))
        compressed_size = len(
            json.dumps(
                compressed_data, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")
        )

        if compressed_size >= original_size:
            print(
                f"Warning: Compressed file ({compressed_size} bytes) is not smaller than original ({original_size} bytes)"
            )
            print("Compression may not be beneficial for this file.")
        else:
            savings = (1 - compressed_size / original_size) * 100
            print(
                f"Compression saved {savings:.1f}% space ({original_size} → {compressed_size} bytes)"
            )

        output_path = get_unique_filename(f"{Path(file_path).stem}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(compressed_data, f, ensure_ascii=False, separators=(",", ":"))

        print(f"File compressed: {output_path}")
    except Exception as e:
        print(f"Compression error: {e}")


def decompress_file(json_path):
    """Decompress file from JSON"""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        words = data["words"]
        data_ids = data["data"]
        extension = data.get("extension", ".txt")

        # Create reverse mapping (number -> word)
        id_to_word = {v: k for k, v in words.items()}

        # Restore text
        restored_tokens = []
        for item in data_ids:
            if isinstance(item, int):
                # It's a compressed token
                restored_tokens.append(id_to_word[item])
            else:
                # It's an original uncompressed token
                restored_tokens.append(item)

        restored_text = "".join(restored_tokens)

        output_path = get_unique_filename(f"{Path(json_path).stem}{extension}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(restored_text)

        print(f"File decompressed: {output_path}")
    except Exception as e:
        print(f"Decompression error: {e}")


def main():
    """Main interface"""
    while True:
        print("\n=== Enhanced Text File Compressor ===")
        print("1. compress - Compress file")
        print("2. decompress - Decompress file")
        print("3. exit - Exit")

        choice = input("Choose operation: ").strip().lower()

        if choice in ["1", "compress"]:
            file_path = input("Enter text file path: ").strip()
            if os.path.exists(file_path):
                compress_file(file_path)
            else:
                print("File not found")

        elif choice in ["2", "decompress"]:
            json_path = input("Enter JSON file path: ").strip()
            if os.path.exists(json_path):
                decompress_file(json_path)
            else:
                print("File not found")

        elif choice in ["3", "exit"]:
            print("Goodbye!")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
