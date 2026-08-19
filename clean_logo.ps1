Add-Type -TypeDefinition @"
using System;
using System.Drawing;
using System.Drawing.Imaging;

public class ImageProcessor {
    public static void CleanAndCropLogo(string srcPath, string outPath) {
        using (Bitmap src = new Bitmap(srcPath)) {
            Bitmap dest = new Bitmap(src.Width, src.Height, PixelFormat.Format32bppArgb);
            
            for (int y = 0; y < src.Height; y++) {
                for (int x = 0; x < src.Width; x++) {
                    Color c = src.GetPixel(x, y);
                    float hue = c.GetHue();
                    float sat = c.GetSaturation();
                    float bri = c.GetBrightness();
                    
                    bool isLogo = false;
                    // Keep vibrant cyan, lime green and yellow/cyan highlights of the emblem
                    if (sat > 0.15 && bri > 0.12) {
                        if (hue >= 50 && hue <= 235) {
                            isLogo = true;
                        }
                    }
                    
                    if (isLogo) {
                        dest.SetPixel(x, y, Color.FromArgb(255, c.R, c.G, c.B));
                    } else {
                        dest.SetPixel(x, y, Color.FromArgb(0, 0, 0, 0));
                    }
                }
            }
            
            int minX = src.Width, minY = src.Height, maxX = 0, maxY = 0;
            for (int y = 0; y < src.Height; y++) {
                for (int x = 0; x < src.Width; x++) {
                    if (dest.GetPixel(x, y).A > 0) {
                        if (x < minX) minX = x;
                        if (x > maxX) maxX = x;
                        if (y < minY) minY = y;
                        if (y > maxY) maxY = y;
                    }
                }
            }
            
            int pad = 15;
            minX = Math.Max(0, minX - pad);
            minY = Math.Max(0, minY - pad);
            maxX = Math.Min(src.Width - 1, maxX + pad);
            maxY = Math.Min(src.Height - 1, maxY + pad);
            
            int cropW = maxX - minX + 1;
            int cropH = maxY - minY + 1;
            
            using (Bitmap cropped = new Bitmap(cropW, cropH, PixelFormat.Format32bppArgb)) {
                using (Graphics g = Graphics.FromImage(cropped)) {
                    g.DrawImage(dest, new Rectangle(0, 0, cropW, cropH), new Rectangle(minX, minY, cropW, cropH), GraphicsUnit.Pixel);
                }
                cropped.Save(outPath, ImageFormat.Png);
            }
            dest.Dispose();
        }
    }
}
"@ -ReferencedAssemblies System.Drawing

[ImageProcessor]::CleanAndCropLogo("C:\Users\AD Bhi Creative Stud\.gemini\antigravity\brain\88193d6b-0359-44dc-9922-5e61d0ddd332\.user_uploaded\media_1787144519537.jpg", "e:\App istalor\develpment\alhafiz_logo_transparent.png")
Copy-Item "e:\App istalor\develpment\alhafiz_logo_transparent.png" "e:\App istalor\develpment\alhafiz_official_logo.png" -Force
Write-Output "Clean cropped transparent logo created!"
