@echo off
echo ========================================
echo  Iniciando Flask com AWS Toolkit
echo ========================================
echo.

REM Ativa o ambiente virtual
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [AVISO] Ambiente virtual nao encontrado
    echo Execute setup.bat primeiro
    pause
    exit /b 1
)

REM Define variáveis de ambiente para forçar uso de credenciais do sistema
set AWS_SDK_LOAD_CONFIG=1
set AWS_PROFILE=default

echo.
echo Configuracoes:
echo - AWS_SDK_LOAD_CONFIG: %AWS_SDK_LOAD_CONFIG%
echo - AWS_PROFILE: %AWS_PROFILE%
echo.
echo Iniciando aplicacao Flask...
echo.

REM Inicia a aplicacao
python app.py
