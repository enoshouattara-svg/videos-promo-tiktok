# Synthèse vocale locale avec les voix Windows déjà installées (aucun envoi sur Internet).
# Utilisation : powershell -NoProfile -ExecutionPolicy Bypass -File voice_synth.ps1 -JobFile jobs.json
# jobs.json = [ {"voice":"Paul","rate":1.0,"pitch":1.0,"text":"...","out":"C:/chemin/ligne1.wav"}, ... ]
param([Parameter(Mandatory = $true)][string]$JobFile)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType = WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, $type) {
    $task = $asTask.MakeGenericMethod($type).Invoke($null, @($op))
    $null = $task.Wait(-1)
    $task.Result
}
$jobs = ConvertFrom-Json -InputObject ([System.IO.File]::ReadAllText($JobFile, [System.Text.Encoding]::UTF8))
$synth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$voices = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices
foreach ($j in $jobs) {
    $v = $voices | Where-Object { $_.DisplayName -like "*$($j.voice)*" -and $_.Language -like 'fr*' } | Select-Object -First 1
    if (-not $v) { throw "voix introuvable : $($j.voice)" }
    $synth.Voice = $v
    $synth.Options.SpeakingRate = [double]$j.rate
    $synth.Options.AudioPitch = [double]$j.pitch
    $stream = Await ($synth.SynthesizeTextToStreamAsync([string]$j.text)) ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
    $net = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
    $ms = New-Object System.IO.MemoryStream
    $net.CopyTo($ms)
    [System.IO.File]::WriteAllBytes([string]$j.out, $ms.ToArray())
    "ok  $($v.DisplayName)  rate=$($j.rate)  ->  $($j.out)  ($($ms.Length) octets)"
}
