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

 <img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/03ec7f22-84ef-4fd5-896e-637878dcea2c" />


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

<img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/d6d22349-589f-479c-bfd2-a0a1e31f8f82" />




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

### DXTBZ2 Texture Converter
A tool to convert proprietary BZ2 encoded textures to PNG or DDS. 
* **DXTBZ2 to DDS**
* **DXTBZ2 to PNG**
* **Single or Batch Processing**
* **Thanks to VEARIE for the DXTBZ2 direct python code!**

<img width="1152" height="932" alt="image" src="https://github.com/user-attachments/assets/7a0372f8-aea8-4fc1-9181-9dfe072af651" />

### Bulk DDS Recompressor (CLI)

`src/recompress.py` walks a whole mod folder and rewrites every uncompressed
`.dds` as DXT1 or DXT5 in place, keeping the mip chain. This is the one that
moves the needle on a big mod: ISDF Chronicles shipped **7.8 GB of DDS, of which
6.4 GB was uncompressed**, and this takes the folder to roughly 2.4 GB without
changing a single resolution.

```
python src/recompress.py "<mod folder>" --backup "<somewhere safe>" [--dry-run]
```

It is a separate path from the GUI's Texture Manager tab rather than a mode of
it, because the two have different constraints:

* **No `texconv.exe`.** The GUI shells out to DirectXTex, which has to be
  downloaded and placed next to the exe. This is pure Python on the numpy/Pillow
  dependencies already declared.
* **It can read the files that matter.** The GUI path goes
  `Image.open(path).convert("RGBA")`, and Pillow will not open an R5G6B5 DDS at
  all — which is the single biggest class of uncompressed art in the wild (295
  of ISDF Chronicles' 906 uncompressed files are R5G6B5 normal maps).
* **Channel order comes from the pixel-format bit masks, not from a guess.**
  Most 32-bit DDS files are ARGB, but nine of that mod's are ABGR, and all nine
  are normal maps. A reader that hard-codes BGR swaps X and Z on them and
  quietly wrecks the lighting.
* **Source mips are transcoded, not regenerated**, so the author's own mip chain
  survives exactly and no resampling filter gets chosen on their behalf. A chain
  is generated only for files that shipped without one.

#### What it decides, and why

**DXT1 vs DXT5** comes from whether mip 0 has alpha the renderer could act on.
The common "RGBA32 whose alpha is 255 everywhere" case is very common — 247 of
429 in that mod — and costs 0.5 bpp instead of 1.0 with nothing lost, because
there is nothing in the channel to lose. The test has a tolerance: those mission
loading screens are alpha 255 everywhere except 2432 texels at exactly 254, out
of 8.4 million. Reading `min < 255` literally there doubles the file to preserve
one part in 255 of blend on 0.03% of an image that is drawn opaque and
fullscreen.

**UI art is skipped** (`src/uiscan.py`, override with `--compress-ui`). BC1
quantises each 4×4 block to two endpoints, which on a glyph edge or a thin HUD
rule reads as ringing where the same error on a diffuse map is invisible. The
scan finds them by the material scheme they inherit — `BZSprite/AlphaHUD` and
`BZSprite/AlphaHUDPixel` — not by filename, so it catches `bzfont` and
`numbers2` without also catching `BZBaseCockpit`, which is a world-space model.
The whole UI set is under 1% of the art, so this costs nothing worth having.

**Every file is verified by decoding what was written**, not by trusting the
settings that were applied, and the summary reports colour RMSE plus two extra
columns:

* normal maps get mean angular deviation of the decoded normal. For scale, BC1
  measured 0.28–0.47° on real art, against the **3.70° per code step** that
  R5G6B5 — the format most of these normal maps already ship in — imposes
  anyway. BC1 is four times smaller *and* an order of magnitude inside the
  existing error floor.
* DXT5 files get mean alpha error. The BC4 encoder is exact on binary alpha,
  which is the cutout case that actually matters.

**Originals are copied out and hash-checked before anything is overwritten**, and
later runs re-derive from that backup rather than from the already-compressed
live file — so changing a setting and re-running replays the whole job cleanly
instead of compounding on itself.


---

## Installation & Requirements

### For Users
Download the latest `BZR Texture Manager.exe` from the Releases section. No Python installation is required.

### For Developers
If you wish to run from source or modify the tool:

## 1. Clone the repo:
   git clone https://github.com/YourUsername/Battlezone98Redux_TextureManager.git

## 2. Install dependencies:
   pip install customtkinter Pillow numpy imageio imageio[freeimage]

## 3. Download texconv.exe from Microsoft's DirectXTex GitHub. Place texconv.exe in the root folder before running or building.

## 4. Run the application:
   python tex_man.py

## 5. Build command:
   python -m PyInstaller --noconfirm --onefile --windowed --name "BZR Texture Manager" --icon "bzrtex.ico" --add-data "bzrtex.ico;." --collect-all customtkinter --copy-metadata imageio tex_man.py

