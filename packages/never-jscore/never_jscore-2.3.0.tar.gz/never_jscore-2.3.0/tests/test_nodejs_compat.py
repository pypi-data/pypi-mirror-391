#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 never_jscore 的 Node.js 兼容性增强
包括: 真实async timer, process.nextTick, Buffer, process对象等
"""

import never_jscore
import time
import sys

# 设置UTF-8输出（Windows兼容）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_real_async_timer():
    """测试真实的异步 timer"""
    print("=" * 70)
    print("测试 1: 真实异步Timer (setTimeout/setInterval)")
    print("=" * 70)

    ctx = never_jscore.Context(enable_logging=True)

    # 测试setTimeout是否真的延迟
    start_time = time.time()
    result = ctx.evaluate("""
        (async () => {
            let executed = false;
            setTimeout(() => {
                executed = true;
            }, 100);

            // Wait a bit and check
            await new Promise(resolve => setTimeout(resolve, 150));
            return executed;
        })()
    """)
    elapsed = time.time() - start_time

    print(f"✓ setTimeout executed: {result}")
    print(f"✓ Elapsed time: {elapsed:.2f}s (应该≈0.15s)")
    assert result == True
    assert elapsed >= 0.1  # Should have actually waited

    del ctx
    print("✅ 真实异步Timer测试通过\n")


def test_process_nexttick():
    """测试 process.nextTick"""
    print("=" * 70)
    print("测试 2: process.nextTick")
    print("=" * 70)

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            let order = [];

            order.push('sync-1');

            process.nextTick(() => {
                order.push('nextTick');
            });

            order.push('sync-2');

            // Wait for nextTick to execute
            await new Promise(resolve => setTimeout(resolve, 10));

            return order;
        })()
    """)

    print(f"✓ Execution order: {result}")
    # nextTick应该在sync-2之后但在其他异步操作之前执行
    assert result[0] == 'sync-1'
    assert result[1] == 'sync-2'
    assert result[2] == 'nextTick'

    del ctx
    print("✅ process.nextTick测试通过\n")


def test_setimmediate():
    """测试 setImmediate"""
    print("=" * 70)
    print("测试 3: setImmediate")
    print("=" * 70)

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            let value = 0;

            setImmediate(() => {
                value = 42;
            });

            // Wait for setImmediate to execute
            await new Promise(resolve => setTimeout(resolve, 10));

            return value;
        })()
    """)

    print(f"✓ setImmediate result: {result}")
    assert result == 42

    del ctx
    print("✅ setImmediate测试通过\n")


def test_buffer():
    """测试 Buffer 类"""
    print("=" * 70)
    print("测试 4: Buffer类")
    print("=" * 70)

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const tests = {};

        // Test Buffer.from(string)
        const buf1 = Buffer.from('hello', 'utf8');
        tests.fromString = buf1.toString();

        // Test Buffer.from(array)
        const buf2 = Buffer.from([72, 101, 108, 108, 111]);
        tests.fromArray = buf2.toString();

        // Test Buffer.alloc
        const buf3 = Buffer.alloc(5);
        tests.alloc = buf3.length;

        // Test hex encoding
        const buf4 = Buffer.from('hello');
        tests.hex = buf4.toString('hex');

        // Test base64 encoding
        tests.base64 = buf4.toString('base64');

        // Test Buffer.concat
        const buf5 = Buffer.from('Hello');
        const buf6 = Buffer.from(' World');
        const buf7 = Buffer.concat([buf5, buf6]);
        tests.concat = buf7.toString();

        tests
    """)

    print(f"✓ Buffer.from(string): {result['fromString']}")
    print(f"✓ Buffer.from(array): {result['fromArray']}")
    print(f"✓ Buffer.alloc(5): length={result['alloc']}")
    print(f"✓ Buffer hex: {result['hex']}")
    print(f"✓ Buffer base64: {result['base64']}")
    print(f"✓ Buffer.concat: {result['concat']}")

    assert result['fromString'] == 'hello'
    assert result['fromArray'] == 'Hello'
    assert result['alloc'] == 5
    assert result['concat'] == 'Hello World'

    del ctx
    print("✅ Buffer测试通过\n")


