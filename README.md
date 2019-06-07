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

## 错误状态

### 400：参数错误

- 类型错误：例如，传入整型的用户名
- 长度错误：传入超过函数所需个数的参数
- 格式错误：例如，传入的CN刊号不符合格式

### 401：会话错误

- 登入失败：用户名或密码错误
- Session错误：Session不存在或已过期

### 403：权限错误

- Session正确，但该用户无权限

### 409：请求冲突

- 破坏了完整性：例如，重复注册
- 破坏了一致性：例如，删除已有征订的期刊

### 412：缺乏前置条件

- 例如：添加征订时期刊不存在

### 500：服务器内部错误

- 其他所有（暂未发现的）错误