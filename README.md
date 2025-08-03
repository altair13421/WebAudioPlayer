# WebAudioPlayer

First of all, Forgive me for the abomination of a UI
I know it's Trash, that is why I am REACTing with a Frontend

This is For Me, and Practice,

need to visit `/v1/` and in the scan Folder, to Scan and Add the Songs to the Library.

the Frontend is in
[This URL](https://github.com/altair13421/webaudiofe) My Repo.
Will Update Documentation

## Features remaining

- Need to Add Romaji Support (Japanese Done)
- need to add artist playlist, or artist all songs support

## Deployment

### venv

    ```sh
    # Create ENV Non Sudo Commands All
    python -m venv venv

    # linux
    source venv/bin/activate

    # Windows
    .\\venv\\Scripts\\activate

    # Installing packages
    pip install -r requirements.txt

    # Runserver
    python manage.py runserver 0.0.0.0:8008
    ```

### Docker

Docker Config to look at

    ```yml
    services:
    ## Frontend Service here

    backend:
        build:
        context: ./WebAudioPlayer
        dockerfile: Dockerfile
        container_name: webaudio_backend
        environment:
        - DJANGO_SETTINGS_MODULE=WebPlayer.settings
        - PYTHONUNBUFFERED=1
        - SQLITE_DB_PATH=/app/data/db.sqlite3
        - DATABASE_URL=sqlite:////app/data/db.sqlite3
        volumes:
        - ./WebAudioPlayer:/app
        - ./data:/app/data  # can't remove the volume ACCIDENTALLY, so it's not in volume, but in a separate folder
        - /mnt/games/Music:/app/music  # Music directory. WHERE YOUR MUSIC IS
        ports:
        - "8008:8008" # Expose this port, cause, 8000 I would use for other apps for reasons including dev
        restart: unless-stopped
        # command: >
        # gunicorn --bind 0.0.0.0:8008 --workers 3 WebPlayer.wsgi:application
        command: ["sh", "-c", "python manage.py runserver 0.0.0:8008"]
    ```

File Structure to note:

    ```txt
    .
    ├── data
    ├── docker-compose.yml
    ├── webaudiofe # Frontend
    └── WebAudioPlayer # Backend
    ```

Docker Building

    ```sh
    # First need to Copy it in the parent folder
    cp docker-compose.yml ../docker-compose.yml

    # Build Backend
    docker-compose build backend
    # or with file
    docker-compose -f docker-compose.yml build backend

    # Or build all
    docker-compose build

    # if you want it to run directly
    docker-compose up --build

    # If you already built it, and now... you want to run it
    docker-compose up
    ```
