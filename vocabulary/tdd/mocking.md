# 何时 Mock

只在**系统边界** mock：

- 外部 API（支付、邮件等）
- 数据库（有时——优先测试库）
- 时间/随机性
- 文件系统（有时）

不要 mock：

- 你自己的类/模块
- 内部协作者
- 任何你控制的东西

## 为可 mock 而设计

在系统边界，设计容易 mock 的接口：

**1. 用依赖注入**

从外部传入依赖，而非在内部创建它们：

```typescript
// 容易 mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// 难 mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. 优先 SDK 风格接口，而非通用 fetcher**

为每个外部操作写具体函数，而非一个带条件逻辑的通用函数：

```typescript
// GOOD: 每个函数独立可 mock
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: mock 里要塞条件逻辑
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

SDK 方式意味着：

- 每个 mock 返回一个具体形状
- 测试 setup 里无条件逻辑
- 更容易看出测试命中哪些端点
- 每个端点有类型安全
