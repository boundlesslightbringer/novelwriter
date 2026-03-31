"""Script to initialize the local MongoDB Knowledge Graph database."""

from src.world_bible_tools import init_kg_db


def main() -> None:
    """Run the initialization function for the local database."""
    print("Initializing local MongoDB Knowledge Graph database...")
    result = init_kg_db("novelwriter_kg")
    print(result)


if __name__ == "__main__":
    main()
