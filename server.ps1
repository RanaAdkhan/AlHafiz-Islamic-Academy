# AlHafiz Islamic Quran Academy - PowerShell Native HTTP Web Server
$port = 5000
$prefix = 'http://localhost:5000/'
$root = $PSScriptRoot

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)

try {
    $listener.Start()
    Write-Host '========================================================='
    Write-Host 'AlHafiz Islamic Quran Academy Web Server is LIVE!'
    Write-Host 'URL: http://localhost:5000'
    Write-Host '========================================================='
} catch {
    Write-Host "Error starting listener: $_"
    exit 1
}

$mimeTypes = @{
    '.html' = 'text/html; charset=utf-8';
    '.htm'  = 'text/html; charset=utf-8';
    '.css'  = 'text/css; charset=utf-8';
    '.js'   = 'application/javascript; charset=utf-8';
    '.json' = 'application/json; charset=utf-8';
    '.png'  = 'image/png';
    '.jpg'  = 'image/jpeg';
    '.jpeg' = 'image/jpeg';
    '.mp3'  = 'audio/mpeg';
    '.svg'  = 'image/svg+xml';
    '.ico'  = 'image/x-icon'
}

while ($listener.IsListening) {
    try {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response

        $response.Headers.Add('Access-Control-Allow-Origin', '*')
        $response.Headers.Add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        $response.Headers.Add('Access-Control-Allow-Headers', 'Content-Type, Authorization')

        if ($request.HttpMethod -eq 'OPTIONS') {
            $response.StatusCode = 200
            $response.Close()
            continue
        }

        $rawUrl = $request.Url.LocalPath
        if ($rawUrl -eq '/' -or [string]::IsNullOrWhiteSpace($rawUrl)) {
            $rawUrl = '/index.html'
        }

        $localPath = Join-Path $root ($rawUrl.TrimStart('/'))

        if (Test-Path -LiteralPath $localPath -PathType Leaf) {
            $ext = [System.IO.Path]::GetExtension($localPath).ToLower()
            $contentType = if ($mimeTypes.ContainsKey($ext)) { $mimeTypes[$ext] } else { 'application/octet-stream' }
            $response.ContentType = $contentType
            $response.StatusCode = 200
            $bytes = [System.IO.File]::ReadAllBytes($localPath)
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } elseif ($rawUrl.StartsWith('/api/')) {
            $response.ContentType = 'application/json; charset=utf-8'
            $jsonRes = '{"status":"success"}'
            if ($rawUrl -eq '/api/courses') {
                $jsonRes = '{"status":"success","courses":[{"title":"Quran With Tajweed"},{"title":"Hifz-ul-Quran"},{"title":"Noorani Qaida"},{"title":"Islamic Studies"},{"title":"Quran Translation"}]}'
            } elseif ($rawUrl -eq '/api/teachers') {
                $jsonRes = '{"status":"success","teachers":[{"name":"Hafiz Allah Ditta"},{"name":"Qaria Fatima"},{"name":"Qari Muhammad Usama"}]}'
            } elseif ($rawUrl -eq '/api/admin/stats') {
                $jsonRes = '{"status":"success","stats":{"total_registrations":12,"pending_registrations":3,"enrolled_registrations":9,"popular_course":"Quran With Tajweed"}}'
            }
            $response.StatusCode = 200
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonRes)
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $indexPath = Join-Path $root 'index.html'
            $response.ContentType = 'text/html; charset=utf-8'
            $response.StatusCode = 200
            $bytes = [System.IO.File]::ReadAllBytes($indexPath)
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        }
        $response.Close()
    } catch {
        # continue loop
    }
}
