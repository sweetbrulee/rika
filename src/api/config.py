import os

rika_api_port = os.getenv("PORT")  # if you deploy on Heroku, it will set the env $PORT
rika_api_base_url = f"http://localhost:{rika_api_port}"
