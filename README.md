##### Run the script "setup.sh" to run the app. What does it do?

#### Installs python

    - ´sudo apt install python3´

#### Installs nvm and nodejs

    - ´curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash´
    - ´nvm --version´
    - ´nvm install node´
    - ´node --version´ 

#### Creates react app

    - ´npm create vite@latest frontend -- --template react´

#### Creates Virtual Environment for backend

    - ´python3 -m venv backend-venv´
    - ´source backend-venv/bin/activate´


#### Installs Flask, FlaskORM (Object Relational Mapping) and other frontend needs

    - ´pip3 install Flask' 
    - ´pip3 install Flask-SQLAlchemy´   # (map the entries in SQL into a Python Object so we can operate on them)
    - ´pip3 install flask-cors´         # (cross origin requests)
    - ´npm install react-router-dom´

#### Runs Backend + FrontEnd

    - ´python3 backend/main.py´

    ...and on another terminal:

    - ´npm run frontend/dev´

