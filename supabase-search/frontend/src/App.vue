<template>
  <div class="container">
    <header class="header">
      <h1>🔍 <span>语义搜索</span></h1>
      <p>输入任何问题，AI 会理解你的意图并找到相关内容</p>
      <div class="badge">✅ 向量已就绪 · 共 {{ totalCount }} 条数据</div>
    </header>

    <!-- 搜索框 -->
    <div class="search-box">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="输入你想搜索的内容..."
        @keyup.enter="doSearch"
        autofocus
      />
      <button @click="doSearch" :disabled="loading">
        {{ loading ? '⏳ 搜索中...' : '🔍 搜索' }}
      </button>
    </div>

    <!-- 示例标签 - 从环境变量读取 -->
    <div class="examples" v-if="exampleTags.length > 0">
      <span
        v-for="tag in exampleTags"
        :key="tag"
        class="tag"
        @click="quickSearch(tag)"
      >
        {{ tag }}
      </span>
    </div>

    <!-- 数据统计 -->
    <div class="data-stats">
      <span>📊 总数据: <span class="num">{{ totalCount }}</span></span>
      <span>✅ 有向量: <span class="num">{{ vectorCount }}</span></span>
      <span>📋 上次搜索: <span class="num">{{ lastSearch || '-' }}</span></span>
    </div>

    <!-- 控制面板 -->
    <div class="controls">
      <div class="control-group">
        <label>🎯 阈值</label>
        <input
          type="range"
          v-model.number="threshold"
          min="0.1"
          max="0.9"
          step="0.05"
        />
        <span class="threshold-value">{{ threshold.toFixed(2) }}</span>
      </div>
      <div class="control-group">
        <label>📄 数量</label>
        <select v-model.number="limit">
          <option :value="3">3</option>
          <option :value="5">5</option>
          <option :value="10">10</option>
          <option :value="20">20</option>
        </select>
      </div>
      <div class="stats">{{ statusMessage }}</div>
    </div>

    <!-- 结果区域 -->
    <div id="results">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>🔍 AI 正在理解你的问题...</p>
      </div>

      <div v-else-if="errorMessage" class="error-msg">
        ❌ {{ errorMessage }}
      </div>

      <div v-else-if="results.length === 0 && !loading" class="empty">
        <div class="icon">🔍</div>
        <p>输入搜索词，开始探索</p>
        <div class="hint" v-if="exampleTags.length > 0">试试点击上面的标签</div>
      </div>

      <div v-else>
        <div
          v-for="(item, index) in results"
          :key="item.id"
          class="result-item"
        >
          <span class="rank">#{{ index + 1 }}</span>
          <span style="font-size:13px;color:#999;">ID: {{ item.id }}</span>
          <div class="content" v-html="highlightText(item.content, searchQuery)"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

// ============================================================
// 从环境变量读取配置
// ============================================================
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL
const ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY

// 读取快捷搜索标签（用户可自定义）
const tagsString = import.meta.env.VITE_EXAMPLE_TAGS || ''
const exampleTags = ref<string[]>([])

// 解析标签
if (tagsString) {
  exampleTags.value = tagsString.split(',').map(t => t.trim()).filter(t => t.length > 0)
}

// 如果没有配置，使用默认值
if (exampleTags.value.length === 0) {
  exampleTags.value = ['Supabase', '向量搜索', 'Edge Functions', '数据库', '机器学习']
}

// 检查环境变量是否配置
if (!SUPABASE_URL || !ANON_KEY) {
  console.error('❌ 请在 .env.local 中配置 VITE_SUPABASE_URL 和 VITE_SUPABASE_ANON_KEY')
}

const API_URL = `${SUPABASE_URL}/functions/v1/search`
const DATA_URL = `${SUPABASE_URL}/rest/v1/embeddings?select=id,content,embedding`

// ============================================================
// 状态
// ============================================================
const searchQuery = ref(exampleTags.value[0] || 'Supabase')
const threshold = ref(0.3)
const limit = ref(5)
const loading = ref(false)
const results = ref<any[]>([])
const errorMessage = ref('')
const statusMessage = ref('💡 输入关键词开始搜索')
const totalCount = ref(0)
const vectorCount = ref(0)
const lastSearch = ref('')

