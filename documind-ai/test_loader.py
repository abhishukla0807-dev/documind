from app.ingestion.loader import RepoLoader

# Replace with your actual repo ID from Phase 1 if different
REPO_DIR = r"A:\documind\data\repos\c60dd947-ff82-4009-8440-8e24b6855798"


def run_test():
    print(f"Loading files from: {REPO_DIR}")
    loader = RepoLoader(REPO_DIR)

    try:
        files = loader.load_repository_files()
        print(f"\n✅ Total valid files loaded: {len(files)}")

        print("\nSample files:")
        for f in files[:5]:
            print(f" - [{f['extension']}] {f['file_path']} ({len(f['content'])} characters)")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    run_test()