@echo off
setlocal

REM run_qwen3_vl_rerank.bat - wrapper for run_qwen3_vl_rerank.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_qwen3_vl_rerank.ps1" -CondaEnv exevision-vl %*

endlocal
