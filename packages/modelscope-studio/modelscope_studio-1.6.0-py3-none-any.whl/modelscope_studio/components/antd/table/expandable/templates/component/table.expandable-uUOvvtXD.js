import { Z as f, g as G } from "./Index-BX6nL7CX.js";
const B = window.ms_globals.React, x = window.ms_globals.ReactDOM.createPortal, I = window.ms_globals.createItemsContext.createItemsContext;
var T = {
  exports: {}
}, b = {};
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
function H(l, t, r) {
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
b.Fragment = V;
b.jsx = H;
b.jsxs = H;
T.exports = b;
var X = T.exports;
const {
  SvelteComponent: $,
  assign: C,
  binding_callbacks: y,
  check_outros: ee,
  children: j,
  claim_element: D,
  claim_space: te,
  component_subscribe: P,
  compute_slots: oe,
  create_slot: se,
  detach: u,
  element: L,
  empty: S,
  exclude_internal_props: E,
  get_all_dirty_from_scope: ne,
  get_slot_changes: le,
  group_outros: re,
  init: ie,
  insert_hydration: p,
  safe_not_equal: ae,
  set_custom_element_data: z,
  space: ce,
  transition_in: w,
  transition_out: g,
  update_slot_base: ue
} = window.__gradio__svelte__internal, {
  beforeUpdate: _e,
  getContext: de,
  onDestroy: me,
  setContext: fe
} = window.__gradio__svelte__internal;
function R(l) {
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
      s && s.l(o), o.forEach(u), this.h();
    },
    h() {
      z(t, "class", "svelte-1rt0kpf");
    },
    m(e, o) {
      p(e, t, o), s && s.m(t, null), l[9](t), r = !0;
    },
    p(e, o) {
      s && s.p && (!r || o & /*$$scope*/
      64) && ue(
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
      g(s, e), r = !1;
    },
    d(e) {
      e && u(t), s && s.d(e), l[9](null);
    }
  };
}
function pe(l) {
  let t, r, n, s, e = (
    /*$$slots*/
    l[4].default && R(l)
  );
  return {
    c() {
      t = L("react-portal-target"), r = ce(), e && e.c(), n = S(), this.h();
    },
    l(o) {
      t = D(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(u), r = te(o), e && e.l(o), n = S(), this.h();
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
      16 && w(e, 1)) : (e = R(o), e.c(), w(e, 1), e.m(n.parentNode, n)) : e && (re(), g(e, 1, 1, () => {
        e = null;
      }), ee());
    },
    i(o) {
      s || (w(e), s = !0);
    },
    o(o) {
      g(e), s = !1;
    },
    d(o) {
      o && (u(t), u(r), u(n)), l[8](null), e && e.d(o);
    }
  };
}
function k(l) {
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
  const _ = f(k(t)), d = f();
  P(l, d, (i) => r(0, n = i));
  const m = f();
  P(l, m, (i) => r(1, s = i));
  const h = [], A = de("$$ms-gr-react-wrapper"), {
    slotKey: N,
    slotIndex: q,
    subSlotIndex: K
  } = G() || {}, U = c({
    parent: A,
    props: _,
    target: d,
    slot: m,
    slotKey: N,
    slotIndex: q,
    subSlotIndex: K,
    onDestroy(i) {
      h.push(i);
    }
  });
  fe("$$ms-gr-react-wrapper", U), _e(() => {
    _.set(k(t));
  }), me(() => {
    h.forEach((i) => i());
  });
  function F(i) {
    y[i ? "unshift" : "push"](() => {
      n = i, d.set(n);
    });
  }
  function W(i) {
    y[i ? "unshift" : "push"](() => {
      s = i, m.set(s);
    });
  }
  return l.$$set = (i) => {
    r(17, t = C(C({}, t), E(i))), "svelteInit" in i && r(5, c = i.svelteInit), "$$scope" in i && r(6, o = i.$$scope);
  }, t = E(t), [n, s, d, m, a, c, o, e, F, W];
}
class Ie extends $ {
  constructor(t) {
    super(), ie(this, t, we, pe, ae, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: he
} = window.__gradio__svelte__internal, O = window.ms_globals.rerender, v = window.ms_globals.tree;
function be(l, t = {}) {
  function r(n) {
    const s = f(), e = new Ie({
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
          }, c = o.parent ?? v;
          return c.nodes = [...c.nodes, a], O({
            createPortal: x,
            node: v
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((_) => _.svelteInstance !== s), O({
              createPortal: x,
              node: v
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
  useItems: xe,
  withItemsContextProvider: Ce,
  ItemHandler: ye
} = I("antd-table-columns"), {
  useItems: Pe,
  withItemsContextProvider: Se,
  ItemHandler: Ee
} = I("antd-table-row-selection-selections"), {
  useItems: Re,
  withItemsContextProvider: ke,
  ItemHandler: Oe
} = I("antd-table-row-selection"), {
  useItems: Te,
  withItemsContextProvider: He,
  ItemHandler: ve
} = I("antd-table-expandable"), je = be((l) => /* @__PURE__ */ X.jsx(ve, {
  ...l
}));
export {
  je as TableExpandable,
  je as default
};
