import importlib.resources

def export_labs(output_filename="my_all_labs.py"):
    """
    Exports the entire content of the bundled labs.py file.
    
    Args:
        output_filename (str): The name of the file to save the lab code to.
                               Defaults to "my_all_labs.py".
    """
    print(f"Exporting lab code to '{output_filename}'...")
    
    try:
        # This safely finds and reads the labs.py file from within the installed package
        source_code = importlib.resources.read_text(__package__, "labs.py")
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(source_code)
            
        print(f"Successfully exported all lab code to '{output_filename}'.")
    except Exception as e:
        print(f"An error occurred during export: {e}")