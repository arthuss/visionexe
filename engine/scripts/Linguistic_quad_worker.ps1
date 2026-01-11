$python = "python"

$jobs = @(
  @{ path="C:\Users\sasch\visionexe\engine\workers\worker_llm_analysis_semantic-historical.py"; args="--use-gemini --force --chapter-batch" },
  @{ path="C:\Users\sasch\visionexe\engine\workers\worker_llm_analysis_synthactic.py";        args="--use-gemini --force --chapter-batch" },
  @{ path="C:\Users\sasch\visionexe\engine\workers\worker_llm_analysis_Morphologic.py";      args="--use-gemini --force --chapter-batch" },
  @{ path="C:\Users\sasch\visionexe\engine\workers\worker_llm_analysis_graphematic.py";      args="--use-gemini --force --chapter-batch" }
)

foreach ($job in $jobs) {
  $name = Split-Path $job.path -Leaf
  Start-Process "cmd.exe" -ArgumentList @(
    "/k",  # /c = schließt am Ende sofort; /k lässt offen
    "title $name && `"$python`" `"$($job.path)`" $($job.args)"
  )
}
