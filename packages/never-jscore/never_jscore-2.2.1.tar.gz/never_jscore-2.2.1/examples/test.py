import never_jscore
import execjs

js = """
    function aaa(){
    try {
        var bin = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 6, 1, 96, 1, 127, 1, 127, 3, 2, 1, 0, 5, 3, 1, 0, 1, 7, 8, 1, 4, 116, 101, 115, 116, 0, 0, 10, 16, 1, 14, 0, 32, 0, 65, 1, 54, 2, 0, 32, 0, 40, 2, 0, 11]);
        var mod = new WebAssembly.Module(bin);
        var inst = new WebAssembly.Instance(mod, {});

        return (inst.exports.test(4) !== 0);
    } catch (e) {
        return false;
    }
    
    }
"""
ctx2 = execjs.compile(js)
print(ctx2.call("aaa"))
ctx = never_jscore.Context(enable_extensions=True)

ctx.compile(js)
print(ctx.call("aaa",[]))