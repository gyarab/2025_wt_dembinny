import os
import shutil
import sys
import time
import subprocess
import ctypes

DEFAULT_PATH = ""

# Optimal settings for your machine based on the benchmark
def strategy_fill_disk_optimal(filepath, bytes_to_add):
    chunk_size = 10 * 1024 * 1024  # 10 MB is your sweet spot
    mode = 'ab' if os.path.exists(filepath) else 'wb'
    
    with open(filepath, mode) as f:
        written = 0
        # Pre-allocate the memory buffer once
        data_chunk = b'\0' * chunk_size
        
        while written < bytes_to_add:
            remaining = bytes_to_add - written
            if remaining < chunk_size:
                f.write(b'\0' * remaining)
                written += remaining
            else:
                f.write(data_chunk)
                written += chunk_size

# --- Strategy 1: Standard Writer (10MB Chunks) ---
def strategy_standard(filepath, bytes_to_add):
    chunk_size = 10 * 1024 * 1024  # 10 MB
    _write_chunks(filepath, bytes_to_add, chunk_size)

# --- Strategy 2: Large Buffer Writer (100MB Chunks) ---
# Often faster on modern HDDs/SSDs by reducing OS call overhead
def strategy_large_chunk(filepath, bytes_to_add):
    chunk_size = 100 * 1024 * 1024  # 100 MB
    _write_chunks(filepath, bytes_to_add, chunk_size)

# --- Strategy 3: Unbuffered / Raw IO (Advanced) ---
# Uses unbuffered binary IO. Can be faster or slower depending on OS caching.
def strategy_unbuffered(filepath, bytes_to_add):
    chunk_size = 10 * 1024 * 1024
    # 0 buffer size turns off buffering
    _write_chunks(filepath, bytes_to_add, chunk_size, buffering=0)

# ==========================================
# STRATEGY 1: Fast Allocation (Recommended)
# ==========================================
def strategy_fast_allocate(filepath, bytes_to_add):
    """
    Extends the file size instantly using the filesystem table.
    On NTFS, this reserves the space (lowering free space) without 
    physically writing zeros to every block.
    Speed: Extremely Fast (GBs in milliseconds).
    """
    mode = 'ab' if os.path.exists(filepath) else 'wb'
    with open(filepath, mode) as f:
        # Get current position (size)
        f.seek(0, os.SEEK_END)
        current_size = f.tell()
        
        # Calculate new total size
        new_size = current_size + bytes_to_add
        
        # Truncate essentially "resizes" the file.
        # The OS reserves the clusters immediately.
        f.truncate(new_size)

# ==========================================
# STRATEGY 2: Random Data (Secure/No Compression)
# ==========================================
def strategy_random(filepath, bytes_to_add):
    """
    Writes random bytes. Useful if your disk controller compresses data.
    Speed: Slow (High CPU usage).
    """
    chunk_size = 10 * 1024 * 1024 # 10 MB
    mode = 'ab' if os.path.exists(filepath) else 'wb'
    
    with open(filepath, mode) as f:
        written = 0
        while written < bytes_to_add:
            remaining = bytes_to_add - written
            current_chunk_size = min(chunk_size, remaining)
            
            # os.urandom generates random bytes
            f.write(os.urandom(current_chunk_size))
            written += current_chunk_size
            
            # Simple progress
            sys.stdout.write(f"\rRandom Write: {written/bytes_to_add:.1%}")
            sys.stdout.flush()
    print()

# ==========================================
# STRATEGY 3: True NTFS Sparse File
# ==========================================
def strategy_sparse_ntfs(filepath, bytes_to_add):
    """
    Creates a 'Sparse File'. 
    WARNING: This increases 'File Size' but DOES NOT consume physical 
    disk space. It will NOT lower your 'Free Space' counter effectively.
    """
    # 1. Create/Open the file
    mode = 'ab' if os.path.exists(filepath) else 'wb'
    with open(filepath, mode) as f:
        pass # Just ensure it exists

    # 2. Mark as Sparse using Windows fsutil (Requires Admin usually)
    # This tells NTFS "don't actually allocate space for zeros"
    try:
        subprocess.run(f'fsutil sparse setflag "{filepath}"', shell=True, check=True)
    except subprocess.CalledProcessError:
        print("Warning: Could not set sparse flag (Are you Admin?). Proceeding anyway...")

    # 3. Seek and Write 1 byte at the end
    with open(filepath, 'r+b') as f:
        f.seek(0, os.SEEK_END)
        current_size = f.tell()
        target_size = current_size + bytes_to_add
        
        # We only write the LAST byte. Everything before it is a "hole".
        f.seek(target_size - 1)
        f.write(b'\0')

