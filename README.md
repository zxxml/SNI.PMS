# 期刊管理系统（后端实现）

## 功能概览

1. 用户相关
2. 期刊征订
3. 期刊登记
4. 文章登记
5. 期刊搜索
6. 文章搜索
7. 借阅管理

## 调用方法

仅支持`JSON-RPC`接口。`datetime`对象序列化为时间戳。

## 运行环境

在`Ubuntu 18.04`，`Python 3.6.8`下测试通过。依赖库见`requirements.txt`，可通过pip安装。

```bash
sudo apt-get update && sudo apt-get install python3-dev python3-pip libev-dev
git clone https://github.com/zxxml/SNI.PMS.git && cd SNI.PMS
pip3 install -U -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
cp example.ini settings.ini && cd sni && python3 app.py
```

## 命名规则

- `add`前缀：添加
- `get`前缀：查询
- `set`前缀：修改
- `del`前缀：删除
- `full`后缀：**嵌套查询**
- `advanced`后缀：**模糊查询**
- `reverse`后缀：反向查询
