export function moneyToCents(value) {
  const s = String(value).trim();
  if (!/^\d+(?:\.\d{1,2})?$/.test(s)) throw new Error('金额请填写非负数字，最多两位小数。');
  const [whole, frac = ''] = s.split('.');
  const cents = Number(whole) * 100 + Number(frac.padEnd(2, '0'));
  if (!Number.isSafeInteger(cents) || cents > 100000000) throw new Error('金额超出可计算范围。');
  return cents;
}
export function unitRate(cents, quota, multiplierTenths = 10) {
  const numerator = BigInt(cents) * BigInt(multiplierTenths) * 10n;
  const denominator = BigInt(quota);
  const scaled = (numerator * 2n + denominator) / (denominator * 2n);
  return `${scaled / 10000n}.${String(scaled % 10000n).padStart(4, '0')}`;
}
export function selectPlans(services, { usage, budget, billing = '按量', service = 'all', multiplier = '1' }) {
  const text = String(usage).trim();
  if (!/^\d+$/.test(text) || Number(text) < 1 || Number(text) > 1000000) throw new Error('用量请填写 1 至 1,000,000 的整数 GB。');
  if (!['按量', '月付'].includes(billing)) throw new Error('请选择按量或普通月付。');
  if (!['0.1', '1', '2', '3'].includes(String(multiplier))) throw new Error('请选择列出的扣量倍率。');
  const cents = moneyToCents(budget), required = Number(text), mt = Math.round(Number(multiplier) * 10);
  return services.flatMap(s => (service === 'all' || service === s.id) ? (s.pricing || []).filter(p =>
    p.billing === billing && moneyToCents(p.price_cny) <= cents && p.quota_gb_for_unit_price * 10 >= required * mt
  ).map(p => ({ ...p, service_id: s.id, service_name: s.name, url: s.url,
    price_cents: moneyToCents(p.price_cny), effective_rate: unitRate(moneyToCents(p.price_cny), p.quota_gb_for_unit_price, mt),
    effective_quota: p.quota_gb_for_unit_price * 10 / mt })) : [])
    .sort((a, b) => a.price_cents - b.price_cents || b.quota_gb_for_unit_price - a.quota_gb_for_unit_price || a.service_id.localeCompare(b.service_id));
}
