# -*- coding: utf-8 -*-
"""
模型预加载管理器 - 在应用启动时预加载所有必要的模型
"""

import time
from loguru import logger
from typing import Dict, Any

class ModelPreloadManager:
    """
    统一管理所有模型的预加载
    """
    
    def __init__(self):
        self.loaded_models: Dict[str, Any] = {}
        self.load_times: Dict[str, float] = {}
        
    def preload_all_models(self):
        """
        预加载所有必要的模型
        """
        logger.info("🚀 开始预加载所有模型...")
        total_start = time.time()
        
        # 1. 预加载实体搜索模型
        self._preload_entity_searcher()
        
        # 2. 预加载RAG检索模型
        self._preload_rag_retriever()
        
        # 3. 预加载LLM客户端
        self._preload_llm_client()
        
        # 4. 预加载意图分类器
        self._preload_intent_classifiers()
        
        total_time = time.time() - total_start
        logger.info(f"✅ 所有模型预加载完成，总耗时: {total_time:.2f}秒")
        self._print_load_summary()
        
    def _preload_entity_searcher(self):
        """预加载实体搜索模型"""
        start_time = time.time()
        try:
            from model.graph_entity.search_model import INSTANCE
            
            # INSTANCE 是全局单例，尝试重新加载
            if hasattr(INSTANCE, 'reload'):
                try:
                    INSTANCE.reload()
                except Exception as reload_error:
                    logger.warning(f"实体搜索模型reload失败，尝试build: {reload_error}")
                    if hasattr(INSTANCE, 'build'):
                        INSTANCE.build()
            
            self.loaded_models['entity_searcher'] = INSTANCE
            self.load_times['entity_searcher'] = time.time() - start_time
            logger.info(f"✅ 实体搜索模型加载成功，耗时: {self.load_times['entity_searcher']:.2f}秒")
            
        except Exception as e:
            logger.error(f"❌ 实体搜索模型加载失败: {e}")
            self.load_times['entity_searcher'] = time.time() - start_time
            
    def _preload_rag_retriever(self):
        """预加载RAG检索模型"""
        start_time = time.time()
        try:
            from model.rag.retriever_model import INSTANCE
            
            # 设置允许反序列化以避免pickle警告
            if hasattr(INSTANCE, 'vector_db'):
                vector_db = INSTANCE.vector_db
                if hasattr(vector_db, '_allow_dangerous_deserialization'):
                    vector_db._allow_dangerous_deserialization = True
            
            # INSTANCE 是全局单例，尝试重新加载
            if hasattr(INSTANCE, 'reload'):
                try:
                    INSTANCE.reload()
                except Exception as reload_error:
                    logger.warning(f"RAG模型reload失败，尝试build: {reload_error}")
                    if hasattr(INSTANCE, 'build'):
                        INSTANCE.build()
            
            self.loaded_models['rag_retriever'] = INSTANCE
            self.load_times['rag_retriever'] = time.time() - start_time
            logger.info(f"✅ RAG检索模型加载成功，耗时: {self.load_times['rag_retriever']:.2f}秒")
            
        except Exception as e:
            logger.error(f"❌ RAG检索模型加载失败: {e}")
            self.load_times['rag_retriever'] = time.time() - start_time
            
    def _preload_llm_client(self):
        """预加载LLM客户端"""
        start_time = time.time()
        try:
            from lang_chain.client.client_factory import ClientFactory
            
            # 获取并初始化客户端
            factory = ClientFactory()
            client = factory.get_client()
            
            # 测试连接
            if hasattr(client, '_check_ollama_running'):
                client._check_ollama_running()
            
            self.loaded_models['llm_client'] = client
            self.load_times['llm_client'] = time.time() - start_time
            logger.info(f"✅ LLM客户端加载成功，耗时: {self.load_times['llm_client']:.2f}秒")
            
        except Exception as e:
            logger.error(f"❌ LLM客户端加载失败: {e}")
            self.load_times['llm_client'] = time.time() - start_time
            
    def _preload_intent_classifiers(self):
        """预加载意图分类器"""
        start_time = time.time()
        try:
            # 预加载统一意图分类器
            from qa.unified_intent_classifier import get_unified_classifier
            classifier = get_unified_classifier()
            self.loaded_models['unified_classifier'] = classifier
            
            # 预加载LLM中心分类器
            from qa.llm_centric_classifier import get_llm_centric_classifier
            llm_classifier = get_llm_centric_classifier()
            self.loaded_models['llm_classifier'] = llm_classifier
            
            self.load_times['intent_classifiers'] = time.time() - start_time
            logger.info(f"✅ 意图分类器加载成功，耗时: {self.load_times['intent_classifiers']:.2f}秒")
            
        except Exception as e:
            logger.error(f"❌ 意图分类器加载失败: {e}")
            self.load_times['intent_classifiers'] = time.time() - start_time
            
    def _print_load_summary(self):
        """打印加载总结"""
        logger.info("📊 模型加载时间统计:")
        for model_name, load_time in self.load_times.items():
            status = "✅" if model_name in self.loaded_models else "❌"
            logger.info(f"  {status} {model_name}: {load_time:.2f}秒")
            
    def get_loaded_model(self, model_name: str):
        """获取已加载的模型"""
        return self.loaded_models.get(model_name)
        
    def is_model_loaded(self, model_name: str) -> bool:
        """检查模型是否已加载"""
        return model_name in self.loaded_models


# 全局预加载管理器实例
_preload_manager = None

def get_preload_manager() -> ModelPreloadManager:
    """获取全局预加载管理器实例"""
    global _preload_manager
    if _preload_manager is None:
        _preload_manager = ModelPreloadManager()
    return _preload_manager