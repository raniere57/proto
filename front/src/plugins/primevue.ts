import type { App } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Password from 'primevue/password'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import MultiSelect from 'primevue/multiselect'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Toast from 'primevue/toast'
import Dialog from 'primevue/dialog'
import ProgressSpinner from 'primevue/progressspinner'
import Message from 'primevue/message'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

export function registerPrimeVueComponents(app: App) {
  app.component('Button', Button)
  app.component('InputText', InputText)
  app.component('Textarea', Textarea)
  app.component('Password', Password)
  app.component('Select', Select)
  app.component('DatePicker', DatePicker)
  app.component('MultiSelect', MultiSelect)
  app.component('Tag', Tag)
  app.component('Divider', Divider)
  app.component('DataTable', DataTable)
  app.component('Column', Column)
  app.component('Toast', Toast)
  app.component('Dialog', Dialog)
  app.component('ProgressSpinner', ProgressSpinner)
  app.component('Message', Message)
  app.component('ConfirmDialog', ConfirmDialog)
}
