#=========================================================================
# PWQ QR Gen 4 - World's Most Advanced QR Code Generator
#=========================================================================
#==================== MODULE IMPORTING =============================#
from __future__ import annotations
import os.path
from PIL import Image, ImageDraw
from collections.abc import Sequence
from typing import Union, Optional
import itertools
import collections
import re
# ========================================================================#
"""
================ PWQ QR Gen 4 — Fully Customizable QR Code Generator ================

This project builds on [Project Nayuki's QR Code Generator](https://github.com/nayuki/QR-Code-generator)

--- 🚀 What's New?
• PWQAI & Manual Mode — automatic parameter selection or full manual control
• Custom logo support — Instagram, YouTube, WhatsApp, or any uploaded image
• Color & shape customization — circle/square grids, RGB foreground/background
• 16 encoding techniques — UTF-8, UTF-16BE, ISO-8859-1, ISO-8859-3, and more
• ECI encoding support — Extended Channel Interpretation
• Built-in renderer — generate and save QR codes directly to file

--- 📜 Licensing
• Base code © 2025 Project Nayuki — MIT License
• All new features © 2025 PWQQRGen4 by Pawlex — MIT License

--- ⚠️ Tips & Cautions
• Manual mode EC levels: `PWQ_QR_GEN_4.PWQ_QR_Ecl.{Level}`
  - `.Low` (7% recovery), `.Medium` (15%), `.Quartile` (25%), `.High` (30%)
• Mask range: `0–7` — each applies a different filter, all are scannable
• Version range: `1–40` — determines QR size in modules/grids
"""


