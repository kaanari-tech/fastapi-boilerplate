import ulid


def get_id() -> str:
    return ulid.new().str
