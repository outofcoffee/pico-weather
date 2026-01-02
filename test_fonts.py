import sys
sys.path.append('fonts')

try:
    import freesans18
    import freesans20
    import freesans24
    print("✓ All fonts imported successfully")
    print(f"freesans18: {freesans18.height()}px height")
    print(f"freesans20: {freesans20.height()}px height")
    print(f"freesans24: {freesans24.height()}px height")
except ImportError as e:
    print(f"✗ Font import failed: {e}")
except AttributeError as e:
    print(f"✗ Font module missing height() function: {e}")
