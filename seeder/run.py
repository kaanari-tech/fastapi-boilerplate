from pathlib import Path

import fire
from sqlalchemyseed import load_entities_from_json
from sqlalchemyseed import Seeder

from app.db import drop_all_tables
from app.db import get_db


def drop_tables() -> None:
    drop_all_tables()


def seed() -> None:
    print("start: import_seed")
    db = next(get_db())
    seeds_json_files = list(Path(__file__).parent.glob("json/*.json"))
    try:
        entities = []
        for file in seeds_json_files:
            print(f"load seed file={str(file)}")
            entities.append(load_entities_from_json(str(file)))

        seeder = Seeder(db)
        seeder.seed(entities)
        db.commit()
        print("end: seeds import completed")
    except Exception as e:
        db.rollback()
        print(f"end: seeds import failed. detail={e}")


if __name__ == "__main__":
    fire.Fire()
