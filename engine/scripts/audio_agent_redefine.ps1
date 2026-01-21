param(
    [int]$Start = 1,
    [int]$End = 2,
    [string]$StoryRoot = "",
    [string]$StoryConfig = ""
)

$ScriptRoot = $PSScriptRoot
$Runner = Join-Path $ScriptRoot "run_audio_agent.ps1"

& $Runner -Start $Start -End $End -StoryRoot $StoryRoot -StoryConfig $StoryConfig
