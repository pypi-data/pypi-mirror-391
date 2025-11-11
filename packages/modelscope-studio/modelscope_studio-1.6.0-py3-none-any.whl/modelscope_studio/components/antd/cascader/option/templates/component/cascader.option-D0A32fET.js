import { Z as m, g as G } from "./Index-B7y4AeQg.js";
const B = window.ms_globals.React, I = window.ms_globals.ReactDOM.createPortal, H = window.ms_globals.createItemsContext.createItemsContext;
var O = {
  exports: {}
}, g = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var J = B, M = Symbol.for("react.element"), V = Symbol.for("react.fragment"), Y = Object.prototype.hasOwnProperty, Z = J.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Q = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(l, t, r) {
  var n, s = {}, e = null, o = null;
  r !== void 0 && (e = "" + r), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (n in t) Y.call(t, n) && !Q.hasOwnProperty(n) && (s[n] = t[n]);
  if (l && l.defaultProps) for (n in t = l.defaultProps, t) s[n] === void 0 && (s[n] = t[n]);
  return {
    $$typeof: M,
    type: l,
    key: e,
    ref: o,
    props: s,
    _owner: Z.current
  };
}
g.Fragment = V;
g.jsx = T;
g.jsxs = T;
O.exports = g;
var X = O.exports;
const {
  SvelteComponent: $,
  assign: y,
  binding_callbacks: x,
  check_outros: ee,
  children: j,
  claim_element: D,
  claim_space: te,
  component_subscribe: C,
  compute_slots: oe,
  create_slot: se,
  detach: _,
  element: L,
  empty: S,
  exclude_internal_props: k,
  get_all_dirty_from_scope: ne,
  get_slot_changes: le,
  group_outros: re,
  init: ie,
  insert_hydration: p,
  safe_not_equal: ae,
  set_custom_element_data: z,
  space: ce,
  transition_in: w,
  transition_out: v,
  update_slot_base: _e
} = window.__gradio__svelte__internal, {
  beforeUpdate: ue,
  getContext: fe,
  onDestroy: de,
  setContext: me
} = window.__gradio__svelte__internal;
function E(l) {
  let t, r;
  const n = (
    /*#slots*/
    l[7].default
  ), s = se(
    n,
    l,
    /*$$scope*/
    l[6],
    null
  );
  return {
    c() {
      t = L("svelte-slot"), s && s.c(), this.h();
    },
    l(e) {
      t = D(e, "SVELTE-SLOT", {
        class: !0
      });
      var o = j(t);
      s && s.l(o), o.forEach(_), this.h();
    },
    h() {
      z(t, "class", "svelte-1rt0kpf");
    },
    m(e, o) {
      p(e, t, o), s && s.m(t, null), l[9](t), r = !0;
    },
    p(e, o) {
      s && s.p && (!r || o & /*$$scope*/
      64) && _e(
        s,
        n,
        e,
        /*$$scope*/
        e[6],
        r ? le(
          n,
          /*$$scope*/
          e[6],
          o,
          null
        ) : ne(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      r || (w(s, e), r = !0);
    },
    o(e) {
      v(s, e), r = !1;
    },
    d(e) {
      e && _(t), s && s.d(e), l[9](null);
    }
  };
}
function pe(l) {
  let t, r, n, s, e = (
    /*$$slots*/
    l[4].default && E(l)
  );
  return {
    c() {
      t = L("react-portal-target"), r = ce(), e && e.c(), n = S(), this.h();
    },
    l(o) {
      t = D(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(_), r = te(o), e && e.l(o), n = S(), this.h();
    },
    h() {
      z(t, "class", "svelte-1rt0kpf");
    },
    m(o, a) {
      p(o, t, a), l[8](t), p(o, r, a), e && e.m(o, a), p(o, n, a), s = !0;
    },
    p(o, [a]) {
      /*$$slots*/
      o[4].default ? e ? (e.p(o, a), a & /*$$slots*/
      16 && w(e, 1)) : (e = E(o), e.c(), w(e, 1), e.m(n.parentNode, n)) : e && (re(), v(e, 1, 1, () => {
        e = null;
      }), ee());
    },
    i(o) {
      s || (w(e), s = !0);
    },
    o(o) {
      v(e), s = !1;
    },
    d(o) {
      o && (_(t), _(r), _(n)), l[8](null), e && e.d(o);
    }
  };
}
function P(l) {
  const {
    svelteInit: t,
    ...r
  } = l;
  return r;
}
function we(l, t, r) {
  let n, s, {
    $$slots: e = {},
    $$scope: o
  } = t;
  const a = oe(e);
  let {
    svelteInit: c
  } = t;
  const u = m(P(t)), f = m();
  C(l, f, (i) => r(0, n = i));
  const d = m();
  C(l, d, (i) => r(1, s = i));
  const h = [], A = fe("$$ms-gr-react-wrapper"), {
    slotKey: N,
    slotIndex: q,
    subSlotIndex: K
  } = G() || {}, U = c({
    parent: A,
    props: u,
    target: f,
    slot: d,
    slotKey: N,
    slotIndex: q,
    subSlotIndex: K,
    onDestroy(i) {
      h.push(i);
    }
  });
  me("$$ms-gr-react-wrapper", U), ue(() => {
    u.set(P(t));
  }), de(() => {
    h.forEach((i) => i());
  });
  function F(i) {
    x[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function W(i) {
    x[i ? "unshift" : "push"](() => {
      s = i, d.set(s);
    });
  }
  return l.$$set = (i) => {
    r(17, t = y(y({}, t), k(i))), "svelteInit" in i && r(5, c = i.svelteInit), "$$scope" in i && r(6, o = i.$$scope);
  }, t = k(t), [n, s, f, d, a, c, o, e, F, W];
}
class ge extends $ {
  constructor(t) {
    super(), ie(this, t, we, pe, ae, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Ie
} = window.__gradio__svelte__internal, R = window.ms_globals.rerender, b = window.ms_globals.tree;
function be(l, t = {}) {
  function r(n) {
    const s = m(), e = new ge({
      ...n,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: l,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? b;
          return c.nodes = [...c.nodes, a], R({
            createPortal: I,
            node: b
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((u) => u.svelteInstance !== s), R({
              createPortal: I,
              node: b
            });
          }), a;
        },
        ...n.props
      }
    });
    return s.set(e), e;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((s) => {
      window.ms_globals.initialize = () => {
        s();
      };
    })), window.ms_globals.initializePromise.then(() => {
      n(r);
    });
  });
}
const {
  useItems: ye,
  withItemsContextProvider: xe,
  ItemHandler: ve
} = H("antd-cascader-options"), Ce = be((l) => /* @__PURE__ */ X.jsx(ve, {
  ...l,
  allowedSlots: ["default"],
  itemChildren: (t) => t.default.length > 0 ? t.default : void 0
}));
export {
  Ce as CascaderOption,
  Ce as default
};
