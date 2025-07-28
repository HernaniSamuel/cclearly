from collections import defaultdict

# Mapeia tag -> [(priority, function)]
TRANSLATORS = defaultdict(list)

def register(tag_name, priority=0):
    def wrapper(func):
        TRANSLATORS[tag_name].append((priority, func))
        TRANSLATORS[tag_name].sort(key=lambda pair: -pair[0])
        return func
    return wrapper
