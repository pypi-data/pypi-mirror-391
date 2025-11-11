import { Z as m, g as M } from "./Index-DtD6TnCp.js";
const T = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal, I = window.ms_globals.antd.Divider;
var j = {
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
var V = T, Y = Symbol.for("react.element"), Z = Symbol.for("react.fragment"), H = Object.prototype.hasOwnProperty, Q = V.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, X = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function L(r, t, l) {
  var n, o = {}, e = null, s = null;
  l !== void 0 && (e = "" + l), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) H.call(t, n) && !X.hasOwnProperty(n) && (o[n] = t[n]);
  if (r && r.defaultProps) for (n in t = r.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: Y,
    type: r,
    key: e,
    ref: s,
    props: o,
    _owner: Q.current
  };
}
w.Fragment = Z;
w.jsx = L;
w.jsxs = L;
j.exports = w;
var k = j.exports;
const {
  SvelteComponent: $,
  assign: S,
  binding_callbacks: E,
  check_outros: ee,
  children: z,
  claim_element: A,
  claim_space: te,
  component_subscribe: R,
  compute_slots: se,
  create_slot: oe,
  detach: c,
  element: N,
  empty: x,
  exclude_internal_props: P,
  get_all_dirty_from_scope: ne,
  get_slot_changes: re,
  group_outros: le,
  init: ie,
  insert_hydration: p,
  safe_not_equal: ae,
  set_custom_element_data: q,
  space: _e,
  transition_in: g,
  transition_out: v,
  update_slot_base: ce
} = window.__gradio__svelte__internal, {
  beforeUpdate: ue,
  getContext: fe,
  onDestroy: de,
  setContext: me
} = window.__gradio__svelte__internal;
function C(r) {
  let t, l;
  const n = (
    /*#slots*/
    r[7].default
  ), o = oe(
    n,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      t = N("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      t = A(e, "SVELTE-SLOT", {
        class: !0
      });
      var s = z(t);
      o && o.l(s), s.forEach(c), this.h();
    },
    h() {
      q(t, "class", "svelte-1rt0kpf");
    },
    m(e, s) {
      p(e, t, s), o && o.m(t, null), r[9](t), l = !0;
    },
    p(e, s) {
      o && o.p && (!l || s & /*$$scope*/
      64) && ce(
        o,
        n,
        e,
        /*$$scope*/
        e[6],
        l ? re(
          n,
          /*$$scope*/
          e[6],
          s,
          null
        ) : ne(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      l || (g(o, e), l = !0);
    },
    o(e) {
      v(o, e), l = !1;
    },
    d(e) {
      e && c(t), o && o.d(e), r[9](null);
    }
  };
}
function pe(r) {
  let t, l, n, o, e = (
    /*$$slots*/
    r[4].default && C(r)
  );
  return {
    c() {
      t = N("react-portal-target"), l = _e(), e && e.c(), n = x(), this.h();
    },
    l(s) {
      t = A(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), z(t).forEach(c), l = te(s), e && e.l(s), n = x(), this.h();
    },
    h() {
      q(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      p(s, t, a), r[8](t), p(s, l, a), e && e.m(s, a), p(s, n, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, a), a & /*$$slots*/
      16 && g(e, 1)) : (e = C(s), e.c(), g(e, 1), e.m(n.parentNode, n)) : e && (le(), v(e, 1, 1, () => {
        e = null;
      }), ee());
    },
    i(s) {
      o || (g(e), o = !0);
    },
    o(s) {
      v(e), o = !1;
    },
    d(s) {
      s && (c(t), c(l), c(n)), r[8](null), e && e.d(s);
    }
  };
}
function O(r) {
  const {
    svelteInit: t,
    ...l
  } = r;
  return l;
}
function ge(r, t, l) {
  let n, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const a = se(e);
  let {
    svelteInit: _
  } = t;
  const u = m(O(t)), f = m();
  R(r, f, (i) => l(0, n = i));
  const d = m();
  R(r, d, (i) => l(1, o = i));
  const h = [], K = fe("$$ms-gr-react-wrapper"), {
    slotKey: U,
    slotIndex: F,
    subSlotIndex: W
  } = M() || {}, B = _({
    parent: K,
    props: u,
    target: f,
    slot: d,
    slotKey: U,
    slotIndex: F,
    subSlotIndex: W,
    onDestroy(i) {
      h.push(i);
    }
  });
  me("$$ms-gr-react-wrapper", B), ue(() => {
    u.set(O(t));
  }), de(() => {
    h.forEach((i) => i());
  });
  function G(i) {
    E[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function J(i) {
    E[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return r.$$set = (i) => {
    l(17, t = S(S({}, t), P(i))), "svelteInit" in i && l(5, _ = i.svelteInit), "$$scope" in i && l(6, s = i.$$scope);
  }, t = P(t), [n, o, f, d, a, _, s, e, G, J];
}
class we extends $ {
  constructor(t) {
    super(), ie(this, t, ge, pe, ae, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: he
} = window.__gradio__svelte__internal, D = window.ms_globals.rerender, b = window.ms_globals.tree;
function be(r, t = {}) {
  function l(n) {
    const o = m(), e = new we({
      ...n,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: r,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, _ = s.parent ?? b;
          return _.nodes = [..._.nodes, a], D({
            createPortal: y,
            node: b
          }), s.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== o), D({
              createPortal: y,
              node: b
            });
          }), a;
        },
        ...n.props
      }
    });
    return o.set(e), e;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      n(l);
    });
  });
}
const ye = be(({
  children: r,
  ...t
}) => T.Children.count(r) > 0 ? /* @__PURE__ */ k.jsx(I, {
  ...t,
  children: r
}) : /* @__PURE__ */ k.jsx(I, {
  ...t
}));
export {
  ye as Divider,
  ye as default
};
