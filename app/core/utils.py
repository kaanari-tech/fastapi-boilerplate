import ulid


def get_id():
    return ulid.new().str