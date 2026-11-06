"""Create a local .env with a random secret, preserving any existing .env."""
import secrets
from pathlib import Path

backend = Path(__file__).resolve().parents[1]
destination = backend / ".env"
content = (backend / ".env.example").read_text(encoding="utf-8")
content = content.replace(
    "replace-with-a-locally-generated-value", secrets.token_urlsafe(64)
)
try:
    with destination.open("x", encoding="utf-8") as env_file:
        env_file.write(content)
except FileExistsError:
    print("backend/.env already exists; left unchanged.")
else:
    print("Created backend/.env. Set your local database credentials in this file.")
