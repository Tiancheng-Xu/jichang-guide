import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { moneyToCents, unitRate, selectPlans } from '../web/plan-utils.mjs';
const services = JSON.parse(readFileSync(new URL('../data/services.json', import.meta.url))).services;
test('decimal half-up matches published dataset for all 53 plans', () => {
 let count=0;
 for (const s of services) for (const p of s.pricing || []) {
  assert.equal(unitRate(moneyToCents(p.price_cny),p.quota_gb_for_unit_price),p.nominal_cny_per_gb);count++;
 }
 assert.equal(count,53);
 assert.equal(unitRate(7590,6000),'0.0127');
});
test('3x nodes require 150 nominal GB for 50 actual GB',()=>{
 const rows=selectPlans(services,{usage:50,budget:50,service:'wangji',billing:'按量',multiplier:'3'});
 assert.deepEqual(rows.map(p=>p.price_cny),['44']);assert.equal(rows[0].effective_rate,'0.6600');
});
test('budget is upfront and billing types stay separate',()=>{
 const rows=selectPlans(services,{usage:100,budget:10,billing:'月付',multiplier:'1'});
 assert.deepEqual(rows.map(p=>p.service_id),['niubi','paoche','yesha']);
 assert.ok(rows.every(p=>p.billing==='月付'));assert.ok(!rows.some(p=>p.service_id==='yiyuan'));
});
test('boundaries, no result and invalid inputs are explicit',()=>{
 assert.equal(selectPlans(services,{usage:200,budget:'13.90',service:'niubi'}).length,1);
 assert.equal(selectPlans(services,{usage:201,budget:'13.90',service:'niubi'}).length,0);
 assert.equal(selectPlans(services,{usage:1,budget:0}).length,0);
 for(const value of ['-1','NaN','1e3','100.001','Infinity']) assert.throws(()=>moneyToCents(value));
 for(const value of ['0','1.5','NaN','1000001']) assert.throws(()=>selectPlans(services,{usage:value,budget:50}));
 assert.throws(()=>selectPlans(services,{usage:50,budget:50,billing:'年付'}));
});
