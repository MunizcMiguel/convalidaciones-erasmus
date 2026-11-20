# OCR local con el motor integrado de Windows (Windows.Media.Ocr, sin descargas ni red).
# Uso: powershell -NoProfile -ExecutionPolicy Bypass -File ocr_windows.ps1 <lista.tsv> [en-US]
# <lista.tsv>: una linea por imagen, "ruta_imagen<TAB>ruta_json_salida" (UTF-8).
# Salida JSON por imagen: {"lines":[{"text":..., "words":[[texto, x, y, ancho, alto], ...]}]} (pixeles).
param([string]$ListFile, [string]$Lang = "en-US")
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, [Type]$t) {
    $task = $asTaskGeneric.MakeGenericMethod($t).Invoke($null, @($op)); $task.Wait(-1) | Out-Null; $task.Result
}
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new($Lang))
if ($null -eq $engine) { throw "Idioma OCR no disponible: $Lang" }
foreach ($pair in Get-Content -Encoding UTF8 $ListFile) {
    if (-not $pair.Trim()) { continue }
    $img, $out = $pair -split "`t"
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($img)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bmp = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $res = Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
    $lines = @()
    foreach ($l in $res.Lines) {
        $ws = @()
        foreach ($w in $l.Words) { $r = $w.BoundingRect; $ws += , @($w.Text, $r.X, $r.Y, $r.Width, $r.Height) }
        $lines += , @{ text = $l.Text; words = $ws }
    }
    $json = ConvertTo-Json -Depth 6 -Compress @{ lines = $lines }
    [System.IO.File]::WriteAllText($out, $json, (New-Object System.Text.UTF8Encoding($false)))
    $stream.Dispose()
}
