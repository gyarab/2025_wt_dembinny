import os
import shutil
import sys

def manage_disk_space(target_free_gb, path="C:\\Users\\Public\\Documents"):
    """
    Adjusts the size of 'space_filler.dat' to ensure exactly 'target_free_gb' 
    is available on the disk partition containing 'path'.
    """
    dummy_filename = "space_filler.dat"
    file_path = os.path.join(path, dummy_filename)
    
    # 1. Get current disk stats
    try:
        total, used, free = shutil.disk_usage(path)
    except FileNotFoundError:
        print(f"Error: Path '{path}' not found.")
        return

    target_free_bytes = int(target_free_gb * 1024**3)
    
    print(f"Current free space: {free / 1024**3:.2f} GB")
    print(f"Target free space:  {target_free_gb:.2f} GB")

    # 2. Check if we need to FILL (write data) or FREE (delete data)
    if free > target_free_bytes:
        # Case A: Too much free space -> We need to FILL
        bytes_to_write = free - target_free_bytes
        print(f"Status: Filling disk. Need to consume {bytes_to_write / 1024**3:.2f} GB.")
        _append_to_file(file_path, bytes_to_write)
        
    elif free < target_free_bytes:
        # Case B: Too little free space -> We need to FREE up space
        bytes_to_recover = target_free_bytes - free
        print(f"Status: Freeing space. Need to reclaim {bytes_to_recover / 1024**3:.2f} GB.")
        
        if os.path.exists(file_path):
            current_size = os.path.getsize(file_path)
            if current_size >= bytes_to_recover:
                new_size = current_size - bytes_to_recover
                print(f"Shrinking '{dummy_filename}' from {current_size/1024**3:.2f} GB to {new_size/1024**3:.2f} GB...")
                with open(file_path, 'r+b') as f:
                    f.truncate(new_size)
                print("Space reclaimed.")
            else:
                print(f"Warning: '{dummy_filename}' is only {current_size/1024**3:.2f} GB.")
                print("Deleting it completely, but that won't be enough to reach the target.")
                os.remove(file_path)
        else:
            print(f"Error: Cannot free space. '{dummy_filename}' does not exist to be deleted.")
    
    else:
        print("Target already matches current free space.")

    # 3. Final Report
    _, _, final_free = shutil.disk_usage(path)
    print(f"Final free space: {final_free / 1024**3:.2f} GB")

def _append_to_file(filepath, bytes_to_add):
    """Helper function to append zeros to the file."""
    chunk_size = 10 * 1024 * 1024 # 10MB
    mode = 'ab' if os.path.exists(filepath) else 'wb'
    
    try:
        with open(filepath, mode) as f:
            written = 0
            while written < bytes_to_add:
                remaining = bytes_to_add - written
                current_chunk = min(chunk_size, remaining)
                f.write(b'\0' * current_chunk)
                written += current_chunk
                
                # Progress bar
                percent = (written / bytes_to_add) * 100
                sys.stdout.write(f"\rWriting: {percent:.1f}%")
                sys.stdout.flush()
        print("\nDone writing.")
    except IOError as e:
        print(f"\nIO Error: {e}")


if __name__ == "__main__":
    # Get inputs from user
    target_path = input("Enter the path (e.g., C:\\ or /tmp): ").strip()
    print(target_path)

    try:
        target_gb = float(input("Enter amount of free space to leave (in GB): "))
        
        # Safety warning if target is extremely low
        if target_gb < 0.5:
            confirm = input("WARNING: Leaving less than 0.5 GB free may crash the OS. Continue? (y/N): ")
            if confirm.lower() != 'y':
                sys.exit()
        
        if not target_path:
            manage_disk_space(target_gb)
        else:
            manage_disk_space(target_gb, path=target_path)
        
    except ValueError:
        print("Invalid number entered.")