class PWQ_QR_GEN_4():
    @staticmethod # Functional
    def create_text_format_object(segs: list[PWQ_QR_Segmentation], eclvl: PWQ_QR_GEN_4.PWQ_QR_Ecl, ver: int, mask: int) -> PWQ_QR_GEN_4:
        """
        This functions encodes the data into segments and creates the bytearray with the 4-bit mode indicator, the character count, terminator bits, pad bits
        and repeating pattern bits.
        """
        return PWQ_QR_GEN_4.encode_segmented_data(segs, eclvl=eclvl, version=ver, mask=mask)

    @staticmethod # Functional
    def encode_segmented_data(segs: Sequence[[PWQ_QR_Segmentation]], eclvl: PWQ_QR_GEN_4.PWQ_QR_Ecl = 'Udf', version: int = -1, mask: int = - 1):
        """
        Returns the actual encoded data bytes for current version and EC level. Includes the 4-bit mode indicator, the character count bits, the actual text
        data bits, the terminator bits + pad bits and lastly the repeating pattern bits. Afterwards packs the bytes into Big-Endian, and converts into hexa-
        decimal bytearray.
        """
        num_datacwmax: int = PWQ_QR_GEN_4._get_num_datacw(version, eclvl) * 8
        num_datacwused: Optional[int] = PWQ_QR_Segmentation._get_encode_bits(segs, version)
        pwqbb = _PWQ_Bit_Buffer()
        # ==== Concatenate segments to create data bit string =================#
        # ==== (4-bit mode indicator, character count bits, and text data bits) ===#
        for seg in segs:
            pwqbb._construct_bit(seg._get_mode()._get_mode_bits(), 1 << 2) # 4-bit mode indicator
            pwqbb._construct_bit(seg._get_numchars(), seg._get_mode()._get_num_charcount_bits(version)) # Character count bits
            pwqbb.extend(seg._bitdata) # Text data bits
        assert len(pwqbb) == num_datacwused
        # ======== Add terminator bits and pad to fill the byte =================#
        assert len(pwqbb) <= num_datacwmax
        pwqbb._construct_bit(0, min(4, num_datacwmax-len(pwqbb))) # 4 Terminator bits / However many are left in pwqbb
        pwqbb._construct_bit(0, -len(pwqbb) % 8) # Pad up to a byte if necessary
        assert len(pwqbb) % 8 == 0
        # ======= Pad with alternating repeating pattern =======================#
        for repbyte in itertools.cycle((0xEC, 0x11)):
            if len(pwqbb) >= num_datacwmax: break
            pwqbb._construct_bit(repbyte, 1 << 3)
        # ====== Pack bits into bytes in Big Endian (MSB-LSB) ==================#
        bytedatacw: Union[bytes, Sequence[int]] = bytearray([0] * (len(pwqbb) // 8))
        for (i, b) in enumerate(pwqbb): bytedatacw[i >> 3] |= b << (7 - (i & 7))
        return bytedatacw

    # ============= Placeholder type hints ===================================#
    _input_txt: str
    _version: int
    _eclvl: Union[str, PWQ_QR_GEN_4.PWQ_QR_Ecl]
    _mask: int = -1 # Illegal value, further overwritten by constructor
    _logoimg:Union[str, PWQ_QR_GEN_4]
    _bgcolor: Sequence[int, int, int]
    _fgcolor: Sequence[int, int, int]
    _savefilepath: str
    _filename: str
    _gridsize: int
    _quietzonesize: int
    _PWQAI_mode: bool
    _modulesmatrix: list[list[bool]] # All pixels on the QR code
    _staticmodules: list[list[bool]] # Pixels that form part of static patterns and are thus skipped during data-bit placement
    _bytedatacw: Union[bytes, Sequence[int]]

    # ========= Private-Field Variables ======================================#
    _minver: int = 1
    _maxver: int = 40
    _pencount_1: int = 3
    _pencount_2: int = 3
    _pencount_3: int = 40
    _pencount_4: int = 10
    _eccw_per_block: Sequence[Sequence[int]] = (
        # Index 0 is set to an illegal value thus utilised solely for padding
        (-1, 7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28, 28, 28, 28, 30, 30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),  # Low
        (-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28),  # Medium
        (-1, 13, 22, 18, 26, 18, 24, 18, 22, 20, 24, 28, 26, 24, 20, 30, 24, 28, 28, 26, 30, 28, 30, 30, 30, 30, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),  # Quartile
        (-1, 17, 28, 22, 16, 22, 28, 26, 26, 24, 28, 24, 28, 22, 24, 24, 30, 28, 28, 26, 28, 30, 24, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30))  # High

    _num_ecblocks: Sequence[Sequence[int]] = (
        # Index 0 is set to an illegal value thus utilised solely for padding
        (-1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 4, 6, 6, 6, 6, 7, 8, 8, 9, 9, 10, 12, 12, 12, 13, 14, 15, 16, 17, 18,19, 19, 20, 21, 22, 24, 25),  # Low
        (-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49),  # Medium
        (-1, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8, 8, 10, 12, 16, 12, 17, 16, 18, 21, 20, 23, 23, 25, 27, 29, 34, 34, 35, 38,40,43, 45, 48, 51, 53, 56, 59, 62, 65, 68),  # Quartile
        (-1, 1, 1, 2, 4, 4, 4, 5, 6, 8, 8, 11, 11, 16, 16, 18, 16, 19, 21, 25, 25, 25, 34, 30, 32, 35, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 70, 74, 77, 81))  # High

    _maskpatterns: Sequence[collections.abc.Callable[[int,int],int]] = (
        (lambda x, y: (x + y) % 2),
        (lambda x, y: y % 2),
        (lambda x, y: x % 3),
        (lambda x, y: (x + y) % 3),
        (lambda x, y: (x//3 + y//2) % 2),
        (lambda x, y: x * y % 2 + x * y % 3),
        (lambda x, y: (x * y % 2 + x * y % 3) % 2),
        (lambda x, y: ((x + y) % 2 + x * y % 3) % 2)
    )

    def __init__(self, input_txt: str, savefilepath: str, filename: str, backgcolor: Sequence[int, int, int] = (255, 255, 255), foregcolor: Sequence[int, int, int] = (0, 0, 0), gridshape: str = "square", gridsize: int = 10,  quietzonesize: int = 4,
                 logoimg: Union[str, PWQ_QR_GEN_4] = None, encoding: str = "UTF-8", version: int = None, eclvl: Union[str, PWQ_QR_GEN_4.PWQ_QR_Ecl] = None, mask: int = None, PWQAI_mode: bool = False):
        """
This is PWQ QR Gen 4 — a fully customizable QR code generator supporting all QR versions,
error correction levels, masking patterns, RGB color customization, 16 encoding techniques,
logo embedding, and more.
:param input_txt: The text to encode into the QR code.
:param savefilepath: The directory path where the rendered QR code image will be saved.
:param filename: The name of the output QR code file.
:param backgcolor: Background color of the QR code, as an (R, G, B) tuple. Default is white.
:param foregcolor: Foreground (module) color of the QR code, as an (R, G, B) tuple. Default is black.
:param gridshape: Shape of the modules. Options:
    - Squares: ["square", "default", "None", ""]
    - Circles: ["circle", "round", "oval"]
    Default is "square".
:param gridsize: Pixel size of each module. Affects visual appearance, not QR version.
:param quietzonesize: Size of the quiet zone (border) in module units.
:param logoimg: Logo image to embed at the center of the QR code. Options:
    - Presets: ["instagram", "youtube", "whatsapp", "netflix", "messenger", "paypal", "gmail"]
    - Custom: Provide full file path to a .png image with transparency.
    See cautions above for recommended sizing.
:param version: QR version (1–40), which determines matrix size from 21×21 to 177×177 modules.
:param eclvl: Error correction level. Use `PWQ_QR_GEN_4.PWQ_QR_Ecl.{Level}`:
    - .Low (7%), .Medium (15%), .Quartile (25%), .High (30%)
:param mask: Mask pattern (0–7). Each applies a different module filter. See cautions above.
:param PWQAI_mode: If True, enables automatic selection of optimal version, mask, and encoding.
"""

        # ================ Assignment of Variables ===========================#
        self._minver: int = 1
        self._maxver: int = 40
        self._logoimg = logoimg
        self._bgcolor = backgcolor
        self._fgcolor = foregcolor
        self._savefilepath = savefilepath
        self._filename = filename
        self._gridshape = gridshape
        self._gridsize = gridsize
        self._quietzonesize = quietzonesize
        PWQ_QR_GEN_4._logoimg = logoimg
        self._logoid = PWQ_QR_GEN_4.PWQ_QR_Logo.generate_logo_path()
        if self._logoid is not None:
            self._logoimg_path = os.path.join(r".venv\Lib\site-packages\pwq_qr_gen_4", str(self._logoid)) if type(self._logoid) != tuple else self._logoid[0]
        if not os.path.exists(self._savefilepath): raise FileNotFoundError("Provided File Path does not exist and/or isn't correct!")
        if input_txt is not None: self._input_txt = input_txt
        if input_txt is None: raise PWQAIUnprovidedError(f"User is compelled to provide desired text input data! Provided data: {input_txt} is invalid!")
        segs: list[PWQ_QR_Segmentation] = PWQ_QR_Segmentation.compute_segmentation(self._input_txt, encoding=encoding)

        # ============= Dual-Mode Support & Variable Compute ================#
        self._PWQAI_mode = PWQAI_mode
        # ------- PWQAI mode
        if self._PWQAI_mode:
            pwqversion, num_datacwused = PWQ_QR_GEN_4.PWQ_AI_Mode.pwq_autoversion_selection(segs, self._PWQAI_mode)
            pwqeclvl: PWQ_QR_GEN_4.PWQ_AI_Mode = PWQ_QR_GEN_4.PWQ_AI_Mode.pwq_autoeclvl_booster(num_datacwused, pwqversion)
            self._version = pwqversion
            self._eclvl = pwqeclvl
            self._size = self._version * 4 + 17
            self._modulesmatrix = [[False] * self._size for _ in range(self._size)]
            self._staticmodules = [[False] * self._size for _ in range(self._size)]
            pwqmask: PWQ_QR_GEN_4.PWQ_AI_Mode = PWQ_QR_GEN_4.PWQ_AI_Mode .pwq_automask_selection(self)
            self._modulesmatrix = [[False] * self._size for _ in range(self._size)]
            self._staticmodules = [[False] * self._size for _ in range(self._size)]
            self._mask = pwqmask
        # -------- Manual mode
        elif not self._PWQAI_mode:
            if any(param is None for param in (version, eclvl, mask)): raise PWQAIUnprovidedError("Manual mode requires version, eclvl, and mask valid states to be provided")
            else:
                self._version = version
                self._eclvl = eclvl
                self._size = version * 4 + 17
                self._modulesmatrix = [[False] * self._size for _ in range(self._size)]
                self._staticmodules = [[False] * self._size for _ in range(self._size)]
                self._mask = mask
        elif self._PWQAI_mode is None or type(self._PWQAI_mode) != bool: raise PWQAIUnprovidedError(f"Provided PWQAI Mode is invalid/unprocessable by PWQ QR Gen 4: {self._PWQAI_mode}")
        # ============== Call sequence methods inside of constructor ===========#
        self._bytedatacw = PWQ_QR_GEN_4.create_text_format_object(segs, self._eclvl, self._version, self._mask)
        self.compute_static_patterns()
        finalallcw: bytes = self._compute_ecbits_interleaving(bytearray(self._bytedatacw))
        self.codeword_matrix_placement(finalallcw)
        self.mask_application(self._mask)
        self.compute_format_bchbits(self._mask)
        self.pwqqrgen4_renderer()

    # ========= PWQ QR Gen 4 Rendering ===================================#
    def pwqqrgen4_renderer(self, offsetx: int = 8, offsety: int = 8) -> None:
        """
        This method is a helper function, which "renders" the QR code from a 2D matrix of boolean values
        into any image-related format provided by the user inside of filename parameter. Based on the Pillow
        (PIL) library, loops thru every module and using the bools renders each one of the modules of the QR
        code. Fully supports custom color customization for BOTH the background and foreground (grid color).
        Features custom gridshape parameter, allowing the user to specify the shape of the grid, either squa-
        res or circles. Permits the user to adjust the grid and quiet zone (border) size in px format. Afterwar-
        ds saves the QR code into specified by the user location on their local disk drive.
        """
        total = (self._size + self._quietzonesize * 2) * self._gridsize
        img = Image.new("RGB", (total, total), self._bgcolor)
        draw = ImageDraw.Draw(img)
        for y in range(self._size):
            for x in range(self._size):
                if self._modulesmatrix[y][x]:
                    left = (x + self._quietzonesize) * self._gridsize
                    top = (y + self._quietzonesize) * self._gridsize
                    if self._gridshape.lower() in ["square", "default", "None",""]: draw.rectangle([left, top, left + self._gridsize - 1, top + self._gridsize - 1], fill=self._fgcolor)
                    if self._gridshape.lower() in ["circle", "round", "oval"]: draw.circle([left, top, left + self._gridsize - 1, top + self._gridsize - 1], radius=self._gridsize//2, fill=self._fgcolor)
        # ======= Logo Placement =============================================#
        if type(self._logoid) == tuple:
            print("custom logo!")
            logoimg = Image.open(self._logoimg_path).convert("RGBA").resize((147, 147), Image.LANCZOS)
            datas = logoimg.getdata()
            target = (192, 192, 192)
            tolerance = 5
            def is_light_gray(r, g, b, tol=10): return all(abs(c - t) <= tol for c, t in zip((r, g, b), target))
            new_data = []
            for r, g, b, a in datas:
                if is_light_gray(r, g, b, tolerance): new_data.append((255, 255, 255, 0))  # fully transparent
                else: new_data.append((r, g, b, a))
            logoimg.putdata(new_data)
        if self._logoid is not None:
            logoimg = Image.open(self._logoimg_path).convert("RGBA")
            datas = logoimg.getdata()
            target = (192, 192, 192)
            tolerance = 5
            def is_light_gray(r, g, b, tol=10): return all(abs(c - t) <= tol for c, t in zip((r, g, b), target))
            new_data = []
            for r, g, b, a in datas:
                if is_light_gray(r, g, b, tolerance):new_data.append((255, 255, 255, 0))  # fully transparent
                else:new_data.append((r, g, b, a))
            logoimg.putdata(new_data)
            logosize = int(total * 0.175) # 20% of the total size of qr code (approx.)
            curlogoaspect: int = int(logoimg.width // logoimg.height) if logoimg.width >= logoimg.height else int(logoimg.height // logoimg.width)
            logoimage = logoimg.resize((logosize, int(logosize / curlogoaspect)), Image.LANCZOS)
            img = img.convert("RGBA")
            pos = (total // 2 - logoimage.width//2, total // 2 - logoimage.width//2)
            img.paste(logoimage, pos, logoimage)
        img.save(os.path.join(self._savefilepath, self._filename))

    # ========= Mask Application and Penalization =============================#
    def mask_application(self, mask: int) -> None:
        """
        Applies provided mask to the 2D matrix of boolean values. Utilises Logical XOR,
        to fuse the current state of the matrix with the mask rules. The provided mask
        MUST be in range of 0 through 7, else ValueError is to be occured.
        """
        if not (0 <= mask <= 7): raise ValueError("Mask is out of range and/or in invalid state!")
        masker: collections.abc.Callable[[int,int],int] = PWQ_QR_GEN_4._maskpatterns[mask]
        for y in range(self._size):
            for x in range(self._size): self._modulesmatrix[y][x] ^= (masker(x, y) == 0) and (not self._staticmodules[y][x])

    def _get_penalty_score_v2(self, mask: int) -> int:
        """
        This method computes the penalty score for a given mask applied to the QR code.
        Utilizes all 4 ISO-specified rules, alongside it's correlating penalty score for each
        rule. Returns the total penalty score for given mask.
        """
        penscore: int = 0
        matrix = self._modulesmatrix
        # Rule #1 ---------
        for y in range(self._size):
            run_color = matrix[y][0]
            run_length = 1
            for x in range(1, self._size):
                if matrix[y][x] == run_color: run_length += 1
                else:
                    if run_length >= 5: penscore += 3 + (run_length - 5)
                    run_color = matrix[y][x]
                    run_length = 1
            if run_length >= 5: penscore += 3 + (run_length - 5)
        for x in range(self._size):
            run_color = matrix[0][x]
            run_length = 1
            for y in range(1, self._size):
                if matrix[y][x] == run_color: run_length += 1
                else:
                    if run_length >= 5: penscore += 3 + (run_length - 5)
                    run_color = matrix[y][x]
                    run_length = 1
            if run_length >= 5: penscore += 3 + (run_length - 5)
        # Rule #2 -------
        for y in range(0, self._size - 1):
            for x in range(0, self._size - 1):
                isdark: bool = matrix[y][x]
                if (matrix[y][x + 1] == isdark and matrix[y + 1][x] == isdark and matrix[y + 1][x + 1] == isdark): penscore += 3
        # Rule #3 -------
        pattern = [True, False, True, True, True, False, True, False, False, False, False]
        inv_pattern = [not b for b in pattern]
        for y in range(self._size):
            for x in range(self._size - 10):
                segment = matrix[y][x:x + 11]
                if segment == pattern or segment == inv_pattern: penscore += 40
        for x in range(self._size):
            for y in range(self._size - 10):
                segment = [matrix[y + k][x] for k in range(11)]
                if segment == pattern or segment == inv_pattern: penscore += 40
        # Rule #4 -------
        dark: int = sum((1 if cell else 0) for row in matrix for cell in row)
        total: int = self._size ** 2  # Note that size is odd, so dark/total != 1/2
        darkratio: float = (dark * 100)/total
        k: int = (abs(dark * 20 - total * 10) + total - 1) // total - 1
        assert 0 <= k <= 9
        penscore += k * PWQ_QR_GEN_4._pencount_4
        return penscore

    # ======== Codeword Matrix-Placement ==================================#
    def codeword_matrix_placement(self, data: bytes) -> None:
        """
        This method simply places the stream of bytes (EC + data) following the famous zig-zag
        pattern. Utilizes bit-shifting flooring advantage to index each byte into its correct index
        of the final matrix. Doesn't return any object, solely fills the 2D matrix with boolean values.
        """
        assert len(data) == PWQ_QR_GEN_4._get_numdata_modules(self._version) // 8
        i: int = 0  # Bit index into the data
        # Do the funny zigzag scan
        for right in range(self._size - 1, 0, -2):  # Index of right column in each column pair
            if right <= 6:
                right -= 1
            for vert in range(self._size):  # Vertical counter
                for j in range(2):
                    x: int = right - j  # Actual x coordinate
                    upward: bool = (right + 1) & 2 == 0
                    y: int = (self._size - 1 - vert) if upward else vert  # Actual y coordinate
                    if (not self._staticmodules[y][x]) and (i < len(data) * 8):
                        getbit = _get_sequence_bit(data[i >> 3], 7 - (i & 7))
                        self._modulesmatrix[y][x] = getbit
                        i += 1
                # If this QR Code has any remainder bits (0 to 7), they were assigned as
                # 0/false/light by the constructor and are left unchanged by this method
        assert i == len(data) * 8

    # ======== Static Pattern Calculation ====================================#
    def _set_module(self, x: int, y: int, isdark: bool) -> None:
        """
        This method focuses on both filling the 2D matrix with static pattern bits,
        as well as filling the static modules 2D matrix, which later is utilized in bit
        placement method, to avoid overriding patterns by data.
        """
        assert type(isdark) is bool and 0 <= x < self._size and 0 <= y < self._size
        self._modulesmatrix[y][x] = isdark
        self._staticmodules[y][x] = True

    def compute_finder_pattern(self, centerx: int, centery: int) -> None:
        """
        This function writes the bits/pixels that form a finder pattern. Works by
        looping from -4 to 5, starting from the center pixel, utilizing Chebyschev
        Distance or Infinity Norm to skip the white rings.
        """
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                ocx, ocy = centerx + dx, centery + dy
                if (0 <= ocx < self._size) and (0 <= ocy < self._size):
                    Chebyshevdist: bool = max(abs(dx), abs(dy)) not in (2, 4)
                    self._set_module(ocx, ocy, Chebyshevdist)

    def compute_alignment_pattern(self, centerx: int, centery: int) -> None:
        """
        This function is structurly equivalent to finder pattern creator, nevertheless
        differs by range of loop. The alignment pattern is 5x5, while the finder one
        is 7x7, thus the alignment loop range is only from -2 to 3. Both utilize Cheby-
        shev distance to skip white rings.
        """
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                ocx, ocy = centerx + dx, centery + dy
                if (0 <= ocx < self._size) and (0 <= ocy < self._size):
                    Chebyshevdist: bool = max(abs(dx), abs(dy)) != 1
                    self._set_module(ocx, ocy, Chebyshevdist)

    def compute_format_bchbits(self, mask: int) -> None:
        """
        This function despite computing the BCH-encoded format bits, it also writes
        the bits to both the matrices. It firstly OR's the format bits and mask,
        makes defensive copy, then loops thru the remainder/generator length (10),
        at the end of the loop the variable rembits will have EXACTLY 10 bits, which
        later are OR'd with the defensive copy and OR'd 15-bit format bits are lastly
        XOR'd with a Format Bit Mask (Hex: 0x5412).
        Once the 15-bit format string is ready, it writes both copies, one 15-bit to
        the top-left, one 7-bit on the bottom alongside 8-bit top-right one.
        """

        datafbmsk: int = self._eclvl.formatbits << 3 | mask
        rembits: int = datafbmsk # Defensive copy
        for _ in range(10):
            rembits = (rembits << 1) ^ ((rembits >> 9) * 0x537)
        bchbits: int =  (datafbmsk << 10 | rembits) ^ 0x5412
        assert bchbits >> 15 == 0
        # ----------- First Copy (15-bits top-left) -------------------------------#
        for i in range(0, 6):
            self._set_module(8, i, _get_sequence_bit(bchbits, i))
        self._set_module(8, 7, _get_sequence_bit(bchbits, 6))
        self._set_module(8, 8, _get_sequence_bit(bchbits, 7))
        self._set_module(7, 8, _get_sequence_bit(bchbits, 8))
        for i in range(9, 15):
            self._set_module(14-i, 8, _get_sequence_bit(bchbits, i))
        # ----------- Second Copy (7-bit bottom-left | 8-bit top-right) ----------#
        for i in range(0, 8):
            self._set_module(self._size-1-i, 8, _get_sequence_bit(bchbits, i))
        for i in range(8, 15):
            self._set_module(8, self._size - 15 + i, _get_sequence_bit(bchbits, i))
        self._set_module(8, self._size - 8, True)

    def compute_version_info_bits(self) -> None:
        """
        This function; similarly to the BCH-bits, computes remainder bits for version
        info (version 7+ only). Similar structure to format bits method, yet the final
        string of version info is 18-bits long, since the version itself is a 6-bit value.
        The generator here is 12-bits, thus the loop range is equal. After the loop,
        the variable rember should be EXACTLY 12-bits long. Afterwards it gets
        OR'd with the actual 6-bit version to get the final 18-bits, and does NOT
        utilize masking, unlike format bits. Afterwards it places the bits in the cor-
        rect spots throughout the QR code.
        """
        if self._version < 7: return
        remver: int = self._version # 6-bit value
        for _ in range(12): remver = (remver << 1) ^ ((remver >> 11) * 0x1F25) # remver is 12-bit remainder bits
        verbits: int = self._version << 12 | remver  # XOR'd give 18-bit version info bit
        assert verbits >> 18 == 0
        for i in range(18):
            self._set_module(self._size-11+i%3, i//3, _get_sequence_bit(verbits, i))
            self._set_module(i//3, self._size-11+i%3 ,_get_sequence_bit(verbits, i))

    def compute_static_patterns(self) -> None:
        """
        This method combines every pattern-writer helper method together. Writes
        both vertical and horizontal timing patterns, draws all 3 finder patterns,
        utilizes alignment pattern position generator to get all positions wherein the
        alignment pattern(s) are being placed. Afterwards simply calls the format
        bits compute method with a dummy mask which later gets overriden in the
        constructor, and calls the version info compute method.
        """
        # ===== Timing Pattern ===============================================#
        for i in range(self._size):
            self._set_module(6, i, i % 2 == 0)
            self._set_module(i, 6, i % 2 == 0)
        # ====== Finder Pattern ==============================================#
        self.compute_finder_pattern(3, 3)
        self.compute_finder_pattern(self._size-4, 3)
        self.compute_finder_pattern(3, self._size-4)
        # ===== Alignment Pattern(s) =========================================#
        alignpatposs: list[int] = self._get_alignment_pattern_positions()
        numalignpat: int = len(alignpatposs)
        bypassing: Sequence[tuple[int, int]] = ((0,0), (0, numalignpat-1),(numalignpat-1, 0))
        for apx in range(numalignpat):
            for apy in range(numalignpat):
                if (apx, apy) not in bypassing:
                    self.compute_alignment_pattern(alignpatposs[apx], alignpatposs[apy])
        # ===== Format Bits ==================================================#
        self.compute_format_bchbits(0) # Dummy mask, further overwritten
        # ====== Version Info Bits (Ver +7) ===================================#
        self.compute_version_info_bits()

    # ======== Error Correction Bit Handling =================================#
    @staticmethod
    def _compute_gf256_multiplication(x: int, y: int) -> int:
        """This function returns the product of the two given field elements modulo GF(2^8/0x11D). Compute GF 8-bit
        multiplication without the need for ANY log/antilog table.

         Algorithm adapted from Project Nayuki's QR Code Generator.
         """
        if (x >> 8 != 0) or (y >> 8 != 0): raise ValueError("Byte out of range")
        z: int = 0
        for i in reversed(range(8)): z = (z << 1) ^ ((z >> 7) * 0x11D) ^ ((y >> i) & 1) * x
        assert z >> 8 == 0
        return z

    @staticmethod
    def _compute_rs_ecgenerator(degree: int) -> bytes:
        """
        This function creates the generator polynomial with degree of the total length
        of EC bits. Works by stacking GF256 multiplication between the generator
        at index j and current root value, and accumulating the product at index j of
        the generator. Afterwards for every j + 1 value that's less than degree,
        we xor the generator's index j value, with value at j + 1. Lastly after every
        first dim iteration of degree, rootval is multiplied by 0x02, or simply doubled.
        The final generator polynomial consists of a bytearray simulating a polynomial,
        with degree of EC bits.
        """
        if not (1 <= degree <= 255): raise ValueError("Degree value is out of range and/or in invalid state!")
        generator = bytearray([0] * (degree-1) + [1])
        rootval: int = 1
        for _ in range(degree):
            for j in range(degree):
                generator[j] = PWQ_QR_GEN_4._compute_gf256_multiplication(generator[j], rootval)
                if j + 1 < degree: generator[j] ^= generator[j+1]
            rootval = PWQ_QR_GEN_4._compute_gf256_multiplication(rootval, 0x02)
        return generator

    @staticmethod
    def _compute_rs_rembits(data: bytes, generator: bytes) -> bytes:
        """
        This function computes the actual "division" between the data polynomial and
        the generator one. The division is actually a XOR between the rembits at index
        i and GF256 multiplication of current coefficient and current factor. The coef-
        ficient is really just the value stored inside of generator bytearray, while the
        factor is the XOR between current value in data polynomial and rembits without
        it's index 0. Returns the remainder bits in form of bytes, and length of EC bits,
        provided in generator compute method.
        """
        rembits = bytearray([0] * len(generator))
        for bit in data:
            factor: int =  bit ^ rembits.pop(0)
            rembits.append(0)
            for (i, coef) in enumerate(generator): rembits[i] ^= PWQ_QR_GEN_4._compute_gf256_multiplication(coef, factor)
        return rembits

    def _compute_ecbits_interleaving(self, data: bytearray) -> bytes:
        # -------- Prepare data -----------------------------------------------------#
        version: int = self._version
        assert len(data) == PWQ_QR_GEN_4._get_num_datacw(version, self._eclvl)
        numecblocks: int = PWQ_QR_GEN_4._num_ecblocks[self._eclvl.ordidx][version]
        lenecblock: int = PWQ_QR_GEN_4._eccw_per_block[self._eclvl.ordidx][version]
        allcwcount: int = PWQ_QR_GEN_4._get_numdata_modules(version) // 8
        shortblockcount: int = numecblocks - allcwcount % numecblocks
        shortblocklen: int = allcwcount // numecblocks
        # ------------ Compute EC bits & Interleave -------------------------------#
        blocks: list[bytes] = []
        rsdivgen: bytes = PWQ_QR_GEN_4._compute_rs_ecgenerator(lenecblock)
        datprocsd: int = 0
        for block in range(numecblocks):
            curdat: bytearray = data[datprocsd:datprocsd + shortblocklen - lenecblock + (0 if block < shortblockcount else 1)]
            datprocsd += len(curdat)
            ecrembits: bytes = PWQ_QR_GEN_4._compute_rs_rembits(curdat, rsdivgen)
            if block < shortblockcount: curdat.append(0)
            blocks.append(curdat+ecrembits)
        assert datprocsd == len(data)
        ecbits = bytearray()
        for byte in range(len(blocks[0])):
            for (i, blk) in enumerate(blocks):
                if (byte != shortblocklen - lenecblock) or (i >= shortblockcount): ecbits.append(blk[byte])
        assert len(ecbits) == allcwcount
        return ecbits

    # ======== Accessor Methods ===========================================#
    def _get_version(self) -> int: return self._version # Returns QR Code's version in range from 1 to 40
    def _get_size(self) -> int: return self._size # Returns QR Code's size, dependant on version from range 21 to 177
    def _get_error_correction_level(self) -> PWQ_QR_GEN_4.PWQ_QR_Ecl: return self._eclvl # Returns QR Code's Error Correction Level
    def _get_mask(self) -> int: return self._mask # Returns QR Code's Mask (0-7)
    def _get_module(self, x: int, y: int) -> bool: return (0 <= x <= self._size) and (0 <= y <= self._size) and  self._modulesmatrix[y][x] # Returns True if the module at y,x is set to True (Light) else False (Dark)

    def _get_alignment_pattern_positions(self) -> list[int]:
        """
        This method generator alignment pattern(s) position(s) based on the selected
        version. Utilizes a special algorithm that generates both, the number of align-
        ment patterns, as well as their correlating positions. Returns a list of integers.

        Algorithm adapted from Project Nayuki's QR Code Generator.
        """
        if self._version == 1: return []
        else:
            numalignpat: int = self._version // 7 + 2
            spacing: int = (self._version * 8 + numalignpat * 3 + 5) // (numalignpat * 4 - 4) * 2
            alignpatposs: list[int] = [(self._size - 7 - alignpat * spacing) for alignpat in range(numalignpat-1)] + [6]
            return list(reversed(alignpatposs))

    @staticmethod # Functional
    def _get_numdata_modules(ver: int) -> int:
        """ This function generates the total number of placeable modules within a QR code.
         The output ranges from [208, 29648] according to trustable sources. This includes
         remainder bits, thus might not contain full bytes. Credits to Nayuki."""
        if not (PWQ_QR_GEN_4._minver <= ver <= PWQ_QR_GEN_4._maxver): raise ValueError("Version number is out of range!")
        datamodules: int = (16 * ver + 128) * ver + 64
        if ver >= 2:
            numalign: int = ver // 7 + 2
            datamodules -= (25 * numalign - 10) * numalign - 55
            if ver >= 7:
                datamodules -= 36
        assert 208 <= datamodules <= 29648
        return datamodules

    @staticmethod # Functional
    def _get_num_datacw(ver: int, eclvl: PWQ_QR_GEN_4.PWQ_QR_Ecl) -> int:
        """  This method computes the total number of data codewords utiliized in a
        QR code, taking aside the EC bits. Works by taking all of the data modules in
        QR code version, and substracting the product of ec cw (codewords) per block
        and number of ec blocks for a given version. """
        return PWQ_QR_GEN_4._get_numdata_modules(ver) // 8 - PWQ_QR_GEN_4._eccw_per_block[eclvl.ordidx][ver] * PWQ_QR_GEN_4._num_ecblocks[eclvl.ordidx][ver]

    # ================== Class object dedicated to automatic adjustment and selection of variables and QR code parameters ================================================================================================
    class PWQ_AI_Mode():
        _pwqaimode: bool

        def __init__(self, pwqaimode: bool):
            self._pwqaimode = pwqaimode

        @staticmethod
        def pwq_autoversion_selection(segs, pwqaimode, minver: int = 1, maxver: int = 40):
            """
            This method loops through all versions, and outputs the minimal version for provided
            input data. Works by simply comparing the total capacity for current version, with
            the necessary minimum capacity to store the given input text. Once found the loop
            breaks. If neither of the 40 versions fit the input data, DataTooLongError shall
            be raised. Returns the used data bits number and the selected version.

            Partially adapted from Project Nayuki's QR Code Generator — specifically the
            segment division logic and structural approach.

            """
            if not pwqaimode: raise PWQAIUnprovidedError("PWQAI Mode has not been turned on!")
            eclvl: PWQ_QR_GEN_4.PWQ_QR_Ecl = PWQ_QR_GEN_4.PWQ_QR_Ecl._Low
            selver: int = -1
            for ver in range(minver, maxver + 1):
                num_datacwmax: int = PWQ_QR_GEN_4._get_num_datacw(ver, eclvl) * 8
                num_datacwused: Optional[int] = PWQ_QR_Segmentation._get_encode_bits(segs, ver)
                if (num_datacwused is not None) and (num_datacwused <= num_datacwmax):
                    selver = ver
                    break
                if ver >= maxver:
                    msg: str = "Segment is not in valid range to encode!"
                    if num_datacwused is not None:
                        msg = f"The length of data provided: {num_datacwused}, nevertheless the maximum capacity at given version/EC level is: {num_datacwmax}"
                    raise DataTooLongError(msg)
            assert num_datacwused is not None
            return selver, num_datacwused

        @staticmethod
        def pwq_autoeclvl_booster(num_datacwused: int, version: int):
            """
            This function loops through all 3 higher levels of EC, to find out if any of them
            are suitable to fit inside of the QR code while assuring space left for data. If
            neither of the higher levels fit, seleclvl is set to Low as fallback. If any of them
            do fit, the seleclvl is set to the neweclvl, boosting the Error Correction. Returns
            selected Error Correction Level.

            Partially adapted from Project Nayuki's QR Code Generator — specifically the
            General Concept
            """
            seleclvl: PWQ_QR_GEN_4.PWQ_QR_Ecl = PWQ_QR_GEN_4.PWQ_QR_Ecl._Low
            for neweclvl in (PWQ_QR_GEN_4.PWQ_QR_Ecl._Medium, PWQ_QR_GEN_4.PWQ_QR_Ecl._Quartile, PWQ_QR_GEN_4.PWQ_QR_Ecl._High):
                if num_datacwused <= PWQ_QR_GEN_4._get_num_datacw(version, neweclvl) * 8: seleclvl = neweclvl
            return seleclvl

        @staticmethod
        def pwq_automask_selection(self) -> int:
            """
            This method automatically chooses the most suitable mask for current QR code.
            Works by setting rules, and penalizing the mask's filter if broken. The mask with
            minimal penalty score, wins, thus getting returned and selected.
            """
            msk: int = -1
            if msk == -1:
                minpen: int = 1 << 32
                for candmsk in range(8):
                    self.mask_application(candmsk)
                    self.compute_format_bchbits(candmsk)
                    penscore: int = self._get_penalty_score_v2(candmsk)
                    if penscore < minpen:
                        msk = candmsk
                        minpen = penscore
                    self.mask_application(candmsk)
            assert 0 <= msk <= 7
            return msk

    # ================== Class object dedicated to logo scaling & placement =============================================================================================================================================
    class PWQ_QR_Logo():
        def __init__(self):
            pass
        @staticmethod
        def generate_logo_path():
            """
            This function checks which type of logo the user desires to include in the
            QR code. If set to any of the predefined ones such as: "instagram" or
            "netflix" that is the logo which is to appear on the center of the QR Code.
            If the user sets logoimg to None, False or "", then no logo will appear.
            And lastly if the user provides the path corresponding to a custom image
            on their local disk drive, the last of the option will return true, and further
            will be decoded specifically to utilise the custom logo.
            """
            if PWQ_QR_GEN_4._logoimg.lower() in ["instagram", "insta", "inst"]: return "Instagram_Logo.png"
            elif PWQ_QR_GEN_4._logoimg.lower() in ["youtube", "yt"]: return "Youtube_Logo.png"
            elif PWQ_QR_GEN_4._logoimg.lower() in ["whatsapp"]: return "Whatsapp_Logo.png"
            elif PWQ_QR_GEN_4._logoimg.lower() in ["paypal"]: return "Paypal_Logo.png"
            elif PWQ_QR_GEN_4._logoimg.lower() in ["gmail", "googlemail"]: return "Gmail_Logo.png"
            elif PWQ_QR_GEN_4._logoimg.lower() in ["messenger", "mess"]: return "Messenger_Logo.png"
            elif PWQ_QR_GEN_4._logoimg.lower() in ["netflix"]: return "Netflix_Logo.png"
            elif PWQ_QR_GEN_4._logoimg.lower() in ["none", "", "No", "false"]: return None
            else: return (PWQ_QR_GEN_4._logoimg, "custom")

    # =================== Class object dedicated to Error Correction Levels ============================================================================================================================================
    class PWQ_QR_Ecl():
        """
        This class is entirely dedicated to simply store data about Error Correction
        Levels. Creates public constants outisde of the class to make them accesable
        much easier throughout the rest of the code.

        Algorithm adapted from Project Nayuki's QR Code Generator.
        """
        ordidx: int
        formatbits: int
        def __init__(self,  ordidx: int, formatbits: int) -> None:
            self.ordidx = ordidx
            self.formatbits = formatbits

        # ======= Placeholders Constants =====================================#
        _Low: PWQ_QR_GEN_4.PWQ_QR_Ecl
        _Medium: PWQ_QR_GEN_4.PWQ_QR_Ecl
        _Quartile: PWQ_QR_GEN_4.PWQ_QR_Ecl
        _High: PWQ_QR_GEN_4.PWQ_QR_Ecl

    # ============= Assign Values to each EC level ===========================#
    PWQ_QR_Ecl._Low = PWQ_QR_Ecl(0, 1)
    PWQ_QR_Ecl._Medium = PWQ_QR_Ecl(1, 0)
    PWQ_QR_Ecl._Quartile = PWQ_QR_Ecl(2, 3)
    PWQ_QR_Ecl._High = PWQ_QR_Ecl(3, 2)

# ============================ Class object dedicated to converting segments & preparation of input data ================================================================================================================
class PWQ_QR_Segmentation():
    """
    This class is entirely dedicated to converting segments into corresponding modes,
    create class object containing correlating self attributes to selected mode. Prepa-
    res input data for further computation and utilization.

    Partially adapted from Project Nayuki's QR Code Generator — specifically the
    segment division logic and structural approach.

    """
    # =========== Segment Constructor Methods ============================#
    @staticmethod
    def make_seg_bytes(data: Union[bytes, Sequence[int]]) -> PWQ_QR_Segmentation:
        """
        This method is utilized when input data is filtered as bytes mode. Constructs bits inside of
        _PWQ_Bit_Buffer class, and converts them into bytes. Returns a class object, which initia-
        lizes the self attributes methods and variables correlated to selected mode.
        """
        pwqbb = _PWQ_Bit_Buffer()
        for bit in data: pwqbb._construct_bit(bit, 1 << 3)
        return PWQ_QR_Segmentation(PWQ_QR_Segmentation.PWQ_QR_Mode._Byte, len(data), pwqbb)

    @staticmethod
    def make_seg_numeric(digits: str) -> PWQ_QR_Segmentation:
        """
        This method is utilized when input data is filtered as numeric mode. Consumes
        up to 3 digits per iteration (most efficient value), constructs the digit into
        a list inside of _PWQ_Bit_Buffer class, and loops through every digit.
        Returns a class object, which initializes the self attributes methods and
        variables correlated to selected mode.
        """
        if not PWQ_QR_Segmentation.is_numeric(digits): raise ValueError("Given string contains non-numeric characters!")
        pwqbb = _PWQ_Bit_Buffer()
        itr: int = 0
        digitsperiteration: int = 3
        while itr < len(digits):
            n: int = min(len(digits) - itr, digitsperiteration)
            pwqbb._construct_bit(int(digits[itr: itr + n]), n * digitsperiteration + 1)
            itr += n
        return PWQ_QR_Segmentation(PWQ_QR_Segmentation.PWQ_QR_Mode._Numeric, len(digits), pwqbb)

    @staticmethod
    def make_seg_alphanumeric(text: str) -> PWQ_QR_Segmentation:
        """
        This method is utilized when input data is filtered as alphanumeric mode.
        Utilizes a predefined lookup table to convert 2 characters per iteration,
        converts these 2 characters, adds them together and contructors them
        in 11-bit integer values. Returns a class object, which initializes the self
        attributes methods and variables correlated to selected mode.
        """
        if not PWQ_QR_Segmentation.is_alphanumeric(text): raise ValueError("Given text contains unencodable characters in alphanumeric mode!")
        pwqbb = _PWQ_Bit_Buffer()
        chunksize: int = 2
        for i in range(0, len(text)-1, chunksize):
            current: int = PWQ_QR_Segmentation._AlphaNumeric_Encoding_Table[text[i]] * 45
            current += PWQ_QR_Segmentation._AlphaNumeric_Encoding_Table[text[i + 1]]
            pwqbb._construct_bit(current, 11)
        if  len(text) % 2 > 0:
            pwqbb._construct_bit(PWQ_QR_Segmentation._AlphaNumeric_Encoding_Table[text[-1]], 6)
        return PWQ_QR_Segmentation(PWQ_QR_Segmentation.PWQ_QR_Mode._Alphanumeric, len(text), pwqbb)

    @staticmethod
    def make_seg_eci(value: int) -> PWQ_QR_Segmentation:
        """
        Rarely used ECI: Extended Channel Interpretation. Requires the use of
        bytes mode conversion, and special encoding techniques. Returns a class
        object, which initializes the self attributes methods and variables correlated
        to selected mode.
        """
        pwqbb = _PWQ_Bit_Buffer()
        if value < 0: raise ValueError("ECI Assignment value is out of range!")
        elif value < (1 << 7): pwqbb._construct_bit(value, 1 << 3)
        elif value < (1 << 14):
            pwqbb._construct_bit(0b10, 1 << 1)
            pwqbb._construct_bit(value, 14)
        elif value < 1000000:
            pwqbb._construct_bit(0b110, 3)
            pwqbb._construct_bit(value, 21)
        else: raise ValueError("ECI Assignment value is out of range!")
        return PWQ_QR_Segmentation(PWQ_QR_Segmentation.PWQ_QR_Mode._ECI, 0, pwqbb)

    @staticmethod
    def compute_segmentation(text: str, encoding: str = "UTF-8") -> list[PWQ_QR_Segmentation]:
        """
        This function filters the input data based on its mode, and converts the data into segments,
        while adding the converted characters/bits into _PWQ_Bit_Buffer class' self attribute.
        Returns list of segments which are class objects with self attribute adjusted to filtered mode.

        Partially adapted from Project Nayuki's QR Code Generator — specifically the
        concept.
        """
        if text == "":
            return []
        elif PWQ_QR_Segmentation.is_numeric(text):
            return [PWQ_QR_Segmentation.make_seg_numeric(text)]
        elif PWQ_QR_Segmentation.is_alphanumeric(text):
            return [PWQ_QR_Segmentation.make_seg_alphanumeric(text)]
        elif PWQ_QR_Segmentation.is_bytes(text):
            return [PWQ_QR_Segmentation.make_seg_bytes(text.encode(encoding if encoding.upper() in PWQ_QR_Segmentation._ECI_Encoding_Table else "UTF-8"))] # Use UTF-8 encoding as fallback for unsupported user-provided encoding
        else:
            if encoding.upper() in PWQ_QR_Segmentation._ECI_Encoding_Table:
                ecival: int = PWQ_QR_Segmentation._ECI_Encoding_Table[encoding.upper()]
                eciseg: PWQ_QR_Segmentation = PWQ_QR_Segmentation.make_seg_eci(ecival)
                byteseg: list[PWQ_QR_Segmentation] = PWQ_QR_Segmentation.make_seg_bytes(text.encode(encoding))
                return [eciseg, byteseg]
            else: raise ECIEncodingError(f"PWQ QR Gen 4 does not support provided encoding technique: {encoding}")

    # ========= Investigator Methods ======================================#
    @staticmethod
    def is_numeric(text: str) -> bool: return PWQ_QR_Segmentation._Numeric_REGEX.fullmatch(text) is not None
    @staticmethod
    def is_alphanumeric(text: str) -> bool: return PWQ_QR_Segmentation._AlphaNumeric_REGEX.fullmatch(text) is not None
    @staticmethod
    def is_bytes(text: str) -> bool: return not (PWQ_QR_Segmentation.is_numeric(text) or PWQ_QR_Segmentation.is_alphanumeric(text))

    # ========== Public Constants ===========================================#
    _Numeric_REGEX: re.Pattern[str] = re.compile(r"[0-9]*") # Numeric Mode Searcher-Helper
    _AlphaNumeric_REGEX: re.Pattern[str] = re.compile(r"[A-Z0-9 $%*+./:-]*") # Alphanumeric Mode Searcher-Helper
    _AlphaNumeric_Encoding_Table: dict[str, int] = {char: i for (i, char) in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")} # Alphanumeric encoding table
    _ECI_Encoding_Table: dict[str, int] ={ # Table with 16 diffrent encoding techniques
    "ISO-8859-1": 3,       # Western European
    "ISO-8859-2": 4,       # Central European
    "ISO-8859-3": 5,       # South European
    "ISO-8859-4": 6,       # North European
    "ISO-8859-5": 7,       # Cyrillic
    "ISO-8859-6": 8,       # Arabic
    "ISO-8859-7": 9,       # Greek
    "ISO-8859-8": 10,      # Hebrew
    "ISO-8859-9": 11,      # Turkish
    "ISO-8859-13": 15,     # Baltic
    "ISO-8859-15": 17,     # Western European (Euro)
    "Shift_JIS": 20,       # Japanese
    "UTF-8": 26,           # Unicode (most common)
    "UTF-16BE": 28,        # Unicode Big Endian
    "UTF-16LE": 29,        # Unicode Little Endian
    "Windows-1252": 21     # Microsoft Western European (not officially in QR spec, but widely used)
    }

    # =========== Placeholder type hints =====================================#
    _mode: PWQ_QR_Segmentation.PWQ_QR_Mode
    _numchars: int
    _bitdata: Sequence[int]

    def __init__(self, mode: PWQ_QR_Segmentation.PWQ_QR_Mode, numchars: int, bitdata: Sequence[int]) -> None:
        if numchars < 0: # If numchars is less than 0 (invalid)
            raise ValueError # Raise ValueError
        self._mode = mode
        self._numchars = numchars
        self._bitdata = list(bitdata) # Create a Defensive Copy

    # ============= Accessor Methods ================================#
    def _get_mode(self) -> PWQ_QR_Segmentation.PWQ_QR_Mode: return self._mode
    def _get_numchars(self) -> int: return self._numchars
    def _get_bitdata(self) -> list[int]: return list(self._bitdata)

    @staticmethod
    def _get_encode_bits(segs: Sequence[PWQ_QR_Segmentation], version: int) -> Optional[int]:
        """  Calculate the number of bits needed to encode the given segments at given version.
         Returns a positive number if successful else None if segment has too many characters
         to fit its length field. Essentially 4-bit mode indicator, character count bits & length of
         actual data. """
        encodebits: int = 0
        for segment in segs:
            sebits: int = segment._get_mode()._get_num_charcount_bits(version)
            if segment._get_numchars() >= (1 << sebits): return None
            encodebits += (
                4 + # Mode indicator bits
                sebits + # character count
                len(segment._bitdata) # length of actual data
            )
        return encodebits

    # ============= Class object dedicated to mode indicator, character count and structure for different version and mode ranges ==========================================================================================
    class PWQ_QR_Mode():
        """ Description of mode indicator bits and character counts for different modes and versions. """

        _modebits: int # Mode Indicator 4-bit val
        _charcounts = tuple[int, int, int] # Number of character count bits for three different version ranges

        def __init__(self, modebits: int, charcounts: tuple[int, int, int]):
            self._modebits = modebits # 4-Bit mode indicator
            self._charcounts = charcounts # number of character count for different modes and versions

        # ============= Accessor Methods ================================#
        def _get_mode_bits(self) -> int: return self._modebits # Simply returns the 4-bit value
        def _get_num_charcount_bits(self, version: int) -> int: return self._charcounts[(version + 7) // 17]  # This function returns the correct character counts for 3 versions ranges: 1-9 -> Index = 0, 10-26 -> Index = 1, 27-40 -> Index = 2

        # Mode placeholders, simply type hints ================================
        _Numeric: PWQ_QR_Segmentation.PWQ_QR_Mode
        _Alphanumeric: PWQ_QR_Segmentation.PWQ_QR_Mode
        _Byte: PWQ_QR_Segmentation.PWQ_QR_Mode
        _Kanji: PWQ_QR_Segmentation.PWQ_QR_Mode
        _ECI: PWQ_QR_Segmentation.PWQ_QR_Mode

     # Different mode bits and character counts for diffrent modes, and versions
    PWQ_QR_Mode._Numeric = PWQ_QR_Mode(0x1, (10,12,14))
    PWQ_QR_Mode._Alphanumeric = PWQ_QR_Mode(0x2, (9, 11, 13))
    PWQ_QR_Mode._Byte = PWQ_QR_Mode(0x4, (8, 16, 16))
    PWQ_QR_Mode._Kanji = PWQ_QR_Mode(0x8, (8, 10, 12))
    PWQ_QR_Mode._ECI = PWQ_QR_Mode(0x7, (0, 0, 0))

# ====================== Class object dedicated to bit construction and storage =========================================================================================================================================
class _PWQ_Bit_Buffer(list[int]):
    def _construct_bit(self, bit_val: int, num_bit_p: int = None) -> None:
        """
        Helper function, that contstruct a bit appending it to self attribute as "buffer".
        Either the user provides the desired length of bits, or if num_bit_p is left alone,
        its initially set to None, making the program choose the smallest amount of bits.
        """
        num_bit = num_bit_p if num_bit_p is not None else len(str(format(bit_val, '01b'))) # Check whether to auto-choose bit number, or the user has provided one
        if num_bit is None or num_bit < 0 or not (0 <= bit_val < 2 ** num_bit): # Check whether num_bit is None, or num_bit is less than or equal to 0, or value is out of bounds
            raise BitOverflowError(f"Value {bit_val} is not valid for given number of provided bits {num_bit}") # Raise BitOverflowError
        self.extend(((bit_val >> i) & 1) for i in reversed(range(num_bit))) # Else extend the self attribute by adding each one of the bits for length of num_bit eg. bit_val = 5, num_bit_p = 4 => self = [0, 1, 0, 1]

def _get_sequence_bit(x: int, i: int) -> bool:
    """
    This function returns True if the ith element of list x is set to 1. Otherwise returns False
    """
    return (x >> i) & 1 != 0
# =============== Error Class Objects ===============================================================================================================================================================================
class BitOverflowError(ValueError):
    """
    Custom error to help detach bugs and errors throughout the code. Used when
    bits have overflown, or bit is invalid.
    """
    def __init__(self, msg):
        super().__init__(f"{msg}")

class ECIEncodingError(RuntimeError):
    """
    Custom error which occurs during invalidation of encoding procedure.
    """
    def __init__(self, msg):
        super().__init__(f"{msg}")

class PWQAIUnprovidedError(AttributeError):
    """
    Custom error to inform the user of unprovided PWQAI mode's parameter(s).
    """
    def __init__(self, msg):
        super().__init__(f"{msg}")

class DataTooLongError(ValueError):
    """
    Custom error to inform the user the provided data is in invalid state and/or range.
    """
    def __init__(self, msg):
        super().__init__(f"{msg}")