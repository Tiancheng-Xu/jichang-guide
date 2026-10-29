import { selectPlans } from './plan-utils.mjs';
const form = document.querySelector('#plan-filter');
const table = document.querySelector('#filtered-plans');
const status = document.querySelector('#filter-status');
const services = JSON.parse(document.querySelector('#service-data').textContent).services;
function render() {
  try {
    const inputs = Object.fromEntries(new FormData(form));
    const plans = selectPlans(services, inputs);
    table.replaceChildren();
    for (const plan of plans) {
      const row = document.createElement('tr');
      const values = [plan.service_name, `${plan.price_cny} 元`, plan.quota_display,
        `约 ${plan.effective_quota.toLocaleString('zh-CN', {maximumFractionDigits:2})} GB`, `${plan.effective_rate} 元`];
      for (const value of values) { const cell = document.createElement('td'); cell.textContent = value; row.append(cell); }
      const cell = document.createElement('td'), link = document.createElement('a');
      link.href = plan.url; link.rel = 'sponsored noopener'; link.textContent = '访问入口'; cell.append(link); row.append(cell); table.append(row);
    }
    if (!plans.length) { const row = document.createElement('tr'), cell = document.createElement('td'); cell.colSpan = 6; cell.textContent = '参考报价中没有符合条件的套餐。可以提高预算、调整计费方式或减少用量。'; row.append(cell); table.append(row); }
    status.textContent = `找到 ${plans.length} 个符合用量和首付预算的参考套餐，按付款金额升序。统一按 ${inputs.multiplier}× 扣量估算。`;
  } catch (error) { status.textContent = error.message; table.replaceChildren(); }
}
form.addEventListener('submit', event => { event.preventDefault(); render(); });
form.addEventListener('change', render);
form.addEventListener('input', render);
render();
