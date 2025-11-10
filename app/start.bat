@echo off
echo ========================================
echo  Iniciando DynamoDB Manager
echo ========================================
echo.

REM Ativa o ambiente virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [AVISO] Ambiente virtual nao encontrado
    echo Execute setup.bat primeiro
    pause
    exit /b 1
)

REM Verifica se o .env existe
if not exist .env (
    echo [AVISO] Arquivo .env nao encontrado
    echo Copiando .env.example para .env...
    copy .env.example .env
    echo.
    echo Configure suas credenciais AWS no arquivo .env
    echo Pressione qualquer tecla para continuar...
    pause
)

REM Inicia a aplicacao
python app.py
