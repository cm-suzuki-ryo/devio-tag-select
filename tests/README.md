# テスト環境

## Docker テスト

### Haiku テスト
```bash
docker build -f tests/Dockerfile.haiku-test -t haiku-test .
docker run --rm -e AWS_DEFAULT_REGION=ap-northeast-1 -v ~/.aws:/root/.aws:ro haiku-test
```

### Nova テスト
```bash
docker build -f tests/Dockerfile.nova-test -t nova-test .
docker run --rm -e AWS_DEFAULT_REGION=ap-northeast-1 -v ~/.aws:/root/.aws:ro nova-test
```

### GPT テスト
```bash
docker build -f tests/Dockerfile.gpt-test -t gpt-test .
docker run --rm -e AWS_DEFAULT_REGION=ap-northeast-1 -v ~/.aws:/root/.aws:ro gpt-test
```

## テストファイル

- `test_enhanced.py` - Haikuテスト
- `test_nova.py` - Novaテスト  
- `test_gpt.py` - GPTテスト
- `claude_env_code*.py` - Claude環境変数版テスト用コード

## 価格設定

環境変数で各モデルの価格を設定：
- `INPUT_PRICE_PER_MILLION` - 入力トークン価格（USD/100万トークン）
- `OUTPUT_PRICE_PER_MILLION` - 出力トークン価格（USD/100万トークン）
- `USD_TO_JPY` - 為替レート
