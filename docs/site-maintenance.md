# 在线套餐筛选器的构建与维护

[返回选购指南](../README.md) · [打开在线页面](https://jichang-guide.271251549.workers.dev/)

在线页面把现有参考数据转换成静态 HTML，筛选在访问者的浏览器中运行。不开设账号，不接收订单，不配置点击统计。

## 数据与构建

- 主数据：[services.json](../data/services.json)，包含8家服务入口、53档参考报价及来源状态。
- 预算比较：[comparisons.json](../data/comparisons.json)，包含预算筛选结果与费用分界。
- 构建脚本：[build_site.py](../scripts/build_site.py)。
- 筛选逻辑：[plan-utils.mjs](../web/plan-utils.mjs)。

在仓库根目录运行，要求 Python 3.11+ 和 Node.js 22+，没有第三方构建依赖：

```sh
python3 scripts/build_site.py
node --test tests/plan-utils.test.mjs
python3 tests/check_site.py
```

输出目录为 `site/`，其中包含首页、预算页、来源说明、JSON、CSV、站点地图与 robots.txt。生成目录已忽略，不当作原始数据编辑。

## 筛选规则

筛选器只支持单个按量包或一个普通月付套餐。输入用量和首付预算，用标称流量除以所选倍率估算可传输额度，结果按实付金额排序。年付和日享仍保留在完整表格中，但不混入普通月付筛选。

单价采用整数分币及有理数运算，四舍五入到4位小数，避免 75.9／6000 在浮点计算中显示为0.0126的问题。月付、按量的付款周期和单价含义见[计算方法](buying-guide.md)。

## 托管目标

当前目标为 Cloudflare Worker `jichang-guide` 的纯静态资源托管，域名为 `jichang-guide.271251549.workers.dev`。没有 Worker 请求处理脚本、数据库或推理服务。

使用[官方静态资源上传流程](https://developers.cloudflare.com/workers/static-assets/direct-upload/)更新：生成文件清单，上传发生变化的资源，再将完成令牌关联到该 Worker。上传令牌仅在内存中使用，不写入源文件、日志或仓库。不覆盖其他 Worker，也不创建付费资源或修改现有域名。

如改变公开域名，需同时更新构建脚本中的 `ORIGIN`，重新生成 canonical、Open Graph URL、JSON-LD、robots.txt 和 sitemap.xml；核对所有内部链接与数据下载后再发布。

## 发布后的检查

检查首页、预算页、来源页、JSON、CSV、robots.txt、sitemap.xml 与 JavaScript 的状态码和内容类型；不存在的路径应返回404。确认8个服务入口仍与维护者提供的原链接一致。

页面可访问、静态检查通过或元数据齐全，都不等于已被搜索引擎收录，也不等于排名或 AI 引用已经提升。

Cloudflare 的 `workers.dev` 域名可能对默认 Python urllib 客户端返回1010。HTTP健康检查应使用明确的客户端标识，例如 `JichangGuideHealthcheck/1.0`，并结合响应正文判断原因，不能把单个客户端被拦当作所有访客不可访问。[Cloudflare 1010 说明](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1010/)。当前普通访问检查通过；搜索引擎实际抓取和浏览器视觉验收另行记录。
