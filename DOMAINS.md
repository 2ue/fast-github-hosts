# GitHub 完整域名列表

> 基于 GitHub Meta API 分析和实际测试获取的完整域名清单
>
> 更新时间：2025-11-20
>
> 来源：https://api.github.com/meta

---

## 📊 域名统计

| 分类 | 域名数量 | 优先级 | 说明 |
|------|---------|-------|------|
| 核心服务 | 12 | P0 | GitHub主站和基础API |
| CDN静态资源 | 5 | P0 | 页面加载必需 |
| UserContent | 18 | P0 | 图片、文件访问 |
| 包管理器 | 5 | P0 | npm/docker/maven等 |
| AWS S3存储 | 5 | P1 | Release和大文件 |
| Copilot | 2 | P1 | AI编程助手 |
| Actions | 1 | P1 | CI/CD流水线 |
| 开发工具 | 1 | P2 | VS Code Web |
| **总计** | **49** | - | **精简版** |

---

## 🎯 精简版域名列表（49个）

### 一、核心服务（12个）- P0必须

```
github.com                      # 主站
api.github.com                  # REST API
gist.github.com                 # Gist服务
codeload.github.com             # 代码下载
github.blog                     # 官方博客
github.community                # 社区论坛
github.dev                      # 在线IDE
alive.github.com                # 存活检测
live.github.com                 # 实时服务
education.github.com            # 教育版
collector.github.com            # 数据收集
central.github.com              # 中心服务
```

### 二、CDN与静态资源（5个）- P0必须

```
github.githubassets.com         # CDN资源
github.io                       # Pages托管
github.map.fastly.net           # Fastly CDN映射
github.global.ssl.fastly.net    # Fastly SSL CDN
githubstatus.com                # 状态页面
```

### 三、UserContent系列（18个）- P0必须

```
raw.githubusercontent.com       # 原始文件
raw.github.com                  # 原始文件（legacy）
objects.githubusercontent.com   # Git对象存储
avatars.githubusercontent.com   # 用户头像
avatars0.githubusercontent.com  # 头像CDN 0
avatars1.githubusercontent.com  # 头像CDN 1
avatars2.githubusercontent.com  # 头像CDN 2
avatars3.githubusercontent.com  # 头像CDN 3
avatars4.githubusercontent.com  # 头像CDN 4
avatars5.githubusercontent.com  # 头像CDN 5
camo.githubusercontent.com      # Badge代理
user-images.githubusercontent.com       # 用户图片
private-user-images.githubusercontent.com  # 私有图片
cloud.githubusercontent.com     # 云端资源
desktop.githubusercontent.com   # 桌面客户端
favicons.githubusercontent.com  # 网站图标
media.githubusercontent.com     # 媒体文件
pkg-containers.githubusercontent.com    # 容器包
```

### 四、包管理器（5个）- P0必须

```
ghcr.io                         # GitHub Container Registry
maven.pkg.github.com            # Maven包
npm.pkg.github.com              # NPM包
nuget.pkg.github.com            # NuGet包
rubygems.pkg.github.com         # RubyGems包
```

### 五、AWS S3存储（5个）- P1重要

```
github-cloud.s3.amazonaws.com                               # 云存储
github-com.s3.amazonaws.com                                 # 仓库存储
github-production-release-asset-2e65be.s3.amazonaws.com     # Release资源
github-production-user-asset-6210df.s3.amazonaws.com        # 用户资源
github-production-repository-file-5c1aeb.s3.amazonaws.com   # 仓库文件
```

### 六、GitHub Copilot（2个）- P1重要

```
api.individual.githubcopilot.com    # Copilot个人API
copilot-proxy.githubusercontent.com # Copilot代理
```

### 七、GitHub Actions（1个）- P1重要

```
pipelines.actions.githubusercontent.com     # Actions流水线
```

### 八、开发工具（1个）- P2可选

```
vscode.dev                      # VS Code Web版
```

---

## 🚀 扩展版域名列表（120+个）

### 额外的Actions域名（50+个）

如果你使用GitHub Actions，需要额外添加以下域名：

#### Actions认证与核心
```
vstoken.actions.githubusercontent.com
broker.actions.githubusercontent.com
launch.actions.githubusercontent.com
runner-auth.actions.githubusercontent.com
tokenghub.actions.githubusercontent.com
setup-tools.actions.githubusercontent.com
pkg.actions.githubusercontent.com
results-receiver.actions.githubusercontent.com
mpsghub.actions.githubusercontent.com
```

