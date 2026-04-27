<template>
  <div>
    <div class="page-header">
      <h1>Dashboard NOC TX</h1>
      <p>Análise completa de protocolos e insights operacionais</p>
    </div>

    <div class="card">
      <div class="filters">
        <label>Período:</label>
        <Select v-model="periodo" :options="opcoesPeriodo" optionLabel="nome" optionValue="valor" @change="carregar" />
        <Tag severity="info" class="total-badge">Total: {{ data?.total_protocolos || 0 }} protocolos</Tag>
      </div>
    </div>

    <div v-if="loading" class="card" style="text-align:center;padding:4rem"><ProgressSpinner /></div>

    <template v-if="data">
      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-icon">📋</div>
          <div class="stat-label">Total</div>
          <div class="stat-value">{{ data.total_protocolos }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-icon">🔴</div>
          <div class="stat-label">Ativos</div>
          <div class="stat-value">{{ data.protocolos_ativos }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-icon">✅</div>
          <div class="stat-label">Resolvidos</div>
          <div class="stat-value">{{ data.protocolos_resolvidos }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-icon">📈</div>
          <div class="stat-label">Taxa de Resolução</div>
          <div class="stat-value">{{ data.taxa_resolucao }}%</div>
          <div class="progress-bar"><div class="progress-fill" :style="{width: data.taxa_resolucao + '%'}"></div></div>
        </div>
      </div>

      <!-- Protocolos Críticos -->
      <div v-if="data.protocolos_criticos?.length" class="card alert-critical">
        <h3>⚠️ Protocolos Críticos (ativos há mais de 24h)</h3>
        <div v-for="p in data.protocolos_criticos" :key="p.id" class="critical-item">
          <span><strong>{{ p.numero }}</strong> — {{ p.tipo_evento }}</span>
          <router-link :to="`/protocolos/${p.id}`"><Tag value="Ver detalhes" severity="danger" /></router-link>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="charts-grid">
        <div class="card chart-card">
          <h3>📊 Eventos</h3>
          <canvas ref="eventosCanvas"></canvas>
        </div>
        <div class="card chart-card">
          <h3>🌐 Redes</h3>
          <canvas ref="redesCanvas"></canvas>
        </div>
        <div class="card chart-card">
          <h3>📍 Estados</h3>
          <canvas ref="estadosCanvas"></canvas>
        </div>
        <div class="card chart-card">
          <h3>👥 Top Responsáveis</h3>
          <canvas ref="responsaveisCanvas"></canvas>
        </div>
        <div class="card chart-card full-width">
          <h3>📅 Evolução Mensal</h3>
          <canvas ref="temporalCanvas"></canvas>
        </div>
      </div>

      <!-- Top Trechos + POPs -->
      <div class="tables-grid">
        <div class="card" v-if="data.top_trechos?.length">
          <h3>🏆 Top Trechos</h3>
          <DataTable :value="data.top_trechos" stripedRows size="small">
            <Column field="trecho" header="Trecho" />
            <Column field="total" header="Total">
              <template #body="{ data }"><Tag :value="data.total" /></template>
            </Column>
          </DataTable>
        </div>
        <div class="card" v-if="data.top_pops_a?.length">
          <h3>📡 Top POPs (A)</h3>
          <DataTable :value="data.top_pops_a" stripedRows size="small">
            <Column field="pop" header="POP" />
            <Column field="total" header="Total">
              <template #body="{ data }"><Tag :value="data.total" /></template>
            </Column>
          </DataTable>
        </div>
        <div class="card" v-if="data.top_pops_b?.length">
          <h3>📡 Top POPs (B)</h3>
          <DataTable :value="data.top_pops_b" stripedRows size="small">
            <Column field="pop" header="POP" />
            <Column field="total" header="Total">
              <template #body="{ data }"><Tag :value="data.total" /></template>
            </Column>
          </DataTable>
        </div>
      </div>

      <!-- Eventos Detalhados -->
      <div class="card" v-if="data.eventos?.length">
        <h3>🔍 Análise por Tipo de Evento</h3>
        <DataTable :value="data.eventos" stripedRows size="small">
          <Column field="tipo_evento" header="Evento" />
          <Column field="total" header="Total" />
          <Column field="ativos" header="Ativos"><template #body="{ data }"><Tag v-if="data.ativos" :value="data.ativos" severity="danger" /><span v-else>0</span></template></Column>
          <Column field="resolvidos" header="Resolvidos"><template #body="{ data }"><Tag v-if="data.resolvidos" :value="data.resolvidos" severity="success" /><span v-else>0</span></template></Column>
          <Column header="Taxa"><template #body="{ data }">{{ data.total ? Math.round(data.resolvidos/data.total*100) : 0 }}%</template></Column>
        </DataTable>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import ProgressSpinner from 'primevue/progressspinner'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import { getDashboardNoc } from '@/api/dashboard'
import { extractError } from '@/api/client'
import { useToast } from 'primevue/usetoast'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)
const toast = useToast()

const eventosCanvas = ref<HTMLCanvasElement | null>(null)
const redesCanvas = ref<HTMLCanvasElement | null>(null)
const estadosCanvas = ref<HTMLCanvasElement | null>(null)
const responsaveisCanvas = ref<HTMLCanvasElement | null>(null)
const temporalCanvas = ref<HTMLCanvasElement | null>(null)
const data = ref<any>(null)
const loading = ref(true)
const periodo = ref('30')

const opcoesPeriodo = [
  { nome: 'Últimos 7 dias', valor: '7' },
  { nome: 'Últimos 30 dias', valor: '30' },
  { nome: 'Últimos 90 dias', valor: '90' },
  { nome: 'Últimos 6 meses', valor: '180' },
  { nome: 'Último ano', valor: '365' },
  { nome: 'Todos', valor: 'todos' },
]

const colors = ['#667eea', '#e74c3c', '#f39c12', '#27ae60', '#3498db', '#9b59b6', '#1abc9c', '#e67e22', '#2ecc71', '#e91e63']

async function carregar() {
  loading.value = true
  try {
    data.value = await getDashboardNoc(periodo.value)
    await nextTick()
    renderCharts()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Erro', detail: extractError(err), life: 5000 })
  } finally { loading.value = false }
}

function destroyCharts() {
  document.querySelectorAll('.chart-card canvas').forEach((el: any) => { el.__chart?.destroy() })
}

function renderCharts() {
  if (!data.value) return
  destroyCharts()

  const opts = { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom' as const, labels: { boxWidth: 12, padding: 8 } } } }

  // Eventos
  if (eventosCanvas.value && data.value.eventos?.length) {
    ;(eventosCanvas.value as any).__chart = new Chart(eventosCanvas.value.getContext('2d')!, {
      type: 'doughnut',
      data: { labels: data.value.eventos.map((e: any) => e.tipo_evento), datasets: [{ data: data.value.eventos.map((e: any) => e.total), backgroundColor: colors }] },
      options: opts,
    })
  }

  // Redes
  if (redesCanvas.value && data.value.redes?.length) {
    ;(redesCanvas.value as any).__chart = new Chart(redesCanvas.value.getContext('2d')!, {
      type: 'pie',
      data: { labels: data.value.redes.map((r: any) => r.tipo), datasets: [{ data: data.value.redes.map((r: any) => r.total), backgroundColor: colors }] },
      options: opts,
    })
  }

  // Estados
  if (estadosCanvas.value && data.value.estados?.length) {
    const labels = data.value.estados.map((e: any) => e.estado)
    const valores = data.value.estados.map((e: any) => e.total)
    ;(estadosCanvas.value as any).__chart = new Chart(estadosCanvas.value.getContext('2d')!, {
      type: 'bar',
      data: { labels, datasets: [{ label: 'Protocolos', data: valores, backgroundColor: colors[0], borderRadius: 4 }] },
      options: { ...opts, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
    })
  }

  // Responsáveis
  if (responsaveisCanvas.value && data.value.responsaveis?.length) {
    const labels = data.value.responsaveis.map((r: any) => r.nome.length > 20 ? r.nome.slice(0, 18) + '…' : r.nome)
    const totais = data.value.responsaveis.map((r: any) => r.total)
    ;(responsaveisCanvas.value as any).__chart = new Chart(responsaveisCanvas.value.getContext('2d')!, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          { label: 'Total', data: totais, backgroundColor: colors[0], borderRadius: 4 },
        ],
      },
      options: { ...opts, indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, ticks: { precision: 0 } } } },
    })
  }

  // Evolução Mensal
  if (temporalCanvas.value && data.value.evolucao_mensal?.length) {
    const labels = data.value.evolucao_mensal.map((m: any) => {
      const [y, mo] = m.mes.split('-')
      const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
      return `${meses[parseInt(mo) - 1]}/${y.slice(2)}`
    })
    ;(temporalCanvas.value as any).__chart = new Chart(temporalCanvas.value.getContext('2d')!, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { label: 'Total', data: data.value.evolucao_mensal.map((m: any) => m.total), borderColor: colors[0], backgroundColor: colors[0] + '20', fill: true, tension: 0.3 },
          { label: 'Rupturas', data: data.value.evolucao_mensal.map((m: any) => m.rupturas), borderColor: colors[1], tension: 0.3 },
          { label: 'Atenuações', data: data.value.evolucao_mensal.map((m: any) => m.atenuacoes), borderColor: colors[2], tension: 0.3 },
        ],
      },
      options: { ...opts, plugins: { legend: { position: 'top' } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
    })
  }
}

