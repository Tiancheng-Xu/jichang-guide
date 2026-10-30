from pathlib import Path
from html import escape as esc
from decimal import Decimal
import json,csv,io,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'site'
ORIGIN='https://jichang.baby2b.online'
REPO='https://github.com/Tiancheng-Xu/jichang-guide'
data=json.loads((ROOT/'data/services.json').read_text());comparisons=json.loads((ROOT/'data/comparisons.json').read_text());source=data['pricing_source']['url']
OUT.mkdir(exist_ok=True)
for name in ['style.css','app.mjs','plan-utils.mjs']:shutil.copy2(ROOT/'web'/name,OUT/name)
def e(x):return esc(str(x),quote=True)
def table(headers,rows):return '<div class="tablewrap" tabindex="0" role="region" aria-label="可横向滚动的套餐表"><table><thead><tr>'+''.join('<th scope="col">'+e(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def link(s,label='访问入口'):return f'<a href="{e(s["url"])}" rel="sponsored noopener">{label}</a>'
def shell(path,title,description,body,extra=''):
 canonical=ORIGIN+path
 labels={'/budget/':'预算对比','/methodology/':'来源与方法','/guide/':'新手指南','/usage/':'按用量比较'}
 breadcrumb=''
 if path in labels:
  breadcrumb=f'<nav class="breadcrumbs" aria-label="面包屑"><a href="/">首页</a><span aria-hidden="true"> / </span><span aria-current="page">{e(labels[path])}</span></nav>'
 ld={'@context':'https://schema.org','@type':'WebPage','name':title,'url':canonical,'description':description,'inLanguage':'zh-CN','isPartOf':{'@type':'WebSite','name':'机场选购指南','url':ORIGIN+'/'},'author':{'@type':'Person','name':'Tiancheng-Xu','url':'https://github.com/Tiancheng-Xu'}}
 if path in labels:ld['breadcrumb']={'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'首页','item':ORIGIN+'/'},{'@type':'ListItem','position':2,'name':labels[path],'item':canonical}]}
 return f'''<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large"><link rel="canonical" href="{canonical}"><meta property="og:site_name" content="机场选购指南"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(description)}"><meta property="og:type" content="website"><meta property="og:locale" content="zh_CN"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{canonical}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><script type="application/ld+json">{json.dumps(ld,ensure_ascii=False).replace('<','\\u003c')}</script>{extra}</head><body><a class="skip" href="#main">跳到主要内容</a><header class="topbar"><nav class="wrap nav" aria-label="主导航"><a class="brand" href="/"><span>G</span>机场选购指南</a><div class="navlinks"><a href="/#calculator">套餐计算器</a><a href="/budget/">预算对比</a><a href="/guide/">新手指南</a><a href="/methodology/">来源与方法</a><a href="{REPO}">GitHub</a></div></nav></header><main id="main" class="wrap">{breadcrumb}{body}</main><footer class="footer"><div class="wrap"><div class="footerline"><span>机场选购指南 · Tiancheng-Xu</span><span><a href="/data/plans.csv">下载 CSV</a>　<a href="/data/services.json">查看 JSON</a>　<a href="{REPO}/issues">信息更正</a></span></div><p>独立资料整理；报价未从当前订单页核验，未做独立测速。通过部分链接注册或消费，维护者可能获得奖励，具体以服务商规则为准。</p><p>没有注册或支付表单，筛选在你的浏览器中完成。本项目未配置点击统计；托管平台的数据处理以其政策为准。</p></div></footer></body></html>'''
allplans=[]
for s in data['services']:
 for p in s['pricing'] or []:allplans.append((s,p))
initial=[(s,p) for s,p in allplans if p['billing']=='按量' and Decimal(p['price_cny'])<=50 and p['quota_gb_for_unit_price']>=50]
initial.sort(key=lambda x:(Decimal(x[1]['price_cny']),-x[1]['quota_gb_for_unit_price']))
initrows=''.join('<tr>'+''.join('<td>'+v+'</td>' for v in [e(s['name']),e(p['price_cny'])+' 元',e(p['quota_display']),e(p['quota_gb_for_unit_price'])+' GB',e(p['nominal_cny_per_gb'])+' 元',link(s)])+'</tr>' for s,p in initial)
options=''.join(f'<option value="{s["id"]}">{e(s["name"])}</option>' for s in data['services'])
body=f'''<section class="hero"><div><div class="eyebrow">先看实际付款 · 再比每 GB 成本</div><h1>按量付费机场对比，<br>算清每 GB 和首次付款。</h1><p class="lead">比较 8 家机场的服务特点、按量与月付报价。用真实的付款金额和扣量倍率筛选，算清标称单价与实际流量成本。</p><div class="meta"><span>8 家服务入口</span><span>53 档参考套餐</span><span>资料：2026-10-28</span></div></div><aside class="hero-note"><div class="number">¥ / GB</div><h2>最低单价 ≠ 最低首付</h2><p>大包的每 GB 单价可能更低，但需要先支付整包金额。月付、按量、年付和日享，也有不同的额度周期。</p><a href="/budget/">查看 10／20／50 元预算对比 →</a></aside></section><p class="notice">报价及特点来自 <a href="{source}">2026-10-26 的固定参考版本</a>，尚未完成当前官网价格核验。一元机场缺少可靠套餐资料，暂不参与价格筛选。</p><p class="section-intro">第一次搜索机场 VPN？先了解<a href="/guide/">机场与 VPN 的区别、订阅和客户端如何配合</a>，再按自己的用量比较费用。</p>
<section id="calculator" class="section"><h2>套餐计算器：这笔预算能覆盖多少用量？</h2><p class="section-intro">只选一个套餐，以标称额度覆盖目标用量。普通月付按一个月计算；按量比较一次付款。年付和日享在下方完整表中单列。</p><div class="panel"><form id="plan-filter"><div class="filters"><label class="field">计费方式<select name="billing"><option>按量</option><option>月付</option></select></label><label class="field">服务<select name="service"><option value="all">全部服务</option>{options}</select></label><label class="field">预计用量（GB）<input name="usage" type="number" min="1" max="1000000" step="1" value="50" inputmode="numeric" required></label><label class="field">单次付款预算（元）<input name="budget" type="number" min="0" max="1000000" step="0.01" value="50" inputmode="decimal" required></label><label class="field">统一扣量倍率<select name="multiplier"><option value="1">1× 标准估算</option><option value="0.1">0.1× 特殊节点</option><option value="2">2×</option><option value="3">3×</option></select></label></div><div class="filterfooter"><button class="btn" type="submit">筛选套餐</button><span class="fine">倍率仅作统一情景计算，不表示每家都提供该倍率节点。</span></div></form><p id="filter-status" class="fine" role="status" aria-live="polite">默认按 50 GB 用量、50 元首付、1× 扣量比较。</p><div class="tablewrap" tabindex="0" role="region" aria-label="筛选结果"><table><thead><tr><th>服务</th><th>付款金额</th><th>标称额度</th><th>估算可传输</th><th>元／实际 GB</th><th>入口</th></tr></thead><tbody id="filtered-plans">{initrows}</tbody></table></div></div><noscript><p>你没有启用 JavaScript。上方仍展示默认条件下的参考结果；全部套餐和来源可在下方阅读。</p></noscript></section>
<section class="section"><div class="grid"><article class="card"><h3>每月只用 20／50／100 GB？</h3><p>比较满足用量的单个套餐首付，不把很大的流量包当成最低花费。</p><a href="/usage/">查看按用量比较 →</a></article><article class="card"><h3>预算是 10／20／50 元？</h3><p>普通月费、按量首付与年付折算价分开看，弄清当前需要付多少钱。</p><a href="/budget/">查看预算与付款周期 →</a></article><article class="card"><h3>数据从哪里来？</h3><p>提供固定版本来源、单位价格算法和原始数据下载，方便重新计算。</p><a href="/methodology/">查看来源与计算方法 →</a></article></div></section>
<section id="plans" class="section"><h2>8 家机场特点与完整套餐价格</h2><p class="section-intro">以下顺序不是质量排名。金额为人民币，单价保留 4 位小数；月度额度与全年合计明确区分。</p><div class="links">'''
body+=''.join(f'<a class="chip" href="#{s["id"]}">{e(s["name"])}</a>' for s in data['services'])+'</div>'
for s in data['services']:
 body+=f'<article id="{s["id"]}" class="service"><div class="service-head"><h3>{e(s["name"])}</h3>{link(s)}</div>'
 if not s['pricing']:body+='<p class="fine">尚未取得可靠套餐信息，不根据品牌名称推断价格。入口已保留，资料待补。</p>'
 else:
  body+='<ul>'+''.join('<li>'+e(f)+'</li>' for f in s['features'])+'</ul>'
  rows=[]
  for p in s['pricing']:
   note=p['notes'] or '—'
   if p.get('selected_node_multiplier'):note+=f"；3× 节点约 {p['selected_node_cny_per_actual_gb']} 元／实际 GB"
   rows.append([e(p['billing']),e(p['price_cny']),e(p['quota_display']),e(p['nominal_cny_per_gb']),e(note)])
  body+=table(['计费方式','金额（元）','标称额度','元／GB','说明'],rows)
 body+='</article>'
body+='</section><section class="section faq"><h2>选购常见问题</h2>'
faqs=[('机场与 VPN 是一回事吗？','机场是代理节点订阅服务的俗称，VPN 是虚拟专用网络技术。具体产品的协议、客户端和流量路由可能不同，不能仅凭名称判断速度或隐私。'),('注册账号后，客户端和订阅还需要分别准备吗？','先核对服务商说明。账号用于管理套餐；订阅提供节点或配置；客户端负责读取兼容配置。三者可能由同一产品提供，也可能需要分别准备。'),('按量流量包每 GB 很便宜，就应该买最大包吗？','先看自己实际需要的用量及一次付款金额。没有用完或提前失效的流量会提高实际成本；最低标称单价不能直接代表低总支出。'),('3 倍率代表速度快 3 倍吗？','不代表。3× 通常指实际传输 1 GB 扣除 3 GB 标称额度。24 元／100 GB 的包，按 3× 使用时约能传输 33.33 GB，每实际 GB 约 0.72 元。'),('年付 24.9 元，可以按每月约 2.075 元付款吗？','年费除以 12 是折算值。该例首次仍需支付全年 24.9 元；每月额度和退款规则也要另行确认。'),('这些服务都支持 ChatGPT 或流媒体吗？','本项目没有独立验证应用可用性。节点连通、账号条件、支持地区和服务条款需要分别检查。'),('这里的价格是今天的官网现价吗？','不是。报价来自明确标注的第三方固定版本，整理与重新计算不等于当前官网核验；最终以服务商当时页面为准。')]
body+=''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q,a in faqs)+'</section>'
# No executable inline JavaScript: the data block is non-executable JSON.
body+='<script id="service-data" type="application/json">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script>'
dataset={'@context':'https://schema.org','@type':'Dataset','name':'8家机场参考套餐与每GB单价','description':'7家共53档第三方参考套餐；一元机场价格未知。保留计费周期、标称流量、来源与单价计算口径。','url':ORIGIN+'/methodology/','citation':source,'creator':{'@type':'Person','name':'Tiancheng-Xu','url':'https://github.com/Tiancheng-Xu'},'distribution':[{'@type':'DataDownload','encodingFormat':'text/csv','contentUrl':ORIGIN+'/data/plans.csv'},{'@type':'DataDownload','encodingFormat':'application/json','contentUrl':ORIGIN+'/data/services.json'}]}
extra='<script type="application/ld+json">'+json.dumps(dataset,ensure_ascii=False)+'</script><script type="module" src="/app.mjs"></script>'
(OUT/'index.html').write_text(shell('/','机场套餐价格对比与计算器｜按量付费、月付、每GB单价','按预算、流量和扣量倍率筛选8家机场参考套餐，比较53档按量、月付、年付报价及每GB单价，附来源、CSV数据、10/20/50元预算计算和机场与VPN新手指南。',body,extra))
method=f'''<section class="section text"><div class="eyebrow">来源公开 · 计算可复核</div><h1>报价来源与每 GB 单价计算方法</h1><p>维护者：<a href="https://github.com/Tiancheng-Xu">Tiancheng-Xu</a>。本项目提供费用资料和计算工具，没有独立测速，也不是服务商官网。</p><h2>资料范围</h2><p>2026-10-28 从<a href="{source}">参考仓库的固定版本</a>整理7家53档套餐，一元机场报价未知。资料源提交日期为2026-10-26。没有把整理日当作官网现价核验日。</p><h2>每 GB 单价的公式</h2><ul><li>按量：套餐总价 ÷ 标称GB。</li><li>月付：月费 ÷ 每月标称GB。</li><li>年付且每月重置：年费 ÷（每月标称GB × 12）。</li><li>节点实际单价：标称单价 × 扣量倍率。</li></ul><p>金额按人民币计算，单价保留4位小数、四舍五入。TB暂按1,000 GB换算，若后台采用1,024口径应重算。年付合计额度不代表可一次用完。</p><h2>筛选器的适用边界</h2><p>筛选器比较单个按量包或一个普通月付套餐。以首付预算过滤，以标称额度除以所选倍率覆盖目标用量，按付款总额排序。它不组合购买多个包、不套用未核验优惠，不把年付或日享混进普通月付结果。选择0.1×或3×是统一情景假设，不代表所有服务都有这种节点。</p><h2>下载与复算</h2><p><a href="/data/plans.csv">53档报价 CSV</a> · <a href="/data/services.json">原始结构化数据 JSON</a> · <a href="{REPO}/tree/main/tests">计算规则验证</a></p><p>页面默认结果、完整表格和可下载数据使用同一个来源文件生成。公开数据不包含个人账号记录、邮箱、验证码或订阅密钥。</p><h2>更正信息</h2><p>发现价格变更时，可在<a href="{REPO}/issues">GitHub 提交公开来源与观察日期</a>。请勿上传账号密码或个人交易明细。</p></section>'''
method=method.replace('</section>','<p>刚开始选购？先阅读<a href="/guide/">机场、VPN、订阅与客户端入门指南</a>，再查看<a href="/budget/">付款预算对比</a>。</p></section>')
(OUT/'methodology').mkdir(exist_ok=True);(OUT/'methodology/index.html').write_text(shell('/methodology/','机场每GB单价怎么算｜来源、倍率、年付与数据下载','说明53档参考套餐的来源、GB与TB换算、扣量倍率、按量月付年付单价公式，并提供CSV和JSON下载。',method))
budgetbody='<section class="section"><div class="eyebrow">预算不是折算月价</div><h1>10／20／50 元预算：按量、月付与付款分界</h1><p class="section-intro">基于相同第三方参考报价计算。每个预算包含边界值，每家选预算内标称流量最多的一个套餐。未组合购买，未叠加优惠。</p>'
budgetbody+='<p>不清楚订阅和软件的关系？先看<a href="/guide/">新手指南</a>。本页计算口径见<a href="/methodology/">来源与方法</a>。</p>'
byid={s['id']:s for s in data['services']}
for kind in ['月付','按量']:
 rows=[]
 for r in comparisons['budget_comparisons']:
  if r['billing']!=kind:continue
  vals=[]
  for x in r['budget_selections']:
   p=x['selected'];vals.append(e(f"{p['price_cny']} 元／{p['quota_gb_for_unit_price']:,} GB") if p else '无已收录档位')
  rows.append([e(byid[r['service_id']]['name']),*vals])
 budgetbody+=f'<h2>{"普通月付" if kind=="月付" else "单个按量包首付"}预算</h2>'+table(['服务','≤10 元','≤20 元','≤50 元'],rows)
budgetbody+='<p class="notice">按量表中的1 GB小额／体验包并不代表常规月付价。家宽3×时实际流量会减少；月付表不含日享和年付折算。</p><h2>同一家按量和月付的分界用量</h2><p>假设1×扣量、流量不提前失效且无额外费用。公式：月费 × 按量包GB ÷ 按量包总价。分界点描述按量流量的平均消耗价值，并非按量包每月分期收款。</p>'
rows=[]
for t in comparisons['payg_monthly_break_even']:
 rows.append([e(byid[t['service_id']]['name']),e(f"{t['payg_price_cny']} 元／{t['payg_gb']} GB"),e(f"{t['monthly_price_cny']} 元／{t['monthly_gb']} GB"),e(t['break_even_usage_gb'])+' GB／月'])
budgetbody+=table(['服务','按量包','月付档','分界用量'],rows)
budgetbody+=f'<p>例如FlyBit的36元／128 GB按量包与15元／128 GB月付，分界约53.33 GB／月。用量低于此值时，前者平均消耗价值较低，但首次仍需付款36元。完整假设见<a href="{REPO}/blob/main/docs/budget-comparison.md">预算与年付付款比较</a>。</p><p><a href="/usage/">按每月 20／50／100 GB 比较首付</a> · <a href="/#calculator">返回计算器自行筛选 →</a></p></section>'
(OUT/'budget').mkdir(exist_ok=True);(OUT/'budget/index.html').write_text(shell('/budget/','10元20元50元机场预算对比｜按量、月付与费用分界','比较10/20/50元预算内的按量包与普通月付，计算5家按量和月付的分界用量，区分首付金额、平均成本与年付折算价。',budgetbody))
(OUT/'data').mkdir(exist_ok=True);shutil.copy2(ROOT/'data/services.json',OUT/'data/services.json')
buf=io.StringIO();w=csv.writer(buf);w.writerow(['service','billing','price_cny','quota_display','quota_gb_for_unit_price','nominal_cny_per_gb','notes','source_url','price_verified'])
for s,p in allplans:w.writerow([s['name'],p['billing'],p['price_cny'],p['quota_display'],p['quota_gb_for_unit_price'],p['nominal_cny_per_gb'],p['notes'],source,'false'])
(OUT/'data/plans.csv').write_text(buf.getvalue())
(OUT/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#182a39"/><circle cx="32" cy="32" r="22" fill="#f1c75b"/><text x="17" y="43" font-family="sans-serif" font-size="32" font-weight="bold" fill="#182a39">G</text></svg>')
(OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
guide=(ROOT/'web/beginner-guide.html').read_text()
(OUT/'guide').mkdir(exist_ok=True);(OUT/'guide/index.html').write_text(shell('/guide/','机场与VPN有什么区别｜订阅、客户端和套餐选购指南','解释机场VPN的常见叫法、代理订阅与客户端关系、设备兼容检查，以及按量月付年付、流量倍率和付款前的选购方法。',guide))
usagebody='<section class="section"><div class="eyebrow">按自己的用量比较 · 不以大包单价代替首付</div><h1>每月 20／50／100 GB：机场按量与月付费用对比</h1><p class="section-intro">为了覆盖一个月的目标用量，单个已收录套餐至少需要支付多少钱？以下按相同参考数据计算，不是全网最低价或质量排名。</p><p class="notice">报价沿用 2026-10-26 的第三方固定版本，未完成当前官网核验。默认 1× 扣量、不叠加优惠、不组合购买；年付和日享不混入普通月付。</p>'
for billing in ['按量','月付']:
 rows=[]
 for service in data['services']:
  for multiplier in ([1,3] if service['id']=='wangji' and billing=='按量' else [1]):
   cells=[]
   for usage in [20,50,100]:
    candidates=[p for p in service['pricing'] or [] if p['billing']==billing and p['quota_gb_for_unit_price']>=usage*multiplier]
    chosen=min(candidates,key=lambda p:(Decimal(p['price_cny']),-p['quota_gb_for_unit_price'])) if candidates else None
    cells.append(e(f"{chosen['price_cny']} 元（{chosen['quota_gb_for_unit_price']:,} GB）") if chosen else '无已收录档位')
   rows.append([e(service['name'])+('／家宽 3×' if multiplier==3 else '／1×'),*cells])
 usagebody+=f'<h2>{"单个按量包的最低首付" if billing=="按量" else "普通月付的最低月费"}</h2>'+table(['服务／扣量口径','使用 20 GB','使用 50 GB','使用 100 GB'],rows)
usagebody+='<h2>怎么读这两张表？</h2><ul><li>括号中的 GB 是整包标称额度，不是一定会用掉的流量。按量余量是否保留，应核对有效期。</li><li>3× 时实际使用 50 GB，需要至少 150 GB 标称额度；当前单包选择为网际快车 44 元／200 GB。</li><li>年费折算月价不等于月付金额。例如 24.9 元年付首次需全额支付，不能按约 2.075 元购买一个月。</li><li>无已收录档位可能是缺少资料或本页不包含该计费类型，不能据此认定服务商一定没有这个套餐。</li></ul><h2>进一步比较</h2><p>用量变化或节点倍率不同，可到<a href="/#calculator">套餐计算器</a>自行筛选；限制首次付款时看<a href="/budget/">10／20／50 元预算</a>。先读<a href="/guide/">新手指南</a>，或检查<a href="/methodology/">来源与计算公式</a>。</p></section>'
(OUT/'usage').mkdir(exist_ok=True);(OUT/'usage/index.html').write_text(shell('/usage/','每月20GB50GB100GB机场费用对比｜按量首付与普通月付','计算覆盖每月20、50、100GB用量的单个机场参考套餐最低付款额，区分按量包、普通月付、家宽3倍率和年付折算。',usagebody))
urls=['/','/budget/','/methodology/','/guide/','/usage/'];(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{ORIGIN}{p}</loc></url>' for p in urls)+'</urlset>')
(OUT/'404.html').write_text(shell('/404.html','页面未找到｜机场选购指南','此页面不存在，请返回套餐计算器或完整套餐表。','<section class="section"><h1>这个页面不存在</h1><p><a href="/">返回套餐计算器</a></p></section>').replace('index,follow,max-snippet:-1,max-image-preview:large','noindex,follow'))
(OUT/'_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n")
print(json.dumps({'files':len([p for p in OUT.rglob('*') if p.is_file()]),'total_bytes':sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()),'plans':len(allplans),'canonical_origin':ORIGIN},ensure_ascii=False))
