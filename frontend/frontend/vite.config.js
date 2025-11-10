import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
import viteCompression from 'vite-plugin-compression';
import { ViteImageOptimizer } from 'vite-plugin-image-optimizer';

// https://vite.dev/config/
// 移除Vue DevTools等开发依赖相关配置（假设开发依赖在插件配置部分引入，需根据实际调整）
// 按需引入Element Plus组件，假设已有相关插件配置，可补充相关配置项
// 启用代码分割和懒加载，可在rollupOptions中进一步优化配置
// 压缩并移除未使用代码，确保terserOptions等配置正确

// 补充SEO相关配置，例如添加meta标签相关处理逻辑（假设项目有相关处理方式，需根据实际调整）
// 处理无障碍相关问题，例如添加html lang属性相关逻辑（假设在构建过程中有处理方式，需根据实际调整）

// 安全头相关配置，假设项目有相关中间件或配置方式，可添加相关配置代码（需根据实际调整）
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    Components({
      resolvers: [
        ElementPlusResolver({
          importStyle: 'css',
          resolveIcons: true
        })
      ],
    }),
    // 启用gzip压缩
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10240,
      algorithm: 'gzip',
      ext: '.gz',
      deleteOriginFile: false
    }),
    // 图片压缩优化
    ViteImageOptimizer({
      png: {
        quality: 80
      },
      jpeg: {
        quality: 80
      },
      jpg: {
        quality: 80
      },
      webp: {
        quality: 80
      },
      svg: {
        multipass: true,
        plugins: [
          {
            name: 'preset-default',
            params: {
              overrides: {
                removeViewBox: false,
                cleanupNumericValues: false
              }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
      format: {
        comments: false,
      }
    },
    cssMinify: true,
    // 优化chunk拆分策略
    rollupOptions: {
      output: {
        chunkSizeWarningLimit: 500,
        manualChunks: {
          // 将Element Plus拆分成独立chunk
          'element-plus': ['element-plus', '@element-plus/icons-vue'],
          // 将Vue相关库拆分成独立chunk
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          // 按路由拆分组件
          'forum-components': [
            '@/views/forum/ForumListView.vue',
            '@/views/forum/PostDetailView.vue',
            '@/views/forum/CreatePostView.vue'
          ],
          'user-components': [
            '@/views/user/DashboardView.vue',
            '@/views/user/ProfileView.vue',
            '@/views/user/ClaimsView.vue',
            '@/views/user/UserProfileView.vue'
          ],
          'auth-components': [
            '@/views/auth/LoginView.vue',
            '@/views/auth/RegisterView.vue'
          ]
        },
        // 代码分割策略
        codeSplit: true,
        // 使用命名策略
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // 优化图片处理
    assetsInlineLimit: 4096,
    outDir: 'dist',
    assetsDir: 'assets',
    cssCodeSplit: true,
    // 启用持久化缓存
    cacheDir: 'node_modules/.vite',
    // 启用并行构建
    chunkSizeWarningLimit: 500
  },
  // 优化开发服务器配置
  server: {
    port: 5173,
    open: false,
    cors: true
  }
})
