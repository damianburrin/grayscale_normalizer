<H1>Grayscale Normalizer / Greyscale Normaliser</H1>
This software was developed by Created by Chris Fulton and is hosted here with his permission.  Chris wants the utility to be accesbile free to all and hopefully developed and improved upon the the Laser Engraving Community


<img width="1172" height="800" alt="image" src="https://github.com/user-attachments/assets/0d59bc59-aefb-4eeb-af92-05a7dd542dd9" />

<img width="1919" height="1077" alt="image" src="https://github.com/user-attachments/assets/49ecb4a5-81a6-4d86-8910-72279500eef2" />



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

<H1>Installing/Running</H1>
To run this tool you can use one of the following methods

<H2>Using Python</H2>
Download the source code from the repository
Pip install the Pillow library (pip install PIL or pip3 install PIL)
Open the source code with python3 and run the script

<H2>Windows Stand Alone Execuatable</H2>
Download the grey scale normalizer zip file and extract the contents 
<img width="868" height="232" alt="image" src="https://github.com/user-attachments/assets/de81fffa-beea-424a-a7b1-57a2c32e4ccb" />

Double click on the executable
Windows will identify that this is an unkown publisher
<img width="585" height="514" alt="image" src="https://github.com/user-attachments/assets/323e64a3-65e3-4bf9-a6fb-e7136c059a72" />

Click Run Anyway and the utility will load


<H1>Use</H1>

<img width="647" height="655" alt="image" src="https://github.com/user-attachments/assets/28b1e065-a115-4881-8ec6-7f2c85e5489c" />


1.  Use a tool such as SculptOK or Imag-R to convert your image to an image depth map and then open the image in the utility
<img width="1914" height="1079" alt="image" src="https://github.com/user-attachments/assets/9516aadf-8430-482d-be4b-01e965095892" />

2.  Adust the gamma and levels as required
<img width="1896" height="816" alt="image" src="https://github.com/user-attachments/assets/76a8dab2-bd7f-499c-969e-6a94618a7565" />

3.  Press Normalize
<img width="1867" height="918" alt="image" src="https://github.com/user-attachments/assets/6e30a1b6-9ad8-4bd7-8b48-2113ff7a44c5" />

4.  Save the output image
   
5.  Use lightburn 3D slicing mode to engrave you image with your preferred setting for the material you are using
<img width="510" height="691" alt="image" src="https://github.com/user-attachments/assets/edf33078-3dd9-44d3-b322-f17c4a2f8b9f" />







