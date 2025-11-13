DEFAULT_SLOT_NAME = ":"


def normalize_slot_name(name: str):
    return DEFAULT_SLOT_NAME if name == "default" else name
