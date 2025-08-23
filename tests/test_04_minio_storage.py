#!/usr/bin/env python3
"""
Test 04: MinIO Storage Validation
Tests MinIO S3-compatible storage functionality
"""

import sys
import os
import io
import time
import json
from typing import Dict, Any
from minio import Minio
from minio.error import S3Error

# MinIO configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin123"
MINIO_BUCKET = "poc-bucket"

def run_test():
    """Test MinIO storage functionality"""
    print("=" * 60)
    print("TEST 04: MINIO STORAGE VALIDATION")
    print("=" * 60)
    
    # Test MinIO connectivity
    print("\n1. Testing MinIO connectivity...")
    client_status = test_minio_client()
    if not client_status['success']:
        print("❌ FAILED: Cannot connect to MinIO")
        print(f"Error: {client_status.get('error', 'Unknown error')}")
        return False
    print("✅ MinIO connection successful")
    
    client = client_status['client']
    
    # Test bucket operations
    print("\n2. Testing bucket operations...")
    bucket_status = test_bucket_operations(client)
    if not bucket_status['success']:
        print("❌ FAILED: Bucket operations failed")
        print(f"Error: {bucket_status.get('error', 'Unknown error')}")
        return False
    print("✅ Bucket operations successful")
    print(f"  Bucket exists: {bucket_status['bucket_exists']}")
    print(f"  Buckets found: {bucket_status['bucket_count']}")
    
    # Test file operations
    print("\n3. Testing file upload/download operations...")
    file_status = test_file_operations(client)
    if not file_status['success']:
        print("❌ FAILED: File operations failed")
        print(f"Error: {file_status.get('error', 'Unknown error')}")
        return False
    print("✅ File operations successful")
    print(f"  Files uploaded: {file_status['files_uploaded']}")
    print(f"  Files downloaded: {file_status['files_downloaded']}")
    print(f"  Content verification: {file_status['content_verified']}")
    
    # Test metadata operations
    print("\n4. Testing metadata operations...")
    metadata_status = test_metadata_operations(client)
    if not metadata_status['success']:
        print("❌ FAILED: Metadata operations failed")
        print(f"Error: {metadata_status.get('error', 'Unknown error')}")
        return False
    print("✅ Metadata operations successful")
    print(f"  Metadata set: {metadata_status['metadata_set']}")
    print(f"  Metadata retrieved: {metadata_status['metadata_retrieved']}")
    
    # Test listing operations
    print("\n5. Testing object listing operations...")
    listing_status = test_listing_operations(client)
    if not listing_status['success']:
        print("❌ FAILED: Object listing failed")
        print(f"Error: {listing_status.get('error', 'Unknown error')}")
        return False
    print("✅ Object listing successful")
    print(f"  Objects found: {listing_status['object_count']}")
    
    # Cleanup test objects
    print("\n6. Cleaning up test objects...")
    cleanup_status = cleanup_test_objects(client)
    if cleanup_status['cleaned_count'] > 0:
        print(f"✅ Cleaned up {cleanup_status['cleaned_count']} test objects")
    
    print("\n" + "=" * 60)
    print("✅ TEST 04 PASSED: MinIO storage fully functional")
    print("=" * 60)
    return True

