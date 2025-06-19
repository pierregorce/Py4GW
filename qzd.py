from multiprocessing.shared_memory import SharedMemory
from HeroAI.types import GameStruct  # Using the imported definition
import gc
import json


# Ensure no remaining references exist

def decode_structure(structure, depth=0):
    print(f"Before decoding: {gc.get_referrers(structure)}")
    """
        Recursively decode and print any ctypes.Structure or array-like object.

        Args:
            structure (ctypes.Structure or array): The structure or array to decode.
            depth (int): Current recursion depth (for indentation).
        """
    indent = "  " * depth  # Indentation based on recursion depth

    # Print information about the structure being decoded
    # print(f"{indent}Decoding structure at depth {depth}:")
    # print(f"{indent}References to structure: {gc.get_referrers(structure)}")

    # Check if the structure is a ctypes.Structure with _fields_
    if hasattr(structure, "_fields_"):
        # Loop through all fields in the structure
        for field_name, field_type in structure._fields_:
            field_value = getattr(structure, field_name)
            print(f"{indent}{field_name}: {field_value}")

            # Check if this field is another nested structure or array
            if hasattr(field_value, "_fields_") or hasattr(field_value, "__len__"):
                # Recursively decode nested fields
                decode_structure(field_value, depth + 1)

    # Handle array-like objects (e.g., ctypes arrays)
    elif hasattr(structure, "__len__"):  # This checks for array-like objects
        print(f"{indent}Array with {len(structure)} elements:")
        for i, item in enumerate(structure):
            print(f"{indent}[{i}]")  # Print array index
            decode_structure(item, depth + 1)  # Recursively decode each item

    # Handle any unknown or fallback cases
    else:
        print(f"{indent}Unknown object: {structure}")

def structure_to_dict(structure):
    """
    Converts a ctypes.Structure (or array) into a dictionary recursively.

    Args:
        structure (ctypes.Structure or ctypes array): The structure to convert.

    Returns:
        dict: A dictionary representation of the structure.
    """
    if hasattr(structure, "_fields_"):  # Handle ctypes.Structure
        result = {}
        for field_name, field_type in structure._fields_:
            field_value = getattr(structure, field_name)
            if hasattr(field_value, "_fields_") or hasattr(field_value, "__len__"):
                # Recursively convert nested structure or array
                result[field_name] = structure_to_dict(field_value)
            else:
                # Primitive value
                result[field_name] = field_value
        return result

    elif hasattr(structure, "__len__"):  # Handle ctypes arrays
        return [structure_to_dict(item) for item in structure]

    return structure  # Fallback for unknown object types

def read_shared_memory():
    SHARED_MEMORY_FILE_NAME = "HeroAI_Mem"

    try:
        # Attach to shared memory
        shm = SharedMemory(name=SHARED_MEMORY_FILE_NAME)
        print(f"References to shared memory buffer: {gc.get_referrers(shm.buf)}")

        print(f"References to shared memory buffer: {gc.get_referrers(shm.buf)}")

        # Map the shared memory to the GameStruct
        game_struct = GameStruct.from_buffer(shm.buf)

        # Copy the game_struct into a new variable (converted as a dictionary for JSON)
        game_struct_dict = structure_to_dict(game_struct)

        # Serialize the copied structure to JSON and print it
        game_struct_json = json.dumps(game_struct_dict, indent=4)
        print("GameStruct JSON:")
        print(game_struct_json)

        #
        # # Access and print fields from the GameStruct
        # print("GameStruct Data:")
        # for field_name, field_type in game_struct._fields_:
        #     print(f"{field_name}: {getattr(game_struct, field_name)}")
        #
        # # Decode and print the GameStruct
        # print("Decoding GameStruct from shared memory:")
        # decode_structure(game_struct)

        # Ensure no references to the GameStruct exist
        del game_struct

        # Cleanup
        shm.close()

    except FileNotFoundError:
        print(f"Shared memory '{SHARED_MEMORY_FILE_NAME}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    read_shared_memory()