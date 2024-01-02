Django refactor of openipam. The original app is installed and run as normal:

Run the backend api with these command in the root directory (Also covered in the readme in root):

```
poetry shell
poetry install
./manage.py runserver
```

Navigating to localhost:8000 will bring you to the old app.

The refactored app is under the url /ui. This includes a refactored api and a new react frontend. To get the frontend ready, go to /openipam/frontend and run:

```
npm install
```
