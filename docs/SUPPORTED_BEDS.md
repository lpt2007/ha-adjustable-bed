# Supported Bed Brands

This document provides detailed information about each supported bed brand, including known working models, protocol details, and brand-specific notes.

## Table of Contents

- [Linak](#linak)
- [Richmat](#richmat)
- [Keeson](#keeson)
- [Solace](#solace)
- [MotoSleep](#motosleep)
- [Leggett & Platt](#leggett--platt)
- [Reverie](#reverie)
- [Okimat](#okimat)

---

## Linak

**Status:** ✅ Fully Tested

### Known Working Models
- Linak DPG1M (OEM controller used in many beds)
- IKEA PRAKTVÄDD
- IKEA VARDÖ
- Many OEM adjustable beds with Linak motors

### Features
| Feature | Supported |
|---------|-----------|
| Motor Control | ✅ |
| Position Feedback | ✅ |
| Memory Presets | ✅ (4 slots) |
| Massage | ✅ (if equipped) |
| Under-bed Lights | ✅ |

### Protocol Details
- **Service UUID:** `99fa0001-338a-1024-8a49-009c0215f78a`
- **Command Format:** Single-byte commands
- **Position Notification:** Real-time position feedback available

### Notes
- Most reliable protocol with position feedback
- Disabling angle sensing is recommended to prevent conflicts with physical remote
- Some Linak beds may be sold under different brand names

---

## Richmat

**Status:** ⚠️ Untested (Protocol Implemented)

### Known Working Models
- Richmat HJA5 series
- Various OEM beds with Richmat controllers
- Some Sven & Son beds
- Some Lucid beds

### Protocol Variants

#### Nordic Variant
- Simple single-byte commands
- **Service UUID:** `6e400001-b5a3-f393-e0a9-e50e24dcca9e`
- Auto-detected but can be manually selected

#### WiLinke Variant
- 5-byte commands with checksum
- **Checksum:** `command + 111`
- Multiple service UUIDs supported
- Auto-detected based on discovered services

### Features
| Feature | Supported |
|---------|-----------|
| Motor Control | ✅ |
| Position Feedback | ❌ |
| Memory Presets | ✅ (2 slots) |
| Massage | ✅ |
| Under-bed Lights | ✅ |

### Notes
- If commands don't work, try switching between Nordic and WiLinke variants in options
- WiLinke variant is more common in newer beds

---

## Keeson

**Status:** ⚠️ Untested (Protocol Implemented)

### Known Working Models
- Member's Mark (Sam's Club) adjustable beds
- Purple adjustable bases
- ErgoMotion beds
- Some Costco beds with Keeson controllers

### Protocol Variants

#### Base (BaseI4/BaseI5)
- 8-byte commands with XOR checksum
- **Service UUID:** `0000ffe5-0000-1000-8000-00805f9b34fb`
- Most common variant for Member's Mark, Purple, ErgoMotion

#### KSBT
- 6-byte Okin-style commands
- **Service UUID:** `6e400001-b5a3-f393-e0a9-e50e24dcca9e` (same as Nordic UART)
- Used in older Keeson remotes

### Features
| Feature | Supported |
|---------|-----------|
| Motor Control | ✅ |
| Position Feedback | ❌ |
| Memory Presets | ✅ (4 slots) |
| Massage | ✅ |
| Safety Lights | ✅ |

### Notes
- Base variant is recommended for most beds
- Motors can be controlled simultaneously (head + feet together)

---

## Solace

**Status:** ⚠️ Untested (Protocol Implemented)

### Known Working Models
- Solace hospital/care beds
- Some medical adjustable beds

### Features
| Feature | Supported |
|---------|-----------|
| Motor Control | ✅ |
| Position Feedback | ❌ |
| Memory Presets | ✅ (5 slots) |
| Lift/Tilt | ✅ |
| Massage | ❌ |

### Protocol Details
- **Service UUID:** `0000ffe0-0000-1000-8000-00805f9b34fb`
- **Command Format:** 11-byte pre-defined command packets
- Commands must be repeated for motor movement

### Notes
- Designed for hospital/care environments
- Supports lift (height) and tilt adjustments
- Same UUID as MotoSleep but different protocol

---

## MotoSleep

**Status:** ⚠️ Untested (Protocol Implemented)

### Known Working Models
- Beds with HHC (Hangzhou Huaci) controllers
- Some budget adjustable beds

### Detection
- Identified by BLE device name starting with "HHC"
- Example names: `HHC3611243CDEF`, `HHC_xxxx`

### Features
| Feature | Supported |
|---------|-----------|
| Motor Control | ✅ |
| Position Feedback | ❌ |
| Memory Presets | ✅ (2 slots) |
| Massage | ✅ |
| Under-bed Lights | ✅ |

### Protocol Details
- **Service UUID:** `0000ffe0-0000-1000-8000-00805f9b34fb`
- **Command Format:** 2-byte ASCII commands `[$, ASCII_CHAR]`
- Very simple protocol

### Notes
- Distinguished from Solace by device name prefix "HHC"
- Commands are simple ASCII characters

---

## Leggett & Platt

**Status:** ⚠️ Untested (Protocol Implemented)

### Known Working Models
- Leggett & Platt Prodigy 2.0
- Leggett & Platt S-Cape 2.0
- Some Tempur-Pedic bases (non-Ergo)
- Fashion Bed Group bases

### Protocol Variants

#### Gen2 (Richmat-based)
- ASCII text commands
- **Service UUID:** `45e25100-3171-4cfc-ae89-1d83cf8d8071`
- Most common variant
- Supports RGB lighting with hex color commands

#### Okin
- Binary commands (same as Keeson/Okimat)
- **Service UUID:** `62741523-52f9-8864-b1ab-3b3a8d65950b`
- Requires BLE pairing before use

### Features
| Feature | Supported |
|---------|-----------|
| Motor Control | ✅ (Okin) / ⚠️ (Gen2 - preset-based) |
| Position Feedback | ❌ |
| Memory Presets | ✅ (4 slots) |
| Massage | ✅ |
| RGB Lighting | ✅ (Gen2 only) |

### Notes
- Gen2 uses position-based presets rather than direct motor control
- Okin variant requires pairing through system Bluetooth settings first

---

## Reverie

**Status:** ⚠️ Untested (Protocol Implemented)

### Known Working Models
- Reverie 9T
- Reverie 8Q
- Reverie 7S
- Various Reverie adjustable bases

### Features
| Feature | Supported |
|---------|-----------|
| Motor Control | ✅ (position-based, 0-100%) |
| Position Feedback | ✅ (partial) |
| Memory Presets | ✅ (4 slots) |
| Massage | ✅ (0-10 levels) |
| Wave Massage | ✅ |
| Under-bed Lights | ✅ |

### Protocol Details
- **Service UUID:** `1b1d9641-b942-4da8-89cc-98e6a58fbd93`
- **Command Format:** XOR checksum `[0x55, ...bytes, checksum]`
- **Checksum Calculation:** All bytes XOR'd together XOR 0x55

### Notes
- Position-based motor control (move to specific percentage)
- Supports position notifications for feedback
- Massage has 10 intensity levels

---

## Okimat

**Status:** ⚠️ Untested (Protocol Implemented)

### Known Working Models
- Okimat beds
- Some European adjustable beds with Okin motors
- Beds with Okin RF remotes

### Features
| Feature | Supported |
|---------|-----------|
| Motor Control | ✅ |
| Position Feedback | ❌ |
| Memory Presets | ✅ (4 slots) |
| Massage | ✅ |
| Lights | ✅ |

### Protocol Details
- **Service UUID:** `62741523-52f9-8864-b1ab-3b3a8d65950b`
- **Command Format:** 6-byte Okin commands `[0x04, 0x02, ...int_bytes]`
- Same protocol as Leggett & Platt Okin variant

### Requirements
- **BLE Pairing Required:** Must pair through system Bluetooth settings before use

### Notes
- Uses same protocol as Leggett & Platt Okin variant
- Pairing is mandatory - integration will fail without it
- Some beds may show as "Okin" in Bluetooth scan

---

## Not Yet Supported

### Octo (Cloud-based)
- Tempur-Pedic Ergo series
- Beautyrest SmartMotion
- Serta Motion series
- **Reason:** Requires cloud API, not local BLE control

---

## Identifying Your Bed Type

1. **Check the remote or controller box** for brand markings
2. **Scan for BLE devices** - the device name often indicates the brand
3. **Look at service UUIDs** in a BLE scanner app
4. **Check the bed frame** for manufacturer labels

### Common Device Name Patterns
| Pattern | Likely Brand |
|---------|--------------|
| `HHC*` | MotoSleep |
| `DPG*` | Linak |
| `Richmat*` | Richmat |
| `Okin*` | Okimat |

If your bed isn't detected automatically, use manual configuration and try different bed types until one works.
