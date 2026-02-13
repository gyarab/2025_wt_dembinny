import os
from pathlib import Path
import shutil
import sys
import time
import subprocess
import ctypes
import argparse

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
        # os.makedirs(DEFAULT_PATH, exist_ok=True)
        subprocess.run(f'mkdir {DEFAULT_PATH}', shell=True, check=False)
        # Mark folder as hidden on Windows using Win32 API
        try:
            if os.name == 'nt':
                FILE_ATTRIBUTE_HIDDEN = 0x02
                # SetFileAttributesW returns non-zero on successimport subprocess
                res = subprocess.run(f'attrib +h "{sys.path}"', shell=True, check=False)
                if not res:
                    print(f"Warning: failed to set hidden attribute for {DEFAULT_PATH}")
            else:
                # On Unix-like systems 'hidden' convention is a leading dot in the name.
                # We don't rename automatically here to avoid surprising behavior; inform the user.
                print(f"Note: Hiding folders by attribute is Windows-specific. On Unix, prefix with a '.' to hide: {DEFAULT_PATH}")
        except Exception as e:
            print(f"Error setting hidden attribute for {DEFAULT_PATH}: {e}")
    return DEFAULT_PATH
def get_user_path():
    user_path = Path.home()
    return user_path


def parse_args(argv=None):
    """Parse CLI args.

    Mutually exclusive actions:
      - --keep: leave N GB free (fills or shrinks helper file)
      - --fill: add N GB by writing/reserving space (default helper file)
      - --free: delete helper file(s)
      - --fake: create sparse fake-space file(s)
    """
    p = argparse.ArgumentParser(
        prog="killer.py",
        description="Consume or reclaim disk space using a helper file (and optional sparse 'fake space' files).",
    )

    p.add_argument(
        "--path",
        "-p",
        default="C:\\Users\\Public\\Documents",
        help="Target directory to operate in (default: C:\\Users\\Public\\Documents)",
    )

    p.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive menu mode",
    )

    grp = p.add_mutually_exclusive_group(required=False)
    grp.add_argument("--keep", type=float, metavar="GB", help="Leave GB free (fills or frees to reach target)")
    grp.add_argument("--fill", type=float, metavar="GB", help="Fill additional GB (adds GB to helper file)")
    grp.add_argument("--free", action="store_true", help="Free everything created by this tool in the path")
    grp.add_argument(
        "--fake",
        type=float,
        metavar="GB",
        help="Create sparse fake-space file(s) totaling GB (won't consume physical space)",
    )

    p.add_argument(
        "--strategy",
        choices=["standard", "large", "unbuffered", "fast", "random"],
        default="standard",
        help="Write strategy for real fill/keep operations",
    )
    p.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmations",
    )
    p.add_argument(
        "--max-fake-file-gb",
        type=float,
        default=10_000,
        metavar="GB",
        help="Max size per fake sparse file before splitting (default: 10000)",
    )
    p.add_argument(
        "--fake-folder",
        default="space_filler_fake_folder",
        help="Folder name (under --path) for multi-file fake space (default: space_filler_fake_folder)",
    )

    args = p.parse_args(argv)
    if not args.interactive and args.keep is None and args.fill is None and not args.free and args.fake is None:
        p.error("one of --keep/--fill/--free/--fake is required unless --interactive is used")
    return args


def pick_strategy(name: str):
    return {
        "standard": strategy_standard,
        "large": strategy_large_chunk,
        "unbuffered": strategy_unbuffered,
        "fast": strategy_fast_allocate,
        "random": strategy_random,
    }[name]


def helper_file_path(path: str):
    return os.path.join(path, "space_filler.dat")


def free_everything(path: str):
    """Delete helper file and fake-space artifacts created by this tool."""
    hf = helper_file_path(path)
    if os.path.exists(hf):
        os.remove(hf)
        print(f"Removed {hf}")

    fake_file = os.path.join(path, "space_filler_fake.dat")
    if os.path.exists(fake_file):
        os.remove(fake_file)
        print(f"Removed {fake_file}")

    fake_folder = os.path.join(path, "space_filler_fake_folder")
    if os.path.isdir(fake_folder):
        # remove only known pattern files, then folder if empty
        for name in os.listdir(fake_folder):
            if name.startswith("space_filler_fake_") and name.endswith(".dat"):
                try:
                    os.remove(os.path.join(fake_folder, name))
                except OSError:
                    pass
        try:
            os.rmdir(fake_folder)
            print(f"Removed {fake_folder}")
        except OSError:
            print(f"Left {fake_folder} (not empty or locked)")


def ensure_path_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def apply_keep_free_gb(path: str, keep_gb: float, write_strategy):
    """Ensure that at least keep_gb remains free by filling/shrinking helper file."""
    ensure_path_exists(path)
    manage_disk_space(keep_gb, path=path, write_strategy=write_strategy)


def apply_fill_gb(path: str, fill_gb: float, write_strategy):
    """Fill additional GB by growing the helper file."""
    ensure_path_exists(path)
    bytes_to_add = int(fill_gb * 1024**3)
    hf = helper_file_path(path)
    print(f"Filling {fill_gb:.2f} GB at {hf}...")
    write_strategy(hf, bytes_to_add)


