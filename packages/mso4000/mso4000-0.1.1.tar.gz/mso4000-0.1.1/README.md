# MSO4000 Library

Simple, clean library for Tektronix MSO4000 series oscilloscopes.

## Features

- ✅ Connection checking
- ✅ Single waveform capture
- ✅ Multiple waveform recording to CSV
- ✅ Simple, clean API

## Installation

Install from PyPI:

```bash
pip install mso4000
```

## Quick Start

### 1. Check Connection

```python
from mso4000 import check_connection

success, info = check_connection()
if success:
    print(f"Connected: {info}")
else:
    print(f"Error: {info}")
```

### 2. Record Waveforms to CSV (One-liner)

```python
from mso4000 import quick_record

# Record 10 waveforms and save to CSV
filename = quick_record(channel=1, max_records=10)
print(f"Saved to: {filename}")
```

### 3. Get Acquisition Information

```python
from mso4000 import MSO4000

scope = MSO4000(channel=1)

if scope.connect():
    # Get acquisition parameters
    info = scope.get_acquisition_info()
    scope.close()
```

### 4. Full Control

```python
from mso4000 import MSO4000

# Create scope interface
scope = MSO4000(channel=1)

# Connect
if scope.connect():
    # Get acquisition info
    info = scope.get_acquisition_info()
    
    # Capture single waveform
    waveform = scope.capture_waveform()
    print(f"Captured {len(waveform)} samples")
    
    # Or record multiple to CSV
    filename = scope.record_to_csv(max_records=20)
    print(f"Saved to: {filename}")
    
    # Close connection
    scope.close()
```

## API Reference

### `MSO4000` Class

#### `__init__(channel=1)`
Initialize the oscilloscope interface.

**Parameters:**
- `channel` (int): Channel number (1-4), default 1

#### `check_connection() -> Tuple[bool, Optional[str]]`
Check if oscilloscope is connected.

**Returns:**
- `(True, device_info)` if connected
- `(False, error_message)` if not connected

#### `connect() -> bool`
Connect to oscilloscope and configure for waveform transfer.

**Returns:**
- `True` if successful
- `False` if failed

#### `capture_waveform() -> Optional[np.ndarray]`
Capture a single waveform.

**Returns:**
- `numpy.ndarray` of voltage values, or `None` if failed

#### `record_to_csv(filename=None, max_records=None, delay=0.5) -> Optional[str]`
Record multiple waveforms and save to CSV.

**Parameters:**
- `filename` (str, optional): Output filename (auto-generated if None)
- `max_records` (int, optional): Maximum waveforms to record (None = until Ctrl+C)
- `delay` (float): Delay between captures in seconds (default 0.5)

**Returns:**
- Filename of saved CSV, or `None` if failed

#### `get_acquisition_info() -> Optional[dict]`
Get acquisition parameters (sampling rate, time window, number of samples).

**Returns:**
- Dictionary with:
  - `num_samples`: Samples per waveform
  - `time_window_sec`: Time window in seconds
  - `sampling_rate_hz`: Sampling rate in Hz
  - `time_per_sample_sec`: Time between samples
  - `timebase_s_div`: Timebase in s/div
  - `channel`: Channel number
  - `ch_scale_v_div`: Channel scale in V/div

Also prints a formatted table of acquisition parameters.

#### `close()`
Close connection to oscilloscope.

### Convenience Functions

#### `check_connection() -> Tuple[bool, Optional[str]]`
Quick function to check connection.

#### `quick_record(channel=1, max_records=None, filename=None) -> Optional[str]`
Quick function to connect and record waveforms.

**Parameters:**
- `channel` (int): Channel number (1-4)
- `max_records` (int, optional): Maximum waveforms (None = until Ctrl+C)
- `filename` (str, optional): Output filename (auto-generated if None)

**Returns:**
- Filename of saved CSV, or `None` if failed

## CSV Output Format

The CSV file contains:
- **Column 1:** Sample index (0 to N-1)
- **Column 2:** Time in seconds (relative to waveform start)
- **Columns 3+:** Voltage values for each recorded waveform

Example:
```csv
Sample_Index,Time_sec,Waveform_1_V,Waveform_2_V,Waveform_3_V
0,0.000000,-0.123456,0.234567,-0.345678
1,0.000010,-0.125432,0.236789,-0.347890
...
```

## Examples

See `example_mso4000.py` for complete examples.

## Requirements

- Python 3.6+
- pyvisa
- numpy

## Notes

- The library automatically selects USB resources (skips serial ports)
- Uses binary encoding (RIBINARY) for efficient data transfer
- Default timeout is 30 seconds for waveform transfers
- Press Ctrl+C to stop recording

## License

MIT License - See LICENSE file for details

