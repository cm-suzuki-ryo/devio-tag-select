#!/bin/bash

# MeCab Lambda Layer 作成スクリプト
mkdir -p mecab-layer/python/lib/python3.11/site-packages
cd mecab-layer

# MeCabバイナリとライブラリをダウンロード
wget https://github.com/SamuraiT/mecab-python3/releases/download/v1.0.6/mecab-python3-1.0.6.tar.gz
tar -xzf mecab-python3-1.0.6.tar.gz

# Python用MeCabをインストール
pip install mecab-python3 -t python/lib/python3.11/site-packages/

# 辞書ファイルをダウンロード
mkdir -p opt/mecab/dic
cd opt/mecab/dic
wget https://github.com/taku910/mecab/releases/download/mecab-0.996/mecab-ipadic-2.7.0-20070801.tar.gz
tar -xzf mecab-ipadic-2.7.0-20070801.tar.gz

cd ../../../

# レイヤーZIPファイルを作成
zip -r mecab-layer.zip python/ opt/

echo "MeCab Lambda Layer created: mecab-layer.zip"
