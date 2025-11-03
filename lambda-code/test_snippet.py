#!/usr/bin/env python3
import json

def truncate_snippet(text, max_length=160):
    """スニペットを指定文字数で切り詰め"""
    if len(text) <= max_length:
        return text
    
    # 文末で切り詰め
    truncated = text[:max_length]
    
    # 最後の句読点で切る
    last_period = max(truncated.rfind('。'), truncated.rfind('！'), truncated.rfind('？'))
    if last_period > max_length * 0.7:  # 70%以上の位置にある場合
        return truncated[:last_period + 1]
    
    # 句読点がない場合は「...」で終了
    return truncated[:max_length - 3] + "..."

# テスト
test_text = "AWS Lambdaは、サーバーを管理することなくコードを実行できるコンピューティングサービスです。従来のサーバー管理の手間を省き、開発者はビジネスロジックに集中できます。この記事では、Lambda関数の作成から実際のデプロイまでの手順を詳しく解説します。"

result = truncate_snippet(test_text, 160)
print(f"Original length: {len(test_text)}")
print(f"Truncated length: {len(result)}")
print(f"Result: {result}")
