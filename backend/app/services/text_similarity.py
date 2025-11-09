"""
文本相似度匹配服务
用于计算帖子内容的相似度，提高智能匹配准确性
"""
from typing import List, Tuple
import re
import math
from collections import Counter

class TextSimilarityService:
    """文本相似度计算服务"""
    
    @staticmethod
    def simple_tokenize(text: str) -> List[str]:
        """
        简单的中文分词（不需要额外依赖）
        使用正则表达式分离中文字符和英文单词
        """
        if not text:
            return []
        
        # 转小写
        text = text.lower()
        
        # 提取中文字符（按字符分）
        chinese_chars = re.findall(r'[\u4e00-\u9fa5]', text)
        
        # 提取英文单词
        english_words = re.findall(r'[a-z]+', text)
        
        # 提取数字
        numbers = re.findall(r'\d+', text)
        
        # 合并所有token
        tokens = chinese_chars + english_words + numbers
        
        return tokens
    
    @staticmethod
    def calculate_cosine_similarity(text1: str, text2: str) -> float:
        """
        计算两段文本的余弦相似度（0-1之间）
        使用简单的词频向量和余弦相似度公式
        """
        if not text1 or not text2:
            return 0.0
        
        # 分词
        tokens1 = TextSimilarityService.simple_tokenize(text1)
        tokens2 = TextSimilarityService.simple_tokenize(text2)
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # 计算词频
        vec1 = Counter(tokens1)
        vec2 = Counter(tokens2)
        
        # 获取所有唯一词
        all_words = set(vec1.keys()) | set(vec2.keys())
        
        # 构建向量
        v1 = [vec1.get(word, 0) for word in all_words]
        v2 = [vec2.get(word, 0) for word in all_words]
        
        # 计算点积
        dot_product = sum(a * b for a, b in zip(v1, v2))
        
        # 计算向量长度
        magnitude1 = math.sqrt(sum(a * a for a in v1))
        magnitude2 = math.sqrt(sum(b * b for b in v2))
        
        # 避免除以0
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        # 余弦相似度
        similarity = dot_product / (magnitude1 * magnitude2)
        
        return round(similarity, 4)
    
    @staticmethod
    def calculate_jaccard_similarity(text1: str, text2: str) -> float:
        """
        计算两段文本的Jaccard相似度（0-1之间）
        基于集合的交集和并集
        """
        if not text1 or not text2:
            return 0.0
        
        # 分词
        tokens1 = set(TextSimilarityService.simple_tokenize(text1))
        tokens2 = set(TextSimilarityService.simple_tokenize(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # 计算交集和并集
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        
        if not union:
            return 0.0
        
        # Jaccard系数
        similarity = len(intersection) / len(union)
        
        return round(similarity, 4)
    
    @staticmethod
    def calculate_combined_similarity(text1: str, text2: str) -> float:
        """
        综合相似度：结合余弦相似度和Jaccard相似度
        权重：余弦相似度 70%，Jaccard相似度 30%
        """
        cosine_sim = TextSimilarityService.calculate_cosine_similarity(text1, text2)
        jaccard_sim = TextSimilarityService.calculate_jaccard_similarity(text1, text2)
        
        # 加权平均
        combined = cosine_sim * 0.7 + jaccard_sim * 0.3
        
        return round(combined, 4)
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        """
        提取文本关键词（高频词）
        """
        tokens = TextSimilarityService.simple_tokenize(text)
        
        if not tokens:
            return []
        
        # 过滤停用词（简单版本）
        stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
            '都', '一', '个', '上', '也', '很', '到', '说', '要', '去',
            '你', '会', '着', '没', '看', '好', '自己', '这', '那', '能'
        }
        
        # 过滤停用词和单字符token
        filtered_tokens = [
            token for token in tokens 
            if token not in stopwords and len(token) > 1
        ]
        
        # 统计词频
        word_freq = Counter(filtered_tokens)
        
        # 返回top N关键词
        keywords = [word for word, _ in word_freq.most_common(top_n)]
        
        return keywords
