<H1>Grayscale Normalizer / Greyscale Normaliser</H1>
Created by Chris Fulton
<img width="1172" height="800" alt="image" src="https://github.com/user-attachments/assets/0d59bc59-aefb-4eeb-af92-05a7dd542dd9" />



Grayscale Normalizer – simple Windows UI (Tkinter)

Updates (2025-08-16)
- Added sliders for Black Level, White Level, and Gamma.
- Automatically analyzes the image upon load (no Analyze button anymore).
- Analysis output now includes the file name so it's clear which image was analyzed.

Features
- Open a grayscale image (PNG/JPG/TIFF, etc.). Color images are converted to grayscale.
- Analyze brightness distribution: histogram + stats (min, max, mean, std, dynamic range, entropy) – auto on open.
- Normalize using adjustable black/white levels and gamma; save to user-chosen location.
- Side-by-side preview of input vs. output + before/after metrics.

Dependencies: Pillow (PIL). Everything else is standard library.


<img width="1910" height="1025" alt="image" src="https://github.com/user-attachments/assets/8e0b7f51-6f22-4567-bdb4-334b9020d562" />


