#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据生成脚本
生成多样化的测试数据导入数据库，覆盖各功能模块的数据类型和场景
"""

import os
import sys
import random
import datetime
import string
import sqlite3
import io
from datetime import timedelta

# 设置UTF-8编码环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"

# 配置标准输出为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 确保脚本在正确的目录下运行
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 数据库连接函数
def get_db_connection(db_path='lostandfound.db'):
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        sys.exit(1)

# 生成随机字符串
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# 生成随机中文姓名
def generate_random_chinese_name():
    surnames = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴', 
                '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
    names = ['伟', '芳', '娜', '秀英', '敏', '静', '强', '磊', '军', '洋', 
             '勇', '艳', '杰', '秀英', '敏', '静', '丽', '强', '磊', '军']
    return random.choice(surnames) + random.choice(names)

# 生成随机手机号
def generate_random_phone():
    prefix = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
              '150', '151', '152', '153', '155', '156', '157', '158', '159',
              '170', '171', '172', '173', '175', '176', '177', '178',
              '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
    return random.choice(prefix) + ''.join(random.choices(string.digits, k=8))

# 生成随机邮箱
def generate_random_email():
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'qq.com', '163.com', '126.com', 'sina.com', 'outlook.com']
    username = generate_random_string(random.randint(5, 12)).lower()
    return f"{username}@{random.choice(domains)}"

# 生成随机日期
def generate_random_date(start_year=2023, end_year=2025):
    start_date = datetime.datetime(start_year, 1, 1)
    end_date = datetime.datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# 生成测试用户数据
def generate_test_users(conn, count=50):
    print(f"开始生成 {count} 个测试用户...")
    cursor = conn.cursor()
    
    # 检查admin用户是否存在
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        # 创建admin用户
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, phone, name, is_admin, credit_score, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'admin', 
            'admin@example.com',
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # 密码: admin123
            generate_random_phone(),
            '管理员',
            1,
            100,
            datetime.datetime.now(),
            datetime.datetime.now()
        ))
        print("创建管理员用户: admin / admin123")
    
    # 创建普通用户
    user_roles = ['student', 'teacher', 'staff']
    
    # 正常值、边界值和异常值的分布
    # 70% 正常值, 20% 边界值, 10% 异常值
    value_distribution = ['normal'] * 35 + ['boundary'] * 10 + ['abnormal'] * 5
    
    for i in range(count):
        username = f"user{i+1}"
        # 检查用户是否已存在
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        if cursor.fetchone()[0] > 0:
            continue
        
        # 决定这个用户数据的类型
        data_type = random.choice(value_distribution)
        
        if data_type == 'normal':
            # 正常值
            name = generate_random_chinese_name()
            email = generate_random_email()
            phone = generate_random_phone()
            role = random.choice(user_roles)
            credit_score = random.randint(60, 100)
        elif data_type == 'boundary':
            # 边界值
            name = generate_random_chinese_name() * 5  # 较长的名字
            email = f"{'a' * 30}@example.com"  # 较长的邮箱前缀
            phone = '1' + '0' * 10  # 边界手机号
            role = random.choice(user_roles + ['visitor'])  # 添加一个额外角色
            credit_score = random.choice([0, 1, 59, 60, 100, 101])  # 信用分边界值
        else:
            # 异常值
            name = generate_random_string(100)  # 非常长的名字
            email = generate_random_string(5)  # 无效邮箱格式
            phone = generate_random_string(8)  # 无效手机号
            role = generate_random_string(10)  # 无效角色
            credit_score = random.choice([-10, 150, None])  # 超出范围的信用分
            if credit_score is None:
                credit_score = 50  # 数据库可能不接受NULL，使用默认值
        
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, phone, name, role, credit_score, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                username,
                email,
                '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # 密码: admin123
                phone,
                name,
                role,
                credit_score,
                generate_random_date(),
                datetime.datetime.now()
            ))
        except Exception as e:
            print(f"插入用户 {username} 时出错: {e}")
            # 尝试使用更安全的值重新插入
            try:
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, phone, name, role, credit_score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    username,
                    f"{username}@example.com",
                    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
                    generate_random_phone(),
                    username,
                    'student',
                    50,
                    generate_random_date(),
                    datetime.datetime.now()
                ))
                print(f"已使用安全值重新插入用户 {username}")
            except Exception as e2:
                print(f"重新插入用户 {username} 时仍然出错: {e2}")
    
    conn.commit()
    print(f"测试用户生成完成")

# 生成测试分类数据
def generate_test_categories(conn):
    print("开始生成测试分类...")
    cursor = conn.cursor()
    
    # 预定义的分类列表
    categories = [
        ('电子设备', '手机、电脑、平板等电子设备'),
        ('证件卡片', '身份证、银行卡、学生证等'),
        ('服饰配饰', '衣服、鞋子、帽子、眼镜等'),
        ('书包文具', '书包、课本、笔记本、笔等'),
        ('生活用品', '雨伞、水杯、钥匙等'),
        ('运动器材', '球类、球拍、运动服等'),
        ('其他物品', '其他类型的失物')
    ]
    
    for name, description in categories:
        # 检查分类是否已存在
        cursor.execute("SELECT COUNT(*) FROM categories WHERE name = ?", (name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO categories (name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                name,
                description,
                datetime.datetime.now(),
                datetime.datetime.now()
            ))
    
    conn.commit()
    print("测试分类生成完成")

# 生成测试帖子数据
def generate_test_posts(conn, count=50):
    print(f"开始生成 {count} 个测试帖子...")
    cursor = conn.cursor()
    
    # 获取用户ID列表
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取分类ID列表
    cursor.execute("SELECT id FROM categories")
    category_ids = [row[0] for row in cursor.fetchall()]
    
    # 帖子类型
    post_types = ['lost', 'found']
    
    # 地点列表
    locations = ['教学楼A区', '教学楼B区', '图书馆', '食堂', '操场', '宿舍区', '校门口', '停车场', '体育馆', '实验室']
    
    # 物品描述模板
    lost_item_descriptions = [
        "我在{location}丢失了{item_name}，{details}，如有拾到者请联系我，必有重谢！",
        "寻找于{date}在{location}丢失的{item_name}，{details}，请帮忙留意。",
        "{details}，如有捡到{item_name}的同学，请与我联系，谢谢！",
    ]
    
    found_item_descriptions = [
        "在{location}捡到{item_name}，{details}，请失主联系认领。",
        "于{date}在{location}拾到{item_name}，{details}，请失主提供相关信息前来认领。",
        "{details}，请失主确认信息后联系我领取{item_name}。",
    ]
    
    # 物品名称列表
    item_names = {
        '电子设备': ['iPhone 15', '华为Mate 60', 'MacBook Pro', 'AirPods', 'iPad', '小米手环', '充电宝', '蓝牙耳机'],
        '证件卡片': ['身份证', '学生证', '校园卡', '银行卡', '驾驶证', '护照', '会员卡'],
        '服饰配饰': ['黑色外套', '灰色围巾', '棒球帽', '近视眼镜', '太阳镜', '手表', '手链', '钱包'],
        '书包文具': ['黑色双肩包', '蓝色文件夹', '笔记本', '钢笔', '计算器', 'U盘', '字典', '教科书'],
        '生活用品': ['雨伞', '水杯', '钥匙串', '保温杯', '钱包', '背包', '帽子'],
        '运动器材': ['篮球', '足球', '羽毛球拍', '乒乓球拍', '运动手表', '瑜伽垫', '跳绳'],
        '其他物品': ['充电宝', '耳机', '雨伞', '帽子', '手套', '口罩', '背包']
    }
    
    # 获取分类名称映射
    cursor.execute("SELECT id, name FROM categories")
    category_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 正常值、边界值和异常值的分布
    value_distribution = ['normal'] * 35 + ['boundary'] * 10 + ['abnormal'] * 5
    
    for i in range(count):
        # 决定这个帖子数据的类型
        data_type = random.choice(value_distribution)
        
        user_id = random.choice(user_ids)
        category_id = random.choice(category_ids)
        post_type = random.choice(post_types)
        location = random.choice(locations)
        
        # 根据分类选择物品名称
        category_name = category_map.get(category_id, '其他物品')
        item_name = random.choice(item_names.get(category_name, item_names['其他物品']))
        
        # 生成日期
        date = generate_random_date(2024, 2025)
        
        if data_type == 'normal':
            # 正常值
            details = generate_random_string(random.randint(10, 30))
            
            if post_type == 'lost':
                description_template = random.choice(lost_item_descriptions)
                description = description_template.format(
                    location=location, 
                    item_name=item_name,
                    details=details,
                    date=date.strftime('%Y-%m-%d')
                )
                title = f"寻找丢失的{item_name}"
            else:
                description_template = random.choice(found_item_descriptions)
                description = description_template.format(
                    location=location,
                    item_name=item_name,
                    details=details,
                    date=date.strftime('%Y-%m-%d')
                )
                title = f"拾到{item_name}"
            
            # 状态
            status = random.choice(['pending', 'resolved']) if post_type == 'found' else 'active'
            
            # 图片（可选）
            image_url = f"/uploads/images/{generate_random_string(8)}.jpg" if random.random() > 0.3 else None
            
        elif data_type == 'boundary':
            # 边界值
            details = generate_random_string(500)  # 较长的描述
            
            if post_type == 'lost':
                title = f"寻找丢失的{item_name}" * 5  # 较长的标题
                description = "很长的描述" * 50  # 非常长的描述
            else:
                title = f"拾到{item_name}" * 5
                description = "很长的描述" * 50
            
            # 边界状态
            status = random.choice(['pending', 'resolved', 'active', 'deleted'])
            
            # 特殊图片URL
            image_url = f"/uploads/images/{generate_random_string(50)}.jpg"
            
        else:
            # 异常值
            details = generate_random_string(1000)  # 超长描述
            
            # 异常标题和描述
            title = generate_random_string(200)  # 超长标题
            description = None  # 空描述
            
            # 无效状态
            status = generate_random_string(10)
            
            # 无效图片URL
            image_url = generate_random_string(20)
        
        try:
            cursor.execute("""
                INSERT INTO posts (author_id, category_id, title, description, post_type, location, status, 
                                image_url, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                category_id,
                title,
                description,
                post_type,
                location,
                status,
                image_url,
                date,
                datetime.datetime.now()
            ))
        except Exception as e:
            print(f"插入帖子 #{i+1} 时出错: {e}")
            # 尝试使用更安全的值重新插入
            try:
                cursor.execute("""
                    INSERT INTO posts (author_id, category_id, title, description, post_type, location, status, 
                                    image_url, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    category_id,
                    f"测试帖子 #{i+1}",
                    "这是一个测试帖子",
                    post_type,
                    location,
                    'active',
                    None,
                    date,
                    datetime.datetime.now()
                ))
                print(f"已使用安全值重新插入帖子 #{i+1}")
            except Exception as e2:
                print(f"重新插入帖子 #{i+1} 时仍然出错: {e2}")
    
    conn.commit()
    print(f"测试帖子生成完成")

# 生成测试认领数据
def generate_test_claims(conn, count=30):
    print(f"开始生成 {count} 个测试认领记录...")
    cursor = conn.cursor()
    
    # 获取帖子ID列表（只选择可认领的帖子）
    cursor.execute("SELECT id, author_id, post_type FROM posts WHERE post_type = 'found' AND status != 'resolved'")
    post_data = cursor.fetchall()
    
    # 获取用户ID列表
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # 认领状态
    claim_statuses = ['pending', 'approved', 'rejected', 'canceled']
    
    # 认领理由模板
    claim_reasons = [
        "这是我的{item_name}，{details}，可以提供购买凭证。",
        "我确定这是我的物品，{details}，感谢您的帮助。",
        "我于{date}在{location}丢失了{item_name}，{details}。",
        "这个{item_name}是我的，{details}，请确认归还。"
    ]
    
    # 地点列表
    locations = ['教学楼A区', '教学楼B区', '图书馆', '食堂', '操场', '宿舍区']
    
    # 获取物品名称
    post_map = {}
    for post_id, author_id, post_type in post_data:
        cursor.execute("SELECT title FROM posts WHERE id = ?", (post_id,))
        title = cursor.fetchone()[0]
        # 从标题中提取物品名称
        item_name = title.replace('拾到', '').strip()
        post_map[post_id] = {'author_id': author_id, 'item_name': item_name}
    
    for i in range(count):
        if not post_map:
            break
            
        post_id = random.choice(list(post_map.keys()))
        post_info = post_map[post_id]
        
        # 认领人不能是发布者
        possible_claimers = [uid for uid in user_ids if uid != post_info['author_id']]
        if not possible_claimers:
            continue
            
        claimer_id = random.choice(possible_claimers)
        status = random.choice(claim_statuses)
        
        # 生成认领理由
        details = generate_random_string(random.randint(10, 20))
        date = generate_random_date(2024, 2025)
        location = random.choice(locations)
        
        reason_template = random.choice(claim_reasons)
        reason = reason_template.format(
            item_name=post_info['item_name'],
            details=details,
            date=date.strftime('%Y-%m-%d'),
            location=location
        )
        
        # 处理时间（只有已处理的认领才有）
        processed_at = date + timedelta(days=random.randint(1, 7)) if status in ['approved', 'rejected'] else None
        
        cursor.execute("""
            INSERT INTO claims (post_id, claimer_id, reason, status, processed_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            post_id,
            claimer_id,
            reason,
            status,
            processed_at,
            date,
            datetime.datetime.now()
        ))
        
        # 如果认领被批准，更新帖子状态
        if status == 'approved':
            cursor.execute(
                "UPDATE posts SET status = 'resolved', updated_at = ? WHERE id = ?",
                (datetime.datetime.now(), post_id)
            )
            # 从可用帖子中移除
            del post_map[post_id]
    
    conn.commit()
    print(f"测试认领记录生成完成")

