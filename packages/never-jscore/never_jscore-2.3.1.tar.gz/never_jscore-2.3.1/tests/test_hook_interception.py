"""
Hook拦截功能测试
测试 __neverjscore_return__() 提前返回机制
"""

import never_jscore
import time
import sys

# 修复Windows控制台的Unicode编码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def test_basic_early_return():
    """测试基本的提前返回功能"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            function testFunc() {
                __neverjscore_return__({ intercepted: true, value: 42 });
                // 下面的代码不会执行
                return { intercepted: false, value: 0 };
            }

            return testFunc();
        })()
    """)

    assert result['intercepted'] == True
    assert result['value'] == 42
    print("✓ 基本提前返回测试通过")


def test_early_return_alias_dollar_return():
    """测试 $return 别名"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            $return({ method: '$return', success: true });
            return { method: 'normal', success: false };
        })()
    """)

    assert result['method'] == '$return'
    assert result['success'] == True
    print("✓ $return 别名测试通过")


def test_early_return_alias_dollar_exit():
    """测试 $exit 别名"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            $exit({ method: '$exit', code: 0 });
            return { method: 'normal', code: -1 };
        })()
    """)

    assert result['method'] == '$exit'
    assert result['code'] == 0
    print("✓ $exit 别名测试通过")


def test_xmlhttprequest_send_hook():
    """测试XMLHttpRequest.send Hook拦截"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            // Hook XMLHttpRequest.send
            const originalSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.send = function(data) {
                __neverjscore_return__({
                    hook: 'XMLHttpRequest.send',
                    method: this._method,
                    url: this._url,
                    data: data
                });
            };

            // 创建并发送请求
            const xhr = new XMLHttpRequest();
            xhr.open('POST', 'https://api.example.com/data');
            xhr.send('encrypted_payload_12345');

            // 不会到达这里
            return { status: 'completed' };
        })()
    """)

    assert result['hook'] == 'XMLHttpRequest.send'
    assert result['method'] == 'POST'
    assert result['url'] == 'https://api.example.com/data'
    assert result['data'] == 'encrypted_payload_12345'
    print("✓ XMLHttpRequest.send Hook测试通过")


def test_encryption_function_hook():
    """测试加密函数Hook拦截"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            function multiLayerEncrypt(data) {
                const layer1 = btoa(data);
                const layer2 = md5(layer1);

                // 在第二层拦截
                $return({
                    layers: 2,
                    layer1_result: layer1,
                    layer2_result: layer2,
                    original: data
                });

                // 第三层不会执行
                const layer3 = sha256(layer2);
                return layer3;
            }

            return multiLayerEncrypt('sensitive_data');
        })()
    """)

    assert result['layers'] == 2
    assert 'layer1_result' in result
    assert 'layer2_result' in result
    assert result['original'] == 'sensitive_data'
    print("✓ 加密函数Hook测试通过")


def test_conditional_early_return():
    """测试条件提前返回"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            let callCount = 0;

            function processItem(item) {
                callCount++;

                if (item.includes('TARGET')) {
                    $exit({
                        found: true,
                        callCount: callCount,
                        item: item
                    });
                }

                return item.toUpperCase();
            }

            // 多次调用
            processItem('item1');
            processItem('item2');
            processItem('TARGET_item');  // 在这里拦截
            processItem('item4');  // 不会执行

            return { found: false, callCount: callCount };
        })()
    """)

    assert result['found'] == True
    assert result['callCount'] == 3  # 只执行了3次
    assert 'TARGET' in result['item']
    print("✓ 条件提前返回测试通过")


def test_early_return_with_complex_data():
    """测试返回复杂数据结构"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            const complexData = {
                user: {
                    id: 12345,
                    name: 'test_user',
                    roles: ['admin', 'user']
                },
                session: {
                    token: 'abc123xyz',
                    expires: Date.now() + 3600000
                },
                metadata: {
                    ip: '192.168.1.1',
                    userAgent: 'Mozilla/5.0'
                },
                encrypted: btoa('secret_data'),
                hash: md5('verification_string')
            };

            __neverjscore_return__(complexData);

            return { error: 'should not reach here' };
        })()
    """)

    assert result['user']['id'] == 12345
    assert result['user']['name'] == 'test_user'
    assert len(result['user']['roles']) == 2
    assert 'token' in result['session']
    assert 'encrypted' in result
    assert 'hash' in result
    print("✓ 复杂数据结构返回测试通过")


def test_early_return_skips_async_operations():
    """测试提前返回能跳过异步操作"""
    ctx = never_jscore.Context()

    start_time = time.time()

    result = ctx.evaluate("""
        (async () => {
            let executed = [];

            executed.push('step1');

            // 提前返回，后续的延迟操作不会执行
            $return({
                executed: executed,
                skipped_timer: true
            });

            // 下面的延迟操作不会执行
            await new Promise(resolve => setTimeout(() => {
                executed.push('step2_delayed');
                resolve();
            }, 1000));

            executed.push('step3');

            return { executed: executed, skipped_timer: false };
        })()
    """)

    elapsed = time.time() - start_time

    assert result['executed'] == ['step1']
    assert result['skipped_timer'] == True
    assert elapsed < 0.5  # 应该立即返回，不会等待1秒
    print("✓ 跳过异步操作测试通过")


