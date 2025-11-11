# finosdk

一个用于获取金融数据的 Python SDK。

## 安装

通过 pip 安装 `finosdk`：

```bash
pip install finosdk
```

### 初始化

在使用 `finosdk` 之前，需要进行初始化，设置你的 API 密钥（如果需要）：

```python
import finosdk as fino

fino.init(api_key=""http://127.0.0.1:8003/data_api")
# 或者
fino.init(username='username', password='password')
```

### 示例代码

以下是一个完整的示例代码：

```python
# 获取可用产品
products = fino.get_avaliable_products(date_time="2024-01-01")
print("Available products:", products)

# 其他的接口获取特定产品的数据
product_data = fino.get_product_data(product_id="product123", date_time="2024-01-01")
print("Product data:", product_data)
```

## 支持的功能

- 获取特定产品的详细数据

## 依赖

- `requests`：用于发送 HTTP 请求
- `pandas`：用于数据处理和分析

## 许可证

`finosdk` 使用 MIT 许可证。详情请查看 [LICENSE](LICENSE) 文件。
