#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author     :zhaoyukai
# @Time       :2025/11/11 14:53

"""

"""
import os

from datetime import datetime, timedelta
from .sync_cwbq import mongo_uri
from loguru import logger
from functools import lru_cache
from pymongo import MongoClient, ASCENDING

@lru_cache(maxsize=None)
def get_mongo_client():
    """
        延迟初始化 MongoClient
        使用 lru_cache 确保单例模式
        """
    logger.info("创建新的 MongoClient 连接（延迟初始化）")
    return MongoClient(
        mongo_uri,
        maxPoolSize=20,
        connect=False,  # 延迟连接
    )

def sync_to_mongo(database, collection, data, ttl_index="expire_at", expire_after_seconds=os.getenv("MONGO_RESULT_EXPIRES") if os.getenv("MONGO_RESULT_EXPIRES") else 604800):
    mongo_client = get_mongo_client()
    if f"{ttl_index}_1" not in mongo_client[database][collection].index_information():
        # 创建 TTL 索引
        mongo_client[database][collection].create_index(
            [(ttl_index, ASCENDING)],
            expireAfterSeconds=expire_after_seconds,
            name=f"{ttl_index}_1"
        )
        logger.info(f"✅ TTL 索引创建成功: {f'{ttl_index}_1'}, 过期时间: {expire_after_seconds}秒")
    # 计算过期时间
    expire_at = datetime.utcnow() + timedelta(seconds=expire_after_seconds)
    # 添加过期时间字段
    if isinstance(data, dict):
        data[ttl_index] = expire_at
    else:
        # 如果是列表，为每个文档添加过期时间
        for doc in data:
            doc[ttl_index] = expire_at
    result = mongo_client[database][collection].insert_one(data) if isinstance(data, dict) else mongo_client[database][collection].insert_many(data)
    logger.info(f"{database} || {collection} || {len(result.inserted_ids)} || 存入MongoDB成功!")