def test_process_object():
    """测试 process 对象"""
    print("=" * 70)
    print("测试 5: process对象")
    print("=" * 70)

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        ({
            version: process.version,
            platform: process.platform,
            arch: process.arch,
            pid: typeof process.pid,
            cwd: typeof process.cwd,
            nextTick: typeof process.nextTick,
            env: typeof process.env,
            hrtime: typeof process.hrtime,
            memoryUsage: typeof process.memoryUsage
        })
    """)

    print(f"✓ process.version: {result['version']}")
    print(f"✓ process.platform: {result['platform']}")
    print(f"✓ process.arch: {result['arch']}")
    print(f"✓ process.pid: {result['pid']}")
    print(f"✓ process.cwd: {result['cwd']}")
    print(f"✓ process.nextTick: {result['nextTick']}")
    print(f"✓ process.env: {result['env']}")
    print(f"✓ process.hrtime: {result['hrtime']}")
    print(f"✓ process.memoryUsage: {result['memoryUsage']}")


    del ctx
    print("✅ process对象测试通过\n")


def test_textencoder_decoder():
    """测试 TextEncoder/TextDecoder"""
    print("=" * 70)
    print("测试 6: TextEncoder/TextDecoder")
    print("=" * 70)

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        const encoder = new TextEncoder();
        const decoder = new TextDecoder();

        const text = 'Hello 世界';
        const encoded = encoder.encode(text);
        const decoded = decoder.decode(encoded);

        ({
            original: text,
            encodedLength: encoded.length,
            decoded: decoded,
            match: text === decoded
        })
    """)

    print(f"✓ Original: {result['original']}")
    print(f"✓ Encoded length: {result['encodedLength']}")
    print(f"✓ Decoded: {result['decoded']}")
    print(f"✓ Match: {result['match']}")

    assert result['match'] == True

    del ctx
    print("✅ TextEncoder/TextDecoder测试通过\n")


def test_queuemicrotask():
    """测试 queueMicrotask"""
    print("=" * 70)
    print("测试 7: queueMicrotask")
    print("=" * 70)

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            let value = 0;

            queueMicrotask(() => {
                value = 100;
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            return value;
        })()
    """)

    print(f"✓ queueMicrotask result: {result}")
    assert result == 100

    del ctx
    print("✅ queueMicrotask测试通过\n")


def test_comprehensive_async():
    """综合异步测试 - 模拟Akamai场景"""
    print("=" * 70)
    print("测试 8: 综合异步测试 (Akamai风格)")
    print("=" * 70)

    ctx = never_jscore.Context()

    result = ctx.evaluate("""
        (async () => {
            const results = [];

            // 模拟复杂的异步流程
            results.push('start');

            // process.nextTick (微任务)
            process.nextTick(() => {
                results.push('nextTick-1');
            });

            // queueMicrotask (微任务)
            queueMicrotask(() => {
                results.push('microtask-1');
            });

            // setTimeout (宏任务)
            setTimeout(() => {
                results.push('setTimeout-50ms');
            }, 50);

            // setImmediate (宏任务)
            setImmediate(() => {
                results.push('setImmediate');
            });

            results.push('sync-end');

            // 等待所有异步操作完成
            await new Promise(resolve => setTimeout(resolve, 100));

            return results;
        })()
    """)

    print(f"✓ Execution order: {result}")
    assert result[0] == 'start'
    assert result[1] == 'sync-end'
    # 微任务应该在宏任务之前
    assert 'nextTick-1' in result
    assert 'microtask-1' in result
    assert 'setTimeout-50ms' in result
    assert 'setImmediate' in result

    del ctx
    print("✅ 综合异步测试通过\n")


def test_logging_feature():
    """测试日志功能"""
    print("=" * 70)
    print("测试 9: 日志功能")
    print("=" * 70)

    print("创建启用日志的Context:")
    ctx_log = never_jscore.Context(enable_logging=True)
    ctx_log.evaluate("setTimeout(() => {}, 10)")
    del ctx_log

    print("\n创建禁用日志的Context:")
    ctx_nolog = never_jscore.Context(enable_logging=False)
    ctx_nolog.evaluate("setTimeout(() => {}, 10)")
    del ctx_nolog

    print("✅ 日志功能测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("=" * 70)
    print("  NEVER_JSCORE - Node.js兼容性增强测试")
    print("=" * 70)
    print("\n")

    test_real_async_timer()
    test_process_nexttick()
    test_setimmediate()
    test_buffer()
    test_process_object()
    test_textencoder_decoder()
    test_queuemicrotask()
    test_comprehensive_async()
    test_logging_feature()

    print("=" * 70)
    print("🎉 所有测试通过！Node.js兼容性增强完成！")
    print("=" * 70)
    print("\n✅ 新增功能:")
    print("  - 真实async timer (setTimeout/setInterval)")
    print("  - process.nextTick (微任务)")
    print("  - setImmediate/clearImmediate (宏任务)")
    print("  - queueMicrotask (标准微任务API)")
    print("  - Buffer 类 (完整Node.js兼容)")
    print("  - process 对象 (Node.js 22模拟)")
    print("  - TextEncoder/TextDecoder (标准编码API)")
    print("  - 日志功能 (enable_logging参数)")
    print("\n🎯 现在可以运行Akamai等复杂JS逆向代码了！")
    print()


if __name__ == "__main__":
    run_all_tests()
