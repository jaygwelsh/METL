#!/usr/bin/env python3
import os
import sys
import time
import argparse
import platform
import json
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import hashlib

def generate_key_pair():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

def sign_data(data_str, private_key):
    signature = private_key.sign(data_str.encode('utf-8'))
    return signature

def verify_signature(data_str, signature, public_key):
    try:
        public_key.verify(signature, data_str.encode('utf-8'))
        return True
    except Exception:
        return False

def create_test_file(file_path):
    content = b"stable file content for hashing"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(content)

def compute_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(16384), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def embed_metadata(file_path, metadata_dict, private_key):
    # Compute file hash
    file_hash = compute_file_hash(file_path)
    metadata_dict["file_hash"] = file_hash

    # Sort and sign the metadata (without signature field)
    metadata_json = json.dumps(metadata_dict, sort_keys=True)
    signature = sign_data(metadata_json, private_key)

    # Add signature to metadata
    metadata_dict["signature"] =  signature.hex()  # Store as hex to avoid issues

    # Write to sidecar
    sidecar_path = f"{file_path}.metl.json"
    with open(sidecar_path, "w") as f:
        json.dump(metadata_dict, f, sort_keys=True)

def verify_metadata(file_path, public_key):
    sidecar_path = f"{file_path}.metl.json"
    if not os.path.exists(sidecar_path):
        print("No sidecar found.")
        return False

    with open(sidecar_path, "r") as f:
        extracted_metadata = json.load(f)

    file_hash = compute_file_hash(file_path)
    if file_hash != extracted_metadata.get("file_hash"):
        print("File hash mismatch.")
        return False

    signature_hex = extracted_metadata.pop("signature", None)
    if not signature_hex:
        print("No signature found in sidecar.")
        return False

    # Convert hex signature back to bytes
    signature = bytes.fromhex(signature_hex)
    metadata_json = json.dumps(extracted_metadata, sort_keys=True)

    return verify_signature(metadata_json, signature, public_key)

def batch_embed(file_path, private_key, iterations=5, batch_size=1):
    stable_metadata = {"fixed_tag": "benchmark"}
    times = []
    for i in range(iterations):
        sidecar = f"{file_path}.metl.json"
        if os.path.exists(sidecar):
            os.remove(sidecar)

        start = time.time()
        for _ in range(batch_size):
            embed_metadata(file_path, stable_metadata.copy(), private_key)
        end = time.time()
        elapsed = end - start
        times.append(elapsed)
        print(f"Embedding batch {i+1}/{iterations} took {elapsed:.4f}s")
    return times

def batch_verify(file_path, public_key, iterations=5, batch_size=1):
    times = []
    for i in range(iterations):
        start = time.time()
        for _ in range(batch_size):
            result = verify_metadata(file_path, public_key)
            if not result:
                print("Verification failed unexpectedly.")
                sidecar = f"{file_path}.metl.json"
                if os.path.exists(sidecar):
                    with open(sidecar, "rb") as f:
                        sidecar_content = f.read()
                    print("Sidecar content:", sidecar_content)
                # Print debugging info:
                # Reload metadata:
                if os.path.exists(sidecar):
                    with open(sidecar, "r") as scf:
                        extracted_metadata = json.load(scf)
                    sig_hex = extracted_metadata.pop("signature", None)
                    metadata_json = json.dumps(extracted_metadata, sort_keys=True)
                    print("Metadata JSON being verified:", metadata_json)
                    print("Signature hex:", sig_hex)
                    print("Public key:", public_key)
                raise RuntimeError("Verification failed. Stopping benchmark.")
        end = time.time()
        elapsed = end - start
        times.append(elapsed)
        print(f"Verification batch {i+1}/{iterations} took {elapsed:.4f}s")
    return times

def summarize(times):
    if not times:
        return {"min": 0, "max": 0, "avg": 0, "total": 0}
    return {
        "min": min(times),
        "max": max(times),
        "avg": sum(times) / len(times),
        "total": sum(times)
    }

def print_summary(embed_stats, verify_stats, embed_iterations, verify_iterations, embed_batch, verify_batch):
    print("\n=== Benchmark Summary ===")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Embedding Iterations: {embed_iterations}, Batch Size: {embed_batch}")
    print(f"Verification Iterations: {verify_iterations}, Batch Size: {verify_batch}")

    print("\nEmbedding Times (seconds):")
    print(f"  Min:   {embed_stats['min']:.4f}")
    print(f"  Max:   {embed_stats['max']:.4f}")
    print(f"  Avg:   {embed_stats['avg']:.4f}")
    print(f"  Total: {embed_stats['total']:.4f}")

    print("\nVerification Times (seconds):")
    print(f"  Min:   {verify_stats['min']:.4f}")
    print(f"  Max:   {verify_stats['max']:.4f}")
    print(f"  Avg:   {verify_stats['avg']:.4f}")
    print(f"  Total: {verify_stats['total']:.4f}\n")

def main():
    parser = argparse.ArgumentParser(description="Run a self-contained Ed25519 benchmark.")
    parser.add_argument("--embed-iterations", type=int, default=5)
    parser.add_argument("--verify-iterations", type=int, default=5)
    parser.add_argument("--embed-batch", type=int, default=1)
    parser.add_argument("--verify-batch", type=int, default=1)
    args = parser.parse_args()

    # Generate keys and test sign/verify in-memory
    private_key, public_key = generate_key_pair()

    test_msg = "test_message_for_sanity_check"
    sig = sign_data(test_msg, private_key)
    if not verify_signature(test_msg, sig, public_key):
        print("In-memory verification failed. Keys or environment are broken.")
        sys.exit(1)
    else:
        print("In-memory sign/verify check passed. Keys are good.")

    # Prepare file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "examples", "sample_files", "test.jpg")
    create_test_file(file_path)

    print("\nStarting Embedding Benchmark...\n")
    embed_times = batch_embed(file_path, private_key, iterations=args.embed_iterations, batch_size=args.embed_batch)

    print("\nStarting Verification Benchmark...\n")
    verify_times = batch_verify(file_path, public_key, iterations=args.verify_iterations, batch_size=args.verify_batch)

    embed_stats = summarize(embed_times)
    verify_stats = summarize(verify_times)
    print_summary(embed_stats, verify_stats, args.embed_iterations, args.verify_iterations, args.embed_batch, args.verify_batch)

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
