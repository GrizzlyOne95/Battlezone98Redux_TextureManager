# BZR Texture Manager (BZRTEX)

A comprehensive utility suite designed for **Battlezone 98 Redux** modders. This tool streamlines the asset pipeline by providing specialized converters and editors for the game's unique file formats.

## Features

### ACT Palette Editor
The ACT Editor is purpose-built for the Battlezone `.ACT` format (256-color indexed palette). Unlike generic editors, this includes a **Quick Jump** system for critical engine-reserved indices.

* **Reserved Index Awareness**: Instant access and labeling for key indices:
    * **Index 223**: Skybox color and Sniperscope lens tint.
    * **Index 209**: Global Fog color (horizon transition).
    * **Indices 0-95 / 224-255**: Primary and Secondary Object ranges. These seem to be ignored by Redux.
    * **Indices 96-222**: Planet-specific terrain smoothing range. These seem to be ignored by Redux.
* **Visual Feedback**: Selected colors are highlighted in a 16x16 grid with real-time RGB and Hex editing.
* **Sync Logic**: Changes to the palette automatically update the preview in the MAP Converter tab.

<img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/f5c0f11f-5506-4652-b143-fe2e90e712c9" />

### Texture Manager (DDS/TGA/PNG)
An advanced processor for standard game textures, optimized for VRAM management and engine compatibility.

* **Format Conversion**: Custom "Convert From" and "Convert To" logic supporting PNG, TGA, and DDS with batch capabilities.
* **Smart Compression**: Support for DXT1 (Opaque) and DXT5 (Interpolated Alpha), or a setting for no compression.
* **Alpha Auto-Detection**: Scans images during batch processing to automatically choose the most efficient compression codec.
* **Power of 2 Rescaling**: Conditional downscaling logic (512 to 4096) to ensure textures fit within performance budgets.
* **Mipmap Generation**: Optional mipmap creation to prevent distant texture shimmering.
* **Automatic Normal/Specular/Emissive Generation**: Optional additional texture generation with flip normals option, and sliders for thresholds.
* **Overwrite Existing Option**
* **Multithreading Support**: Main window won't freeze during long batch processes.
* **Progress Bar**: Shows progress for large batches.

<img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/a6776632-7358-432d-9f2d-a34df1ed48c1" />

### MAP Texture Serializer
Handles the conversion of `.MAP` files, which are the specialized textures used by the legacy Battlezone game system.

* **Bidirectional Conversion**: Convert `.MAP` to `.PNG` for editing and back to `.MAP` for the game.
* **Palette Serialization**: Correctly applies your active `.ACT` palette to indexed MAP files during export. Has built-in palette data so you don't need an ACT file.
* **Correct MAP decoding**: The integrated compatibility codec reads all five MAP pixel formats rather than assuming every non-indexed MAP is 32-bit BGRA.
* **Redux Support**: The simple workflow packs imported images as ARGB8888 for high-definition assets.
* **Advanced MakeMAP dialog**: Full MakeMAP-compatible controls are available directly from the MAP tab.

<img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/4567e542-3944-4e12-8581-ff79bdd0d517" />

### MakeMAP Compatibility

The application integrates a clean-room compatibility implementation of the original **Battlezone MakeMAP (Mar 27 2017)**. The core is `src/makemap_compat.py`; `src/tex_man_entry.py` routes the graphical MAP tab through that codec and adds an **Advanced MakeMAP** dialog. Release builds also package a separate `BZR_MakeMAP_Compat_*` command-line utility for scripting and batch pipelines.

The compatibility layer covers the complete MakeMAP option surface found in the reference executable:

* **All MAP formats**: type 0 indexed, type 1 A4R4G4B4, type 2 R5G6B5, type 3 A8R8G8B8, and type 4 X8R8G8B8.
* **BMP/TGA output** with target-format quantization.
* **Alpha tools**: `-recoveralpha`, `-chromakey`, `-transindex`, and `-undopma`.
* **Color remapping and grading**: `-remap`, `-colorize`, `-desat`, per-channel `-pow*`, `-mul*`, and `-add*` controls.
* **Orientation and quantization**: `-flipx`, `-flipy`, and MakeMAP-style `-diff` error diffusion.
* **Batch behavior**: multiple paths, wildcard patterns, recursive directories, and the original `/option` spelling.

Example CLI usage:

```powershell
BZR_MakeMAP_Compat_Windows.exe -8888 texture.png
BZR_MakeMAP_Compat_Windows.exe -pal moon.act -transindex 0 -diff 100 terrain.png
BZR_MakeMAP_Compat_Windows.exe -4444 -undopma effect.tga
```

See [`docs/MAKEMAP_COMPATIBILITY.md`](docs/MAKEMAP_COMPATIBILITY.md) for the full parity matrix, reverse-engineered format details, transform order, and validation notes.

### LGT Light Converter
A dedicated tool for converting `.LGT` lightmap files into editable `.PNG` images.

* **LGT to PNG**: Decodes game lightmaps into editable grayscale images.
* **PNG to LGT**: Repacks the PNG to an LGT file.
* **Batch Workflow**: Process entire mission folders of lightmaps simultaneously.

<img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/8cf4b58a-7c69-4609-8123-ef11d783878e" />

### DXTBZ2 Texture Converter
A tool to convert proprietary BZ2 encoded textures to PNG or DDS.

* **DXTBZ2 to DDS**
* **DXTBZ2 to PNG**
* **Single or Batch Processing**
* **Thanks to VEARIE for the DXTBZ2 direct Python code!**

<img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/fcf80b0f-364f-4cb3-830c-717cd568f0ca" />

---

## Installation & Requirements

### For Users
Download the latest platform build from the Releases section. The graphical **BZR Texture Manager** contains the MakeMAP integration, and release artifacts also contain the standalone **BZR MakeMAP Compat** command-line utility.

### For Developers

1. Clone the repo:

   ```bash
   git clone https://github.com/GrizzlyOne95/Battlezone98Redux_TextureManager.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Download `texconv.exe` from Microsoft's DirectXTex GitHub and place it in the root folder before using/building the DDS features on Windows.

4. Run the integrated graphical application:

   ```bash
   python src/tex_man_entry.py
   ```

5. Run the MakeMAP-compatible CLI directly:

   ```bash
   python src/makemap_compat.py -8888 texture.png
   ```

6. Run the regression suite:

   ```bash
   python -m unittest discover -s tests -v
   ```