def apply_fake_gb(path: str, fake_gb: float, max_fake_file_gb: float, fake_folder_name: str):
    """Create sparse fake-space file(s) totaling fake_gb in the given path."""
    ensure_path_exists(path)
    if fake_gb <= 0:
        print("Fake size <= 0, nothing to do.")
        return

    total_bytes = int(fake_gb * 1024**3)
    max_bytes_per_file = int(max_fake_file_gb * 1024**3)

    if total_bytes <= max_bytes_per_file:
        fake_file_path = os.path.join(path, "space_filler_fake.dat")
        if os.path.exists(fake_file_path):
            current_size = os.path.getsize(fake_file_path)
            diff = total_bytes - current_size
            if diff == 0:
                print(f"Fake file already at requested size: {fake_gb:.2f} GB")
                return
            if diff < 0:
                with open(fake_file_path, "r+b") as f:
                    f.truncate(total_bytes)
                print(f"Shrunk fake file to {fake_gb:.2f} GB")
                return
            strategy_sparse_ntfs(fake_file_path, diff)
            print(f"Expanded fake file to {fake_gb:.2f} GB")
            return

        strategy_sparse_ntfs(fake_file_path, total_bytes)
        print(f"Created fake space file: {fake_gb:.2f} GB")
        return

    folder_path = os.path.join(path, fake_folder_name)
    print(
        f"Requested fake size {fake_gb:.2f} GB exceeds per-file max {max_fake_file_gb:.2f} GB. "
        f"Creating multiple files in {folder_path}..."
    )
    create_large_fake_space(folder_path, total_bytes, max_bytes_per_file=max_bytes_per_file)


def _prompt_float(prompt: str, default: float | None = None):
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return float(default)
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number.")


def _prompt_path(default_path: str):
    raw = input(
        "Path (enter 0=default hidden, 1=user home, or a full path) "
        f"[default: {default_path}]: "
    ).strip()
    if raw == "":
        return default_path
    if raw.isdecimal():
        match int(raw):
            case 0:
                return get_default_path()
            case 1:
                return str(get_user_path())
            case _:
                return default_path
    return raw


def run_interactive():
    """Interactive menu wrapper around the same actions as CLI."""
    print("SpaceKiller interactive mode")
    print("---------------------------")

    path = _prompt_path("C:\\Users\\Public\\Documents")

    print("\nChoose action:")
    print("  1) Keep N GB free")
    print("  2) Fill N GB")
    print("  3) Free everything")
    print("  4) Fake space (sparse) N GB")
    choice = input("Select [1-4]: ").strip()

    strat = "standard"
    if choice in {"1", "2"}:
        print("\nChoose write strategy:")
        print("  1) standard")
        print("  2) large")
        print("  3) unbuffered")
        print("  4) fast")
        print("  5) random")
        s = input("Select [1-5] (default 1): ").strip() or "1"
        strat = {"1": "standard", "2": "large", "3": "unbuffered", "4": "fast", "5": "random"}.get(s, "standard")
    write_strategy = pick_strategy(strat)

    if choice == "1":
        keep_gb = _prompt_float("Enter GB to keep free: ")
        if keep_gb < 0.5:
            c = input("WARNING: Leaving <0.5 GB free can crash Windows. Continue? (y/N): ").strip().lower()
            if c != "y":
                return
        apply_keep_free_gb(path, keep_gb, write_strategy)
        return

    if choice == "2":
        fill_gb = _prompt_float("Enter GB to fill: ")
        apply_fill_gb(path, fill_gb, write_strategy)
        return

    if choice == "3":
        confirm = input(f"Delete helper/fake files under '{path}'? (y/N): ").strip().lower()
        if confirm == "y":
            free_everything(path)
        return

    if choice == "4":
        fake_gb = _prompt_float("Enter fake sparse GB to create: ")
        max_file_gb = _prompt_float("Max GB per fake file [10000]: ", default=10_000)
        folder = input("Fake folder name [space_filler_fake_folder]: ").strip() or "space_filler_fake_folder"
        apply_fake_gb(path, fake_gb, max_file_gb, folder)
        return

    print("Invalid selection.")

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args.interactive:
        run_interactive()
        sys.exit(0)

    # resolve path shortcuts
    if isinstance(args.path, str) and args.path.isdecimal():
        match int(args.path):
            case 0:
                path = get_default_path()
            case 1:
                path = str(get_user_path())
            case _:
                path = get_default_path()
    else:
        path = args.path

    write_strategy = pick_strategy(args.strategy)

    # Safety warning if keeping extremely low free space
    if args.keep is not None and args.keep < 0.5 and not args.yes:
        confirm = input("WARNING: Leaving less than 0.5 GB free may crash the OS. Continue? (Y/n): ")
        if confirm.lower() == "n":
            sys.exit(1)

    if args.free:
        free_everything(path)
        sys.exit(0)

    if args.fake is not None:
        apply_fake_gb(path, args.fake, args.max_fake_file_gb, args.fake_folder)
        sys.exit(0)

    if args.fill is not None:
        apply_fill_gb(path, args.fill, write_strategy)
        sys.exit(0)

    if args.keep is not None:
        apply_keep_free_gb(path, args.keep, write_strategy)
        sys.exit(0)