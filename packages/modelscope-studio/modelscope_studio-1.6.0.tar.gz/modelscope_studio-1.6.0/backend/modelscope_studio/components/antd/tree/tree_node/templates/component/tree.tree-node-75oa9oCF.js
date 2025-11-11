import { Z as m, g as G } from "./Index-B43LI5I8.js";
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
function T(r, t, l) {
  var n, s = {}, e = null, o = null;
  l !== void 0 && (e = "" + l), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (n in t) Y.call(t, n) && !Q.hasOwnProperty(n) && (s[n] = t[n]);
  if (r && r.defaultProps) for (n in t = r.defaultProps, t) s[n] === void 0 && (s[n] = t[n]);
  return {
    $$typeof: M,
    type: r,
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
  component_subscribe: S,
  compute_slots: oe,
  create_slot: se,
  detach: c,
  element: L,
  empty: k,
  exclude_internal_props: C,
  get_all_dirty_from_scope: ne,
  get_slot_changes: re,
  group_outros: le,
  init: ie,
  insert_hydration: p,
  safe_not_equal: ae,
  set_custom_element_data: N,
  space: _e,
  transition_in: w,
  transition_out: v,
  update_slot_base: ce
} = window.__gradio__svelte__internal, {
  beforeUpdate: ue,
  getContext: fe,
  onDestroy: de,
  setContext: me
} = window.__gradio__svelte__internal;
function E(r) {
  let t, l;
  const n = (
    /*#slots*/
    r[7].default
  ), s = se(
    n,
    r,
    /*$$scope*/
    r[6],
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
      s && s.l(o), o.forEach(c), this.h();
    },
    h() {
      N(t, "class", "svelte-1rt0kpf");
    },
    m(e, o) {
      p(e, t, o), s && s.m(t, null), r[9](t), l = !0;
    },
    p(e, o) {
      s && s.p && (!l || o & /*$$scope*/
      64) && ce(
        s,
        n,
        e,
        /*$$scope*/
        e[6],
        l ? re(
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
      l || (w(s, e), l = !0);
    },
    o(e) {
      v(s, e), l = !1;
    },
    d(e) {
      e && c(t), s && s.d(e), r[9](null);
    }
  };
}
function pe(r) {
  let t, l, n, s, e = (
    /*$$slots*/
    r[4].default && E(r)
  );
  return {
    c() {
      t = L("react-portal-target"), l = _e(), e && e.c(), n = k(), this.h();
    },
    l(o) {
      t = D(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(c), l = te(o), e && e.l(o), n = k(), this.h();
    },
    h() {
      N(t, "class", "svelte-1rt0kpf");
    },
    m(o, a) {
      p(o, t, a), r[8](t), p(o, l, a), e && e.m(o, a), p(o, n, a), s = !0;
    },
    p(o, [a]) {
      /*$$slots*/
      o[4].default ? e ? (e.p(o, a), a & /*$$slots*/
      16 && w(e, 1)) : (e = E(o), e.c(), w(e, 1), e.m(n.parentNode, n)) : e && (le(), v(e, 1, 1, () => {
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
      o && (c(t), c(l), c(n)), r[8](null), e && e.d(o);
    }
  };
}
function P(r) {
  const {
    svelteInit: t,
    ...l
  } = r;
  return l;
}
function we(r, t, l) {
  let n, s, {
    $$slots: e = {},
    $$scope: o
  } = t;
  const a = oe(e);
  let {
    svelteInit: _
  } = t;
  const u = m(P(t)), f = m();
  S(r, f, (i) => l(0, n = i));
  const d = m();
  S(r, d, (i) => l(1, s = i));
  const h = [], z = fe("$$ms-gr-react-wrapper"), {
    slotKey: A,
    slotIndex: q,
    subSlotIndex: K
  } = G() || {}, U = _({
    parent: z,
    props: u,
    target: f,
    slot: d,
    slotKey: A,
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
  return r.$$set = (i) => {
    l(17, t = y(y({}, t), C(i))), "svelteInit" in i && l(5, _ = i.svelteInit), "$$scope" in i && l(6, o = i.$$scope);
  }, t = C(t), [n, s, f, d, a, _, o, e, F, W];
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
function be(r, t = {}) {
  function l(n) {
    const s = m(), e = new ge({
      ...n,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: r,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, _ = o.parent ?? b;
          return _.nodes = [..._.nodes, a], R({
            createPortal: I,
            node: b
          }), o.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== s), R({
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
      n(l);
    });
  });
}
const {
  withItemsContextProvider: ye,
  useItems: xe,
  ItemHandler: ve
} = H("antd-tree-tree-nodes"), Se = be((r) => /* @__PURE__ */ X.jsx(ve, {
  ...r,
  allowedSlots: ["default"],
  itemChildren: (t) => t.default.length > 0 ? t.default : void 0
}));
export {
  Se as TreeTreeNode,
  Se as default
};
