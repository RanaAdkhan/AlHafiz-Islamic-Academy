Add-Type -TypeDefinition @"
using System;
using System.Drawing;
using System.Drawing.Imaging;

public class ImageProcessor {
    public static void CleanAndCropLogo(string srcPath, string outPath) {
        using (Bitmap src = new Bitmap(srcPath)) {
            int minX = src.Width, minY = src.Height, maxX = 0, maxY = 0;
            
            // Background thresholding & finding bounding box
            Bitmap dest = new Bitmap(src.Width, src.Height, PixelFormat.Format32bppArgb);
            
            for (int y = 0; y < src.Height; y++) {
                for (int x = 0; x < src.Width; x++) {
                    Color c = src.GetPixel(x, y);
                    int maxC = Math.Max(c.R, Math.Max(c.G, c.B));
                    int minC = Math.Min(c.R, Math.Min(c.G, c.B));
                    
                    if (maxC < 38) {
                        dest.SetPixel(x, y, Color.FromArgb(0, 0, 0, 0));
                    } else if (maxC < 75 && (maxC - minC) < 20) {
                        int alpha = (int)((maxC - 38) / 37.0 * 255.0);
                        if (alpha > 255) alpha = 255;
                        if (alpha < 0) alpha = 0;
                        dest.SetPixel(x, y, Color.FromArgb(alpha, c.R, c.G, c.B));
                        if (alpha > 40) {
                            if (x < minX) minX = x;
                            if (x > maxX) maxX = x;
                            if (y < minY) minY = y;
                            if (y > maxY) maxY = y;
                        }
                    } else {
                        dest.SetPixel(x, y, Color.FromArgb(255, c.R, c.G, c.B));
                        if (x < minX) minX = x;
                        if (x > maxX) maxX = x;
                        if (y < minY) minY = y;
                        if (y > maxY) maxY = y;
                    }
                }
            }
            
            // Add slight padding around bounding box
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

[ImageProcessor]::CleanAndCropLogo("e:\App istalor\develpment\alhafiz_official_logo.jpg", "e:\App istalor\develpment\alhafiz_logo_transparent.png")
Copy-Item "e:\App istalor\develpment\alhafiz_logo_transparent.png" "e:\App istalor\develpment\alhafiz_official_logo.png" -Force
Write-Output "Clean cropped transparent logo created!"
