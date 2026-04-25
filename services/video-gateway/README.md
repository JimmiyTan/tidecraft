# Video Gateway 服务说明

## 输入

- 主题
- 脚本
- 导出目录

## 输出

- `exports/pending_review/` 下的 mock 导出结果文件

## 依赖

- Python 标准库

## 失败处理

- 导出失败时返回错误信息
- 第一阶段不调用真实视频生成接口
