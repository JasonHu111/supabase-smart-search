#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
向量生成工具
为 embeddings 表中没有向量的记录生成向量

使用方法：
1. 复制 .env.example 为 .env.local
2. 填写你的 Supabase 配置
3. 运行: python scripts/generate_vectors.py
"""

import os
import requests
import time
import sys
from pathlib import Path

# ============================================
# 加载环境变量
# ============================================
def load_env():
    """从 .env.local 加载环境变量"""
    env_path = Path(__file__).parent.parent / '.env.local'
    env_vars = {}
    
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    else:
        print('⚠️ 未找到 .env.local 文件，请复制 .env.example 并配置')
        print('   cp .env.example .env.local')
        sys.exit(1)
    
    return env_vars

# 加载环境变量
env = load_env()
SUPABASE_URL = env.get('VITE_SUPABASE_URL')
SUPABASE_KEY = env.get('VITE_SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print('❌ 请在 .env.local 中配置 VITE_SUPABASE_URL 和 VITE_SUPABASE_ANON_KEY')
    sys.exit(1)


def get_records_without_embedding():
    """获取所有没有向量的记录"""
    url = f'{SUPABASE_URL}/rest/v1/embeddings?select=id,content&embedding=is.null'
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'❌ 获取记录失败: {e}')
        return []


def generate_embedding(record_id, content):
    """为单条记录生成向量"""
    url = f'{SUPABASE_URL}/functions/v1/generate-embedding'
    headers = {
        'Content-Type': 'application/json'
    }
    body = {
        'record': {
            'id': record_id,
            'content': content
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        return response
    except requests.exceptions.RequestException as e:
        print(f'   ❌ 请求失败: {e}')
        return None


def main():
    """主函数"""
    print('=' * 60)
    print('🔍 向量生成工具')
    print('=' * 60)
    print(f'📡 连接: {SUPABASE_URL}')
    
    # 获取需要生成向量的记录
    print('\n📊 检查数据状态...')
    records = get_records_without_embedding()
    
    if records is None:
        print('❌ 获取数据失败，请检查网络和配置')
        sys.exit(1)
    
    if not records:
        print('✅ 所有记录都已有向量！')
        return
    
    print(f'📝 找到 {len(records)} 条记录需要生成向量')
    
    # 确认是否继续
    print(f'\n⚠️  将为 {len(records)} 条记录生成向量，预计耗时 {len(records) * 0.6:.1f} 秒')
    confirm = input('是否继续？(y/n): ')
    if confirm.lower() != 'y':
        print('已取消')
        return
    
    # 为每条记录生成向量
    success = 0
    failed = 0
    failed_records = []
    
    print('\n🔄 开始生成向量...\n')
    
    for i, rec in enumerate(records, 1):
        print(f'[{i}/{len(records)}] 处理 ID {rec["id"]}...')
        print(f'   内容: {rec["content"][:50]}...')
        
        response = generate_embedding(rec['id'], rec['content'])
        
        if response and response.ok:
            print(f'   ✅ 成功')
            success += 1
        else:
            error_msg = response.text if response else '请求超时'
            print(f'   ❌ 失败: {error_msg}')
            failed += 1
            failed_records.append(rec['id'])
        
        # 避免请求过快
        time.sleep(0.5)
    
    # 输出结果
    print('\n' + '=' * 60)
    print(f'📊 完成！')
    print(f'   ✅ 成功: {success}')
    print(f'   ❌ 失败: {failed}')
    
    if failed_records:
        print(f'\n失败的记录 ID: {failed_records}')
        print('💡 可以重新运行脚本重试')


if __name__ == '__main__':
    main()