onMounted(carregar)
</script>

<style scoped>
.filters { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.total-badge { font-size: 0.9rem; padding: 0.4rem 0.8rem; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.stat-card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.stat-card.primary { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
.stat-card.danger { border-left: 4px solid #e74c3c; }
.stat-card.success { border-left: 4px solid #27ae60; }
.stat-card.warning { border-left: 4px solid #f39c12; }
.stat-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.stat-label { font-size: 0.85rem; color: inherit; opacity: 0.8; text-transform: uppercase; }
.stat-value { font-size: 2rem; font-weight: 700; }
.progress-bar { width: 100%; height: 6px; background: rgba(255,255,255,0.3); border-radius: 4px; margin-top: 0.75rem; overflow: hidden; }
.progress-fill { height: 100%; background: white; border-radius: 4px; transition: width 0.5s ease; }
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }
.charts-grid .full-width { grid-column: 1 / -1; }
.chart-card canvas { max-height: 280px; }
.chart-card h3 { font-size: 1.1rem; margin-bottom: 1rem; color: #2c3e50; }
.tables-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; }
.alert-critical { border-left: 4px solid #e74c3c; background: #fff5f5; }
.alert-critical h3 { color: #c0392b; font-size: 1.1rem; margin-bottom: 1rem; }
.critical-item { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0; }
.critical-item:last-child { border: none; }
@media (max-width: 900px) { .charts-grid, .tables-grid { grid-template-columns: 1fr; } }
</style>