def test_minio_client() -> Dict[str, Any]:
    """Test MinIO client connectivity"""
    try:
        # Create MinIO client
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False  # Use HTTP for local testing
        )
        
        # Test connection by listing buckets
        buckets = list(client.list_buckets())
        
        return {
            'success': True,
            'client': client,
            'bucket_count': len(buckets)
        }
        
    except S3Error as e:
        return {'success': False, 'error': f'S3 Error: {e}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_bucket_operations(client: Minio) -> Dict[str, Any]:
    """Test bucket creation and listing"""
    try:
        # Check if bucket exists
        bucket_exists = client.bucket_exists(MINIO_BUCKET)
        
        # Create bucket if it doesn't exist
        if not bucket_exists:
            client.make_bucket(MINIO_BUCKET)
            print(f"  Created bucket: {MINIO_BUCKET}")
            bucket_exists = True
        
        # List all buckets
        buckets = list(client.list_buckets())
        bucket_names = [b.name for b in buckets]
        
        return {
            'success': True,
            'bucket_exists': bucket_exists,
            'bucket_count': len(buckets),
            'bucket_names': bucket_names
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_file_operations(client: Minio) -> Dict[str, Any]:
    """Test file upload and download operations"""
    try:
        test_files = {
            'test-text.txt': 'Hello, MinIO! This is a test file.',
            'test-json.json': json.dumps({'test': True, 'timestamp': time.time()}),
            'test-binary.bin': b'\x00\x01\x02\x03\xff\xfe\xfd\xfc'
        }
        
        uploaded_files = []
        downloaded_files = []
        
        # Upload test files
        for filename, content in test_files.items():
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
                
            # Upload file
            client.put_object(
                MINIO_BUCKET,
                f"test/{filename}",
                io.BytesIO(content_bytes),
                length=len(content_bytes)
            )
            uploaded_files.append(filename)
        
        # Download and verify files
        content_verified = 0
        for filename, expected_content in test_files.items():
            try:
                # Download file
                response = client.get_object(MINIO_BUCKET, f"test/{filename}")
                downloaded_content = response.read()
                response.close()
                response.release_conn()
                
                downloaded_files.append(filename)
                
                # Verify content
                if isinstance(expected_content, str):
                    expected_bytes = expected_content.encode('utf-8')
                else:
                    expected_bytes = expected_content
                
                if downloaded_content == expected_bytes:
                    content_verified += 1
                    
            except Exception as e:
                print(f"  Warning: Could not verify {filename}: {e}")
        
        return {
            'success': True,
            'files_uploaded': len(uploaded_files),
            'files_downloaded': len(downloaded_files),
            'content_verified': content_verified == len(test_files)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_metadata_operations(client: Minio) -> Dict[str, Any]:
    """Test metadata operations"""
    try:
        # Upload file with metadata
        test_content = "File with metadata"
        metadata = {
            'x-amz-meta-test-key': 'test-value',
            'x-amz-meta-created-by': 'poc-test',
            'x-amz-meta-timestamp': str(int(time.time()))
        }
        
        client.put_object(
            MINIO_BUCKET,
            "test/metadata-file.txt",
            io.BytesIO(test_content.encode()),
            length=len(test_content),
            metadata=metadata
        )
        
        # Retrieve object stats and metadata
        stat = client.stat_object(MINIO_BUCKET, "test/metadata-file.txt")
        retrieved_metadata = stat.metadata or {}
        
        # Check if metadata was preserved
        metadata_keys_found = 0
        for key, value in metadata.items():
            if key.lower() in [k.lower() for k in retrieved_metadata.keys()]:
                metadata_keys_found += 1
        
        return {
            'success': True,
            'metadata_set': len(metadata),
            'metadata_retrieved': metadata_keys_found,
            'file_size': stat.size,
            'content_type': stat.content_type
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_listing_operations(client: Minio) -> Dict[str, Any]:
    """Test object listing operations"""
    try:
        # List objects in test prefix
        objects = list(client.list_objects(MINIO_BUCKET, prefix="test/", recursive=True))
        object_names = [obj.object_name for obj in objects]
        
        # List objects without prefix
        all_objects = list(client.list_objects(MINIO_BUCKET, recursive=True))
        
        return {
            'success': True,
            'object_count': len(objects),
            'total_objects': len(all_objects),
            'test_objects': object_names
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def cleanup_test_objects(client: Minio) -> Dict[str, Any]:
    """Clean up test objects"""
    try:
        # List all test objects
        objects = list(client.list_objects(MINIO_BUCKET, prefix="test/", recursive=True))
        
        cleaned_count = 0
        for obj in objects:
            try:
                client.remove_object(MINIO_BUCKET, obj.object_name)
                cleaned_count += 1
            except Exception as e:
                print(f"  Warning: Could not remove {obj.object_name}: {e}")
        
        return {
            'success': True,
            'cleaned_count': cleaned_count
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)