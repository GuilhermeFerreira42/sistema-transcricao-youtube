@echo off
mkdir sistema-transcricao-youtube
cd sistema-transcricao-youtube
mkdir backend
cd backend
echo. > app.py
echo. > youtube_handler.py
echo. > utils.py
cd ..
mkdir frontend
cd frontend
mkdir static
cd static
mkdir css
echo. > css\style.css
mkdir js
echo. > js\main.js
mkdir images
cd ..
mkdir templates
echo. > templates\index.html
cd ..
mkdir data
cd data
mkdir transcriptions
cd ..
echo Estrutura de diretórios criada com sucesso!