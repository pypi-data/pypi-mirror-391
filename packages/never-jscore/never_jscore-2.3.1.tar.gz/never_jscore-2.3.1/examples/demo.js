function C(A) {
    let W = 435879
    let F = 64870
    function T() {
        return W = (((1664525 * W) + A) % F), W / F;
    }

    return T
}
function Q(A) {
    let z = [];
    var rand_value = Math['random']();
    // console.log(rand_value)
    for (let Y = Math['floor']((1 + (10 * rand_value))), T = Math['ceil']((A['length'] / Y)), F = 0; F < T; ++F)
        for (let b = 0; b < Y; ++b)
            (void (0) !== A[((b * T))]) && z['push'](A[((b * T))]);
    return z;
}

Array.prototype.fill = function (U, E, V) {
    let J = this, D = Q(J);
    J["splice"](0, J.length)
    for (let y1 = 0; y1 < D.length; y1++)
        J['push'](D[y1]);

    Math.random = C(2333963845)
    return J
}
const j = function(A) {
    var T = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    for (let q = (T["length"] - 1);(0 < q); q--) {
        var z = Math["floor"]((Math["random"]() * (q + 1)))
            , F = T[q];
        T[q] = T[z],
            T[z] = F;
    }
    for (var b = [], P = 0;(P < A["length"]); ++P)
        b["push"](T[parseInt(A[P], 16)]);
    return b;
};
function get_token(arg1) {
    Math.random = C(495853790);
    var T = arg1.slice(0,40).split('')
    T = T.fill(40)
    var P = j(T).join('');
    var hj = [false, false, true, true, false]
    for (var q, G, L = 0; (L < hj['length']); ++L)
        P += (q = T[L],
            G = void (0),
            G = Math['floor']((128 * Math['random']())),
        (q && ((G% 2)!= 0) || !q && ((G % 2)!= 0)) && G++,
            q = (1 == (q = G['toString'](16))['length']) ? ('0'+ q) : q);
    P = P['toLowerCase']();
    // console.log(P)
    return P
}

async function process(n) {
    return n * n;
}

async function batch(numbers) {
    return await Promise.all(numbers.map(n => process(n)));
}

function arraytest(){
    return new Uint8Array(10)

}

function main(){
    setTimeout(async function () {
        return get_token('5fffa6895ac0748d8c76e61c1f4066d73d6501cf63c3221234')
    },100)
}


