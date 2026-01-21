@echo off
setlocal

REM run_qwen3_vl_instruct.bat - wrapper for run_qwen3_vl_instruct.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_qwen3_vl_instruct.ps1" -CondaEnv exevision-vl %*

endlocal
