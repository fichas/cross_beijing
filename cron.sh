#!/bin/bash

cd /path/to/cross_beijing
echo "开始执行续签"
python cross_bj.py 2>&1 >> /path/to/cross_beijing/logs/cross_bj.log
echo "续签完成"