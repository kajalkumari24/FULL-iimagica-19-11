import os
import zipfile
import shutil

def create_archive():
    base_dir = r"c:\Users\Hii\Downloads\full"
    output_zip = os.path.join(base_dir, "ai-footer-designer.zip")
    
    print(f"Creating archive {output_zip}...")
    include_roots = ["backend", "frontend", "docs"]
    include_files = ["BUILD_STATUS.md", "AGENTS.md", "README.md"]
    
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in include_files:
            fp = os.path.join(base_dir, f)
            if os.path.exists(fp):
                zf.write(fp, f)
                print(f"Added {f}")
        
        for root_name in include_roots:
            root_path = os.path.join(base_dir, root_name)
            for dirpath, dirnames, filenames in os.walk(root_path):
                # Filter out unnecessary directories
                dirnames[:] = [d for d in dirnames if d not in ["node_modules", ".git", "__pycache__", ".pytest_cache", "dist", "uploads"]]
                for fn in filenames:
                    if fn.endswith(".zip"):
                        continue
                    full_fp = os.path.join(dirpath, fn)
                    rel_fp = os.path.relpath(full_fp, base_dir)
                    zf.write(full_fp, rel_fp)
    
    size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"Successfully created: {output_zip} ({size_mb:.2f} MB)")

    # Attempt copy to Downloads root if accessible
    downloads_dest = r"C:\Users\Hii\Downloads\ai-footer-designer.zip"
    try:
        shutil.copy2(output_zip, downloads_dest)
        print(f"Copied to {downloads_dest}")
    except Exception as e:
        print(f"Note: Could not copy to {downloads_dest}: {e}")

if __name__ == "__main__":
    create_archive()
