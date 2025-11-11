# MSO4000 Library

Simple, clean library for Tektronix MSO4000 series oscilloscopes.

## Features

- ✅ Connection checking
- ✅ Single waveform capture
- ✅ Multiple waveform recording to CSV
- ✅ Raw binary data capture and saving
- ✅ Correct time axis calculation using Tektronix formula
- ✅ Detailed waveform inspection with timing verification
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

### 4. Save Raw Binary Data

```python
from mso4000 import quick_save_raw_binary, quick_save_raw_csv

# Save raw binary with metadata
binary_file = quick_save_raw_binary(channel=1)
# Saves: raw_waveform_CH1_<timestamp>.bin
#        raw_waveform_CH1_<timestamp>.metadata

# Save raw waveform as CSV
csv_file = quick_save_raw_csv(channel=1)
```

### 5. Full Control

```python
from mso4000 import MSO4000

# Create scope interface
scope = MSO4000(channel=1)

# Connect
if scope.connect():
    # Get acquisition info
    info = scope.get_acquisition_info()
    
    # Inspect raw event with timing verification
    raw_data = scope.inspect_raw_event()
    
    # Save raw binary with metadata
    binary_file = scope.save_raw_binary()
    
    # Save raw CSV
    csv_file = scope.save_raw_csv()
    
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
Get acquisition parameters including oscilloscope timing parameters.

**Returns:**
- Dictionary with acquisition info including:
  - `num_samples`, `time_window_sec`, `sampling_rate_hz`, `time_per_sample_sec`
  - `timebase_s_div`, `channel`, `ch_scale_v_div`
  - `xincr_sec`: Horizontal sampling interval from oscilloscope
  - `xzero_sec`: Time coordinate of first sample
  - `pt_off`: Point offset (usually 0)

Also prints a formatted table of acquisition parameters.

#### `get_raw_waveform_data() -> Optional[dict]`
Capture raw binary waveform data with header information.

#### `inspect_raw_event() -> Optional[dict]`
Comprehensive inspection of a single event with timing verification.

#### `save_raw_binary(filename=None, save_metadata=True) -> Optional[str]`
Save raw binary waveform data with optional metadata file.

#### `save_raw_csv(filename=None) -> Optional[str]`
Save waveform to CSV with time axis and raw values.

#### `close()`
Close connection to oscilloscope.

### Convenience Functions

#### `check_connection() -> Tuple[bool, Optional[str]]`
Quick function to check connection.

#### `quick_record(channel=1, max_records=None, filename=None) -> Optional[str]`
Quick function to connect and record waveforms.

#### `quick_inspect(channel=1) -> Optional[dict]`
Quick function to inspect a single raw event with timing verification.

#### `quick_get_timing_info(channel=1) -> Optional[dict]`
Quick function to get acquisition timing information.

#### `quick_save_raw_binary(channel=1, filename=None, save_metadata=True) -> Optional[str]`
Quick function to save raw binary waveform data.

#### `quick_save_raw_csv(channel=1, filename=None) -> Optional[str]`
Quick function to save raw waveform to CSV.

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

## Important: Time Axis Calculation (v0.2.0+)

The time axis is now calculated using the official Tektronix formula:

```
Time[n] = XZERO + XINCR * (n - PT_OFF)
```

This ensures exact alignment with the oscilloscope display.

## Notes

- The library automatically selects USB resources (skips serial ports)
- Uses binary encoding (RIBINARY) for efficient data transfer
- Default timeout is 30 seconds for waveform transfers
- Press Ctrl+C to stop recording
- Timing parameters are queried from oscilloscope (v0.2.0+)
- Raw binary files preserve exact oscilloscope output
- All functionality is backward compatible

## License

MIT License - See LICENSE file for details

