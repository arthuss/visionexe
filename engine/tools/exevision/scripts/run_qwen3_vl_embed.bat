@echo off
setlocal

REM run_qwen3_vl_embed.bat - wrapper for run_qwen3_vl_embed.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_qwen3_vl_embed.ps1" -CondaEnv exevision-vl %*

endlocal
