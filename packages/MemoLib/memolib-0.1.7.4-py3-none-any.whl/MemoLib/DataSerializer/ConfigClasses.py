import json
from os import path


class Parent_Config:
    def __init__(self, **kwargs):
        # Initialize attributes dynamically from kwargs
        # This will allow any property to be set dynamically.
        self.__dict__.update(**kwargs)

    def Save(self, file_path):
        """Serialize the object to a file in JSON format."""
        try:
            with open(file_path, "w") as file:
                # Serialize the entire object's attributes (using self.__dict__)
                json.dump(self.__dict__, file, indent=4)
        except Exception as e:
            print(f"Error saving to {file_path}: {e}")

    @classmethod
    def Load(cls, file_path):
        """Deserialize the object from a JSON file."""
        if path.exists(file_path):
            try:
                with open(file_path, "r") as file:
                    data = json.load(file)

                # Create an instance of the class and assign the loaded attributes
                obj = cls(**data)
                return obj
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error loading from {file_path}: {e}")
                obj = cls()  # Return a default object in case of error
                obj.Save(file_path)  # Save the default object to the file
        else:
            # File doesn't exist; create a new object and save it
            obj = cls()
            obj.Save(file_path)
        return obj