def test_early_return_in_nested_functions():
    """测试嵌套函数中的提前返回"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            function level1() {
                return level2();
            }

            function level2() {
                return level3();
            }

            function level3() {
                $exit({ level: 3, nested: true });
                return { level: 0, nested: false };
            }

            level1();

            // 不会到达这里
            return { level: -1, nested: false };
        })()
    """)

    assert result['level'] == 3
    assert result['nested'] == True
    print("✓ 嵌套函数提前返回测试通过")


def test_early_return_with_non_serializable_fallback():
    """测试不可序列化对象的降级处理"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            // 创建循环引用（不可JSON序列化）
            const obj = { name: 'test' };
            obj.self = obj;

            try {
                __neverjscore_return__(obj);
            } catch (e) {
                // 应该降级为字符串
                return { fallback: true, error: e.message };
            }

            return { fallback: false };
        })()
    """)

    # 循环引用应该被转换为字符串 "[object Object]"
    assert isinstance(result, str) or result.get('fallback') == True
    print("✓ 不可序列化对象降级处理测试通过")


def test_multiple_contexts_early_return():
    """测试多个Context的提前返回（串行使用）"""
    # 注意：根据V8限制，不能同时使用多个Context
    # 必须先使用完第一个Context并删除后，才能使用第二个

    # 第一个Context
    ctx1 = never_jscore.Context()
    result1 = ctx1.evaluate("$return({ context: 1 }); { context: 0 }")
    assert result1['context'] == 1
    del ctx1  # 必须删除第一个Context

    # 第二个Context（独立使用）
    ctx2 = never_jscore.Context()
    result2 = ctx2.evaluate("$return({ context: 2 }); { context: 0 }")
    assert result2['context'] == 2
    del ctx2

    print("✓ 多Context提前返回串行测试通过（已修正为串行使用）")


def test_early_return_sync_mode():
    """测试同步模式下的提前返回"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        function syncTest() {
            $return({ mode: 'sync', value: 123 });
            return { mode: 'normal', value: 0 };
        }
        syncTest();
    """, auto_await=False)

    assert result['mode'] == 'sync'
    assert result['value'] == 123
    print("✓ 同步模式提前返回测试通过")


def test_real_world_akamai_style_hook():
    """测试真实场景：Akamai风格的传感器生成Hook"""
    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            // 模拟Akamai传感器生成
            function generateSensorData(config) {
                const timestamp = Date.now();
                const userAgent = navigator.userAgent;

                // 收集指纹
                const fingerprint = {
                    screen: { width: screen.width, height: screen.height },
                    navigator: {
                        platform: navigator.platform,
                        language: navigator.language
                    },
                    timestamp: timestamp
                };

                // 生成哈希
                const fp_str = JSON.stringify(fingerprint);
                const fp_hash = md5(fp_str);

                // 生成签名
                const signature_base = fp_hash + timestamp + config.apiKey;
                const signature = hmacSha256(config.secret, signature_base);

                // 组合最终的传感器数据
                const sensor = {
                    version: '1.0.0',
                    timestamp: timestamp,
                    fingerprint: fp_hash,
                    signature: signature,
                    data: btoa(JSON.stringify({
                        fp: fingerprint,
                        sig: signature
                    }))
                };

                // Hook: 拦截传感器数据
                __neverjscore_return__({
                    intercepted: 'sensor_data',
                    sensor: sensor,
                    raw_fingerprint: fingerprint,
                    debug: {
                        fp_str: fp_str,
                        fp_hash: fp_hash,
                        signature_base: signature_base
                    }
                });

                // 后续的网络请求不会执行
                fetch(config.endpoint, {
                    method: 'POST',
                    body: JSON.stringify(sensor)
                });

                return { status: 'sent' };
            }

            // 执行传感器生成
            return generateSensorData({
                apiKey: 'test_key_123',
                secret: 'test_secret_456',
                endpoint: 'https://akamai.example.com/sensor'
            });
        })()
    """)

    print(result)
    assert result['intercepted'] == 'sensor_data'
    assert 'sensor' in result
    assert 'version' in result['sensor']
    assert 'signature' in result['sensor']
    assert 'raw_fingerprint' in result
    assert 'debug' in result
    print("✓ Akamai风格Hook测试通过")


if __name__ == '__main__':
    print("=" * 70)
    print("Never-JSCore Hook拦截功能测试")
    print("=" * 70)

    # 运行所有测试
    tests = [
        ("基本提前返回", test_basic_early_return),
        ("$return别名", test_early_return_alias_dollar_return),
        ("$exit别名", test_early_return_alias_dollar_exit),
        ("XMLHttpRequest Hook", test_xmlhttprequest_send_hook),
        ("加密函数Hook", test_encryption_function_hook),
        ("条件提前返回", test_conditional_early_return),
        ("复杂数据返回", test_early_return_with_complex_data),
        ("跳过异步操作", test_early_return_skips_async_operations),
        ("嵌套函数返回", test_early_return_in_nested_functions),
        ("不可序列化降级", test_early_return_with_non_serializable_fallback),
        ("多Context串行", test_multiple_contexts_early_return),
        ("同步模式返回", test_early_return_sync_mode),
        ("Akamai风格Hook", test_real_world_akamai_style_hook),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {name} 测试失败: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 所有Hook拦截功能测试通过！")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查")
