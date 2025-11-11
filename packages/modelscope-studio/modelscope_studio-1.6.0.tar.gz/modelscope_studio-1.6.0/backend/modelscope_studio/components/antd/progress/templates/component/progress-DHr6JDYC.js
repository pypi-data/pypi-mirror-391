import { Z as m, g as J, i as V } from "./Index-nsP3kfoB.js";
const B = window.ms_globals.React, G = window.ms_globals.React.useMemo, y = window.ms_globals.ReactDOM.createPortal, Y = window.ms_globals.antd.Progress;
var F = {
  exports: {}
}, w = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Z = B, H = Symbol.for("react.element"), Q = Symbol.for("react.fragment"), X = Object.prototype.hasOwnProperty, $ = Z.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ee = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(s, e, r) {
  var l, o = {}, t = null, n = null;
  r !== void 0 && (t = "" + r), e.key !== void 0 && (t = "" + e.key), e.ref !== void 0 && (n = e.ref);
  for (l in e) X.call(e, l) && !ee.hasOwnProperty(l) && (o[l] = e[l]);
  if (s && s.defaultProps) for (l in e = s.defaultProps, e) o[l] === void 0 && (o[l] = e[l]);
  return {
    $$typeof: H,
    type: s,
    key: t,
    ref: n,
    props: o,
    _owner: $.current
  };
}
w.Fragment = Q;
w.jsx = T;
w.jsxs = T;
F.exports = w;
var te = F.exports;
const {
  SvelteComponent: ne,
  assign: I,
  binding_callbacks: R,
  check_outros: se,
  children: j,
  claim_element: D,
  claim_space: oe,
  component_subscribe: S,
  compute_slots: re,
  create_slot: le,
  detach: a,
  element: L,
  empty: P,
  exclude_internal_props: k,
  get_all_dirty_from_scope: ie,
  get_slot_changes: ce,
  group_outros: ue,
  init: ae,
  insert_hydration: p,
  safe_not_equal: _e,
  set_custom_element_data: z,
  space: fe,
  transition_in: g,
  transition_out: v,
  update_slot_base: de
} = window.__gradio__svelte__internal, {
  beforeUpdate: me,
  getContext: pe,
  onDestroy: ge,
  setContext: we
} = window.__gradio__svelte__internal;
function E(s) {
  let e, r;
  const l = (
    /*#slots*/
    s[7].default
  ), o = le(
    l,
    s,
    /*$$scope*/
    s[6],
    null
  );
  return {
    c() {
      e = L("svelte-slot"), o && o.c(), this.h();
    },
    l(t) {
      e = D(t, "SVELTE-SLOT", {
        class: !0
      });
      var n = j(e);
      o && o.l(n), n.forEach(a), this.h();
    },
    h() {
      z(e, "class", "svelte-1rt0kpf");
    },
    m(t, n) {
      p(t, e, n), o && o.m(e, null), s[9](e), r = !0;
    },
    p(t, n) {
      o && o.p && (!r || n & /*$$scope*/
      64) && de(
        o,
        l,
        t,
        /*$$scope*/
        t[6],
        r ? ce(
          l,
          /*$$scope*/
          t[6],
          n,
          null
        ) : ie(
          /*$$scope*/
          t[6]
        ),
        null
      );
    },
    i(t) {
      r || (g(o, t), r = !0);
    },
    o(t) {
      v(o, t), r = !1;
    },
    d(t) {
      t && a(e), o && o.d(t), s[9](null);
    }
  };
}
function be(s) {
  let e, r, l, o, t = (
    /*$$slots*/
    s[4].default && E(s)
  );
  return {
    c() {
      e = L("react-portal-target"), r = fe(), t && t.c(), l = P(), this.h();
    },
    l(n) {
      e = D(n, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(e).forEach(a), r = oe(n), t && t.l(n), l = P(), this.h();
    },
    h() {
      z(e, "class", "svelte-1rt0kpf");
    },
    m(n, c) {
      p(n, e, c), s[8](e), p(n, r, c), t && t.m(n, c), p(n, l, c), o = !0;
    },
    p(n, [c]) {
      /*$$slots*/
      n[4].default ? t ? (t.p(n, c), c & /*$$slots*/
      16 && g(t, 1)) : (t = E(n), t.c(), g(t, 1), t.m(l.parentNode, l)) : t && (ue(), v(t, 1, 1, () => {
        t = null;
      }), se());
    },
    i(n) {
      o || (g(t), o = !0);
    },
    o(n) {
      v(t), o = !1;
    },
    d(n) {
      n && (a(e), a(r), a(l)), s[8](null), t && t.d(n);
    }
  };
}
function x(s) {
  const {
    svelteInit: e,
    ...r
  } = s;
  return r;
}
function ve(s, e, r) {
  let l, o, {
    $$slots: t = {},
    $$scope: n
  } = e;
  const c = re(t);
  let {
    svelteInit: u
  } = e;
  const _ = m(x(e)), f = m();
  S(s, f, (i) => r(0, l = i));
  const d = m();
  S(s, d, (i) => r(1, o = i));
  const h = [], A = pe("$$ms-gr-react-wrapper"), {
    slotKey: N,
    slotIndex: W,
    subSlotIndex: q
  } = J() || {}, K = u({
    parent: A,
    props: _,
    target: f,
    slot: d,
    slotKey: N,
    slotIndex: W,
    subSlotIndex: q,
    onDestroy(i) {
      h.push(i);
    }
  });
  we("$$ms-gr-react-wrapper", K), me(() => {
    _.set(x(e));
  }), ge(() => {
    h.forEach((i) => i());
  });
  function M(i) {
    R[i ? "unshift" : "push"](() => {
      l = i, f.set(l);
    });
  }
  function U(i) {
    R[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return s.$$set = (i) => {
    r(17, e = I(I({}, e), k(i))), "svelteInit" in i && r(5, u = i.svelteInit), "$$scope" in i && r(6, n = i.$$scope);
  }, e = k(e), [l, o, f, d, c, u, n, t, M, U];
}
class he extends ne {
  constructor(e) {
    super(), ae(this, e, ve, be, _e, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Pe
} = window.__gradio__svelte__internal, O = window.ms_globals.rerender, b = window.ms_globals.tree;
function ye(s, e = {}) {
  function r(l) {
    const o = m(), t = new he({
      ...l,
      props: {
        svelteInit(n) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: s,
            props: n.props,
            slot: n.slot,
            target: n.target,
            slotIndex: n.slotIndex,
            subSlotIndex: n.subSlotIndex,
            ignore: e.ignore,
            slotKey: n.slotKey,
            nodes: []
          }, u = n.parent ?? b;
          return u.nodes = [...u.nodes, c], O({
            createPortal: y,
            node: b
          }), n.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== o), O({
              createPortal: y,
              node: b
            });
          }), c;
        },
        ...l.props
      }
    });
    return o.set(t), t;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      l(r);
    });
  });
}
function Ie(s) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(s.trim());
}
function Re(s, e = !1) {
  try {
    if (V(s))
      return s;
    if (e && !Ie(s))
      return;
    if (typeof s == "string") {
      let r = s.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function C(s, e) {
  return G(() => Re(s, e), [s, e]);
}
const ke = ye(({
  format: s,
  rounding: e,
  ...r
}) => {
  const l = C(s), o = C(e);
  return /* @__PURE__ */ te.jsx(Y, {
    ...r,
    rounding: o,
    format: l
  });
});
export {
  ke as Progress,
  ke as default
};
