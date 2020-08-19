import pickle


class SuperClass:
    """
    All classes that inherit from this class will have the pickle
    method that shouldn't throw any errors. This is done by removing
    all objects that don't inherit from this class and can't be pickled.
    """
    def pickle(self) -> bytes:
        dictionary = self.__dict__.copy()
        keys = tuple(dictionary.keys())
        for key in keys:
            try:
                dictionary[key] = dictionary[key].pickle()
            except AttributeError:
                try:
                    pickle.dumps(dictionary[key])
                except:
                    dictionary.pop(key)
        return pickle.dumps(dictionary)
