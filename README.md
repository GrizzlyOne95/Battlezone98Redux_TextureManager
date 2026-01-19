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

### Texture Manager (DDS/TGA/PNG)
An advanced processor for standard game textures, optimized for VRAM management and engine compatibility.

* **Format Conversion**: Custom "Convert From" and "Convert To" logic supporting PNG, TGA, and DDS.
* **Smart Compression**: Support for DXT1 (Opaque) and DXT5 (Interpolated Alpha).
* **Alpha Auto-Detection**: Scans images during batch processing to automatically choose the most efficient compression codec.
* **Power of 2 Rescaling**: Conditional downscaling logic (512 to 4096) to ensure textures fit within performance budgets.
* **Mipmap Generation**: Optional mipmap creation to prevent distant texture shimmering.

### MAP Texture Serializer
Handles the conversion of `.MAP` files, which are the specialized tile textures used by the Battlezone terrain system.

* **Bidirectional Conversion**: Convert `.MAP` to `.PNG` for editing and back to `.MAP` for the game.
* **Palette Serialization**: Correctly applies your active `.ACT` palette to indexed MAP files during export.
* **Redux Support**: Automatically packs textures as ARGB8888 when required for high-definition assets.

### LGT Light Converter
A dedicated tool for converting `.LGT` lightmap files into editable `.PNG` images.

* **LIT to PNG**: Decodes game lightmaps into editable grayscale images.
* **Batch Workflow**: Process entire mission folders of lightmaps simultaneously.

---

## Installation & Requirements

### For Users
Download the latest `BZR Texture Manager.exe` from the Releases section. No Python installation is required.

### For Developers
If you wish to run from source or modify the tool:

1. **Clone the repo**:
   ```bash
   git clone [https://github.com/YourUsername/Battlezone98Redux_TextureManager.git](https://github.com/YourUsername/Battlezone98Redux_TextureManager.git)
2. **Install dependencies**:
```bash
  pip install customtkinter Pillow numpy imageio imageio[freeimage]
3. **Run the application**:
```bash
  python tex_man.py

 4. **Build Command**:
 ```bash
   python -m PyInstaller --noconfirm --onefile --windowed --name "BZR Texture Manager" --icon "bzrtex.ico" --add-data "bzrtex.ico;." --collect-all customtkinter --copy-metadata imageio "tex_man.py"
