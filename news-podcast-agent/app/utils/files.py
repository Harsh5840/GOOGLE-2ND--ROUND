from pathlib import Path

def get_output_dir() -> Path:
    """Get or create output directory for generated files."""
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    return output_dir 