import sqlite3
import os
import subprocess
import sys

# Setup DB connection
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "unimarket.db")

def get_git_tracked_files():
    try:
        result = subprocess.run(['git', 'ls-files'], cwd=PROJECT_ROOT, capture_output=True, text=True)
        return set(result.stdout.splitlines())
    except Exception as e:
        print(f"Error running git: {e}")
        return set()

def check_images():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n=== CHECKING IMAGE ISSUES ===")
    cursor.execute("SELECT id, product_id, image_url FROM product_images")
    
    tracked_files = get_git_tracked_files()
    print(f"Total git tracked files: {len(tracked_files)}")
    
    issues = []
    
    for row in cursor.fetchall():
        img_id, product_id, image_url = row
        
        if image_url.startswith("/uploads/products/"):
            filename = image_url.replace("/uploads/products/", "")
            # Construct relative path from project root for git check
            rel_path = f"backend/uploads/products/{filename}"
            abs_path = os.path.join(PROJECT_ROOT, rel_path)
            
            # 1. Check if file exists (Case Insensitive - Windows default)
            exists = os.path.exists(abs_path)
            
            # 2. Check Case Sensitivity (Crucial for Linux/Render)
            actual_case_filename = None
            if exists:
                directory = os.path.dirname(abs_path)
                files_in_dir = os.listdir(directory)
                for f in files_in_dir:
                    if f.lower() == filename.lower():
                        actual_case_filename = f
                        break
            
            case_match = (filename == actual_case_filename) if actual_case_filename else False
            
            # 3. Check if tracked by git
            is_tracked = rel_path in tracked_files
            
            if not exists:
                print(f"❌ MISSING FILE: {filename} (Product {product_id})")
                issues.append("missing")
            elif not case_match:
                print(f"⚠️ CASE MISMATCH: DB='{filename}' vs FS='{actual_case_filename}' (Product {product_id})")
                print(f"   -> Will FAIL on Render (Linux)")
                issues.append("case_mismatch")
            elif not is_tracked:
                print(f"⚠️ NOT IN GIT: {filename} (Product {product_id})")
                print(f"   -> Will NOT be deployed to Render")
                issues.append("not_tracked")
            else:
                # print(f"✅ OK: {filename}")
                pass

    print(f"\n=== SUMMARY ===")
    if not issues:
        print("✅ All images look good! (Exist, Case Matches, Tracked in Git)")
    else:
        print(f"Found {len(issues)} issues.")

    conn.close()

if __name__ == "__main__":
    check_images()
