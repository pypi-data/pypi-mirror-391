"""
Simple library for Tektronix MSO4000 series oscilloscopes
Provides connection checking and waveform recording to CSV
"""
import pyvisa
import numpy as np
import time
import csv
from datetime import datetime
from typing import Optional, Tuple, List


class MSO4000:
    """Simple interface for Tektronix MSO4000 series oscilloscopes"""
    
    def __init__(self, channel: int = 1):
        """
        Initialize MSO4000 interface
        
        Args:
            channel: Channel number (1-4)
        """
        self.channel = channel
        self.scope = None
        self.rm = None
        self.timebase = None
        self.ch_scale = None
        self.xincr = None  # Horizontal sampling interval (time per point)
        self.xzero = None  # Time coordinate of first point
        self.pt_off = None  # Point offset (usually 0)
    
    def check_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Check if oscilloscope is connected and accessible
        
        Returns:
            Tuple of (success: bool, device_info: str or None)
        """
        try:
            self.rm = pyvisa.ResourceManager()
            resources = self.rm.list_resources()
            
            # Prefer USB resources
            usb_resources = [r for r in resources if r.startswith('USB')]
            if not usb_resources:
                return False, "No USB oscilloscope found"
            
            resource_name = usb_resources[0]
            self.scope = self.rm.open_resource(resource_name)
            self.scope.timeout = 5000
            
            # Query identification
            idn = self.scope.query("*IDN?")
            device_info = idn.strip()
            
            return True, device_info
            
        except Exception as e:
            return False, f"Connection error: {e}"
    
    def connect(self) -> bool:
        """
        Connect to oscilloscope and configure for waveform transfer
        
        Returns:
            True if successful, False otherwise
        """
        success, info = self.check_connection()
        if not success:
            print(f"❌ {info}")
            return False
        
        try:
            print(f"✓ Connected to: {info}")
            
            # Configure for waveform transfer
            self.scope.write("*CLS")
            self.scope.write(f":DATA:SOURCE CH{self.channel}")
            self.scope.write(":DATA:ENCDG RIBINARY")
            self.scope.write(":WFMOUTPRE:BYT_NR 2")
            self.scope.write(":DATA INIT")
            
            # Get scale info
            self.timebase = float(self.scope.query(":HORIZONTAL:SCALE?"))
            self.ch_scale = float(self.scope.query(f":CH{self.channel}:SCALE?"))
            
            # Get waveform timing parameters (required for correct time axis calculation)
            # According to Tektronix docs: Xn = XZERO + XINCR * (n - PT_OFF)
            try:
                self.xincr = float(self.scope.query(":WFMOUTPRE:XINCR?"))
                self.xzero = float(self.scope.query(":WFMOUTPRE:XZERO?"))
                self.pt_off = float(self.scope.query(":WFMOUTPRE:PT_OFF?"))
            except Exception as e:
                print(f"⚠ Warning: Could not query waveform timing parameters: {e}")
                print("   Time axis may be incorrect. Using fallback calculation.")
                self.xincr = None
                self.xzero = None
                self.pt_off = 0
            
            print(f"✓ Configured: Timebase={self.timebase} s/div, CH{self.channel}={self.ch_scale} V/div")
            if self.xincr is not None:
                print(f"✓ Waveform timing: XINCR={self.xincr:.2e} s, XZERO={self.xzero:.2e} s")
            return True
            
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return False
    
    def get_raw_waveform_data(self) -> Optional[dict]:
        """
        Capture raw binary waveform data with header information for inspection
        
        Returns:
            Dictionary with:
            - 'raw_bytes': Complete raw binary response from oscilloscope
            - 'header_str': ASCII header string
            - 'digit_count': Number of digits in byte count
            - 'byte_count': Number of bytes in waveform data
            - 'header_len': Total header length
            - 'binary_data': Extracted binary waveform data
            - 'waveform': Scaled voltage array
            or None if failed
        """
        if not self.scope:
            print("❌ Not connected. Call connect() first.")
            return None
        
        try:
            self.scope.timeout = 30000  # 30 seconds for data transfer
            
            # Trigger and get waveform
            print("📊 Triggering and capturing raw waveform data...")
            self.scope.write(":TRIGGER:FORCE")
            time.sleep(0.2)
            
            # Get data using write + read_raw for binary data
            self.scope.write("CURVE?")
            curve_data_bytes = self.scope.read_raw()
            
            # Parse binary data header
            curve_data_str = curve_data_bytes.decode('latin1', errors='ignore')
            
            if curve_data_str.startswith('#'):
                digit_count = int(curve_data_str[1])
                byte_count = int(curve_data_str[2:2+digit_count])
                header_len = 2 + digit_count
                
                # Extract binary data
                binary_data = curve_data_bytes[header_len:header_len+byte_count]
                
                # Convert to array (16-bit signed integers, big-endian)
                voltage_array = np.frombuffer(binary_data, dtype='>i2')
                
                # Scale to voltage
                voltage_scaled = (voltage_array / 32768.0) * self.ch_scale * 5.0
                
                return {
                    'raw_bytes': curve_data_bytes,
                    'header_str': curve_data_str[:header_len],
                    'digit_count': digit_count,
                    'byte_count': byte_count,
                    'header_len': header_len,
                    'binary_data': binary_data,
                    'waveform': voltage_scaled,
                }
            else:
                print("⚠ Warning: Not in expected binary format, attempting ASCII parse")
                values = [float(x) for x in curve_data_str.split(',')]
                voltage_scaled = np.array(values)
                
                return {
                    'raw_bytes': curve_data_bytes,
                    'header_str': '',
                    'digit_count': 0,
                    'byte_count': 0,
                    'header_len': 0,
                    'binary_data': curve_data_bytes,
                    'waveform': voltage_scaled,
                }
            
        except Exception as e:
            print(f"❌ Error capturing raw waveform data: {e}")
            return None
    
    def capture_waveform(self) -> Optional[np.ndarray]:
        """
        Capture a single waveform from the oscilloscope
        
        Returns:
            Voltage array (numpy array) or None if failed
        """
        raw_data = self.get_raw_waveform_data()
        if raw_data is None:
            return None
        
        return raw_data['waveform']
    
    def record_to_csv(self, filename: Optional[str] = None, 
                      max_records: Optional[int] = None,
                      delay: float = 0.5) -> Optional[str]:
        """
        Record multiple waveforms and save to CSV
        
        Args:
            filename: Output CSV filename (auto-generated if None)
            max_records: Maximum number of waveforms to record (None = until interrupted)
            delay: Delay between captures in seconds
            
        Returns:
            Filename of saved CSV or None if failed
        """
        if not self.scope:
            print("❌ Not connected. Call connect() first.")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"waveform_data_{timestamp}.csv"
        
        all_data = []
        timestamps = []
        record_count = 0
        
        print(f"\n📝 Recording waveforms... (Press Ctrl+C to stop)")
        print(f"   Output: {filename}\n")
        
        try:
            while True:
                if max_records and record_count >= max_records:
                    print(f"\n✓ Record limit reached ({max_records} records)")
                    break
                
                print(f"[{record_count+1}] Capturing... ", end="", flush=True)
                
                voltage_data = self.capture_waveform()
                
                if voltage_data is not None:
                    all_data.append(voltage_data)
                    timestamps.append(time.time())
                    record_count += 1
                    
                    min_v = voltage_data.min()
                    max_v = voltage_data.max()
                    mean_v = voltage_data.mean()
                    print(f"✓ {len(voltage_data):6d} samples | "
                          f"Min: {min_v:8.4f}V | Max: {max_v:8.4f}V | Mean: {mean_v:8.4f}V")
                    
                    time.sleep(delay)
                else:
                    print("✗ FAILED")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⏹ Recording interrupted by user")
        
        if not all_data:
            print("❌ No data to export!")
            return None
        
        # Export to CSV
        print(f"\n💾 Exporting to {filename}...")
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                max_samples = max(len(wf) for wf in all_data)
                
                # Create header
                headers = ['Sample_Index', 'Time_sec'] + \
                         [f'Waveform_{i+1}_V' for i in range(record_count)]
                
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                # Calculate time axis using proper Tektronix formula: Xn = XZERO + XINCR * (n - PT_OFF)
                num_points = len(all_data[0]) if all_data else 1
                
                if self.xincr is not None and self.xzero is not None:
                    # Use oscilloscope-provided timing parameters (correct method)
                    pt_off = self.pt_off if self.pt_off is not None else 0
                else:
                    # Fallback: calculate from timebase (may be inaccurate)
                    print("⚠ Warning: Using fallback time calculation. Results may be inaccurate.")
                    self.xincr = (self.timebase * 10.0) / num_points
                    self.xzero = 0.0
                    pt_off = 0
                
                # Write data
                for sample_idx in range(max_samples):
                    # Calculate time using Tektronix formula
                    time_value = self.xzero + self.xincr * (sample_idx - pt_off)
                    row = [sample_idx, time_value]
                    
                    for waveform in all_data:
                        if sample_idx < len(waveform):
                            row.append(waveform[sample_idx])
                        else:
                            row.append('')
                    
                    writer.writerow(row)
            
            print(f"✓ Exported {record_count} waveforms, {max_samples} samples each")
            
            import os
            file_size = os.path.getsize(filename)
            print(f"✓ File size: {file_size / 1024 / 1024:.2f} MB")
            
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting: {e}")
            return None
    
    def get_acquisition_info(self) -> Optional[dict]:
        """
        Get acquisition parameters: sampling rate, window size, number of samples
        
        Returns:
            Dictionary with acquisition info or None if not connected
        """
        if not self.scope or not self.timebase:
            print("❌ Not connected. Call connect() first.")
            return None
        
        try:
            # Capture one waveform to get number of samples
            waveform = self.capture_waveform()
            if waveform is None:
                return None
            
            num_samples = len(waveform)
            
            # Use proper timing parameters if available
            if self.xincr is not None:
                time_per_sample = self.xincr
                # Calculate time window from first to last sample
                pt_off = self.pt_off if self.pt_off is not None else 0
                time_first = self.xzero + self.xincr * (0 - pt_off)
                time_last = self.xzero + self.xincr * ((num_samples - 1) - pt_off)
                time_window = abs(time_last - time_first)
                sampling_rate = 1.0 / self.xincr  # Hz
            else:
                # Fallback calculation (may be inaccurate)
                time_window = self.timebase * 10.0  # 10 divisions
                sampling_rate = num_samples / time_window  # Hz
                time_per_sample = time_window / num_samples  # seconds
            
            info = {
                'num_samples': num_samples,
                'time_window_sec': time_window,
                'sampling_rate_hz': sampling_rate,
                'time_per_sample_sec': time_per_sample,
                'timebase_s_div': self.timebase,
                'channel': self.channel,
                'ch_scale_v_div': self.ch_scale,
                'xincr_sec': self.xincr,
                'xzero_sec': self.xzero,
                'pt_off': self.pt_off if self.pt_off is not None else 0,
            }
            
            # Print nicely formatted info
            print("\n" + "="*60)
            print("ACQUISITION PARAMETERS")
            print("="*60)
            print(f"Channel:              CH{self.channel}")
            print(f"Timebase:             {self.timebase*1e3:.3f} ms/div")
            print(f"Channel Scale:        {self.ch_scale:.3f} V/div")
            print(f"Number of Samples:    {num_samples}")
            print(f"Time Window:          {time_window*1e3:.3f} ms ({time_window:.6f} s)")
            print(f"Sampling Rate:        {sampling_rate/1e6:.2f} MHz ({sampling_rate:.0f} Hz)")
            print(f"Time per Sample:      {time_per_sample*1e9:.2f} ns ({time_per_sample*1e6:.3f} µs)")
            if self.xincr is not None:
                print(f"XINCR (from scope):   {self.xincr:.2e} s ({self.xincr*1e9:.2f} ns)")
                print(f"XZERO (from scope):   {self.xzero:.2e} s ({self.xzero*1e9:.2f} ns)")
                print(f"PT_OFF:               {self.pt_off if self.pt_off is not None else 0}")
            else:
                print("⚠ Timing parameters:   Using fallback calculation")
            print("="*60 + "\n")
            
            return info
            
        except Exception as e:
            print(f"❌ Error getting acquisition info: {e}")
            return None
    
    def save_raw_binary(self, filename: Optional[str] = None, 
                       save_metadata: bool = True) -> Optional[str]:
        """
        Capture and save raw binary waveform data from oscilloscope
        
        Args:
            filename: Output filename (auto-generated if None)
            save_metadata: Whether to save a .metadata file with timing info
            
        Returns:
            Filename of saved binary file or None if failed
        """
        raw_data = self.get_raw_waveform_data()
        if raw_data is None:
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_waveform_CH{self.channel}_{timestamp}.bin"
        
        try:
            # Save raw binary data
            with open(filename, 'wb') as f:
                f.write(raw_data['raw_bytes'])
            
            print(f"✓ Saved raw binary data to: {filename}")
            
            # Save metadata if requested
            if save_metadata:
                metadata_filename = filename.replace('.bin', '.metadata')
                with open(metadata_filename, 'w') as f:
                    f.write("# Raw Waveform Metadata\n")
                    f.write(f"# Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"# Channel: CH{self.channel}\n")
                    f.write(f"# Timebase (s/div): {self.timebase}\n")
                    f.write(f"# Channel Scale (V/div): {self.ch_scale}\n\n")
                    
                    f.write("## Binary Format\n")
                    f.write(f"Header string: {raw_data['header_str']}\n")
                    f.write(f"Digit count: {raw_data['digit_count']}\n")
                    f.write(f"Byte count: {raw_data['byte_count']}\n")
                    f.write(f"Header length: {raw_data['header_len']} bytes\n\n")
                    
                    f.write("## Oscilloscope Timing Parameters\n")
                    f.write(f"XINCR (time/point): {self.xincr:.10e} s ({self.xincr*1e9:.6f} ns)\n")
                    f.write(f"XZERO (time offset): {self.xzero:.10e} s ({self.xzero*1e9:.6f} ns)\n")
                    f.write(f"PT_OFF (point offset): {self.pt_off if self.pt_off is not None else 0}\n\n")
                    
                    f.write("## Waveform Properties\n")
                    num_samples = len(raw_data['waveform'])
                    waveform = raw_data['waveform']
                    f.write(f"Number of samples: {num_samples}\n")
                    f.write(f"Data type: 16-bit signed integer (big-endian)\n")
                    f.write(f"Min voltage: {waveform.min():.6f} V\n")
                    f.write(f"Max voltage: {waveform.max():.6f} V\n")
                    f.write(f"Mean voltage: {waveform.mean():.6f} V\n")
                    f.write(f"Std deviation: {waveform.std():.6f} V\n\n")
                    
                    f.write("## Time Axis Formula\n")
                    f.write(f"Xn = XZERO + XINCR * (n - PT_OFF)\n")
                    pt_off = self.pt_off if self.pt_off is not None else 0
                    time_first = self.xzero + self.xincr * (0 - pt_off)
                    time_last = self.xzero + self.xincr * ((num_samples - 1) - pt_off)
                    f.write(f"Time of first sample: {time_first:.10e} s\n")
                    f.write(f"Time of last sample: {time_last:.10e} s\n")
                    f.write(f"Total time window: {abs(time_last - time_first):.10e} s\n")
                
                print(f"✓ Saved metadata to: {metadata_filename}")
            
            return filename
            
        except Exception as e:
            print(f"❌ Error saving binary data: {e}")
            return None
    
    def save_raw_csv(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Capture and save raw binary waveform to CSV with calculated time axis
        
        Args:
            filename: Output CSV filename (auto-generated if None)
            
        Returns:
            Filename of saved CSV file or None if failed
        """
        raw_data = self.get_raw_waveform_data()
        if raw_data is None:
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_waveform_CH{self.channel}_{timestamp}.csv"
        
        try:
            waveform = raw_data['waveform']
            num_samples = len(waveform)
            pt_off = self.pt_off if self.pt_off is not None else 0
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Sample_Index', 'Time_sec', 'Voltage_V', 'Raw_Value_i16'])
                
                # Write data
                for sample_idx in range(num_samples):
                    # Calculate time using Tektronix formula
                    time_value = self.xzero + self.xincr * (sample_idx - pt_off)
                    
                    # Extract raw 16-bit value
                    raw_val = np.frombuffer(
                        raw_data['binary_data'][sample_idx*2:(sample_idx+1)*2], 
                        dtype='>i2'
                    )[0]
                    
                    writer.writerow([
                        sample_idx,
                        time_value,
                        waveform[sample_idx],
                        raw_val
                    ])
            
            print(f"✓ Saved raw waveform CSV to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
            return None
    
    def inspect_raw_event(self) -> Optional[dict]:
        """
        Capture and inspect a single event with detailed header and timing information
        
        Returns:
            Dictionary with raw data and formatted inspection report, or None if failed
        """
        raw_data = self.get_raw_waveform_data()
        if raw_data is None:
            return None
        
        # Print detailed inspection report
        print("\n" + "="*70)
        print("RAW WAVEFORM DATA INSPECTION")
        print("="*70)
        
        print("\n[1] BINARY HEADER (Tektronix format)")
        print("-" * 70)
        print(f"Header string:        '{raw_data['header_str']}'")
        print(f"Header (bytes):       {raw_data['header_str'].encode('latin1')}")
        print(f"Digit count:          {raw_data['digit_count']}")
        print(f"Byte count:           {raw_data['byte_count']}")
        print(f"Header length:        {raw_data['header_len']} bytes")
        
        print("\n[2] OSCILLOSCOPE TIMING PARAMETERS")
        print("-" * 70)
        print(f"XINCR (time/point):   {self.xincr:.2e} s ({self.xincr*1e9:.3f} ns)")
        print(f"XZERO (time offset):  {self.xzero:.2e} s ({self.xzero*1e9:.3f} ns)")
        print(f"PT_OFF (point offset):{self.pt_off if self.pt_off is not None else 0}")
        
        print("\n[3] WAVEFORM DATA PROPERTIES")
        print("-" * 70)
        num_samples = len(raw_data['waveform'])
        print(f"Number of samples:    {num_samples}")
        print(f"Binary data size:     {len(raw_data['binary_data'])} bytes ({num_samples*2} bytes for 16-bit samples)")
        
        waveform = raw_data['waveform']
        print(f"Min voltage:          {waveform.min():.6f} V")
        print(f"Max voltage:          {waveform.max():.6f} V")
        print(f"Mean voltage:         {waveform.mean():.6f} V")
        print(f"Std deviation:        {waveform.std():.6f} V")
        
        print("\n[4] TIME AXIS CALCULATION (using Xn = XZERO + XINCR * (n - PT_OFF))")
        print("-" * 70)
        pt_off = self.pt_off if self.pt_off is not None else 0
        time_first = self.xzero + self.xincr * (0 - pt_off)
        time_last = self.xzero + self.xincr * ((num_samples - 1) - pt_off)
        time_window = abs(time_last - time_first)
        
        print(f"Time of first sample: {time_first:.2e} s ({time_first*1e6:.3f} µs)")
        print(f"Time of last sample:  {time_last:.2e} s ({time_last*1e6:.3f} µs)")
        print(f"Total time window:    {time_window:.2e} s ({time_window*1e6:.3f} µs)")
        
        # Sample a few time values to verify formula
        print("\nSample time axis values (first 5 and last 5 points):")
        for n in list(range(min(5, num_samples))) + list(range(max(0, num_samples-5), num_samples)):
            time_val = self.xzero + self.xincr * (n - pt_off)
            print(f"  n={n:6d}: t={time_val:.2e} s ({time_val*1e9:12.3f} ns)")
        
        print("\n[5] FIRST FEW RAW SAMPLES (16-bit, big-endian)")
        print("-" * 70)
        for i in range(min(10, num_samples)):
            raw_val = np.frombuffer(raw_data['binary_data'][i*2:(i+1)*2], dtype='>i2')[0]
            scaled_val = (raw_val / 32768.0) * self.ch_scale * 5.0
            print(f"  Sample {i:4d}: raw={raw_val:6d}, scaled={scaled_val:10.6f} V, "
                  f"calculated={raw_data['waveform'][i]:10.6f} V")
        
        print("="*70 + "\n")
        
        return raw_data
    
    def close(self):
        """Close connection to oscilloscope"""
        if self.scope:
            self.scope.close()
            self.scope = None
            print("✓ Connection closed")


# Convenience functions
def check_connection() -> Tuple[bool, Optional[str]]:
    """
    Quick function to check if oscilloscope is connected
    
    Returns:
        Tuple of (success: bool, device_info: str or None)
    """
    scope = MSO4000()
    return scope.check_connection()


def quick_record(channel: int = 1, max_records: Optional[int] = None,
                filename: Optional[str] = None) -> Optional[str]:
    """
    Quick function to connect and record waveforms
    
    Args:
        channel: Channel number (1-4)
        max_records: Maximum number of waveforms (None = until interrupted)
        filename: Output CSV filename (auto-generated if None)
        
    Returns:
        Filename of saved CSV or None if failed
    """
    scope = MSO4000(channel=channel)
    
    if not scope.connect():
        return None
    
    try:
        filename = scope.record_to_csv(filename=filename, max_records=max_records)
        return filename
    finally:
        scope.close()


def quick_inspect(channel: int = 1) -> Optional[dict]:
    """
    Quick function to connect and inspect a single raw event
    
    Args:
        channel: Channel number (1-4)
        
    Returns:
        Raw data dictionary or None if failed
    """
    scope = MSO4000(channel=channel)
    
    if not scope.connect():
        return None
    
    try:
        raw_data = scope.inspect_raw_event()
        return raw_data
    finally:
        scope.close()


def quick_get_timing_info(channel: int = 1) -> Optional[dict]:
    """
    Quick function to connect and get acquisition timing information
    
    Args:
        channel: Channel number (1-4)
        
    Returns:
        Acquisition info dictionary or None if failed
    """
    scope = MSO4000(channel=channel)
    
    if not scope.connect():
        return None
    
    try:
        info = scope.get_acquisition_info()
        return info
    finally:
        scope.close()


def quick_save_raw_binary(channel: int = 1, filename: Optional[str] = None,
                          save_metadata: bool = True) -> Optional[str]:
    """
    Quick function to connect and save raw binary waveform data
    
    Args:
        channel: Channel number (1-4)
        filename: Output filename (auto-generated if None)
        save_metadata: Whether to save .metadata file with timing info
        
    Returns:
        Filename of saved binary file or None if failed
    """
    scope = MSO4000(channel=channel)
    
    if not scope.connect():
        return None
    
    try:
        return scope.save_raw_binary(filename=filename, save_metadata=save_metadata)
    finally:
        scope.close()


def quick_save_raw_csv(channel: int = 1, filename: Optional[str] = None) -> Optional[str]:
    """
    Quick function to connect and save raw waveform to CSV
    
    Args:
        channel: Channel number (1-4)
        filename: Output CSV filename (auto-generated if None)
        
    Returns:
        Filename of saved CSV file or None if failed
    """
    scope = MSO4000(channel=channel)
    
    if not scope.connect():
        return None
    
    try:
        return scope.save_raw_csv(filename=filename)
    finally:
        scope.close()


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("MSO4000 Library - Example Usage")
    print("=" * 70 + "\n")
    
    # Check connection
    print("[1] Checking connection...")
    success, info = check_connection()
    if success:
        print(f"✓ {info}\n")
    else:
        print(f"❌ {info}\n")
        exit(1)
    
    # Record waveforms
    print("[2] Recording waveforms...")
    scope = MSO4000(channel=1)
    
    if scope.connect():
        filename = scope.record_to_csv(max_records=5)  # Record 5 waveforms
        if filename:
            print(f"\n✓ Success! Data saved to: {filename}")
        scope.close()

