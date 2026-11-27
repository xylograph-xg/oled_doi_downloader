# OLED DOI 文献获取器（最小版）

## 用途
输入 DOI 后：

1. 使用 OpenAlex 查询论文元数据。
2. 如果 OpenAlex 提供合法开放获取（Open Access, OA）PDF 地址，则自动下载到相对目录 `papers/`。
3. 如果没有可自动获取的 OA PDF，则把论文写入 `data/institution_queue.jsonl`。
4. 不绕过 CARSI、CAPTCHA、出版社访问控制或反爬机制。

## 目录

```text
oled_doi_downloader/
├── download_by_doi.py
├── 一键运行.cmd              # Windows 一键运行
├── macOS一键运行.command      # macOS 一键运行
├── requirements.txt
├── papers/                   # PDF 下载到这里
├── data/
│   └── institution_queue.jsonl  # 首次需要时自动生成
└── README.md
```

所有运行路径都是相对本项目目录的，不依赖你的用户名或固定磁盘路径。

## Windows
双击：

`一键运行.cmd`

首次运行会自动：
- 创建 `.venv`
- 安装 `requests`

然后输入 DOI。

## macOS
双击：

`macOS一键运行.command`

若 macOS 阻止首次打开，可右键文件 → 打开。

也可以在终端执行：

```bash
cd oled_doi_downloader
./macOS一键运行.command
```

## 直接命令行

```bash
python download_by_doi.py 10.1038/s41586-020-2649-2
```

## 输出
成功下载：

```text
papers/2020 - Array programming with NumPy.pdf
```

如果没有可直接下载的 OA 全文：

```text
data/institution_queue.jsonl
```

其中会记录 DOI、标题、年份和 DOI 页面，供后续集中通过学校机构权限处理。

## 下一步可扩展
这个版本先验证 DOI → 元数据 → OA PDF → 队列 的入口是否稳定。后续可以继续加入：
- 批量 DOI
- OpenAlex 检索
- 自动去重
- PDF 元数据校验
- 下载目录监控
- CARSI/学校权限的集中人工队列
- OLED 文献解析与知识图谱摄取
