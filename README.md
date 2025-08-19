<H1>Grayscale Normalizer / Greyscale Normaliser</H1>
This software was developed by Created by Chris Fulton and is hosted here with his permisin.  Chris wants the utility to be accesbile free to all and hopefully developed and improved upon the the Laser Engraving Community


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


<h1>Purpose</h1>
Grayscale images have varying shades of gray, where each shade represents a different level of brightness. In laser engraving, these different shades can be mapped to varying depths of engraving

In laser engraving, setting the number of layers to 256 (or a factor of it like 128 or 512) is often used when working with grayscale images and aiming for varying depths of engraving. This approach allows the laser to create a depth map by treating each grayscale value as a separate layer. By processing the image in passes, with each pass corresponding to a grayscale level, the laser can achieve a more linear relationship between grayscale value and engraving depth. 

When images are downloaded from tools such a SculptOK or Imag-R they are not always fully optimised with 256 specic shades of of grey.  This tool enables that optimisation in hope of procuing cleaner depth maps for engraving.

<H1>Use</H1>
1.  Use a tool such as SculptOK or Imag-R to convert your image to an image depth map
<img width="1914" height="1079" alt="image" src="https://github.com/user-attachments/assets/9516aadf-8430-482d-be4b-01e965095892" />

2.  Adust the gamma and levels as required
<img width="1896" height="816" alt="image" src="https://github.com/user-attachments/assets/76a8dab2-bd7f-499c-969e-6a94618a7565" />

3.  Press Normalize
<img width="1867" height="918" alt="image" src="https://github.com/user-attachments/assets/6e30a1b6-9ad8-4bd7-8b48-2113ff7a44c5" />

4.  Save the output image  
7.  Use lightburn 3D slicing mode to engrave you image.






