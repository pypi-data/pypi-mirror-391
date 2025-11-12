import hashlib
import os


def main():
    for filename in os.listdir("dist/"):
        if filename.endswith(".tar.gz"):
            file_path = os.path.join("dist/", filename)
            print(f"{filename}: {sha256sum(file_path)}")


def sha256sum(file_path: str, chunk_size: int = 8192) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


if __name__ == "__main__":
    main()
