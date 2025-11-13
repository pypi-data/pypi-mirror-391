# service.py
from typing import List, Dict, Any
from .models import ProductSearchInput

def mock_product_database_query(input_data: ProductSearchInput) -> List[Dict[str, Any]]:
    """
    模拟商品查询和推荐逻辑。
    实际项目中应替换为数据库查询、API 调用或推荐算法。
    """
    results = []
    
    for item in input_data.product_list:
        # 示例：返回 mock 数据
        results.append({
            "product_name": item.product_name,
            "brand": item.brand or "未知品牌",
            "specification": item.specification or "标准装",
            "main_effect": item.main_effect,
            "price": 25.80,  # 示例价格
            "production_date": "2025-10-01",
            "stock": "有货",
            "recommend_reason": f"匹配主要功效: {item.main_effect}"
        })
    
    # 可根据 user_preferences 排序（此处省略）
    return results