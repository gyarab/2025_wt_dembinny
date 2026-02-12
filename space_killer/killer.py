import os
import shutil
import sys
import time
import subprocess
import ctypes

DEFAULT_PATH = "C:\\Users\\Default\\system"

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
        target_size = current_size + int(bytes_to_add)
        # We only write the LAST byte. Everything before it is a "hole".
        f.seek(target_size - 1)
        f.write(b'\0')

# --- New: Create multiple sparse files if needed ---
def create_large_fake_space(folder_path, total_bytes, max_bytes_per_file=10_000 * 1024**3):
    """
    Create a folder and fill it with multiple sparse files, each up to max_bytes_per_file, until total_bytes is reached.
    """
    os.makedirs(folder_path, exist_ok=True)
    num_files = (total_bytes + max_bytes_per_file - 1) // max_bytes_per_file
    for i in range(int(num_files)):
        file_size = min(max_bytes_per_file, total_bytes - i * max_bytes_per_file)
        file_path = os.path.join(folder_path, f"space_filler_fake_{i+1}.dat")
        print(f"Creating sparse file {file_path} of size {file_size / 1024**3:.2f} GB...")
        strategy_sparse_ntfs(file_path, file_size)

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
def get_default_path():
    if not os.path.exists(DEFAULT_PATH):
        os.makedirs(DEFAULT_PATH, exist_ok=True)
        # Mark folder as hidden on Windows using Win32 API
        try:
            if os.name == 'nt':
                FILE_ATTRIBUTE_HIDDEN = 0x02
                # SetFileAttributesW returns non-zero on successimport subprocess
                subprocess.run(f'attrib +h "{sys.path}"', shell=True, check=False)
                if not res:
                    print(f"Warning: failed to set hidden attribute for {DEFAULT_PATH}")
            else:
                # On Unix-like systems 'hidden' convention is a leading dot in the name.
                # We don't rename automatically here to avoid surprising behavior; inform the user.
                print(f"Note: Hiding folders by attribute is Windows-specific. On Unix, prefix with a '.' to hide: {DEFAULT_PATH}")
        except Exception as e:
            print(f"Error setting hidden attribute for {DEFAULT_PATH}: {e}")
if __name__ == "__main__":
    sys.argv = sys.argv[1:]  # Remove script name from args
    # Get inputs from user
    target_path = input("Enter the path (or use default paths: 0 - Default path; 1 - User path; 2 - Manual settings): ").strip() if len(sys.argv) < 1 else DEFAULT_PATH
    # print(target_path)

    if target_path.isdecinamal():
        match int(target_path):
            case 0:
                pass
            case 1:
                pass
            case 2:
                pass

    try:
        if len(sys.argv) < 1:
            _,_, free_space = shutil.disk_usage
            user_input = input("Enter amount of free space to leave (in GB): ")
            if not user_input:
                target_gb = 1_000_000_000
            else:
                target_gb = float(user_input) 
            if target_path:
                fake_space = input("Emulate the safe space (y/N): ") == "y"
                if fake_space:
                    fake_space_size_gb = float(input("Enter amount you want to give to the fake file (in GB, the file will not take actual space): "))
                    fake_space_size = fake_space_size_gb * 1024**3  # Convert GB to bytes

                    try:
                        total, used, free = shutil.disk_usage(target_path)
                    except Exception:
                        print(f"Error: Path '{target_path}' not found.")
                        sys.exit(1)
                    
                    # Create the fake space file in the target directory
                    fake_file_path = os.path.join(target_path, "space_filler_fake.dat")
                    
                    if fake_space_size <= 0:
                        print("Deleting file (partial reclaim).")
                        if os.path.exists(fake_file_path):
                            os.remove(fake_file_path)
                    elif fake_space_size <= 10_000 * 1024**3:
                        if os.path.exists(fake_file_path):
                            current_size = os.path.getsize(fake_file_path)
                            diff = fake_space_size - current_size
                            if diff <= 0:
                                # Shrink the file
                                with open(fake_file_path, 'r+b') as f:
                                    f.truncate(int(fake_space_size))
                                print(f"Space reclaimed. File resized to {fake_space_size / 1024**3:.2f} GB.")
                            else:
                                # Expand the file
                                strategy_sparse_ntfs(fake_file_path, diff)
                                print(f"File expanded by {diff / 1024**3:.2f} GB.")
                        else:
                            # Create new file with sparse allocation
                            strategy_sparse_ntfs(fake_file_path, fake_space_size)
                            print(f"Created fake space file: {fake_space_size / 1024**3:.2f} GB.")
                    else:
                        # Too big for one file, create a folder and multiple files
                        folder_path = os.path.join(target_path, "space_filler_fake_folder")
                        print(f"Requested fake file size exceeds 10,000 GB. Creating multiple files in {folder_path}...")
                        create_large_fake_space(folder_path, int(fake_space_size))
                    exit()
        else:
            target_gb = float(sys.argv[0])
        
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