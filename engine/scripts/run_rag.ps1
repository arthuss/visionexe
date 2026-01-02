param(
    [int]$Chapter = 1,
    [string]$Query = "",
    [switch]$Reindex,
    [string]$Config = "rag_config.json"
)

Set-Location -Path $PSScriptRoot

$OutputEncoding = [System.Text.Encoding]::UTF8

$chapterArg = $Chapter.ToString()

if ($Reindex) {
    Write-Host "Indexing chapter $chapterArg..." -ForegroundColor Cyan
    python rag_indexer.py --chapter $chapterArg --config $Config
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Indexing failed." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

if (-not $Query) {
    $Query = "checklist status for this chapter"
}

Write-Host "Query: $Query" -ForegroundColor Yellow
python rag_query.py $Query --chapter $chapterArg --config $Config
