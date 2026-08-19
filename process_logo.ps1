Add-Type -AssemblyName System.Drawing

$srcPath = "e:\App istalor\develpment\alhafiz_official_logo.png"
$src = [System.Drawing.Bitmap]::FromFile($srcPath)
Write-Output "Width: $($src.Width), Height: $($src.Height)"

$dest = New-Object System.Drawing.Bitmap($src.Width, $src.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)

# Background removal: The background is dark/black (low RGB values: R<60, G<60, B<70)
# We can make it transparent with smooth alpha blending
for ($y = 0; $y -lt $src.Height; $y++) {
    for ($x = 0; $x -lt $src.Width; $x++) {
        $pixel = $src.GetPixel($x, $y)
        $r = $pixel.R
        $g = $pixel.G
        $b = $pixel.B
        
        # Calculate brightness and color dominance
        $maxC = [Math]::Max($r, [Math]::Max($g, $b))
        $minC = [Math]::Min($r, [Math]::Min($g, $b))
        
        # Cyan or Green or Gold/Light areas should be preserved
        # Background is dark grey/black (maxC is very low, e.g. < 45)
        if ($maxC -lt 40) {
            # Fully transparent
            $dest.SetPixel($x, $y, [System.Drawing.Color]::FromArgb(0, 0, 0, 0))
        } elseif ($maxC -lt 85 -and ($maxC - $minC) -lt 25) {
            # Soft shadow/edge transition
            $alpha = [int](($maxC - 40) / 45.0 * 255)
            $dest.SetPixel($x, $y, [System.Drawing.Color]::FromArgb($alpha, $r, $g, $b))
        } else {
            # Logo foreground
            $dest.SetPixel($x, $y, [System.Drawing.Color]::FromArgb(255, $r, $g, $b))
        }
    }
}

$src.Dispose()
$dest.Save("e:\App istalor\develpment\alhafiz_logo_transparent.png", [System.Drawing.Imaging.ImageFormat]::Png)
$dest.Dispose()

Write-Output "Transparent logo created successfully!"
