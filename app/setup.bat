@echo off
echo ========================================
echo  DynamoDB Manager - Setup Script
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale o Python 3.8 ou superior
    pause
    exit /b 1
)

echo [1/4] Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo [ERRO] Falha ao criar ambiente virtual
    pause
    exit /b 1
)

echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [3/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)

echo [4/4] Criando arquivo .env...
if not exist .env (
    copy .env.example .env
    echo Arquivo .env criado! Configure suas credenciais AWS.
) else (
    echo Arquivo .env ja existe.
)

echo.
echo ========================================
echo  Setup concluido com sucesso!
echo ========================================
echo.
echo Proximos passos:
echo 1. Configure suas credenciais AWS no arquivo .env
echo 2. Execute: python app.py
echo.
pause
