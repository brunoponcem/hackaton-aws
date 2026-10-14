param(
    [string]$PresentationPath = (Join-Path $PSScriptRoot '../bb-assets-dc11-presentation.pptx')
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $PresentationPath).Path)
try {
    $slides = @($archive.Entries | Where-Object { $_.FullName -match '^ppt/slides/slide\d+\.xml$' } |
        Sort-Object { [int]([regex]::Match($_.Name, '\d+').Value) })
    if ($slides.Count -eq 0) { throw 'La presentación no contiene diapositivas.' }
    foreach ($slide in $slides) {
        $reader = [System.IO.StreamReader]::new($slide.Open())
        try { [xml]$document = $reader.ReadToEnd() } finally { $reader.Dispose() }
        $paragraphs = @($document.SelectNodes('//*[local-name()="p"]') | ForEach-Object {
            $parts = @($_.SelectNodes('.//*[local-name()="t"]') | ForEach-Object { $_.InnerText })
            if ($parts.Count -gt 0) { $parts -join '' }
        })
        if ($paragraphs.Count -eq 0) { throw "Diapositiva sin texto: $($slide.FullName)" }
        "## $($slide.FullName)"
        $paragraphs
        ''
    }
} finally { $archive.Dispose() }