// ============================================================
// 方法
// ============================================================
async function doSearch() {
  const query = searchQuery.value.trim()
  if (!query) {
    errorMessage.value = '请输入搜索词'
    return
  }

  loading.value = true
  errorMessage.value = ''
  statusMessage.value = '⏳ 搜索中...'

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        search: query,
        threshold: threshold.value,
        limit: limit.value,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()

    if (data.error) {
      errorMessage.value = data.error
      results.value = []
      statusMessage.value = '❌ 搜索失败'
      return
    }

    results.value = data.results || []
    lastSearch.value = data.search || query
    statusMessage.value = `✅ 找到 ${results.value.length} 条结果 (阈值: ${threshold.value})`
  } catch (err: any) {
    errorMessage.value = err.message || '搜索失败'
    results.value = []
    statusMessage.value = '❌ 搜索失败'
  } finally {
    loading.value = false
  }
}

function quickSearch(query: string) {
  searchQuery.value = query
  doSearch()
}

function highlightText(text: string, keyword: string): string {
  if (!keyword || !text) return text
  const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(escaped, 'gi')
  return text.replace(regex, (match) => `<mark>${match}</mark>`)
}

async function getDataStats() {
  try {
    const response = await fetch(DATA_URL, {
      headers: { apikey: ANON_KEY },
    })
    const data = await response.json()
    totalCount.value = data.length
    vectorCount.value = data.filter((d: any) => d.embedding).length

    if (totalCount.value === 0) {
      statusMessage.value = '⚠️ 暂无数据，请先添加内容'
    } else if (vectorCount.value === 0) {
      statusMessage.value = '⚠️ 数据正在生成向量，请稍候...'
    } else {
      statusMessage.value = `✅ ${vectorCount.value}/${totalCount.value} 条数据已就绪`
    }
  } catch (err) {
    console.error('获取统计失败:', err)
  }
}

// ============================================================
// 生命周期
// ============================================================
onMounted(() => {
  if (!SUPABASE_URL || !ANON_KEY) {
    statusMessage.value = '⚠️ 请配置 .env.local 文件'
    return
  }
  getDataStats()
  setTimeout(doSearch, 500)
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}
.header h1 {
  font-size: 36px;
  color: #333;
  margin-bottom: 8px;
}
.header h1 span {
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.header p {
  color: #888;
  font-size: 14px;
}
.header .badge {
  display: inline-block;
  background: #e8f5e9;
  color: #2e7d32;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin-top: 8px;
}

.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.search-box input {
  flex: 1;
  padding: 16px 20px;
  font-size: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  outline: none;
  transition: border-color 0.3s;
}
.search-box input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}
.search-box button {
  padding: 16px 40px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.search-box button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}
.search-box button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.examples {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.examples .tag {
  padding: 4px 14px;
  font-size: 13px;
  color: #667eea;
  background: #f0f0ff;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}
.examples .tag:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.data-stats {
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #666;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.data-stats .num {
  font-weight: 700;
  color: #333;
}

.controls {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
  padding: 15px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 20px;
}
.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.control-group label {
  font-size: 14px;
  color: #666;
}
.control-group input[type='range'] {
  width: 120px;
  accent-color: #667eea;
}
.control-group select {
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}
.threshold-value {
  font-weight: 600;
  color: #667eea;
  min-width: 30px;
  font-size: 14px;
}
.stats {
  margin-left: auto;
  color: #888;
  font-size: 14px;
}

#results {
  min-height: 200px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #888;
}
.loading .spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid #f0f0f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty {
  text-align: center;
  padding: 60px 20px;
  color: #aaa;
}
.empty .icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.empty p {
  font-size: 16px;
}
.empty .hint {
  font-size: 13px;
  color: #ccc;
  margin-top: 8px;
}

.result-item {
  padding: 18px 20px;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  margin-bottom: 12px;
  transition: all 0.3s;
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.result-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.08);
  transform: translateX(4px);
}
.result-item .rank {
  display: inline-block;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 12px;
  font-weight: 700;
  padding: 2px 10px;
  border-radius: 20px;
  margin-right: 10px;
}
.result-item .content {
  font-size: 15px;
  line-height: 1.6;
  color: #333;
  margin-top: 6px;
}
.result-item .content :deep(mark) {
  background: #fff3cd;
  padding: 0 4px;
  border-radius: 2px;
}

.error-msg {
  padding: 16px 20px;
  background: #fff5f5;
  border: 1px solid #fcd;
  border-radius: 12px;
  color: #c0392b;
  text-align: center;
}

@media (max-width: 640px) {
  .container {
    padding: 20px;
  }
  .search-box {
    flex-direction: column;
  }
  .search-box button {
    width: 100%;
  }
  .controls {
    flex-direction: column;
    align-items: stretch;
  }
  .stats {
    margin-left: 0;
    text-align: center;
  }
  .header h1 {
    font-size: 28px;
  }
}
</style>