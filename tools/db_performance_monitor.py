#!/usr/bin/env python
"""
数据库性能监控分析脚本
用于分析数据库查询性能、索引使用情况和潜在的性能瓶颈
"""
import os
import sys
import time
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.core.config import settings


def connect_to_db():
    """连接到数据库"""
    db_path = os.environ.get("DATABASE_URL", "backend/lostandfound.db")
    if db_path.startswith("sqlite:///"):
        db_path = db_path[10:]
    
    print(f"连接到数据库: {db_path}")
    return sqlite3.connect(db_path)


def analyze_table_stats(conn):
    """分析表统计信息"""
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    table_stats = []
    for table in tables:
        table_name = table[0]
        if table_name.startswith('sqlite_'):
            continue
            
        # 获取表行数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_count = len(columns)
        
        table_stats.append({
            'table_name': table_name,
            'row_count': row_count,
            'column_count': column_count
        })
    
    return pd.DataFrame(table_stats)


def analyze_index_usage(conn):
    """分析索引使用情况"""
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    index_stats = []
    for table in tables:
        table_name = table[0]
        if table_name.startswith('sqlite_'):
            continue
            
        # 获取表的索引
        cursor.execute(f"PRAGMA index_list({table_name});")
        indexes = cursor.fetchall()
        
        for idx in indexes:
            index_name = idx[1]
            is_unique = idx[2]
            
            # 获取索引列
            cursor.execute(f"PRAGMA index_info({index_name});")
            index_columns = cursor.fetchall()
            column_names = []
            for col in index_columns:
                col_pos = col[0]
                col_name = col[2]
                column_names.append(col_name)
            
            index_stats.append({
                'table_name': table_name,
                'index_name': index_name,
                'is_unique': bool(is_unique),
                'columns': ', '.join(column_names)
            })
    
    return pd.DataFrame(index_stats)


def run_query_analysis(conn, query, description):
    """运行查询分析"""
    cursor = conn.cursor()
    
    # 启用查询计划分析
    cursor.execute("EXPLAIN QUERY PLAN " + query)
    plan = cursor.fetchall()
    
    # 测量查询执行时间
    start_time = time.time()
    cursor.execute(query)
    results = cursor.fetchall()
    execution_time = time.time() - start_time
    
    return {
        'description': description,
        'query': query,
        'plan': plan,
        'result_count': len(results),
        'execution_time': execution_time
    }


def analyze_common_queries(conn):
    """分析常见查询的性能"""
    queries = [
        {
            'query': "SELECT * FROM post WHERE status = 'active' LIMIT 10;",
            'description': "获取活跃帖子"
        },
        {
            'query': "SELECT * FROM post WHERE item_type = 'lost' AND is_claimed = 0 LIMIT 10;",
            'description': "获取未认领的失物帖子"
        },
        {
            'query': "SELECT * FROM claim WHERE status = 'pending' LIMIT 10;",
            'description': "获取待处理的认领请求"
        },
        {
            'query': "SELECT p.*, c.* FROM post p JOIN claim c ON p.id = c.post_id WHERE c.status = 'approved' LIMIT 10;",
            'description': "获取已批准认领的帖子"
        }
    ]
    
    results = []
    for query_info in queries:
        try:
            result = run_query_analysis(conn, query_info['query'], query_info['description'])
            results.append(result)
        except Exception as e:
            print(f"查询分析失败: {query_info['description']}, 错误: {str(e)}")
    
    return results


def generate_performance_report(table_stats, index_stats, query_results):
    """生成性能报告"""
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = Path("performance_reports")
    report_dir.mkdir(exist_ok=True)
    
    report_path = report_dir / f"db_performance_report_{now}.html"
    
    # 创建HTML报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>数据库性能分析报告</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2 { color: #333; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .query-info { background-color: #eef; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .execution-time { font-weight: bold; }
                .warning { color: #c00; }
            </style>
        </head>
        <body>
            <h1>数据库性能分析报告</h1>
            <p>生成时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            
            <h2>表统计信息</h2>
        """)
        
        # 表统计信息
        f.write(table_stats.to_html(index=False))
        
        # 索引统计信息
        f.write("<h2>索引使用情况</h2>")
        f.write(index_stats.to_html(index=False))
        
        # 查询分析结果
        f.write("<h2>常见查询性能分析</h2>")
        for result in query_results:
            f.write(f"""
            <div class='query-info'>
                <h3>{result['description']}</h3>
                <p><strong>查询:</strong> <code>{result['query']}</code></p>
                <p><strong>结果数量:</strong> {result['result_count']}</p>
                <p class='execution-time'>执行时间: {result['execution_time']:.6f} 秒</p>
                <p><strong>查询计划:</strong></p>
                <pre>{str(result['plan'])}</pre>
            </div>
            """)
        
        # 性能建议
        f.write("<h2>性能优化建议</h2>")
        
        # 检查大表是否有索引
        large_tables = table_stats[table_stats['row_count'] > 1000]['table_name'].tolist()
        indexed_tables = index_stats['table_name'].unique().tolist()
        
        unindexed_large_tables = [t for t in large_tables if t not in indexed_tables]
        if unindexed_large_tables:
            f.write(f"<p class='warning'>以下大型表缺少索引，建议添加适当的索引: {', '.join(unindexed_large_tables)}</p>")
        
        # 检查慢查询
        slow_queries = [q for q in query_results if q['execution_time'] > 0.1]
        if slow_queries:
            f.write("<p class='warning'>以下查询执行较慢，可能需要优化:</p>")
            for query in slow_queries:
                f.write(f"<p>- {query['description']} ({query['execution_time']:.6f} 秒)</p>")
        
        f.write("""
        </body>
        </html>
        """)
    
    print(f"性能报告已生成: {report_path}")
    return report_path


def plot_table_sizes(table_stats, save_path=None):
    """绘制表大小图表"""
    plt.figure(figsize=(10, 6))
    plt.bar(table_stats['table_name'], table_stats['row_count'])
    plt.xticks(rotation=45, ha='right')
    plt.title('表行数统计')
    plt.xlabel('表名')
    plt.ylabel('行数')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description='数据库性能监控分析工具')
    parser.add_argument('--no-report', action='store_true', help='不生成HTML报告')
    parser.add_argument('--no-plot', action='store_true', help='不生成图表')
    args = parser.parse_args()
    
    try:
        conn = connect_to_db()
        
        print("分析表统计信息...")
        table_stats = analyze_table_stats(conn)
        print(table_stats)
        
        print("\n分析索引使用情况...")
        index_stats = analyze_index_usage(conn)
        print(index_stats)
        
        print("\n分析常见查询性能...")
        query_results = analyze_common_queries(conn)
        
        if not args.no_report:
            report_path = generate_performance_report(table_stats, index_stats, query_results)
        
        if not args.no_plot:
            plot_dir = Path("performance_reports/plots")
            plot_dir.mkdir(exist_ok=True, parents=True)
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            plot_path = plot_dir / f"table_sizes_{now}.png"
            plot_table_sizes(table_stats, save_path=plot_path)
            print(f"表大小图表已保存: {plot_path}")
        
        conn.close()
        
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()