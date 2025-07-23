<template>
  <div class="asset-snapshot-overview">
    <div class="controls">
      <el-select v-model="baseCurrency" placeholder="选择基准货币" @change="loadData">
        <el-option v-for="c in baseCurrencies" :key="c" :label="c" :value="c" />
      </el-select>
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" @change="loadData" />
    </div>
    <el-table :data="assetData" style="width: 100%">
      <el-table-column prop="platform" label="平台" />
      <el-table-column prop="asset_type" label="资产类型" />
      <el-table-column prop="asset_code" label="资产代码" />
      <el-table-column prop="currency" label="币种" />
      <el-table-column :label="baseCurrency + '金额'">
        <template #default="scope">
          <span>{{ formatAmount(scope.row.base_value, baseCurrency) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="snapshot_time" label="快照时间" />
    </el-table>
    <div class="trend-chart">
      <h3>资产趋势({{ baseCurrency }})</h3>
      <AssetTrendChart :base-currency="baseCurrency" :days="30" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElSelect, ElOption, ElDatePicker, ElTable, ElTableColumn } from 'element-plus'
import AssetTrendChart from './AssetTrendChart.vue'

const baseCurrencies = ['CNY', 'USD', 'EUR']
const baseCurrency = ref('CNY')
const dateRange = ref([])
const assetData = ref([])

const formatAmount = (val, cur) => {
  if (val == null) return '-'
  return new Intl.NumberFormat('zh-CN', { style: 'currency', currency: cur }).format(val)
}

const loadData = async () => {
  let params = new URLSearchParams()
  params.append('base_currency', baseCurrency.value)
  if (dateRange.value.length === 2) {
    params.append('start', dateRange.value[0])
    params.append('end', dateRange.value[1])
  }
  const resp = await fetch('/api/snapshot/assets?' + params.toString())
  assetData.value = await resp.json()
}

onMounted(loadData)
</script>

<style scoped>
.asset-snapshot-overview { padding: 20px; }
.controls { margin-bottom: 20px; display: flex; gap: 20px; }
.trend-chart { margin-top: 40px; }
</style>