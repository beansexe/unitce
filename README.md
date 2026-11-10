# UNITCE — unit calculator for TI-84 Plus CE

UNITCE is a menu-driven unit calculator for the TI-84 Plus CE. Enter numbers with SI or Imperial units, combine them in an expression, and get a result in familiar units such as N or lbf. Leave numbers blank to calculate with units alone. The first term controls the result system, and optional dual output shows both systems.

A native TI-BASIC program with calculator menus. No jailbreak, shell, Python edition, or calculator libraries required.

[Download the complete calculator package](https://github.com/beansexe/unitce/raw/refs/heads/main/UNITCE-download.zip) · [Browse the source](source/)

## Install

1. Install **TI Connect CE** on your computer (Texas Instruments: https://education.ti.com/en/products/computer-software/ti-connect-ce-sw).
2. Connect the TI-84 Plus CE with its USB data cable.
3. Send **all four files** to the calculator: `UNITCE.8xp`, `UCPICK.8xp`, `UCVAL.8xp`, and `UCOUT.8xp`. Choose RAM if asked. They use about 9 KB of program storage, plus working memory.
4. On the calculator, press **PRGM**, select **UNITCE**, and press **ENTER** to paste the command, then **ENTER** to run it.

Only launch UNITCE; the other three programs are helpers. The `.txt` files are readable source, not files to transfer.

## Your example

Choose **NEW EXPRESSION**:

1. Type `9`, ENTER → MASS → SI → kg.
2. Choose MULTIPLY.
3. Type `2`, ENTER → ACCEL → m/s^2. The SI unit menu opens automatically.
4. Choose RESULT: **18 N**.

For Imperial acceleration in step 3, choose **SYSTEM / BACK → IMPERIAL → ft/s^2**. The result is **5.4864 N**, because the first term used SI.

For two outputs, choose **CONFIG → ON: SI + IMPERIAL** before starting. The original example then displays **18 N** and approximately **4.04656 lbf**. The first term's system appears first. Config stays active until you quit the program; it resets to single output when launched again.

## Units alone

At the value screen, just press **ENTER**: the value defaults to **1**. For example, blank → kg, MULTIPLY, blank → m/s^2 gives **1 N**. This performs dimensional arithmetic; it does not introduce an unknown variable or solve equations.

Choose **MORE / BACK → MORE → NO UNIT** for a plain numeric term, such as a multiplier of 2.

## Controls and behavior

- Use arrows and ENTER (or the displayed menu number) to select options.
- Values accept up to 14 characters of decimal digits and a decimal point. The calculator's **(-)** key toggles the sign; **DEL** erases a character. **CLEAR** cancels a value entry. Scientific notation and typed formulas are not accepted in this value field.
- Select a quantity, then units. The first term asks for SI or Imperial; later terms open the most recently selected system. SYSTEM / BACK allows either system or a return to quantity selection.
- MULTIPLY and DIVIDE run before ADD and SUBTRACT; equal-precedence operations run left to right. Parentheses and expression powers are not included. Use repeated multiplication to form powers of units.
- Mixed systems convert automatically. Results use the first term's system, independently of subsequent choices. Adding or subtracting different dimensions shows an error and preserves your expression. Division by zero is caught.
- RESULT → CONVERT lets you choose another unit of the same dimension. Dual output applies to the automatic result screen; a manual conversion shows the requested unit.
- REVIEW / UNDO allows reviewing all terms in SI base units or removing the last term. Review operation codes are 1=multiply, 2=divide, 3=add, 4=subtract; ignore the first term's operation code. Press ENTER at Pause screens to continue.
- HOME returns to the main menu. NEW EXPRESSION clears the expression and asks for its first unit system again. There is a 40-term limit.

## Units included

| Quantity | SI choices | Imperial choices |
|---|---|---|
| Mass | kg, g, mg | lbm, slug, oz |
| Length | m, cm, mm, km | ft, in, yd, mi |
| Time | s, min, hr | s, min, hr |
| Speed | m/s, km/hr | ft/s, mph |
| Acceleration | m/s² | ft/s² |
| Force | N, kN | lbf, poundal |
| Energy | J, kJ | ft·lbf, BTU |
| Power | W, kW | mechanical hp, ft·lbf/s |
| Pressure | Pa, kPa, MPa | psi, psf |
| Area | m², cm² | ft², in² |
| Volume | m³, L, mL | ft³, in³, US gallon |
| Density | kg/m³, g/cm³ | lbm/ft³ |
| Frequency | Hz, kHz | Hz |

Imperial mass in **lbm** is different from force in **lbf**. `1 slug × 1 ft/s² = 1 lbf`; `1 lbm × 1 ft/s² ≈ 0.031081 lbf`. This is intentional. BTU uses the International Table definition; gallon means US liquid gallon, not UK gallon.

Recognized dimensions automatically use familiar units (N/lbf, J/ft·lbf, W/hp, Pa/psi, and so on). Other dimensions display a base-unit template with M, L, T exponents listed underneath: SI uses kg, m, s; Imperial uses slug, ft, s. For example, exponents `1,2,-1` mean kg·m²/s in SI.

## Storage and validation

This program uses calculator variables **A–Z**, **Str0–Str2**, and named lists **UCV, UCM, UCL, UCT, UCOP, UCK, UV, UM, UL, UT, UO** as scratch space and does not restore their previous contents. Back up any existing values stored in these names. It does not use L1–L6 or matrices.

The downloadable files are tokenized `.8xp` programs. Build validation checked binary token round trips. A small host-side TI-BASIC interpreter exercised nine expression/editor scenarios and 28 automatic output-unit cases, including the requested example, units-only input, mixed systems, dual output, operator precedence, undo, conversion rejection, negative decimals, and errors.

**Not tested on a physical calculator or a full TI emulator.** The host interpreter checks program logic, but cannot verify every calculator OS behavior or screen layout. Keep the source so any device-specific issue can be corrected.

## Rebuild or modify

Python 3.12 was used, with the open-source `tivars` package. From the extracted bundle directory:

```sh
python -m venv .venv
.venv/bin/pip install -r source/requirements.txt
.venv/bin/python source/build.py
.venv/bin/python source/test_programs.py
```

On Windows use `.venv\Scripts\python.exe` / `pip.exe`. Rebuilt files appear in a new `output/` subfolder. Edit the unit catalog and program generator in `source/build.py`; `units.json` also lists the catalog and SI conversion factors.
