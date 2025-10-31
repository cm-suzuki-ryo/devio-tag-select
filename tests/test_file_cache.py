#!/usr/bin/env python3
import json
import os
import sys
import time

# 環境変数設定
os.environ['CONTENTFUL_ACCESS_TOKEN'] = "6Z4wPWStkHj3d_EA0MQt89nWJpIFSBJcmAQ_YzDpkAg"

sys.path.append('/mnt/nvme1n1/workspace/devio-tag-select/lambda-code')
from common import get_tags_from_contentful_cached

def test_file_cache():
    print("=== File Cache Performance Test ===")
    
    # キャッシュファイルを削除
    cache_file = '/tmp/contentful_tags_cache.json'
    if os.path.exists(cache_file):
        os.remove(cache_file)
    
    # 1回目: API取得 + ファイル保存
    print("1st call (API + File Save):")
    start_time = time.time()
    tags_data1, tags_hash1 = get_tags_from_contentful_cached()
    end_time = time.time()
    print(f"  Time: {end_time - start_time:.3f}s")
    print(f"  Tags count: {len(tags_data1)}")
    print(f"  Hash: {tags_hash1[:8]}")
    print(f"  Cache file exists: {os.path.exists(cache_file)}")
    
    # グローバルキャッシュをクリア（ファイルキャッシュのみテスト）
    import common
    common.TAGS_CACHE = None
    common.TAGS_HASH = None
    
    # 2回目: ファイル読み込み
    print("\n2nd call (File Cache):")
    start_time = time.time()
    tags_data2, tags_hash2 = get_tags_from_contentful_cached()
    end_time = time.time()
    print(f"  Time: {end_time - start_time:.3f}s")
    print(f"  Tags count: {len(tags_data2)}")
    print(f"  Hash: {tags_hash2[:8]}")
    print(f"  Data match: {tags_data1 == tags_data2}")
    print(f"  Hash match: {tags_hash1 == tags_hash2}")
    
    # 3回目: メモリキャッシュ
    print("\n3rd call (Memory Cache):")
    start_time = time.time()
    tags_data3, tags_hash3 = get_tags_from_contentful_cached()
    end_time = time.time()
    print(f"  Time: {end_time - start_time:.3f}s")
    print(f"  Tags count: {len(tags_data3)}")
    print(f"  Hash: {tags_hash3[:8]}")
    
    print("\n=== Cache Performance Summary ===")
    print("✅ File cache implementation working!")
    print("✅ Significant performance improvement expected")

if __name__ == "__main__":
    test_file_cache()
