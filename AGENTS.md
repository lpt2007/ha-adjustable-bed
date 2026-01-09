# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration for controlling smart adjustable beds via Bluetooth Low Energy (BLE). It replaces the broken `smartbed-mqtt` addon with a native HA integration that uses Home Assistant's Bluetooth stack directly, avoiding the ESPHome Native API compatibility issues that broke the old addon.

**Current status:** Linak beds fully implemented. Other bed types (Richmat, Solace, MotoSleep, Reverie, etc.) are planned but not yet implemented.

## Why the Old Integration Broke

The `smartbed-mqtt` addon (in the `smartbed-mqtt/` folder) broke due to:

1. **ESPHome 2023.6.0+**: BLE proxy became single-client only - HA's ESPHome integration would block smartbed-mqtt from receiving BLE advertisements
2. **ESPHome 2025.5.0+**: New Native API messages (especially `BluetoothScannerStateResponse` id 126) crash the `@2colors/esphome-native-api` JS library

See `smartbed-mqtt-discord-chats/esphome-bug-llm-generated.md` for detailed documentation.

**The new integration solves this** by using HA's native Bluetooth stack (bleak) instead of ESPHome's Native API.

## Architecture

```
custom_components/smartbed/
├── __init__.py          # Integration setup, platform loading
├── config_flow.py       # Device discovery and setup wizard
├── coordinator.py       # BLE connection management (central hub)
├── const.py             # Constants, UUIDs, bed type definitions
├── entity.py            # Base entity class
├── beds/                # Bed controller implementations
│   ├── base.py          # Abstract base class (BedController)
│   └── linak.py         # Linak-specific protocol implementation
├── button.py            # Preset and massage button entities
├── cover.py             # Motor control entities (open=up, close=down)
├── sensor.py            # Position angle feedback entities
└── switch.py            # Light control entities
```

### Key Components

**SmartBedCoordinator** (`coordinator.py`): Central BLE connection manager
- Handles device discovery via HA's Bluetooth integration
- Connection retry with progressive backoff (3 attempts, 5-7.5s delays)
- Auto-disconnect after 60 seconds idle (allows physical remote/app)
- Registers conservative BLE connection parameters (30-50ms intervals)
- Supports preferred adapter selection for multi-proxy setups

**BedController** (`beds/base.py`): Abstract interface all bed types must implement
- `write_command()`: Send command bytes to the bed
- `start_notify()` / `stop_notify()`: Position notification handling
- Motor control methods: `move_head_up()`, `move_legs_down()`, etc.
- Preset methods: `preset_memory()`, `program_memory()`
- Optional features: `lights_on()`, `massage_toggle()`, etc.

**Config Flow** (`config_flow.py`):
- Automatic discovery via BLE service UUIDs
- Manual entry with bed type selection
- Per-device Bluetooth adapter/proxy selection

## Adding a New Bed Type

1. **Document the BLE protocol** - Use nRF Connect or similar to capture GATT services, characteristics, and command bytes

2. **Add constants to `const.py`**:
   ```python
   BED_TYPE_RICHMAT: Final = "richmat"
   RICHMAT_CONTROL_SERVICE_UUID: Final = "..."
   RICHMAT_CONTROL_CHAR_UUID: Final = "..."
   ```

3. **Create controller in `beds/`** (e.g., `richmat.py`):
   - Extend `BedController`
   - Implement all abstract methods
   - Define command bytes as a class (see `LinakCommands`)

4. **Add detection to `config_flow.py`** in `detect_bed_type()`:
   ```python
   if RICHMAT_CONTROL_SERVICE_UUID.lower() in service_uuids:
       return BED_TYPE_RICHMAT
   ```

5. **Update `coordinator.py`** `_create_controller()`:
   ```python
   if self._bed_type == BED_TYPE_RICHMAT:
       from .beds.richmat import RichmatController
       return RichmatController(self)
   ```

6. **Uncomment in `const.py`** `SUPPORTED_BED_TYPES` list

7. **Add to `manifest.json`** `bluetooth` array if using different service UUID for discovery

## Linak BLE Protocol Reference

```
Control Service:   99fa0001-338a-1024-8a49-009c0215f78a
  Write Char:      99fa0002-338a-1024-8a49-009c0215f78a
  Write Mode:      WITH RESPONSE (response=True) - bed expects acknowledgment

Command format: [command_byte, 0x00]

Motor commands:
  0x0B/0x0A = back up/down
  0x09/0x08 = legs up/down
  0x03/0x02 = head up/down
  0x05/0x04 = feet up/down
  0x00 = stop all

Motor timing:
  - 25 repeats at 200ms intervals (5 seconds total movement)
  - ALWAYS send STOP (0x00) after movement completes

Presets:
  0x0E, 0x0F, 0x0C, 0x44 = Memory 1-4
  0x38, 0x39, 0x3A, 0x45 = Program Memory 1-4

Preset timing:
  - 100 repeats at 300ms intervals (30 seconds for full preset movement)
  - NO stop command needed after presets

Single-shot commands (1 write, no repeat):
  - Lights: 0x92 (on), 0x93 (off), 0x94 (toggle)
  - Program memory: 0x38-0x3A, 0x45
  - Massage controls: all massage commands

Position Service: 99fa0020-338a-1024-8a49-009c0215f78a
  Back:  99fa0028 (max 820 raw = 68°)
  Legs:  99fa0027 (max 548 raw = 45°)
  Head:  99fa0026 (3+ motors)
  Feet:  99fa0025 (4 motors)

Position data format:
  - Little-endian 16-bit: raw = data[0] | (data[1] << 8)
  - Angle = max_angle * (raw / max_raw)
```

## Critical Implementation Details

These details were discovered by comparing with the working smartbed-mqtt implementation:

1. **Write with response** - Use `response=True` for all GATT writes. The bed expects write-with-response.

2. **Stop after movement** - Send STOP command (0x00) after motor movement sequences complete.

3. **TypeScript always reconnects** - The original calls `connect()` before every write. Python should use `async_ensure_connected()`.

4. **Presets are long operations** - 100 repeats × 300ms = 30 seconds. Don't timeout early.

## Integration Features

- **Options Flow** - Reconfigure bed settings without deleting the integration
- **Diagnostics** - Download debug info from Settings > Devices > Smart Bed
- **Custom Services** - `smartbed.goto_preset`, `smartbed.save_preset`, `smartbed.stop_all`
- **Auto-reconnection** - Automatically reconnects after unexpected disconnections
- **MAC Validation** - Validates Bluetooth address format during manual setup

## Development

### Testing in Home Assistant

1. Copy `custom_components/smartbed` to your HA's `config/custom_components/`
2. Restart Home Assistant
3. Add debug logging to `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.smartbed: debug
       homeassistant.components.bluetooth: debug
   ```

### Key Configuration Options

- **motor_count**: 2, 3, or 4 motors
- **has_massage**: Enable massage button entities
- **disable_angle_sensing**: Default `true` - keeps physical remote working
- **preferred_adapter**: Lock device to specific ESPHome proxy

### Common Issues

- **Commands timeout**: Another device (app/remote) may be connected - beds only allow one BLE connection
- **Position sensing breaks physical remote**: Enable `disable_angle_sensing` option
- **Connection drops**: Move ESP32 proxy closer to bed, check for interference

## Reference Materials

- `smartbed-mqtt/` - Old Node.js addon (broken, but has protocol implementations for many bed types)
- `smartbed-mqtt-discord-chats/` - Discord exports with reverse-engineering discussions and user reports
- `docs/CONNECTION_GUIDE.md` - User-facing setup and troubleshooting guide
