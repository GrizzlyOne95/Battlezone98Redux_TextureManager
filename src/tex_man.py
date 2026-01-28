import os, struct, math, sys, subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image
import imageio.v3 as iio
import numpy as np
import threading
from ctypes import Structure, c_uint32, c_int, c_uint, c_ubyte

class DXTBZ2Header(Structure):
    _fields_ = [
        ("m_Sig", c_int), ("m_DXTLevel", c_int),
        ("m_1x1Red", c_ubyte), ("m_1x1Green", c_ubyte),
        ("m_1x1Blue", c_ubyte), ("m_1x1Alpha", c_ubyte),
        ("m_NumMips", c_int), ("m_BaseHeight", c_int), ("m_BaseWidth", c_int)
    ]

# --- BZ98 ENGINE CONSTANTS ---
ZONE_RES = 256  # Redux Standard (256x256 per zone)

class BZMapFormat:
    INDEXED, ARGB4444, RGB565, ARGB8888, XRGB8888 = 0, 1, 2, 3, 4
    bpp = [1, 2, 2, 4, 4]

# Full 256-color Moon.act data extracted from BZ98R Toolkit
BUILTIN_MOON_PALETTE = [
    (0, 0, 0), (17, 16, 16), (26, 24, 24), (31, 26, 25), (36, 35, 31), (50, 42, 36),
    (52, 49, 48), (60, 56, 56), (68, 64, 64), (77, 72, 72), (85, 80, 80), (84, 79, 76),
    (112, 108, 104), (116, 129, 125), (133, 138, 133), (178, 174, 174), (191, 188, 188),
    (204, 201, 201), (217, 215, 215), (229, 228, 228), (255, 255, 255), (20, 3, 2),
    (40, 6, 3), (59, 10, 5), (79, 13, 6), (99, 16, 8), (107, 0, 8), (148, 8, 0),
    (140, 33, 8), (148, 16, 0), (156, 24, 0), (173, 57, 0), (189, 82, 8), (206, 99, 16),
    (200, 94, 11), (214, 101, 0), (214, 132, 33), (222, 123, 24), (231, 140, 33),
    (231, 156, 41), (239, 173, 57), (222, 156, 49), (222, 165, 57), (222, 165, 74),
    (231, 173, 99), (239, 189, 90), (247, 198, 82), (239, 206, 115), (249, 249, 149),
    (235, 230, 97), (183, 180, 81), (169, 133, 50), (131, 124, 45), (123, 99, 39),
    (149, 101, 17), (87, 59, 2), (80, 67, 28), (78, 48, 3), (53, 40, 12), (36, 24, 5),
    (171, 72, 69), (169, 168, 158), (153, 150, 139), (249, 249, 195), (223, 216, 188),
    (200, 189, 151), (194, 186, 139), (186, 172, 145), (167, 164, 145), (160, 151, 127),
    (175, 168, 134), (160, 145, 106), (157, 145, 109), (136, 130, 107), (132, 125, 80),
    (116, 104, 81), (96, 94, 83), (84, 73, 55), (115, 72, 1), (106, 81, 30),
    (109, 118, 109), (93, 106, 102), (79, 96, 90), (68, 91, 86), (63, 76, 73),
    (62, 63, 57), (48, 70, 67), (46, 61, 56), (37, 59, 54), (34, 50, 45), (31, 42, 41),
    (24, 36, 32), (19, 23, 21), (16, 14, 14), (15, 10, 6), (7, 11, 9), (181, 191, 204),
    (150, 156, 172), (139, 149, 164), (134, 143, 156), (125, 134, 150), (120, 130, 143),
    (115, 124, 139), (112, 129, 150), (111, 120, 135), (107, 116, 131), (106, 124, 145),
    (101, 117, 141), (100, 111, 128), (100, 108, 123), (96, 108, 123), (96, 104, 120),
    (95, 112, 135), (92, 104, 119), (92, 100, 116), (91, 108, 131), (88, 100, 115),
    (88, 96, 112), (85, 104, 127), (84, 96, 111), (84, 92, 108), (83, 100, 123),
    (80, 96, 119), (80, 92, 108), (80, 88, 104), (76, 96, 119), (76, 92, 116),
    (76, 92, 110), (76, 84, 100), (75, 88, 103), (74, 88, 108), (72, 92, 115),
    (72, 88, 112), (72, 84, 104), (72, 84, 99), (72, 80, 95), (68, 88, 112),
    (68, 84, 108), (68, 80, 100), (68, 76, 92), (67, 84, 102), (67, 80, 95),
    (64, 84, 108), (64, 80, 104), (64, 76, 96), (64, 72, 87), (63, 80, 100),
    (63, 76, 91), (60, 80, 104), (60, 76, 104), (60, 76, 100), (60, 72, 92),
    (60, 68, 83), (59, 76, 96), (59, 72, 87), (56, 76, 100), (56, 72, 100),
    (56, 72, 96), (56, 64, 79), (55, 72, 92), (55, 68, 83), (53, 68, 88),
    (52, 72, 96), (52, 68, 96), (52, 68, 92), (52, 64, 88), (52, 60, 75),
    (51, 64, 79), (49, 64, 84), (48, 68, 92), (48, 64, 92), (48, 60, 84),
    (47, 64, 88), (47, 60, 75), (47, 56, 72), (46, 56, 68), (45, 60, 88),
    (45, 60, 80), (44, 56, 79), (44, 52, 68), (44, 51, 64), (43, 60, 84),
    (40, 56, 80), (40, 56, 76), (40, 52, 76), (40, 48, 64), (40, 48, 60),
    (40, 44, 60), (36, 52, 72), (36, 51, 76), (36, 48, 72), (36, 40, 56),
    (35, 44, 60), (33, 41, 56), (31, 38, 53), (28, 36, 49), (26, 33, 45),
    (24, 30, 41), (22, 27, 38), (20, 24, 34), (17, 22, 30), (15, 19, 26),
    (13, 16, 23), (11, 13, 19), (9, 10, 15), (6, 8, 11), (4, 5, 8), (2, 2, 4),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (0, 0, 0), (0, 0, 0), (0, 255, 255), (0, 127, 127), (0, 63, 63),
    (78, 194, 242), (14, 153, 240), (7, 109, 222), (12, 149, 203), (6, 102, 171),
    (6, 93, 136), (3, 56, 124), (26, 35, 80), (0, 127, 255), (0, 99, 199),
    (0, 70, 141), (0, 34, 69), (0, 21, 42), (0, 255, 0), (0, 127, 0), (0, 63, 0),
    (0, 31, 0), (0, 15, 0), (255, 0, 0), (127, 0, 0), (63, 0, 0), (31, 0, 0),
    (15, 0, 0), (255, 255, 0), (164, 164, 0), (127, 127, 0), (80, 80, 0),
    (64, 64, 0), (255, 0, 255)
]
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
    
