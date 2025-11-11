import { Z as m, g as G } from "./Index-Drs-gKnY.js";
const B = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal, H = window.ms_globals.createItemsContext.createItemsContext;
var O = {
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
var J = B, M = Symbol.for("react.element"), V = Symbol.for("react.fragment"), Y = Object.prototype.hasOwnProperty, Z = J.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Q = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(l, e, r) {
  var n, s = {}, t = null, o = null;
  r !== void 0 && (t = "" + r), e.key !== void 0 && (t = "" + e.key), e.ref !== void 0 && (o = e.ref);
  for (n in e) Y.call(e, n) && !Q.hasOwnProperty(n) && (s[n] = e[n]);
  if (l && l.defaultProps) for (n in e = l.defaultProps, e) s[n] === void 0 && (s[n] = e[n]);
  return {
    $$typeof: M,
    type: l,
    key: t,
    ref: o,
    props: s,
    _owner: Z.current
  };
}
w.Fragment = V;
w.jsx = T;
w.jsxs = T;
O.exports = w;
var X = O.exports;
const {
  SvelteComponent: $,
  assign: I,
  binding_callbacks: S,
  check_outros: ee,
  children: j,
  claim_element: D,
  claim_space: te,
  component_subscribe: x,
  compute_slots: oe,
  create_slot: se,
  detach: _,
  element: L,
  empty: C,
  exclude_internal_props: k,
  get_all_dirty_from_scope: ne,
  get_slot_changes: le,
  group_outros: re,
  init: ie,
  insert_hydration: p,
  safe_not_equal: ae,
  set_custom_element_data: z,
  space: ce,
  transition_in: g,
  transition_out: h,
  update_slot_base: _e
} = window.__gradio__svelte__internal, {
  beforeUpdate: ue,
  getContext: fe,
  onDestroy: de,
  setContext: me
} = window.__gradio__svelte__internal;
function E(l) {
  let e, r;
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
      e = L("svelte-slot"), s && s.c(), this.h();
    },
    l(t) {
      e = D(t, "SVELTE-SLOT", {
        class: !0
      });
      var o = j(e);
      s && s.l(o), o.forEach(_), this.h();
    },
    h() {
      z(e, "class", "svelte-1rt0kpf");
    },
    m(t, o) {
      p(t, e, o), s && s.m(e, null), l[9](e), r = !0;
    },
    p(t, o) {
      s && s.p && (!r || o & /*$$scope*/
      64) && _e(
        s,
        n,
        t,
        /*$$scope*/
        t[6],
        r ? le(
          n,
          /*$$scope*/
          t[6],
          o,
          null
        ) : ne(
          /*$$scope*/
          t[6]
        ),
        null
      );
    },
    i(t) {
      r || (g(s, t), r = !0);
    },
    o(t) {
      h(s, t), r = !1;
    },
    d(t) {
      t && _(e), s && s.d(t), l[9](null);
    }
  };
}
function pe(l) {
  let e, r, n, s, t = (
    /*$$slots*/
    l[4].default && E(l)
  );
  return {
    c() {
      e = L("react-portal-target"), r = ce(), t && t.c(), n = C(), this.h();
    },
    l(o) {
      e = D(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(e).forEach(_), r = te(o), t && t.l(o), n = C(), this.h();
    },
    h() {
      z(e, "class", "svelte-1rt0kpf");
    },
    m(o, a) {
      p(o, e, a), l[8](e), p(o, r, a), t && t.m(o, a), p(o, n, a), s = !0;
    },
    p(o, [a]) {
      /*$$slots*/
      o[4].default ? t ? (t.p(o, a), a & /*$$slots*/
      16 && g(t, 1)) : (t = E(o), t.c(), g(t, 1), t.m(n.parentNode, n)) : t && (re(), h(t, 1, 1, () => {
        t = null;
      }), ee());
    },
    i(o) {
      s || (g(t), s = !0);
    },
    o(o) {
      h(t), s = !1;
    },
    d(o) {
      o && (_(e), _(r), _(n)), l[8](null), t && t.d(o);
    }
  };
}
function P(l) {
  const {
    svelteInit: e,
    ...r
  } = l;
  return r;
}
function ge(l, e, r) {
  let n, s, {
    $$slots: t = {},
    $$scope: o
  } = e;
  const a = oe(t);
  let {
    svelteInit: c
  } = e;
  const u = m(P(e)), f = m();
  x(l, f, (i) => r(0, n = i));
  const d = m();
  x(l, d, (i) => r(1, s = i));
  const v = [], A = fe("$$ms-gr-react-wrapper"), {
    slotKey: K,
    slotIndex: N,
    subSlotIndex: q
  } = G() || {}, U = c({
    parent: A,
    props: u,
    target: f,
    slot: d,
    slotKey: K,
    slotIndex: N,
    subSlotIndex: q,
    onDestroy(i) {
      v.push(i);
    }
  });
  me("$$ms-gr-react-wrapper", U), ue(() => {
    u.set(P(e));
  }), de(() => {
    v.forEach((i) => i());
  });
  function F(i) {
    S[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function W(i) {
    S[i ? "unshift" : "push"](() => {
      s = i, d.set(s);
    });
  }
  return l.$$set = (i) => {
    r(17, e = I(I({}, e), k(i))), "svelteInit" in i && r(5, c = i.svelteInit), "$$scope" in i && r(6, o = i.$$scope);
  }, e = k(e), [n, s, f, d, a, c, o, t, F, W];
}
class we extends $ {
  constructor(e) {
    super(), ie(this, e, ge, pe, ae, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ye
} = window.__gradio__svelte__internal, R = window.ms_globals.rerender, b = window.ms_globals.tree;
function be(l, e = {}) {
  function r(n) {
    const s = m(), t = new we({
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
            ignore: e.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? b;
          return c.nodes = [...c.nodes, a], R({
            createPortal: y,
            node: b
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((u) => u.svelteInstance !== s), R({
              createPortal: y,
              node: b
            });
          }), a;
        },
        ...n.props
      }
    });
    return s.set(t), t;
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
  withItemsContextProvider: Ie,
  useItems: Se,
  ItemHandler: he
} = H("antd-select-options"), xe = be((l) => /* @__PURE__ */ X.jsx(he, {
  ...l,
  allowedSlots: ["default", "options"],
  itemChildrenKey: "options",
  itemChildren: (e) => e.options.length > 0 ? e.options : e.default.length > 0 ? e.default : void 0
}));
export {
  xe as SelectOptions,
  xe as default
};
