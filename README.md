# BZR Texture Manager (BZRTEX)

A comprehensive utility suite designed for **Battlezone 98 Redux** modders. This tool streamlines the asset pipeline by providing specialized converters and editors for the game's unique file formats.

## Features

### ACT Palette Editor
The ACT Editor is purpose-built for the Battlezone `.ACT` format (256-color indexed palette). Unlike generic editors, this includes a **Quick Jump** system for critical engine-reserved indices.

* **Reserved Index Awareness**: Instant access and labeling for key indices:
    * **Index 223**: Skybox color and Sniperscope lens tint.
    * **Index 209**: Global Fog color (horizon transition).
    * **Indices 0-95 / 224-255**: Primary and Secondary Object ranges.
    * **Indices 96-222**: Planet-specific terrain smoothing range.
* **Visual Feedback**: Selected colors are highlighted in a 16x16 grid with real-time RGB and Hex editing.
* **Sync Logic**: Changes to the palette automatically update the preview in the MAP Converter tab.

 <img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/03ec7f22-84ef-4fd5-896e-637878dcea2c" />


### Texture Manager (DDS/TGA/PNG)
An advanced processor for standard game textures, optimized for VRAM management and engine compatibility.

* **Format Conversion**: Custom "Convert From" and "Convert To" logic supporting PNG, TGA, and DDS with batch capabilities.
* **Smart Compression**: Support for DXT1 (Opaque) and DXT5 (Interpolated Alpha), or a setting for no compression.
* **Alpha Auto-Detection**: Scans images during batch processing to automatically choose the most efficient compression codec.
* **Power of 2 Rescaling**: Conditional downscaling logic (512 to 4096) to ensure textures fit within performance budgets.
* **Mipmap Generation**: Optional mipmap creation to prevent distant texture shimmering.

<img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/40b4a2b6-c8fb-4d72-a2af-e1f932427456" />


### MAP Texture Serializer
Handles the conversion of `.MAP` files, which are the specialized textures used by the legacy Battlezone game system.

* **Bidirectional Conversion**: Convert `.MAP` to `.PNG` for editing and back to `.MAP` for the game.
* **Palette Serialization**: Correctly applies your active `.ACT` palette to indexed MAP files during export. Has built in palette data so you don't need an ACT file.
* **Redux Support**: Automatically packs textures as ARGB8888 when required for high-definition assets.

<img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/ac9da67f-380a-45f6-b731-e2050069e520" />


### LGT Light Converter
A dedicated tool for converting `.LGT` lightmap files into editable `.PNG` images.

* **LGT to PNG**: Decodes game lightmaps into editable grayscale images.
* **PNG to LGT**: Repacks the PNG to an LGT file
* **Batch Workflow**: Process entire mission folders of lightmaps simultaneously.

 <img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/8ac91ad6-9bcd-4d4d-ad15-c96b431a160e" />


---

## Installation & Requirements

### For Users
Download the latest `BZR Texture Manager.exe` from the Releases section. No Python installation is required.

### For Developers
If you wish to run from source or modify the tool:

For Developers
If you wish to run from source or modify the tool:

## 1. Clone the repo:
   git clone https://github.com/YourUsername/Battlezone98Redux_TextureManager.git

## 2. Install dependencies:
   pip install customtkinter Pillow numpy imageio imageio[freeimage]

## 3. Run the application:
   python tex_man.py

## 4. Build command:
   python -m PyInstaller --noconfirm --onefile --windowed --name "BZR Texture Manager" --icon "bzrtex.ico" --add-data "bzrtex.ico;." --collect-all customtkinter --copy-metadata imageio tex_man.py