class BZReduxSuite(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Battlezone Texture Manager")
        self.geometry("1150x900")
        ctk.set_appearance_mode("dark")
        
        # Load the Moon Palette as default
        self.palette = [list(c) for c in BUILTIN_MOON_PALETTE]
        self.pal_buttons = []
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.tab_act = self.tabview.add("ACT Palette Editor")
        self.tab_tex = self.tabview.add("Texture Manager")
        self.tab_map = self.tabview.add("MAP Converter")
        self.tab_lgt = self.tabview.add("LGT Converter")
        self.tab_dxt = self.tabview.add("DXTBZ2 Converter")
        
        # New Generation Variables
        self.gen_emissive = ctk.BooleanVar(value=False)
        self.emissive_thresh = ctk.IntVar(value=200)
        self.gen_specular = ctk.BooleanVar(value=False)
        self.spec_contrast = ctk.DoubleVar(value=1.5)
        self.gen_normal = ctk.BooleanVar(value=False)
        self.norm_strength = ctk.DoubleVar(value=2.0)
        self.norm_flip_y = ctk.BooleanVar(value=False) # Optional: Toggle for DX/GL compatibility
        
        # Existing Logic Variables
        self.tex_scale_cutoff = ctk.StringVar(value="Disabled")
        self.tex_auto_alpha = ctk.BooleanVar(value=True)
        self.tex_batch_out = ctk.StringVar(value="[Same as Source]")
        self.tex_from_ext = ctk.StringVar(value="all supported")

        self.setup_act_tab()
        self.setup_texture_tab()
        self.setup_map_tab()
        self.setup_lgt_tab()
        self.setup_dxt_tab()

    def log_msg(self, textbox, message):
        textbox.insert("end", f"> {message}\n")
        textbox.see("end")

# --- ACT PALETTE EDITOR ---
    def setup_act_tab(self):
        ctk.CTkLabel(self.tab_act, text="Battlezone 98 Palette Editor (.ACT)", font=("Arial", 20, "bold")).pack(pady=10)
        
        main_f = ctk.CTkFrame(self.tab_act)
        main_f.pack(pady=10, padx=20, fill="both", expand=True)

        # 1. Left: The 16x16 Grid
        grid_f = ctk.CTkFrame(main_f)
        grid_f.pack(side="left", padx=20, pady=20)
        
        self.pal_buttons = []
        for i in range(256):
            r, g, b = self.palette[i]
            btn = ctk.CTkButton(grid_f, text="", width=25, height=25, 
                                fg_color=f"#{r:02x}{g:02x}{b:02x}",
                                hover_color="#ffffff",
                                command=lambda x=i: self.select_palette_color(x))
            btn.grid(row=i // 16, column=i % 16, padx=1, pady=1)
            self.pal_buttons.append(btn)

        # 2. Middle: Quick Jump Shortcuts (Fixed width/height arguments)
        jump_f = ctk.CTkFrame(main_f, width=140)
        jump_f.pack(side="left", padx=10, fill="y", pady=20)
        ctk.CTkLabel(jump_f, text="Quick Jump", font=("Arial", 12, "bold")).pack(pady=10)
        
        ctk.CTkButton(jump_f, text="Index 209\n(Fog)", fg_color="#5d6d7e", height=50, width=100,
                      command=lambda: self.jump_to_index(209)).pack(pady=5, padx=10)
        
        ctk.CTkButton(jump_f, text="Index 223\n(Sky/Scope)", fg_color="#d4ac0d", text_color="black", height=50, width=100,
                      command=lambda: self.jump_to_index(223)).pack(pady=5, padx=10)
        
        ctk.CTkLabel(jump_f, text="Ranges:", font=("Arial", 10, "italic")).pack(pady=(20, 0))
        
        # Fixed these two buttons specifically:
        ctk.CTkButton(jump_f, text="Terrain (96)", width=100, height=24, 
                      command=lambda: self.jump_to_index(96)).pack(pady=2)
        ctk.CTkButton(jump_f, text="Objects (0)", width=100, height=24, 
                      command=lambda: self.jump_to_index(0)).pack(pady=2)

        # 3. Right: Edit Controls
        ctrl_f = ctk.CTkFrame(main_f)
        ctrl_f.pack(side="right", padx=20, fill="y", expand=True)

        self.sel_idx_var = ctk.StringVar(value="Select a Color")
        self.sel_label = ctk.CTkLabel(ctrl_f, textvariable=self.sel_idx_var, font=("Arial", 16, "bold"))
        self.sel_label.pack(pady=10)

        self.bz_info_var = ctk.StringVar(value="")
        ctk.CTkLabel(ctrl_f, textvariable=self.bz_info_var, text_color="#e67e22", wraplength=200).pack()

        # RGB Sliders
        self.r_val = self.create_color_slider(ctrl_f, "Red", self.update_color_from_sliders)
        self.g_val = self.create_color_slider(ctrl_f, "Green", self.update_color_from_sliders)
        self.b_val = self.create_color_slider(ctrl_f, "Blue", self.update_color_from_sliders)

        # Hex Input
        ctk.CTkLabel(ctrl_f, text="Hex Code:").pack(pady=(10,0))
        self.hex_var = ctk.StringVar()
        self.hex_entry = ctk.CTkEntry(ctrl_f, textvariable=self.hex_var)
        self.hex_entry.pack(pady=5)
        ctk.CTkButton(ctrl_f, text="Apply Hex", command=self.apply_hex).pack(pady=5)

        # File Actions
        ctk.CTkButton(ctrl_f, text="LOAD .ACT", fg_color="#27ae60", command=self.load_act).pack(fill="x", pady=10)
        ctk.CTkButton(ctrl_f, text="SAVE .ACT", fg_color="#2980b9", command=self.save_act).pack(fill="x")

    def jump_to_index(self, idx):
        """Logic to handle the quick jump buttons without crashing"""
        self.select_palette_color(idx)
        
        # Visual feedback: Reset all borders, then highlight the selected one
        for i, btn in enumerate(self.pal_buttons):
            if i == idx:
                btn.configure(border_width=2, border_color="white")
            else:
                btn.configure(border_width=0)

    def select_palette_color(self, idx):
        """Updates UI based on selected palette index"""
        self.selected_index = idx
        r, g, b = self.palette[idx]
        
        # Map BZ ranges and specific indices
        if idx == 209:
            info = "INDEX 209: GLOBAL FOG COLOR\n(Horizon transition color)"
            hint = "#95a5a6"
        elif idx == 223:
            info = "INDEX 223: SKY & SNIPERSCOPE\n(Clear-color and lens tint)"
            hint = "#f1c40f"
        elif 0 <= idx <= 95:
            info = f"INDEX {idx}: Objects (Primary)\n(Unit and building textures)"
            hint = "#3498db"
        elif 96 <= idx <= 222:
            info = f"INDEX {idx}: Planet-Specific\n(Terrain and rock smoothing)"
            hint = "#2ecc71"
        elif 224 <= idx <= 255:
            info = f"INDEX {idx}: Objects (Secondary)\n(Extended object range)"
            hint = "#e67e22"
        else:
            info = f"INDEX {idx}: Standard"
            hint = "#ffffff"

        self.sel_idx_var.set(f"Index: {idx}")
        self.bz_info_var.set(info)
        self.sel_label.configure(text_color=hint)
        
        # Update sliders and Hex entry
        self.r_val.set(r)
        self.g_val.set(g)
        self.b_val.set(b)
        self.hex_var.set(f"#{r:02x}{g:02x}{b:02x}")
        
        # Apply the border highlight here too so clicking the grid works
        for i, btn in enumerate(self.pal_buttons):
            btn.configure(border_width=2 if i == idx else 0, border_color="white")

    def update_color_from_sliders(self, _=None):
        if self.selected_index is None: return
        r, g, b = int(self.r_val.get()), int(self.g_val.get()), int(self.b_val.get())
        self.palette[self.selected_index] = [r, g, b]
        hex_code = f"#{r:02x}{g:02x}{b:02x}"
        self.pal_buttons[self.selected_index].configure(fg_color=hex_code)
        self.hex_var.set(hex_code)
        if hasattr(self, 'update_pal_preview'): self.update_pal_preview()

    def apply_hex(self):
        if self.selected_index is None: return
        hex_val = self.hex_var.get().lstrip('#')
        try:
            r, g, b = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
            self.r_val.set(r); self.g_val.set(g); self.b_val.set(b)
            self.update_color_from_sliders()
        except: pass

    def load_act(self):
        path = filedialog.askopenfilename(filetypes=[("ACT Palette", "*.act")])
        if not path: return
        try:
            with open(path, 'rb') as f:
                raw = f.read(768)
                self.palette = [list(struct.unpack('<3B', raw[i:i+3])) for i in range(0, 768, 3)]
            for i, btn in enumerate(self.pal_buttons):
                r, g, b = self.palette[i]
                btn.configure(fg_color=f"#{r:02x}{g:02x}{b:02x}")
            if hasattr(self, 'update_pal_preview'): self.update_pal_preview()
        except Exception as e: print(f"Load Error: {e}")

    def save_act(self):
        path = filedialog.asksaveasfilename(defaultextension=".act", filetypes=[("ACT Palette", "*.act")])
        if not path: return
        try:
            with open(path, 'wb') as f:
                for color in self.palette:
                    f.write(struct.pack('<3B', *color))
        except Exception as e: print(f"Save Error: {e}")

    def create_color_slider(self, parent, label, cmd):
        ctk.CTkLabel(parent, text=label).pack()
        s = ctk.CTkSlider(parent, from_=0, to=255, command=cmd)
        s.pack(pady=2)
        return s

# --- MAP CONVERTER ---
    def setup_map_tab(self):
        ctk.CTkLabel(self.tab_map, text=".MAP Texture Serializer", font=("Arial", 20, "bold")).pack(pady=10)
        
        # 1. Palette Preview Section
        preview_frame = ctk.CTkFrame(self.tab_map)
        preview_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(preview_frame, text="Active Palette Preview (0-255):", font=("Arial", 12)).pack(pady=2)
        
        self.pal_canvas = ctk.CTkCanvas(preview_frame, height=30, bg="black", highlightthickness=0)
        self.pal_canvas.pack(fill="x", padx=10, pady=5)
        self.update_pal_preview() 

        # 2. Options Frame (Batch Folder & Scaling)
        opts = ctk.CTkFrame(self.tab_map)
        opts.pack(pady=10, padx=20, fill="x")
        
        # Output Path
        self.batch_out_path = ctk.StringVar(value="[Same as Source]")
        ctk.CTkLabel(opts, text="Batch Output Folder:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(opts, textvariable=self.batch_out_path, width=400).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(opts, text="Browse", width=60, command=self.set_batch_out).grid(row=0, column=2, padx=5)

        # Scaling Option
        ctk.CTkLabel(opts, text="Rescale (Batch/Single):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.map_scale_var = ctk.StringVar(value="No Scaling")
        ctk.CTkOptionMenu(opts, variable=self.map_scale_var, values=["No Scaling", "128x128", "256x256", "512x512", "1024x1024"]).grid(row=1, column=1, padx=5, sticky="w")

        # 3. Palette Override Section (Restored)
        pal_opt = ctk.CTkFrame(self.tab_map)
        pal_opt.pack(pady=5, padx=20, fill="x")
        
        self.custom_pal_path = ctk.StringVar(value="[Built-in Workspace Palette]")
        ctk.CTkLabel(pal_opt, text="Palette Override:").pack(side="left", padx=10)
        ctk.CTkEntry(pal_opt, textvariable=self.custom_pal_path, width=350).pack(side="left", padx=5)
        ctk.CTkButton(pal_opt, text="Load .ACT", width=80, fg_color="#27ae60", command=self.ui_load_override_pal).pack(side="left", padx=5)
        ctk.CTkButton(pal_opt, text="Reset", width=50, command=self.reset_map_palette).pack(side="left", padx=5)

        # 4. Actions Frame
        f = ctk.CTkFrame(self.tab_map)
        f.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(f, text="+ Single File (MAP/PNG)", fg_color="#2980b9", height=40, command=self.ui_single_map).pack(side="left", padx=10, expand=True, fill="x")
        ctk.CTkButton(f, text="+ Batch Folder", fg_color="#8e44ad", height=40, command=self.ui_batch_map).pack(side="left", padx=10, expand=True, fill="x")
        
        self.map_log = ctk.CTkTextbox(self.tab_map, height=350)
        self.map_log.pack(padx=20, pady=10, fill="both")

    def update_pal_preview(self, custom_palette=None):
        """Redraws the color strip. Uses workspace palette unless custom_palette is passed."""
        self.pal_canvas.delete("all")
        target_pal = custom_palette if custom_palette else self.palette
        width = 1100 
        color_w = width / 256
        for i in range(256):
            r, g, b = target_pal[i]
            color_hex = f"#{r:02x}{g:02x}{b:02x}"
            self.pal_canvas.create_rectangle(i*color_w, 0, (i+1)*color_w, 30, fill=color_hex, outline="")

    def ui_load_override_pal(self):
        path = filedialog.askopenfilename(filetypes=[("ACT Palette", "*.act")])
        if path:
            self.custom_pal_path.set(path)
            with open(path, 'rb') as f:
                raw = f.read(768)
                temp_pal = [list(struct.unpack('<3B', raw[i:i+3])) for i in range(0, 768, 3)]
                self.update_pal_preview(temp_pal)

    def reset_map_palette(self):
        self.custom_pal_path.set("[Built-in Workspace Palette]")
        self.update_pal_preview() # Reverts to main workspace palette

    def set_batch_out(self):
        folder = filedialog.askdirectory()
        if folder:
            self.batch_out_path.set(folder)

    def process_map_file(self, path, output_folder=None):
        base_name = os.path.basename(path)
        file_no_ext = os.path.splitext(base_name)[0]
        dest_dir = output_folder if (output_folder and os.path.isdir(output_folder)) else os.path.dirname(path)

        # 1. Determine active palette
        active_pal = self.palette
        override_path = self.custom_pal_path.get()
        if os.path.exists(override_path) and override_path.lower().endswith(".act"):
            with open(override_path, 'rb') as f:
                raw = f.read(768)
                active_pal = [list(struct.unpack('<3B', raw[i:i+3])) for i in range(0, 768, 3)]

        if path.lower().endswith(".map"):
            with open(path, 'rb') as f:
                rb, fmt, h, _ = struct.unpack('<4H', f.read(8))
                w = rb // BZMapFormat.bpp[fmt]
                data = f.read()

                if fmt == BZMapFormat.INDEXED:
                    img = Image.frombytes('L', (w, h), data)
                    flat_pal = [v for c in active_pal for v in c]
                    img.putpalette(flat_pal)
                    img = img.convert("RGBA")
                else:
                    img = Image.frombytes('RGBA', (w, h), data, 'raw', 'BGRA')
                
                # Apply Scaling
                scale_val = self.map_scale_var.get()
                if scale_val != "No Scaling":
                    new_size = int(scale_val.split('x')[0])
                    img = img.resize((new_size, new_size), Image.Resampling.LANCZOS)
                
                img.save(os.path.join(dest_dir, file_no_ext + ".png"))
                return f"Exported: {file_no_ext}.png"
        else:
            # PNG -> MAP
            img = Image.open(path).convert("RGBA")
            
            # Apply Scaling
            scale_val = self.map_scale_var.get()
            if scale_val != "No Scaling":
                new_size = int(scale_val.split('x')[0])
                img = img.resize((new_size, new_size), Image.Resampling.LANCZOS)

            b, g, r, a = img.split()
            bgra = Image.merge('RGBA', (b, g, r, a))
            with open(os.path.join(dest_dir, file_no_ext + ".map"), 'wb') as f:
                f.write(struct.pack('<4H', img.width * 4, 3, img.height, 0))
                f.write(bgra.tobytes())
            return f"Packed: {file_no_ext}.map"

    def ui_single_map(self):
        path = filedialog.askopenfilename(filetypes=[("MAP or PNG", "*.map;*.png")])
        if not path: return
        try:
            msg = self.process_map_file(path)
            self.log_msg(self.map_log, msg)
        except Exception as e: self.log_msg(self.map_log, f"ERROR: {e}")

    def ui_batch_map(self):
        src_folder = filedialog.askdirectory(title="Select Source Folder")
        if not src_folder: return
        
        out_dir = self.batch_out_path.get()
        if out_dir == "[Same as Source]": out_dir = None
        
        count = 0
        for file in os.listdir(src_folder):
            if file.lower().endswith((".map", ".png")):
                try:
                    self.process_map_file(os.path.join(src_folder, file), out_dir)
                    count += 1
                except Exception as e:
                    self.log_msg(self.map_log, f"Skip {file}: {e}")
        self.log_msg(self.map_log, f"BATCH COMPLETE: {count} files processed.")

# --- LGT CONVERTER (STITCHING FIXED) ---
    def setup_lgt_tab(self):
        ctk.CTkLabel(self.tab_lgt, text="Terrain Lightmap (.LGT) Manager", font=("Arial", 20, "bold")).pack(pady=10)
        
        # Controls Frame
        ctrl = ctk.CTkFrame(self.tab_lgt)
        ctrl.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(ctrl, text="Map Width (Zones):").grid(row=0, column=0, padx=5)
        self.lgt_width_var = ctk.StringVar(value="0") # 0 = Auto-Square
        ctk.CTkEntry(ctrl, textvariable=self.lgt_width_var, width=60).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(ctrl, text="(Leave 0 for square maps)").grid(row=0, column=2, padx=5)

        btn_f = ctk.CTkFrame(self.tab_lgt)
        btn_f.pack(pady=10)
        ctk.CTkButton(btn_f, text="+ LGT to PNG (Extract)", fg_color="#2980b9", command=self.lgt_to_png).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="+ PNG to LGT (Pack)", fg_color="#e67e22", command=self.png_to_lgt).pack(side="left", padx=10)

        self.lgt_log = ctk.CTkTextbox(self.tab_lgt, height=450)
        self.lgt_log.pack(padx=20, pady=10, fill="both")

    def parse_trn_dimensions(self):
        path = filedialog.askopenfilename(filetypes=[("Terrain File", "*.trn")])
        if not path: return
        try:
            with open(path, 'r') as f:
                content = f.read()
                # Find Width=XXXX in the [Size] section
                import re
                width_match = re.search(r'Width\s*=\s*(\d+)', content)
                if width_match:
                    world_width = int(width_match.group(1))
                    # Redux zones are 1280 units wide
                    zones_wide = world_width // 1280
                    self.lgt_width_var.set(str(zones_wide))
                    self.log_msg(self.lgt_log, f"TRN Parsed: World Width {world_width} = {zones_wide} Zones Wide.")
        except Exception as e:
            self.log_msg(self.lgt_log, f"TRN Error: {e}")

    def lgt_to_png(self):
        path = filedialog.askopenfilename(filetypes=[("Lightmap", "*.lgt")])
        if not path: return
        try:
            file_size = os.path.getsize(path)
            # ZONE_RES is 256 for Redux. Chunks are 128x128 in legacy.
            total_chunks = file_size // (ZONE_RES * ZONE_RES)
            map_chunks = total_chunks - 1 
            
            if map_chunks <= 0:
                raise Exception("File too small to contain map data.")

            gw = int(self.lgt_width_var.get())
            if gw <= 0: gw = int(math.sqrt(map_chunks))
            gh = map_chunks // gw
            
            with open(path, 'rb') as f:
                # 1. Skip the Border Chunk (first 65,536 bytes for Redux)
                f.read(ZONE_RES * ZONE_RES)
                
                full_img = Image.new('L', (gw * ZONE_RES, gh * ZONE_RES))
                
                # 2. Stitch Chunks: Sequential reading placed Top-to-Bottom
                # This fixes the vertical swap by starting the file data at the top row.
                for yseg in range(gh): 
                    for xseg in range(gw):
                        data = f.read(ZONE_RES * ZONE_RES)
                        if not data: break
                        
                        zone_img = Image.frombytes('L', (ZONE_RES, ZONE_RES), data)
                        
                        pos_x = xseg * ZONE_RES
                        pos_y = yseg * ZONE_RES
                        full_img.paste(zone_img, (pos_x, pos_y))
                
                out = os.path.splitext(path)[0] + ".png"
                full_img.save(out)
                self.log_msg(self.lgt_log, f"Exported {gw}x{gh} map. Top-Down segment order applied.")
                
        except Exception as e: self.log_msg(self.lgt_log, f"ERROR: {e}")

    def png_to_lgt(self):
        path = filedialog.askopenfilename(filetypes=[("PNG", "*.png")])
        if not path: return
        try:
            img = Image.open(path).convert('L')
            gw, gh = img.width // ZONE_RES, img.height // ZONE_RES
            
            out = os.path.splitext(path)[0] + ".lgt"
            with open(out, 'wb') as f:
                # 1. Write Border Chunk
                border_color = img.getpixel((0, 0)) # Sample top-left for border color
                f.write(bytes([border_color] * (ZONE_RES * ZONE_RES)))
                
                # 2. Pack Chunks (Top-Down order)
                for yseg in range(gh):
                    for xseg in range(gw):
                        box = (xseg * ZONE_RES, yseg * ZONE_RES, 
                               (xseg + 1) * ZONE_RES, (yseg + 1) * ZONE_RES)
                        zone = img.crop(box)
                        f.write(zone.tobytes())
                        
            self.log_msg(self.lgt_log, f"Packed {gw*gh} zones into .LGT (Top-Down).")
        except Exception as e: self.log_msg(self.lgt_log, f"ERROR: {e}")

    def setup_texture_tab(self):
        ctk.CTkLabel(self.tab_tex, text="Advanced Texture Processor", font=("Arial", 20, "bold")).pack(pady=10)
        
        # Main container to split controls and log
        main_content = ctk.CTkFrame(self.tab_tex)
        main_content.pack(fill="both", expand=True, padx=10, pady=5)

        # Left Column: Format & File Settings
        left_col = ctk.CTkFrame(main_content)
        left_col.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # 1. Format Options
        fmt_f = ctk.CTkFrame(left_col)
        fmt_f.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(fmt_f, text="Format Settings", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        self.tex_to_ext = ctk.StringVar(value=".dds")
        ctk.CTkOptionMenu(fmt_f, variable=self.tex_to_ext, values=[".dds", ".png", ".tga"]).grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(fmt_f, text="Output Format:").grid(row=1, column=0, padx=5)

        self.tex_compress = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(fmt_f, text="DXT Compression", variable=self.tex_compress).grid(row=2, column=0, padx=5, pady=2)
        self.tex_mips = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(fmt_f, text="Gen Mipmaps", variable=self.tex_mips).grid(row=2, column=1, padx=5, pady=2)
        
        # Add to setup_texture_tab under Format Settings
        ctk.CTkLabel(fmt_f, text="Rescale if > :").grid(row=4, column=0, padx=5, pady=5)
        self.tex_scale_cutoff = ctk.StringVar(value="Disabled")
        ctk.CTkOptionMenu(fmt_f, variable=self.tex_scale_cutoff, 
                          values=["Disabled", "512", "1024", "2048", "4096"]).grid(row=4, column=1, padx=5, pady=5)
        
        # FIX: Moved Overwrite into the format frame using grid to match its siblings
        self.tex_overwrite = ctk.BooleanVar(value=False) 
        ctk.CTkCheckBox(fmt_f, text="Overwrite Existing", variable=self.tex_overwrite).grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # --- Advanced Map Generation Section ---
        gen_f = ctk.CTkFrame(left_col)
        gen_f.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(gen_f, text="Map Generation", font=("Arial", 12, "bold")).pack(pady=5)

        # Emissive Row
        e_f = ctk.CTkFrame(gen_f, fg_color="transparent")
        e_f.pack(fill="x", padx=10, pady=2)
        ctk.CTkCheckBox(e_f, text="Create Emissive", variable=self.gen_emissive).pack(side="left")
        ctk.CTkLabel(e_f, text="Threshold:").pack(side="right", padx=5)
        ctk.CTkSlider(e_f, from_=0, to=255, variable=self.emissive_thresh, width=150).pack(side="right")

        # Specular Row
        s_f = ctk.CTkFrame(gen_f, fg_color="transparent")
        s_f.pack(fill="x", padx=10, pady=2)
        ctk.CTkCheckBox(s_f, text="Create Specular", variable=self.gen_specular).pack(side="left")
        ctk.CTkLabel(s_f, text="Contrast:").pack(side="right", padx=5)
        ctk.CTkSlider(s_f, from_=0.5, to=3.0, variable=self.spec_contrast, width=150).pack(side="right")

        # Normal Row
        n_f = ctk.CTkFrame(gen_f, fg_color="transparent")
        n_f.pack(fill="x", padx=10, pady=2)
        ctk.CTkCheckBox(n_f, text="Smart Normal", variable=self.gen_normal).pack(side="left")
        ctk.CTkCheckBox(n_f, text="Flip Y (DX)", variable=self.norm_flip_y).pack(side="left", padx=20)
        ctk.CTkLabel(n_f, text="Strength:").pack(side="right", padx=5)
        ctk.CTkSlider(n_f, from_=0.1, to=10.0, variable=self.norm_strength, width=150).pack(side="right")

        # 3. Actions & Log (Right Column)
        right_col = ctk.CTkFrame(main_content)
        right_col.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        self.tex_log = ctk.CTkTextbox(right_col, height=300)
        self.tex_log.pack(fill="both", expand=True, padx=5, pady=5)

        self.tex_progress = ctk.CTkProgressBar(right_col)
        self.tex_progress.pack(fill="x", padx=5, pady=2)
        self.tex_progress.set(0)

        btn_f = ctk.CTkFrame(right_col)
        btn_f.pack(fill="x", pady=5)
        ctk.CTkButton(btn_f, text="Process Single", command=self.ui_single_tex).pack(side="left", fill="x", expand=True, padx=2)
        ctk.CTkButton(btn_f, text="Batch Folder", command=self.start_batch_thread, fg_color="#8e44ad").pack(side="left", fill="x", expand=True, padx=2)
        
        # Batch Settings
        batch_f = ctk.CTkFrame(left_col)
        batch_f.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(batch_f, text="Batch Settings", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.tex_from_ext = ctk.StringVar(value="all supported")
        ctk.CTkOptionMenu(batch_f, variable=self.tex_from_ext, values=["all supported", ".png", ".tga", ".dds", ".jpg"]).pack(pady=2)
        
        ctk.CTkEntry(batch_f, textvariable=self.tex_batch_out).pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(batch_f, text="Set Output Folder", command=self.set_tex_batch_out).pack(pady=2)

    # --- TEXTURE LOGIC FUNCTIONS ---
    def set_tex_batch_out(self):
        folder = filedialog.askdirectory()
        if folder: 
            self.tex_batch_out.set(folder)

    def start_batch_thread(self):
        src_folder = filedialog.askdirectory(title="Select Source Folder")
        if not src_folder: return
        self.tex_progress.set(0)
        thread = threading.Thread(target=self.ui_batch_tex, args=(src_folder,), daemon=True)
        thread.start()

    def ui_batch_tex(self, src_folder):
        """Thread-safe batch processing with progress updates"""
        out_dir = self.tex_batch_out.get()
        if out_dir == "[Same as Source]": 
            out_dir = None
        
        from_filter = self.tex_from_ext.get().lower()
        
        # Identify valid files
        supported = [".png", ".tga", ".dds", ".jpg", ".bmp"]
        files = [f for f in os.listdir(src_folder) if os.path.splitext(f)[1].lower() in supported]
        
        if from_filter != "all supported":
            files = [f for f in files if os.path.splitext(f)[1].lower() == from_filter]
        
        total = len(files)
        if total == 0:
            self.after(0, lambda: self.log_msg(self.tex_log, "No matching files found."))
            return

        count = 0
        for file in files:
            try:
                msg = self.process_texture(os.path.join(src_folder, file), out_dir)
                count += 1
                # Schedule UI updates on the main thread
                progress = count / total
                self.after(0, lambda m=msg, p=progress: (self.log_msg(self.tex_log, m), self.tex_progress.set(p)))
            except Exception as e:
                self.after(0, lambda f=file, err=e: self.log_msg(self.tex_log, f"Skip {f}: {err}"))
                    
        self.after(0, lambda c=count: self.log_msg(self.tex_log, f"BATCH COMPLETE: {c} textures processed."))

    def process_texture(self, path, output_folder=None):
        base_name = os.path.basename(path)
        file_no_ext = os.path.splitext(base_name)[0]
        dest_dir = output_folder if (output_folder and os.path.isdir(output_folder)) else os.path.dirname(path)
        
        target_ext = self.tex_to_ext.get()
        out_path = os.path.join(dest_dir, file_no_ext + target_ext)
        
        # CHECK FOR OVERWRITE
        if os.path.exists(out_path) and not self.tex_overwrite.get():
            return f"Skipped: {file_no_ext}{target_ext} already exists."

        img = Image.open(path).convert("RGBA")
        w, h = img.size

# --- RESTORED: Power of 2 Rescaling Logic ---
        cutoff_val = self.tex_scale_cutoff.get()
        if cutoff_val != "Disabled":
            try:
                limit = int(cutoff_val)
                # If either dimension exceeds the budget, downscale by half
                if w > limit or h > limit:
                    new_w, new_h = w // 2, h // 2
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    w, h = img.size # Update dimensions for logging
            except ValueError:
                pass

        # Alpha detection
        has_alpha = False
        if self.tex_auto_alpha.get():
            alpha_extrema = img.getchannel('A').getextrema()
            if alpha_extrema and alpha_extrema[0] < 255:
                has_alpha = True
        
        if self.gen_emissive.get(): self.internal_gen_emissive(img, dest_dir, file_no_ext, target_ext)
        if self.gen_specular.get(): self.internal_gen_specular(img, dest_dir, file_no_ext, target_ext)
        if self.gen_normal.get(): self.internal_gen_normal(img, dest_dir, file_no_ext, target_ext)
        
        self.internal_save_img(img, out_path, has_alpha)
        return f"Done: {file_no_ext} ({w}x{h}) -> {target_ext}"  
        
    # --- INTERNAL UTILITIES ---
    def internal_save_img(self, img, out_path, has_alpha):
        if out_path.lower().endswith(".dds"):
            # 1. Save a temp TGA (Lossless, handles alpha well)
            temp_tga = out_path.replace(".dds", "_temp.tga")
            img.save(temp_tga)
            
            # 2. Determine compression format
            # BC1 = DXT1 (No alpha), BC3 = DXT5 (Smooth alpha)
            fmt = "BC3_UNORM" if has_alpha else "BC1_UNORM"
            
            # 3. Setup texconv command
            # -m 0: Generate full mipmap chain
            # -y: Overwrite existing
            # -f: Pixel format
            texconv_bin = resource_path("texconv.exe")
            
            cmd = [
                texconv_bin,
                "-f", fmt,
                "-y",
                "-o", os.path.dirname(out_path),
                temp_tga
            ]
            
            # Handle mipmap setting from your UI
            if self.tex_mips.get():
                cmd.extend(["-m", "0"]) # Full chain
            else:
                cmd.extend(["-m", "1"]) # Single level
                
            try:
                # Hide the console window when running the subprocess
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                subprocess.run(cmd, check=True, startupinfo=startupinfo, capture_output=True)
                
                # texconv creates [filename].dds. If we saved temp as [name]_temp.tga, 
                # it creates [name]_temp.dds. Rename it to the final out_path.
                generated_dds = temp_tga.replace(".tga", ".dds")
                if os.path.exists(generated_dds):
                    if os.path.exists(out_path): os.remove(out_path)
                    os.rename(generated_dds, out_path)
                    
            finally:
                if os.path.exists(temp_tga): os.remove(temp_tga)
                
        else:
            # Standard save for non-DDS files
            img.save(out_path)

    def internal_gen_emissive(self, img, dest, name, ext):
        thresh = self.emissive_thresh.get()
        mask = img.convert("L").point(lambda p: 255 if p > thresh else 0)
        emissive = Image.new("RGBA", img.size, (0, 0, 0, 255))
        emissive.paste(img, (0, 0), mask)
        self.internal_save_img(emissive, os.path.join(dest, f"{name}_e{ext}"), False)

    def internal_gen_specular(self, img, dest, name, ext):
        spec = img.convert("L")
        contrast = self.spec_contrast.get()
        spec = spec.point(lambda p: min(255, int(p * contrast)))
        self.internal_save_img(spec.convert("RGBA"), os.path.join(dest, f"{name}_s{ext}"), False)

    def internal_gen_normal(self, img, dest, name, ext):
        gray = np.array(img.convert("L"), dtype=float)
        grad_x = np.gradient(gray, axis=1)
        grad_y = np.gradient(gray, axis=0)
        strength = self.norm_strength.get()
        nx = -grad_x * strength
        ny = grad_y * strength if self.norm_flip_y.get() else -grad_y * strength
        nz = np.ones_like(gray) * 255.0
        norm = np.sqrt(nx**2 + ny**2 + nz**2)
        nx, ny, nz = nx/norm, ny/norm, nz/norm
        r, g, b = ((nx + 1.0) * 127.5).astype(np.uint8), ((ny + 1.0) * 127.5).astype(np.uint8), (nz * 255.0).astype(np.uint8)
        normal_map = Image.fromarray(np.stack([r, g, b, np.full_like(r, 255)], axis=2))
        self.internal_save_img(normal_map, os.path.join(dest, f"{name}_n{ext}"), False)

    def ui_single_tex(self):
        path = filedialog.askopenfilename()
        if not path: return
        try:
            msg = self.process_texture(path)
            self.log_msg(self.tex_log, msg)
        except Exception as e: 
            self.log_msg(self.tex_log, f"ERROR: {e}")
            
    def setup_dxt_tab(self):
        ctk.CTkLabel(self.tab_dxt, text="DXTBZ2 Texture Converter", font=("Arial", 20, "bold")).pack(pady=10)
        
        # --- Settings Frame ---
        ctrl = ctk.CTkFrame(self.tab_dxt)
        ctrl.pack(pady=10, padx=20, fill="x")

        # Format Selection
        ctk.CTkLabel(ctrl, text="Output Format:").grid(row=0, column=0, padx=10, pady=10)
        self.dxt_out_ext = ctk.StringVar(value=".dds")
        ctk.CTkOptionMenu(ctrl, variable=self.dxt_out_ext, values=[".dds", ".png"]).grid(row=0, column=1, padx=10)

        # Standard Options (Linked to your existing logic)
        self.dxt_mips = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(ctrl, text="Gen Mipmaps (DDS only)", variable=self.dxt_mips).grid(row=1, column=0, padx=20, pady=5)
        
        self.dxt_overwrite = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(ctrl, text="Overwrite Existing", variable=self.dxt_overwrite).grid(row=1, column=1, padx=20, pady=5)

        # --- Action Buttons ---
        btn_f = ctk.CTkFrame(self.tab_dxt)
        btn_f.pack(pady=10)
        ctk.CTkButton(btn_f, text="+ Convert Single .dxtbz2", fg_color="#2980b9", command=self.ui_single_dxt).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="+ Batch Folder", fg_color="#8e44ad", command=self.ui_batch_dxt).pack(side="left", padx=10)

        self.dxt_log = ctk.CTkTextbox(self.tab_dxt, height=400)
        self.dxt_log.pack(padx=20, pady=10, fill="both")

    def process_dxtbz2(self, path):
        """Converts dxtbz2 to a temp DDS, then uses internal_save_img for final compression/format"""
        base_name = os.path.basename(path)
        file_no_ext = os.path.splitext(base_name)[0]
        out_ext = self.dxt_out_ext.get()
        final_out = os.path.join(os.path.dirname(path), file_no_ext + out_ext)

        if os.path.exists(final_out) and not self.dxt_overwrite.get():
            return f"Skipped: {file_no_ext}{out_ext} exists."

        with open(path, "rb") as f:
            header = DXTBZ2Header()
            f.readinto(header)
            
            # Read chunk size for the first mip
            size_raw = f.read(4)
            if not size_raw: return "Error: Empty file"
            chunk_size = struct.unpack("I", size_raw)[0]
            
            # Check for alpha based on data density
            has_alpha = chunk_size // header.m_BaseHeight == header.m_BaseWidth
            
            # Extract raw DXT data
            raw_data = f.read(chunk_size)
            
        # To use your existing PIL/texconv pipeline, we temporarily wrap this in a basic DDS
        temp_dds = path + ".tmp.dds"
        self.internal_wrap_dxt_to_dds(temp_dds, header, raw_data, has_alpha)

        try:
            # Open the wrapped DDS as a PIL image
            with Image.open(temp_dds) as img:
                # Use your existing texture processor logic for compression/mips/format
                # Temporarily override UI variables to match this tab's settings
                old_mips = self.tex_mips.get()
                self.tex_mips.set(self.dxt_mips.get())
                
                self.internal_save_img(img, final_out, has_alpha)
                
                self.tex_mips.set(old_mips) # Restore global state
        finally:
            if os.path.exists(temp_dds): os.remove(temp_dds)

        return f"Converted: {file_no_ext} -> {out_ext}"

    def internal_wrap_dxt_to_dds(self, out_path, header, data, has_alpha):
        """Minimal DDS wrapper to make raw DXT data readable by PIL"""
        with open(out_path, "wb") as f:
            f.write(b"DDS ")
            # Basic Header
            f.write(struct.pack("<IIIIIII 11I", 124, 0x1|0x2|0x4|0x1000, header.m_BaseHeight, header.m_BaseWidth, 0, 0, 1, *[0]*11))
            # Pixel Format (DXT1 or DXT5)
            fourcc = b"DXT5" if has_alpha else b"DXT1"
            f.write(struct.pack("<II4sIIIII", 32, 0x4, fourcc, 0, 0, 0, 0, 0))
            # Caps
            f.write(struct.pack("<IIII I", 0x1000, 0, 0, 0, 0))
            f.write(data)

    def ui_single_dxt(self):
        path = filedialog.askopenfilename(filetypes=[("Legacy Texture", "*.dxtbz2")])
        if not path: return
        try:
            msg = self.process_dxtbz2(path)
            self.log_msg(self.dxt_log, msg)
        except Exception as e:
            self.log_msg(self.dxt_log, f"ERROR: {e}")

    def ui_batch_dxt(self):
        folder = filedialog.askdirectory()
        if not folder: return
        
        def run_batch():
            files = [f for f in os.listdir(folder) if f.lower().endswith(".dxtbz2")]
            for f in files:
                try:
                    msg = self.process_dxtbz2(os.path.join(folder, f))
                    self.after(0, lambda m=msg: self.log_msg(self.dxt_log, m))
                except: pass
            self.after(0, lambda: self.log_msg(self.dxt_log, "Batch Finished."))
            
        threading.Thread(target=run_batch, daemon=True).start()

    # def ui_batch_tex(self, src_folder):
        # """Thread-safe batch processing with progress updates"""
        # out_dir = self.tex_batch_out.get()
        # if out_dir == "[Same as Source]": 
            # out_dir = None
        
        # from_filter = self.tex_from_ext.get().lower()
        
        # # Identify valid files
        # supported = [".png", ".tga", ".dds", ".jpg", ".bmp"]
        # files = [f for f in os.listdir(src_folder) if os.path.splitext(f)[1].lower() in supported]
        
        # if from_filter != "all supported":
            # files = [f for f in files if os.path.splitext(f)[1].lower() == from_filter]
        
        # total = len(files)
        # if total == 0:
            # self.after(0, lambda: self.log_msg(self.tex_log, "No matching files found."))
            # return

        # count = 0
        # for file in files:
            # try:
                # msg = self.process_texture(os.path.join(src_folder, file), out_dir)
                # count += 1
                # # Schedule UI updates on the main thread
                # progress = count / total
                # self.after(0, lambda m=msg, p=progress: (self.log_msg(self.tex_log, m), self.tex_progress.set(p)))
            # except Exception as e:
                # self.after(0, lambda f=file, err=e: self.log_msg(self.tex_log, f"Skip {f}: {err}"))
                    
        # self.after(0, lambda c=count: self.log_msg(self.tex_log, f"BATCH COMPLETE: {c} textures processed."))

if __name__ == "__main__":
    app = BZReduxSuite()
    app.mainloop()
