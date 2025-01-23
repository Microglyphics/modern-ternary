# server/__init__.py
from pathlib import Path
import sys

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.append(str(server_dir))