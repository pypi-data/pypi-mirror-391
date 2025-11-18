def apply(state_fn):
    def wrapper(self, *args):
        for object in self.objects:
            state_fn(self, object, *args)
        return self

    return wrapper