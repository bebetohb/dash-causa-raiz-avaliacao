@echo off
REM Ativa mensagens de log
echo Subindo projeto para o GitHub...

REM Inicializa repositório caso ainda não tenha
git init

REM Adiciona todos os arquivos
git add .

REM Commit padrão
git commit -m "Atualizacao do projeto"

REM Define repositório remoto (troque pela sua URL)
git remote remove origin
git remote add origin https://github.com/bebetohb/dashboard-causa-raiz-avaliacao.git

REM Define branch principal
git branch -M main

REM Envia para o GitHub
git push -u origin main

echo Projeto enviado com sucesso!
pause
