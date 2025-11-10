<template>
  <div>
    <NotificationToast
      v-for="toast in toasts"
      :key="toast.id"
      :title="toast.title"
      :message="toast.message"
      :duration="toast.duration"
      :notificationId="toast.notificationId"
      @close="removeToast(toast.id)"
      @click="handleToastClick(toast)"
      class="mb-2"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useUserStore } from '@/stores/user';
import NotificationToast from './NotificationToast.vue';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();
const toasts = ref([]);
// 从 localStorage 读取上次显示的通知ID，避免刷新页面后重复弹出
const lastNotificationId = ref(parseInt(localStorage.getItem('lastNotificationId')) || null);
const isInitialized = ref(false); // 新增：记录是否已初始化
let pollingInterval = null;
let toastIdCounter = 0;

// 检查新通知
const checkForNewNotifications = async () => {
  try {
    // 即使getNotifications内部出错，也不会中断轮询
    const notifications = await userStore.getNotifications() || [];
    
    // 找出新通知
    if (notifications.length > 0) {
      const latestNotification = notifications[0];
      
      // 只在已初始化后才显示通知（避免页面加载时弹出老通知）
      if (isInitialized.value && latestNotification && (!lastNotificationId.value || latestNotification.id > lastNotificationId.value)) {
        lastNotificationId.value = latestNotification.id;
        // 保存到 localStorage，防止刷新页面后重复弹出
        localStorage.setItem('lastNotificationId', latestNotification.id.toString());
        
        // 显示通知
        showToast({
          title: '新通知',
          message: latestNotification.content,
          notificationId: latestNotification.id
        });
      } else if (!isInitialized.value) {
        // 第一次加载时，只记录ID不显示
        lastNotificationId.value = latestNotification.id;
        // 保存到 localStorage
        localStorage.setItem('lastNotificationId', latestNotification.id.toString());
        isInitialized.value = true;
      }
    } else {
      // 如果没有通知，也标记为已初始化
      if (!isInitialized.value) {
        isInitialized.value = true;
      }
    }
    
    // 异步更新未读计数，不影响主流程
    try {
      await userStore.getUnreadCount();
    } catch (error) {
      console.warn('Failed to update unread count, will retry next time:', error);
    }
  } catch (error) {
    console.error('Failed to check for new notifications:', error);
    // 即使出错也不抛出异常，确保轮询继续进行
  }
};

// 显示通知
const showToast = (toast) => {
  const id = toastIdCounter++;
  toasts.value.push({
    id,
    title: toast.title || '通知',
    message: toast.message,
    duration: toast.duration || 5000,
    notificationId: toast.notificationId
  });
  
  // 限制最多显示3个通知
  if (toasts.value.length > 3) {
    toasts.value.shift();
  }
};

// 移除通知
const removeToast = (id) => {
  const index = toasts.value.findIndex(toast => toast.id === id);
  if (index !== -1) {
    toasts.value.splice(index, 1);
  }
};

// 处理通知点击
const handleToastClick = async (toast) => {
  if (toast.notificationId) {
    // 标记为已读（不等待结果，让用户体验更流畅）
    userStore.markNotificationRead(toast.notificationId).catch(error => {
      console.warn('Failed to mark notification as read, will try again later:', error);
    });
    
    // 如果通知有关联链接，可以在这里处理导航
    const notification = userStore.notifications.find(n => n.id === toast.notificationId);
    if (notification) {
      // 检查notification对象中可能的链接字段
      if (notification.link) {
        router.push(notification.link);
      } else if (notification.related_post_id) {
        // 帖子详情
        router.push(`/forum/${notification.related_post_id}`);
      } else if (notification.related_claim_id) {
        // 认领相关：根据通知类型跳转到合适的标签页
        const t = (notification.type || '').toLowerCase();
        if (t.includes('claim_created')) {
          router.push({ path: '/claims', query: { tab: 'received' } });
        } else if (t.includes('claim_approved') || t.includes('claim_rejected') || t.includes('claim_cancelled')) {
          router.push({ path: '/claims', query: { tab: 'submitted' } });
        } else {
          router.push('/claims');
        }
      }
    }
  }
};

// 开始轮询
const startPolling = () => {
  // 初始检查
  checkForNewNotifications();
  
  // 设置轮询间隔（每30秒检查一次）
  pollingInterval = setInterval(checkForNewNotifications, 30000);
};

onMounted(() => {
  startPolling();
});

onUnmounted(() => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
  }
});

// 暴露方法给外部使用
defineExpose({
  showToast
});
</script>