# 生成测试通知数据
def generate_test_notifications(conn, count=100):
    print(f"开始生成 {count} 个测试通知...")
    cursor = conn.cursor()
    
    # 获取用户ID列表
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # 通知类型和模板
    notification_templates = [
        ('claim_submitted', '有用户对您的帖子发起了认领请求，请查看。'),
        ('claim_approved', '您的认领请求已被批准，请联系发布者领取物品。'),
        ('claim_rejected', '很抱歉，您的认领请求未通过审核。'),
        ('claim_canceled', '认领请求已取消。'),
        ('post_comment', '有用户评论了您的帖子。'),
        ('system_notice', '系统维护通知：平台将于明天凌晨2点-4点进行维护升级。'),
        ('credit_change', '您的信用积分有变动，请查看详情。'),
        ('welcome', '欢迎使用失物招领平台！')
    ]
    
    for i in range(count):
        user_id = random.choice(user_ids)
        notification_type, content = random.choice(notification_templates)
        is_read = random.choice([True, False])
        related_id = random.randint(1, 100) if notification_type in ['claim_submitted', 'claim_approved', 'claim_rejected', 'post_comment'] else None
        
        cursor.execute("""
            INSERT INTO notifications (user_id, type, content, is_read, related_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            notification_type,
            content,
            is_read,
            related_id,
            generate_random_date(2024, 2025)
        ))
    
    conn.commit()
    print(f"测试通知生成完成")

# 生成测试评论数据
def generate_test_comments(conn, count=80):
    print(f"开始生成 {count} 个测试评论...")
    cursor = conn.cursor()
    
    # 获取帖子ID列表
    cursor.execute("SELECT id FROM posts")
    post_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取用户ID列表
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # 评论内容模板
    comment_templates = [
        "我也看到类似的物品，帮你留意一下。",
        "请问具体是在{location}的哪个位置丢失的？",
        "{details}，希望你能尽快找到。",
        "感谢分享，这个信息很有用。",
        "我可以提供一些线索，{details}。",
        "太好了，很高兴能帮到你！",
        "请问可以提供更多细节吗？",
        "我有类似的经历，{details}。"
    ]
    
    # 地点列表
    locations = ['教学楼A区', '教学楼B区', '图书馆', '食堂', '操场', '宿舍区']
    
    for i in range(count):
        post_id = random.choice(post_ids)
        user_id = random.choice(user_ids)
        
        # 生成评论内容
        template = random.choice(comment_templates)
        details = generate_random_string(random.randint(10, 20))
        location = random.choice(locations)
        
        content = template.format(details=details, location=location)
        
        cursor.execute("""
            INSERT INTO comments (post_id, user_id, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            post_id,
            user_id,
            content,
            generate_random_date(2024, 2025),
            datetime.datetime.now()
        ))
    
    conn.commit()
    print(f"测试评论生成完成")

# 主函数
def main():
    print("开始生成测试数据...")
    
    # 连接数据库
    conn = get_db_connection()
    
    try:
        # 生成各类测试数据
        generate_test_users(conn)
        generate_test_categories(conn)
        generate_test_posts(conn)
        generate_test_claims(conn)
        generate_test_comments(conn)
        generate_test_notifications(conn)
        
        print("\n✅ 所有测试数据生成完成！")
        print("\n测试账号信息：")
        print("- 管理员账号: admin / admin123")
        print("- 普通用户账号: user1, user2, ..., user20 (密码均为: admin123)")
        
    except Exception as e:
        print(f"\n❌ 生成测试数据时出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