# --- Shared Helper for Writing ---
def _write_chunks(filepath, bytes_to_add, chunk_size, buffering=-1):
    mode = 'ab' if os.path.exists(filepath) else 'wb'
    try:
        with open(filepath, mode, buffering=buffering) as f:
            written = 0
            # Pre-create the chunk in memory to avoid overhead inside loop
            data_chunk = b'\0' * chunk_size
            
            while written < bytes_to_add:
                remaining = bytes_to_add - written
                
                if remaining < chunk_size:
                    # Create a smaller chunk for the final bits
                    f.write(b'\0' * remaining)
                    written += remaining
                else:
                    f.write(data_chunk)
                    written += chunk_size
                
                # Progress bar (optional, removing this makes it slightly faster)
                percent = (written / bytes_to_add) * 100
                sys.stdout.write(f"\rWriting: {percent:.1f}%")
                sys.stdout.flush()
                
        print("\nDone writing.")
    except IOError as e:
        print(f"\nIO Error: {e}")

# --- Main Logic ---
def manage_disk_space(target_free_gb, path="C:\\Users\\Public\\Documents", write_strategy=strategy_standard):
    """
    Adjusts the size of 'space_filler.dat' using a specific write_strategy.
    """
    dummy_filename = "space_filler.dat"
    file_path = os.path.join(path, dummy_filename)
    
    try:
        total, used, free = shutil.disk_usage(path)
    except FileNotFoundError:
        print(f"Error: Path '{path}' not found.")
        return

    target_free_bytes = int(target_free_gb * 1024**3)
    
    print(f"Current free: {free / 1024**3:.2f} GB | Target free: {target_free_gb:.2f} GB")

    if free > target_free_bytes:
        # FILL
        bytes_to_write = free - target_free_bytes
        print(f"Status: Filling disk. Writing {bytes_to_write / 1024**3:.2f} GB...")
        
        start_time = time.time()
        
        # === CALL THE INJECTED STRATEGY HERE ===
        write_strategy(file_path, bytes_to_write)
        
        elapsed = time.time() - start_time
        print(f"Time taken: {elapsed:.2f} seconds")
        
    elif free < target_free_bytes:
        # FREE (Shrink)
        bytes_to_recover = target_free_bytes - free
        print(f"Status: Freeing space. Reclaiming {bytes_to_recover / 1024**3:.2f} GB.")
        
        if os.path.exists(file_path):
            current_size = os.path.getsize(file_path)
            if current_size >= bytes_to_recover:
                new_size = current_size - bytes_to_recover
                with open(file_path, 'r+b') as f:
                    f.truncate(new_size)
                print("Space reclaimed.")
            else:
                print("Deleting file (partial reclaim).")
                os.remove(file_path)
        else:
            print("Error: Helper file does not exist.")
    else:
        print("Target matches current free space.")

    _, _, final_free = shutil.disk_usage(path)
    print(f"Final free space: {final_free / 1024**3:.2f} GB")

if __name__ == "__main__":
    sys.argv = sys.argv[1:]  # Remove script name from args
    # Get inputs from user
    target_path = input("Enter the path (e.g., C:\\ or /tmp): ").strip() if len(sys.argv) < 1 else DEFAULT_PATH
    # print(target_path)

    try:
        user_input = input("Enter amount of free space to leave (in GB): ")
        if not user_input:
            target_gb = 1_000_000_000
        else:
            target_gb = float(user_input) if len(sys.argv) < 1 else float(sys.argv[0])
        
        if target_gb < 0:
            target_gb = 1_000_000_000


        # Safety warning if target is extremely low
        if target_gb < 0.5 and len(sys.argv) < 1:
            confirm = input("WARNING: Leaving less than 0.5 GB free may crash the OS. Continue? (Y/n): ")
            if confirm.lower() == 'n':
                sys.exit()
        
        write_strategy = strategy_standard
        
        if not target_path:
            manage_disk_space(target_gb, write_strategy=write_strategy)
        else:
            manage_disk_space(target_gb, path=target_path, write_strategy=write_strategy)
        
    except ValueError:
        print("Invalid number entered.")