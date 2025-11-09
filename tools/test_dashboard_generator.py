#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试结果可视化仪表板生成器
从system_test.log和test_report.md生成交互式HTML仪表板
"""

import re
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestResultParser:
    """测试结果解析器"""
    
    def __init__(self, log_file: Path, report_file: Path):
        self.log_file = log_file
        self.report_file = report_file
        
    def parse_log(self) -> Dict[str, Any]:
        """解析system_test.log文件"""
        results = {
            'tests': [],
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        if not self.log_file.exists():
            print(f"警告: 日志文件不存在 {self.log_file}")
            return results
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析测试通过
        passed_pattern = r'INFO - 测试通过: (.*?) \(耗时: ([\d.]+)秒\)'
        for match in re.finditer(passed_pattern, content):
            test_name, duration = match.groups()
            results['tests'].append({
                'name': test_name,
                'status': 'passed',
                'duration': float(duration)
            })
            results['passed'] += 1
        
        # 解析测试失败
        failed_pattern = r'ERROR - 测试失败: (.*?) \(耗时: ([\d.]+)秒\)'
        for match in re.finditer(failed_pattern, content):
            test_name, duration = match.groups()
            results['tests'].append({
                'name': test_name,
                'status': 'failed',
                'duration': float(duration)
            })
            results['failed'] += 1
        
        # 解析错误信息
        error_pattern = r'ERROR - (.*?)(?=\n\d{4}-|\n$|$)'
        for match in re.finditer(error_pattern, content, re.DOTALL):
            error_msg = match.group(1).strip()
            if error_msg and '测试失败' not in error_msg:
                results['errors'].append(error_msg)
        
        results['total'] = results['passed'] + results['failed']
        
        return results
    
    def parse_report(self) -> Dict[str, Any]:
        """解析test_report.md文件"""
        performance_data = []
        
        if not self.report_file.exists():
            print(f"警告: 报告文件不存在 {self.report_file}")
            return {'performance': performance_data}
        
        with open(self.report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析性能表格
        perf_pattern = r'\| (/api/.*?) \| (GET|POST|PUT|DELETE) \| (\d+) \| ([\d.]+) \|'
        for match in re.finditer(perf_pattern, content):
            endpoint, method, status, time = match.groups()
            performance_data.append({
                'endpoint': endpoint,
                'method': method,
                'status_code': int(status),
                'response_time': float(time)
            })
        
        return {'performance': performance_data}


class DashboardGenerator:
    """仪表板生成器"""
    
    def __init__(self, test_results: Dict[str, Any], performance_data: List[Dict]):
        self.test_results = test_results
        self.performance_data = performance_data
        
    def generate_html(self, output_path: Path):
        """生成HTML仪表板"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>失物招领平台 - 测试结果仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .header .timestamp {{
            color: #666;
            font-size: 14px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        
        .stat-card .value {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card.pass .value {{
            color: #10b981;
        }}
        
        .stat-card.fail .value {{
            color: #ef4444;
        }}
        
        .stat-card.total .value {{
            color: #3b82f6;
        }}
        
        .stat-card.rate .value {{
            color: #8b5cf6;
        }}
        
        .progress-bar {{
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
            transition: width 0.5s ease;
        }}
        
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .chart-container h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 300px;
        }}
        
        .test-list {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .test-list h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        
        .test-item {{
            padding: 15px;
            border-left: 4px solid #e5e7eb;
            margin-bottom: 10px;
            background: #f9fafb;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .test-item.passed {{
            border-left-color: #10b981;
            background: #ecfdf5;
        }}
        
        .test-item.failed {{
            border-left-color: #ef4444;
            background: #fef2f2;
        }}
        
        .test-item .name {{
            font-weight: 500;
            color: #333;
        }}
        
        .test-item .status {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .badge.pass {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .badge.fail {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .duration {{
            color: #6b7280;
            font-size: 14px;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 测试结果仪表板</h1>
            <p class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="label">总测试数</div>
                <div class="value">{self.test_results.get('total', 0)}</div>
            </div>
            
            <div class="stat-card pass">
                <div class="label">通过测试</div>
                <div class="value">{self.test_results.get('passed', 0)}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {self._calc_pass_rate()}%"></div>
                </div>
            </div>
            
            <div class="stat-card fail">
                <div class="label">失败测试</div>
                <div class="value">{self.test_results.get('failed', 0)}</div>
            </div>
            
            <div class="stat-card rate">
                <div class="label">通过率</div>
                <div class="value">{self._calc_pass_rate():.1f}%</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📊 测试结果分布</h2>
            <div class="chart-wrapper">
                <canvas id="testDistChart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>⚡ API性能分析</h2>
            <div class="chart-wrapper">
                <canvas id="perfChart"></canvas>
            </div>
        </div>
        
        <div class="test-list">
            <h2>📝 测试用例详情</h2>
            {self._generate_test_list()}
        </div>
    </div>
    
    <script>
        // 测试分布饼图
        const distCtx = document.getElementById('testDistChart');
        new Chart(distCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['通过', '失败'],
                datasets: [{{
                    data: [{self.test_results.get('passed', 0)}, {self.test_results.get('failed', 0)}],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            font: {{
                                size: 14
                            }},
                            padding: 20
                        }}
                    }}
                }}
            }}
        }});
        
        // 性能条形图
        const perfCtx = document.getElementById('perfChart');
        new Chart(perfCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([p['endpoint'] for p in self.performance_data[:10]])},
                datasets: [{{
                    label: '响应时间 (秒)',
                    data: {json.dumps([p['response_time'] for p in self.performance_data[:10]])},
                    backgroundColor: 'rgba(102, 126, 234, 0.6)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                    borderRadius: 5
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return value.toFixed(4) + 's';
                            }}
                        }}
                    }},
                    x: {{
                        ticks: {{
                            maxRotation: 45,
                            minRotation: 45
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return '响应时间: ' + context.parsed.y.toFixed(4) + '秒';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        
        # 写入文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ 仪表板已生成: {output_path}")
    
    def _calc_pass_rate(self) -> float:
        """计算通过率"""
        total = self.test_results.get('total', 0)
        if total == 0:
            return 0.0
        passed = self.test_results.get('passed', 0)
        return (passed / total) * 100
    
    def _generate_test_list(self) -> str:
        """生成测试列表HTML"""
        html_parts = []
        
        for test in self.test_results.get('tests', []):
            status_class = 'passed' if test['status'] == 'passed' else 'failed'
            badge_class = 'pass' if test['status'] == 'passed' else 'fail'
            badge_text = '✓ 通过' if test['status'] == 'passed' else '✗ 失败'
            
            html_parts.append(f"""
            <div class="test-item {status_class}">
                <div class="name">{test['name']}</div>
                <div class="status">
                    <span class="badge {badge_class}">{badge_text}</span>
                    <span class="duration">{test['duration']:.2f}秒</span>
                </div>
            </div>
            """)
        
        if not html_parts:
            return '<p style="color: #666; text-align: center;">暂无测试数据</p>'
        
        return ''.join(html_parts)


def main():
    """主函数"""
    # 项目根目录
    root_dir = Path(__file__).resolve().parent.parent
    
    # 输入文件
    log_file = root_dir / "system_test.log"
    report_file = root_dir / "test_report.md"
    
    # 输出文件
    output_dir = root_dir / "reports"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"test_dashboard_{timestamp}.html"
    
    print("🚀 开始生成测试结果仪表板...")
    print(f"📂 日志文件: {log_file}")
    print(f"📄 报告文件: {report_file}")
    
    # 解析测试结果
    parser = TestResultParser(log_file, report_file)
    test_results = parser.parse_log()
    report_data = parser.parse_report()
    
    print(f"✅ 解析完成: 总计 {test_results['total']} 个测试")
    print(f"   - 通过: {test_results['passed']}")
    print(f"   - 失败: {test_results['failed']}")
    print(f"   - 性能数据: {len(report_data['performance'])} 条")
    
    # 生成仪表板
    generator = DashboardGenerator(test_results, report_data['performance'])
    generator.generate_html(output_file)
    
    # 同时生成一个latest版本便于访问
    latest_file = output_dir / "test_dashboard_latest.html"
    generator.generate_html(latest_file)
    print(f"✅ 最新版本: {latest_file}")
    
    print("\n🎉 仪表板生成完成！")
    print(f"📊 在浏览器中打开: file:///{output_file.absolute()}")


if __name__ == "__main__":
    main()
