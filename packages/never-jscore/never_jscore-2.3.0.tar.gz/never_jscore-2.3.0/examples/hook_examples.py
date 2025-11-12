"""
Hook 拦截示例
演示如何使用 __neverjscore_return__() 进行函数拦截并提前返回

使用场景：
- Hook XMLHttpRequest.send 获取加密后的请求数据
- Hook 加密函数获取中间结果
- 在不需要执行后续代码时提前终止
"""

import never_jscore

def example_1_xmlhttprequest_hook():
    """示例1: Hook XMLHttpRequest.send 拦截请求数据"""
    print("\n=== 示例1: Hook XMLHttpRequest.send ===")

    ctx = never_jscore.Context()

    # 模拟真实场景：加密数据后发送请求
    result = ctx.evaluate("""
        (async () => {
            // 定义加密函数
            function encrypt(data) {
                return btoa(JSON.stringify(data));  // Base64编码模拟加密
            }

            // Hook XMLHttpRequest.send
            const originalSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.send = function(data) {
                // 拦截到加密后的数据，立即返回
                __neverjscore_return__({
                    intercepted: true,
                    method: 'POST',
                    data: data,
                    url: this._url
                });

                // 下面的代码不会执行
                console.log('This will not be printed');
                originalSend.call(this, data);
            };

            // 执行加密和发送流程
            const sensitiveData = {
                username: 'test@example.com',
                password: 'secret123',
                timestamp: Date.now()
            };

            const encrypted = encrypt(sensitiveData);

            const xhr = new XMLHttpRequest();
            xhr.open('POST', 'https://api.example.com/login');
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(encrypted);  // 在这里被拦截并提前返回

            // 下面的代码不会执行
            console.log('Request sent');
            return { status: 'completed' };
        })()
    """)

    print(f"拦截结果: {result}")
    print(f"拦截到的加密数据: {result['data']}")


def example_2_encryption_hook():
    """示例2: Hook 加密函数获取中间结果"""
    print("\n=== 示例2: Hook 加密函数 ===")

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            // 复杂的多层加密流程
            function layer1Encrypt(data) {
                return btoa(data);
            }

            function layer2Encrypt(data) {
                const encrypted = md5(data);
                // Hook: 获取第二层加密结果后立即返回
                $return({
                    layer: 2,
                    algorithm: 'md5',
                    result: encrypted,
                    input: data
                });

                // 后续加密不会执行
                return sha256(encrypted);
            }

            function layer3Encrypt(data) {
                return sha256(data);
            }

            // 执行多层加密
            const original = 'sensitive_data_12345';
            const step1 = layer1Encrypt(original);
            const step2 = layer2Encrypt(step1);  // 在这里被拦截
            const step3 = layer3Encrypt(step2);  // 不会执行

            return step3;
        })()
    """)

    print(f"拦截到第2层加密结果: {result}")


def example_3_conditional_hook():
    """示例3: 条件拦截 - 只在满足条件时提前返回"""
    print("\n=== 示例3: 条件拦截 ===")

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            function processData(data) {
                // 只有当数据包含特定标记时才拦截
                if (data.includes('TARGET')) {
                    $exit({
                        found: true,
                        position: data.indexOf('TARGET'),
                        data: data
                    });
                }

                return data.toUpperCase();
            }

            // 测试多次调用
            processData('normal data');
            processData('another normal');
            processData('this contains TARGET marker');  // 在这里拦截
            processData('will not reach here');

            return { status: 'all processed' };
        })()
    """)

    print(f"条件拦截结果: {result}")


def example_4_crypto_signature_hook():
    """示例4: 真实场景 - Hook 签名生成函数"""
    print("\n=== 示例4: Hook 签名生成 (模拟Akamai) ===")

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            // 模拟Akamai风格的签名生成
            function generateSensor(userAgent, timestamp, path) {
                const data = {
                    userAgent: userAgent,
                    timestamp: timestamp,
                    path: path,
                    random: Math.floor(Math.random() * 1000000)
                };

                // 第一步：组合数据
                const combined = JSON.stringify(data);

                // 第二步：多次哈希
                const hash1 = md5(combined);
                const hash2 = sha256(hash1 + timestamp);

                // 第三步：生成最终签名
                const signature = hmacSha256('secret_key', hash2);

                // Hook: 拦截签名和中间值
                __neverjscore_return__({
                    sensor_data: signature,
                    intermediate: {
                        hash1: hash1,
                        hash2: hash2,
                        timestamp: timestamp,
                        combined: combined
                    },
                    original_data: data
                });

                // 后续的网络请求不会执行
                fetch('https://example.com/verify', {
                    method: 'POST',
                    body: JSON.stringify({ signature: signature })
                });

                return { status: 'sent' };
            }

            // 执行签名生成
            const sensor = generateSensor(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                Date.now(),
                '/api/check'
            );

            return sensor;
        })()
    """)

    print(f"拦截到的签名数据:")
    print(f"  - 最终签名: {result['sensor_data']}")
    print(f"  - MD5中间值: {result['intermediate']['hash1']}")
    print(f"  - SHA256中间值: {result['intermediate']['hash2']}")


def example_5_error_without_early_return():
    """示例5: 对比 - 不使用提前返回的情况"""
    print("\n=== 示例5: 不使用提前返回 (会执行完整流程) ===")

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            let logs = [];

            function encrypt(data) {
                logs.push('Encrypting...');
                const encrypted = btoa(data);
                logs.push('Encrypted: ' + encrypted);
                return encrypted;
            }

            function sendRequest(data) {
                logs.push('Preparing request...');
                logs.push('Sending to server...');
                logs.push('Request completed');
                return { status: 'sent' };
            }

            // 完整执行流程
            const encrypted = encrypt('sensitive_data');
            const response = sendRequest(encrypted);

            return {
                result: response,
                logs: logs
            };
        })()
    """)

    print(f"完整执行日志: {result['logs']}")
    print(f"最终结果: {result['result']}")


if __name__ == '__main__':
    print("=" * 60)
    print("Never-JSCore Hook 拦截示例")
    print("=" * 60)

    # 运行所有示例
    example_1_xmlhttprequest_hook()
    example_2_encryption_hook()
    example_3_conditional_hook()
    example_4_crypto_signature_hook()
    example_5_error_without_early_return()

    print("\n" + "=" * 60)
    print("所有示例执行完成！")
    print("=" * 60)

    print("\n使用方法:")
    print("1. 使用 __neverjscore_return__(value) - 完整函数名")
    print("2. 使用 $return(value) - 简短别名")
    print("3. 使用 $exit(value) - 替代别名")
    print("\n这些函数会立即终止JavaScript执行并返回指定的值到Python")
