# Python app with a GUI for tracking blood pressure measurements

## Description
- User can track their blood pressure levels by saving their daily values of systolic pressure (upper number), diastolic pressure (lower number) and heart rate.
- Application will draw two graphs (morning and evening) of blood pressure and hr values.
- Started this project to make tracking my own blood pressure numbers easier with help of graphs.

## Technology Stack
- Python
- PySide6 library for building GUI
- Pandas and NumPy for data handling.
- Matplotlib for plotting graphs

## Install
- Clone project from GitHub
- Install Python (check https://www.python.org/)
- Install Uv (check https://docs.astral.sh/uv/getting-started/installation/)
- Go into project folder and while in there install dependencies by running: uv sync
- Start application by running (in project folder): uv run python main.py

## Other information
- Your data will be saved to data.csv file. File will be created the first time you save data in application.