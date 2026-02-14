#### install python

    - ´sudo apt install python3´

#### install nvm , nodejs

    - ´curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash´
    - ´nvm --version´
    - ´nvm install node´
    - ´node --version´ 

#### create react app

    - ´npm create vite@latest frontend -- --template react´

#### Create Venv for backend

    - ´python3 -m venv backend-venv´
    - ´source backend-venv/bin/activate´


#### install Flask, FlaskORM (Object Relational Mapping) and other frontend needs

    - ´pip3 install Flask' 
    - ´pip3 install Flask-SQLAlchemy´   # (map the entries in SQL into a Python Object so we can operate on them)
    - ´pip3 install flask-cors´         # (cross origin requests)
    - ´npm install react-router-dom´

#### Run Backend + FrontEnd

    - ´python3 backend/main.py´

    ...and on another terminal:

    - ´npm run frontend/dev´