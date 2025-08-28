import logging
from app import create_app
import os
from dotenv import load_dotenv
import click

# load variables from .env into os.environ
load_dotenv()

app = create_app()
port = int(os.environ.get("PORT", 4444))

if __name__ == "__main__":
    click.echo(f"Flask app started on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
