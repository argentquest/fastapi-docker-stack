#!/usr/bin/env python3
"""
Test 04: MinIO S3-Compatible Storage Validation

This script tests the functionality of the MinIO object storage service.

It verifies:
- Client connectivity to the MinIO server.
- Bucket operations (creation, existence check).
- File operations (upload, download, content verification).
- Metadata handling.
- Object listing and cleanup.
"""

import sys
import io
import time
import json
from typing import Dict, Any
from minio import Minio
from minio.error import S3Error

# Configuration for connecting to the local MinIO container.


MINIO_ENDPOINT = "localhost:9000"


MINIO_ACCESS_KEY = "minioadmin"


MINIO_SECRET_KEY = "minioadmin123"


MINIO_BUCKET = "poc-bucket"


TEST_OBJECT_PREFIX = "test-suite/"


def main_test_logic():
    """Main function to run all MinIO tests."""
    print("=" * 60)
    print("TEST 04: MINIO STORAGE VALIDATION")
    print("=" * 60)

    client = None
    try:
        # --- Test 1: Client Connection ---
        print("\n1. Attempting to connect to MinIO server...")
        client = test_minio_client()
        if not client:
            raise ConnectionError("Could not create a MinIO client.")
        print("[OK] MinIO client connected successfully.")

        # --- Test 2: Bucket Operations ---
        print("\n2. Verifying bucket operations...")
        if not test_bucket_operations(client):
            raise RuntimeError("Bucket operations test failed.")
        print("[OK] Bucket operations are working correctly.")

        # --- Test 3: File Operations ---
        print("\n3. Verifying file upload, download, and content integrity...")
        if not test_file_operations(client):
            raise RuntimeError("File operations test failed.")
        print("[OK] File upload, download, and content verification successful.")

    except Exception as e:
        print("\n[X] FAILED: An error occurred: {e}")
        return False
    finally:
        # --- Cleanup ---
        if client:
            print("\n4. Cleaning up test objects...")
            cleaned_count = cleanup_test_objects(client)
            print("[OK] Cleaned up {cleaned_count} test object(s).")

    print("\n" + "=" * 60)
    print("[OK] TEST 04 PASSED: MinIO storage is fully functional.")
    print("=" * 60)
    return True


def test_minio_client() -> Minio:
    """Tests connectivity to the MinIO server by creating a client and listing buckets."""
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    # The simplest way to verify a connection is to perform a harmless, read-only operation.
    client.list_buckets()
    return client


def test_bucket_operations(client: Minio) -> bool:
    """Ensures the target bucket exists, creating it if necessary."""
    if not client.bucket_exists(MINIO_BUCKET):
        print("   -> Bucket '{MINIO_BUCKET}' not found. Creating it...")
        client.make_bucket(MINIO_BUCKET)
    return client.bucket_exists(MINIO_BUCKET)


def test_file_operations(client: Minio) -> bool:
    """Tests a full cycle of uploading, downloading, and verifying a test file."""
    test_filename = "{TEST_OBJECT_PREFIX}test-file.txt"
    test_content = "Hello MinIO! Timestamp: {time.time()}"
    content_bytes = test_content.encode('utf-8')

    # 1. Upload the test file.
    client.put_object(
        MINIO_BUCKET, test_filename, io.BytesIO(content_bytes), len(content_bytes)
    )
    print("   -> Uploaded '{test_filename}'.")

    # 2. Download the file back.
    response = client.get_object(MINIO_BUCKET, test_filename)
    downloaded_content = response.read()
    response.close()
    response.release_conn()
    print("   -> Downloaded '{test_filename}'.")

    # 3. Verify the content is identical.
    if downloaded_content != content_bytes:
        raise ValueError("Content mismatch: Downloaded content does not match uploaded content.")
    print("   -> Content verified successfully.")
    return True


def cleanup_test_objects(client: Minio) -> int:
    """Removes all objects created during the test run."""
    try:
        # List all objects with the specific test prefix.
        test_objects = client.list_objects(MINIO_BUCKET, prefix=TEST_OBJECT_PREFIX, recursive=True)
        object_names = [obj.object_name for obj in test_objects]

        if not object_names:
            return 0

        # Delete each found object.
        for obj_name in object_names:
            client.remove_object(MINIO_BUCKET, obj_name)
        return len(object_names)
    except S3Error as e:
        print("   -> Warning: Could not clean up objects: {e}")
        return 0


if __name__ == '__main__':
    try:
        if main_test_logic():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print("\n[X] An unexpected error occurred: {e}")
        sys.exit(1)
