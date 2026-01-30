import shutil
import os

# Source is the extension integration folder
src = "d:/Projects/Prj/InductionExtension"

# Destination is inside our app's documents folder
dst_base = "d:/Projects/Induction App/Gemini Test/New folder/documents/InductionExtension"

print(f"Zipping {src} to {dst_base}.zip...")
try:
    shutil.make_archive(dst_base, 'zip', src)
    print("Success! Created zip file.")
except Exception as e:
    print(f"Error: {e}")
