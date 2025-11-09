"""
系统集成测试脚本 - 测试智能匹配和消息推送功能
重点测试：当用户发布claim请求后，系统识别最匹配的失物并向失主发送消息
"""
import os
import sys
from pathlib import Path
import asyncio
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, select
from app.database import engine
from app.models.user import User
from app.models.post import Post
from app.models.category import Category
from app.models.claim import Claim
from app.models.notification import Notification, NotificationType
from app.services.notification_service import NotificationService
from app.core.security import get_password_hash

class TestResult:
    """测试结果类"""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = []
    
    def success(self, message: str, details: list = None):
        self.passed = True
        self.message = message
        self.details = details or []
    
    def fail(self, message: str, details: list = None):
        self.passed = False
        self.message = message
        self.details = details or []
    
    def print_result(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        print(f"\n{status} - {self.name}")
        print(f"  {self.message}")
        if self.details:
            for detail in self.details:
                print(f"    • {detail}")

class SmartMatchingTester:
    """智能匹配系统测试器"""
    
    def __init__(self):
        self.session = Session(engine)
        self.test_results = []
        self.test_users = {}
        self.test_posts = {}
        self.test_category = None
    
    def cleanup_test_data(self):
        """清理测试数据"""
        print("\n🧹 清理旧的测试数据...")
        
        # 删除测试用户创建的数据
        test_emails = ['test_loser@test.com', 'test_finder@test.com', 'test_admin@test.com']
        
        for email in test_emails:
            user = self.session.exec(select(User).where(User.email == email)).first()
            if user:
                # 删除该用户的通知
                notifications = self.session.exec(
                    select(Notification).where(Notification.user_id == user.id)
                ).all()
                for notif in notifications:
                    self.session.delete(notif)
                
                # 删除该用户的认领
                claims = self.session.exec(
                    select(Claim).where(Claim.claimer_id == user.id)
                ).all()
                for claim in claims:
                    self.session.delete(claim)
                
                # 删除该用户的帖子
                posts = self.session.exec(
                    select(Post).where(Post.author_id == user.id)
                ).all()
                for post in posts:
                    self.session.delete(post)
                
                # 删除用户
                self.session.delete(user)
        
        self.session.commit()
        print("✓ 清理完成")
    
    def setup_test_data(self):
        """创建测试数据"""
        print("\n📝 创建测试数据...")
        result = TestResult("测试数据创建")
        
        try:
            # 获取或创建测试分类
            category = self.session.exec(
                select(Category).where(Category.name == "电子产品")
            ).first()
            
            if not category:
                result.fail("未找到'电子产品'分类，请先初始化分类数据")
                self.test_results.append(result)
                return False
            
            self.test_category = category
            
            # 创建测试用户1：失主（丢失iPhone的人）
            loser = User(
                name="测试失主",
                email="test_loser@test.com",
                password_hash=get_password_hash("password123"),
                credit_score=100,
                is_admin=False
            )
            self.session.add(loser)
            self.session.flush()
            self.test_users['loser'] = loser
            
            # 创建测试用户2：拾得者（捡到iPhone的人）
            finder = User(
                name="测试拾得者",
                email="test_finder@test.com",
                password_hash=get_password_hash("password123"),
                credit_score=100,
                is_admin=False
            )
            self.session.add(finder)
            self.session.flush()
            self.test_users['finder'] = finder
            
            # 创建测试帖子1：失物帖（丢失iPhone）
            lost_time = datetime.utcnow() - timedelta(days=2)
            lost_post = Post(
                title="丢失iPhone 14 Pro",
                content="10月21日下午3点左右在图书馆二楼丢失黑色iPhone 14 Pro，手机壳是透明的，屏幕有贴膜。手机对我很重要，里面有很多重要资料，如有捡到请联系我，必有重谢！",
                item_type="lost",
                category_id=category.id,
                author_id=loser.id,
                location="图书馆二楼",
                item_time=lost_time,
                contact_info="微信：loser123",
                status='published',
                is_claimed=False
            )
            self.session.add(lost_post)
            self.session.flush()
            self.test_posts['lost'] = lost_post
            
            # 创建测试帖子2：拾得帖（捡到iPhone）
            found_time = lost_time + timedelta(hours=2)
            found_post = Post(
                title="捡到iPhone手机一部",
                content="10月21日下午5点左右在图书馆二楼自习区捡到一部黑色iPhone手机，有透明手机壳和贴膜。请失主提供详细信息认领。",
                item_type="found",
                category_id=category.id,
                author_id=finder.id,
                location="图书馆二楼",
                item_time=found_time,
                contact_info="QQ：123456",
                status='published',
                is_claimed=False
            )
            self.session.add(found_post)
            self.session.flush()
            self.test_posts['found'] = found_post
            
            # 创建干扰帖子（不同地点的iPhone）
            interference_post = Post(
                title="捡到iPhone手机",
                content="在东门食堂捡到iPhone一部",
                item_type="found",
                category_id=category.id,
                author_id=finder.id,
                location="东门食堂",  # 不同地点
                item_time=found_time,
                contact_info="QQ：654321",
                status='published',
                is_claimed=False
            )
            self.session.add(interference_post)
            self.session.flush()
            self.test_posts['interference'] = interference_post
            
            self.session.commit()
            
            result.success("测试数据创建成功", [
                f"失主用户: {loser.name} (ID: {loser.id})",
                f"拾得者用户: {finder.name} (ID: {finder.id})",
                f"失物帖: {lost_post.title} (ID: {lost_post.id})",
                f"拾得帖: {found_post.title} (ID: {found_post.id})",
                f"干扰帖: {interference_post.title} (ID: {interference_post.id})"
            ])
            self.test_results.append(result)
            return True
            
        except Exception as e:
            result.fail(f"测试数据创建失败: {str(e)}")
            self.test_results.append(result)
            return False
    
    def test_smart_matching(self):
        """测试智能匹配算法"""
        print("\n🔍 测试智能匹配算法...")
        result = TestResult("智能匹配算法")
        
        try:
            lost_post = self.test_posts['lost']
            found_post = self.test_posts['found']
            interference_post = self.test_posts['interference']
            
            # 模拟API调用 - 为lost帖查找匹配的found帖
            from app.api.posts import get_matching_posts
            
            matching_posts = get_matching_posts(
                post_id=lost_post.id,
                limit=10,
                time_range_days=7,
                session=self.session
            )
            
            # 验证匹配结果
            matching_ids = [post.id for post in matching_posts]
            
            details = [
                f"为失物帖 #{lost_post.id} 找到 {len(matching_posts)} 个匹配",
                f"匹配的帖子ID: {matching_ids}"
            ]
            
            # 检查是否包含正确的匹配（相同地点的found帖）
            if found_post.id in matching_ids:
                details.append(f"✓ 正确匹配到拾得帖 #{found_post.id} (相同地点: {found_post.location})")
            else:
                result.fail("智能匹配失败：未找到正确的匹配帖子", details)
                self.test_results.append(result)
                return False
            
            # 检查是否排除了不匹配的帖子
            if interference_post.id not in matching_ids:
                details.append(f"✓ 正确排除干扰帖 #{interference_post.id} (不同地点: {interference_post.location})")
            else:
                details.append(f"⚠ 警告：匹配结果包含不同地点的帖子 #{interference_post.id}")
            
            # 测试反向匹配 - 为found帖查找匹配的lost帖
            reverse_matches = get_matching_posts(
                post_id=found_post.id,
                limit=10,
                time_range_days=7,
                session=self.session
            )
            
            reverse_ids = [post.id for post in reverse_matches]
            details.append(f"反向匹配：为拾得帖 #{found_post.id} 找到 {len(reverse_matches)} 个匹配")
            
            if lost_post.id in reverse_ids:
                details.append(f"✓ 反向匹配成功，找到失物帖 #{lost_post.id}")
            else:
                details.append(f"⚠ 警告：反向匹配未找到失物帖")
            
            result.success("智能匹配算法测试通过", details)
            self.test_results.append(result)
            return True
            
        except Exception as e:
            result.fail(f"智能匹配测试失败: {str(e)}")
            self.test_results.append(result)
            return False
    
    async def test_claim_and_notification(self):
        """测试认领请求和消息推送功能"""
        print("\n📬 测试认领请求和消息推送...")
        result = TestResult("认领请求与消息推送")
        
        try:
            loser = self.test_users['loser']
            finder = self.test_users['finder']
            found_post = self.test_posts['found']
            
            # 记录认领前的通知数量
            before_notif_count = self.session.exec(
                select(Notification).where(Notification.user_id == finder.id)
            ).all()
            before_count = len(before_notif_count)
            
            # 创建认领请求（失主认领拾得者的found帖）
            claim = Claim(
                post_id=found_post.id,
                claimer_id=loser.id,
                message="这是我丢失的iPhone，黑色，有透明壳和贴膜，我可以提供更多证明信息。",
                status='pending'
            )
            self.session.add(claim)
            self.session.commit()
            self.session.refresh(claim)
            
            details = [
                f"失主 '{loser.name}' (ID: {loser.id}) 对拾得帖 #{found_post.id} 发起认领",
                f"认领ID: {claim.id}",
                f"认领状态: {claim.status}"
            ]
            
            # 手动触发通知创建（模拟API中的异步调用）
            await NotificationService.create_claim_notification(
                self.session,
                claim,
                found_post
            )
            
            # 刷新session以获取新创建的通知
            self.session.expire_all()
            
            # 验证通知是否发送给拾得者（帖子作者）
            notifications = self.session.exec(
                select(Notification).where(
                    Notification.user_id == finder.id,
                    Notification.type == NotificationType.CLAIM_CREATED
                ).order_by(Notification.created_at.desc())
            ).all()
            
            after_count = len(notifications)
            new_notif_count = after_count - before_count
            
            if new_notif_count > 0:
                latest_notif = notifications[0]
                details.append(f"✓ 成功创建通知，发送给拾得者 '{finder.name}' (ID: {finder.id})")
                details.append(f"  通知标题: {latest_notif.title}")
                details.append(f"  通知内容: {latest_notif.content}")
                details.append(f"  通知类型: {latest_notif.type}")
                details.append(f"  通知状态: {latest_notif.status}")
                details.append(f"  关联帖子ID: {latest_notif.related_post_id}")
                details.append(f"  关联认领ID: {latest_notif.related_claim_id}")
                
                # 验证通知内容是否正确
                if str(found_post.id) in str(latest_notif.related_post_id):
                    details.append(f"✓ 通知正确关联到帖子 #{found_post.id}")
                
                if str(claim.id) in str(latest_notif.related_claim_id):
                    details.append(f"✓ 通知正确关联到认领 #{claim.id}")
                
                result.success("认领请求和消息推送测试通过", details)
            else:
                result.fail(f"消息推送失败：未创建通知", details)
            
            self.test_results.append(result)
            return new_notif_count > 0
            
        except Exception as e:
            import traceback
            error_details = [str(e), traceback.format_exc()]
            result.fail(f"认领与通知测试失败", error_details)
            self.test_results.append(result)
            return False
    
    async def test_claim_approval_notification(self):
        """测试认领批准通知"""
        print("\n✅ 测试认领批准通知...")
        result = TestResult("认领批准通知")
        
        try:
            loser = self.test_users['loser']
            finder = self.test_users['finder']
            found_post = self.test_posts['found']
            
            # 获取刚才创建的认领
            claim = self.session.exec(
                select(Claim).where(
                    Claim.post_id == found_post.id,
                    Claim.claimer_id == loser.id
                )
            ).first()
            
            if not claim:
                result.fail("未找到认领记录")
                self.test_results.append(result)
                return False
            
            # 批准认领
            claim.status = 'approved'
            claim.confirmed_at = datetime.utcnow()
            claim.owner_reply = "确认是您的手机，请联系我领取。"
            found_post.is_claimed = True
            
            self.session.add(claim)
            self.session.add(found_post)
            self.session.commit()
            
            # 发送批准通知给失主
            await NotificationService.create_claim_approved_notification(
                self.session,
                claim,
                found_post
            )
            
            # 验证通知
            self.session.expire_all()
            notifications = self.session.exec(
                select(Notification).where(
                    Notification.user_id == loser.id,
                    Notification.type == NotificationType.CLAIM_APPROVED
                ).order_by(Notification.created_at.desc())
            ).all()
            
            if notifications:
                latest_notif = notifications[0]
                details = [
                    f"✓ 批准认领成功，认领ID: {claim.id}",
                    f"✓ 帖子 #{found_post.id} 已标记为已认领",
                    f"✓ 成功发送批准通知给失主 '{loser.name}'",
                    f"  通知标题: {latest_notif.title}",
                    f"  通知内容: {latest_notif.content}",
                    f"  拾得者回复: {claim.owner_reply}"
                ]
                result.success("认领批准通知测试通过", details)
            else:
                result.fail("批准通知未创建")
            
            self.test_results.append(result)
            return bool(notifications)
            
        except Exception as e:
            result.fail(f"认领批准测试失败: {str(e)}")
            self.test_results.append(result)
            return False
    
    async def test_complete_workflow(self):
        """测试完整的工作流程"""
        print("\n🔄 测试完整工作流程...")
        result = TestResult("完整工作流程测试")
        
        try:
            # 场景：一个新用户丢失了物品，发现有匹配的拾得帖，发起认领
            loser = self.test_users['loser']
            lost_post = self.test_posts['lost']
            found_post = self.test_posts['found']
            finder = self.test_users['finder']
            
            details = [
                "=== 工作流程 ===",
                f"1. 失主 '{loser.name}' 发布失物帖 #{lost_post.id}",
                f"2. 失主查看智能匹配，发现拾得帖 #{found_post.id}",
                f"3. 失主对拾得帖发起认领请求",
                f"4. 系统向拾得者 '{finder.name}' 发送认领通知",
                f"5. 拾得者批准认领请求",
                f"6. 系统向失主发送批准通知",
                f"7. 双方联系完成物品归还"
            ]
            
            # 验证整个流程的数据完整性
            claim_count = self.session.exec(
                select(Claim).where(Claim.post_id == found_post.id)
            ).all()
            
            notif_to_finder = self.session.exec(
                select(Notification).where(
                    Notification.user_id == finder.id,
                    Notification.type == NotificationType.CLAIM_CREATED
                )
            ).all()
            
            notif_to_loser = self.session.exec(
                select(Notification).where(
                    Notification.user_id == loser.id,
                    Notification.type == NotificationType.CLAIM_APPROVED
                )
            ).all()
            
            details.append("")
            details.append("=== 验证结果 ===")
            details.append(f"✓ 认领请求数: {len(claim_count)}")
            details.append(f"✓ 发送给拾得者的通知: {len(notif_to_finder)}")
            details.append(f"✓ 发送给失主的通知: {len(notif_to_loser)}")
            details.append(f"✓ 帖子已认领状态: {found_post.is_claimed}")
            
            all_ok = (
                len(claim_count) > 0 and
                len(notif_to_finder) > 0 and
                len(notif_to_loser) > 0 and
                found_post.is_claimed
            )
            
            if all_ok:
                result.success("完整工作流程测试通过", details)
            else:
                result.fail("工作流程不完整", details)
            
            self.test_results.append(result)
            return all_ok
            
        except Exception as e:
            result.fail(f"完整流程测试失败: {str(e)}")
            self.test_results.append(result)
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 70)
        print("开始系统集成测试 - 智能匹配与消息推送")
        print("=" * 70)
        
        # 清理旧数据
        self.cleanup_test_data()
        
        # 创建测试数据
        if not self.setup_test_data():
            print("\n❌ 测试数据创建失败，测试终止")
            return
        
        # 执行各项测试
        self.test_smart_matching()
        await self.test_claim_and_notification()
        await self.test_claim_approval_notification()
        await self.test_complete_workflow()
        
        # 打印测试结果
        print("\n" + "=" * 70)
        print("测试结果汇总")
        print("=" * 70)
        
        for test_result in self.test_results:
            test_result.print_result()
        
        # 统计
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        failed = total - passed
        
        print("\n" + "=" * 70)
        print(f"总计: {total} 个测试")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"通过率: {(passed/total*100):.1f}%")
        print("=" * 70)
        
        # 清理测试数据（可选）
        # self.cleanup_test_data()
        
        self.session.close()

async def main():
    """主函数"""
    tester = SmartMatchingTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
