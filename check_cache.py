import os
from pathlib import Path

# Check Hugging Face cache
cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
print(f"Cache directory: {cache_dir}")
print(f"Exists: {cache_dir.exists()}")

# Check BGE model
bge_dir = cache_dir / "models--BAAI--bge-large-en-v1.5"
print(f"\nBGE model directory: {bge_dir}")
print(f"Model cached locally: {bge_dir.exists()}")

if bge_dir.exists():
    # Calculate size
    total_size = sum(f.stat().st_size for f in bge_dir.rglob('*') if f.is_file())
    print(f"Cache size: {total_size/1024/1024:.1f} MB")
    
    # Show some cached files
    print("\nCached files:")
    for i, file in enumerate(list(bge_dir.rglob('*.bin'))[:3]):
        size_mb = file.stat().st_size / 1024 / 1024
        print(f"  - {file.name}: {size_mb:.1f} MB")
    
    # Model weights file
    model_file = list(bge_dir.rglob('model.safetensors')) or list(bge_dir.rglob('pytorch_model.bin'))
    if model_file:
        print(f"\nModel weights: {model_file[0].name} ({model_file[0].stat().st_size/1024/1024:.1f} MB)")
        print("✅ Model is fully cached locally!")
else:
    print("❌ Model not cached - will download on first use")