#### Pipelines系列（26个）
```
pipelinesghubeus1.actions.githubusercontent.com
pipelinesghubeus2.actions.githubusercontent.com
pipelinesghubeus3.actions.githubusercontent.com
pipelinesghubeus4.actions.githubusercontent.com
pipelinesghubeus5.actions.githubusercontent.com
pipelinesghubeus6.actions.githubusercontent.com
pipelinesghubeus7.actions.githubusercontent.com
pipelinesghubeus8.actions.githubusercontent.com
pipelinesghubeus9.actions.githubusercontent.com
pipelinesghubeus10.actions.githubusercontent.com
pipelinesghubeus11.actions.githubusercontent.com
pipelinesghubeus12.actions.githubusercontent.com
pipelinesghubeus13.actions.githubusercontent.com
pipelinesghubeus14.actions.githubusercontent.com
pipelinesghubeus15.actions.githubusercontent.com
pipelinesghubeus20.actions.githubusercontent.com
pipelinesghubeus21.actions.githubusercontent.com
pipelinesghubeus22.actions.githubusercontent.com
pipelinesghubeus23.actions.githubusercontent.com
pipelinesghubeus24.actions.githubusercontent.com
pipelinesghubeus25.actions.githubusercontent.com
pipelinesghubeus26.actions.githubusercontent.com
pipelinesproxcnc1.actions.githubusercontent.com
pipelinesproxcus1.actions.githubusercontent.com
pipelinesproxeau1.actions.githubusercontent.com
pipelinesproxsdc1.actions.githubusercontent.com
pipelinesproxweu1.actions.githubusercontent.com
pipelinesproxwus31.actions.githubusercontent.com
```

#### Runner系列（9个）
```
runnerghubeus1.actions.githubusercontent.com
runnerghubeus20.actions.githubusercontent.com
runnerghubeus21.actions.githubusercontent.com
runnerghubwus31.actions.githubusercontent.com
runnerproxcnc1.actions.githubusercontent.com
runnerproxcus1.actions.githubusercontent.com
runnerproxeau1.actions.githubusercontent.com
runnerproxsdc1.actions.githubusercontent.com
runnerproxweu1.actions.githubusercontent.com
run-actions-1-azure-eastus.actions.githubusercontent.com
run-actions-2-azure-eastus.actions.githubusercontent.com
run-actions-3-azure-eastus.actions.githubusercontent.com
```

#### Azure Blob存储（20个）
```
productionresultssa0.blob.core.windows.net
productionresultssa1.blob.core.windows.net
productionresultssa2.blob.core.windows.net
productionresultssa3.blob.core.windows.net
productionresultssa4.blob.core.windows.net
productionresultssa5.blob.core.windows.net
productionresultssa6.blob.core.windows.net
productionresultssa7.blob.core.windows.net
productionresultssa8.blob.core.windows.net
productionresultssa9.blob.core.windows.net
productionresultssa10.blob.core.windows.net
productionresultssa11.blob.core.windows.net
productionresultssa12.blob.core.windows.net
productionresultssa13.blob.core.windows.net
productionresultssa14.blob.core.windows.net
productionresultssa15.blob.core.windows.net
productionresultssa16.blob.core.windows.net
productionresultssa17.blob.core.windows.net
productionresultssa18.blob.core.windows.net
productionresultssa19.blob.core.windows.net
```

### 额外的包管理器域名

```
npm-proxy.pkg.github.com
npm-beta.pkg.github.com
npm-beta-proxy.pkg.github.com
pypi.pkg.github.com
swift.pkg.github.com
docker-proxy.pkg.github.com
containers.pkg.github.com
```

### Azure Blob包存储

```
mavenregistryv2prod.blob.core.windows.net
npmregistryv2prod.blob.core.windows.net
nugetregistryv2prod.blob.core.windows.net
rubygemsregistryv2prod.blob.core.windows.net
```

### 额外的Copilot域名

```
githubcopilot.com
api.githubcopilot.com
copilot-telemetry.githubusercontent.com
default.exp-tas.com
```

### 安全认证域名

```
tuf-repo.github.com
fulcio.githubapp.com
timestamp.githubapp.com
```

### 其他UserContent

```
objects-origin.githubusercontent.com
release-assets.githubusercontent.com
github-releases.githubusercontent.com
github-registry-files.githubusercontent.com
```

---

## 📝 使用建议

### 最小配置（30个域名）
适合只需要基本GitHub访问的用户：
- 核心服务（12个）
- CDN静态资源（5个）
- UserContent前10个
- 基础包管理（npm、ghcr.io、maven）

### 标准配置（49个域名）
适合大多数开发者：
- 使用本文档的"精简版域名列表"

### 完整配置（120+个域名）
适合重度使用GitHub Actions和企业用户：
- 使用本文档的"精简版 + 扩展版"

---

## 🔄 自动获取最新域名

使用GitHub Meta API获取官方域名列表：

```bash
# 获取所有域名分类
curl -s https://api.github.com/meta | jq '.domains'

# 获取Actions完整域名列表
curl -s https://api.github.com/meta | jq -r '.domains.actions_inbound.full_domains[]'

# 获取网站通配符域名
curl -s https://api.github.com/meta | jq -r '.domains.website[]'
```

---

## ⚠️ 注意事项

1. **通配符域名**：GitHub Meta API返回的部分域名使用通配符（如`*.github.com`），在hosts文件中无法直接使用，需要展开为具体子域名
2. **动态域名**：Actions和Codespaces的某些域名是动态生成的，可能无法完全覆盖
3. **更新频率**：建议每周检查一次GitHub Meta API，确保域名列表最新

---

## 📚 参考资料

- GitHub Meta API: https://api.github.com/meta
- GitHub官方文档: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-githubs-ip-addresses
- Copilot防火墙配置: https://docs.github.com/en/copilot/troubleshooting-github-copilot/troubleshooting-firewall-settings-for-github-copilot
