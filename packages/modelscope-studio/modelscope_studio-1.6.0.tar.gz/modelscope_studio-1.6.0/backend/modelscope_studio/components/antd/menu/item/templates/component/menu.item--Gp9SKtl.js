import { Z as m, g as B, c as G } from "./Index-BH5BVxnF.js";
const W = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal, H = window.ms_globals.createItemsContext.createItemsContext;
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
var J = W, V = Symbol.for("react.element"), Y = Symbol.for("react.fragment"), Z = Object.prototype.hasOwnProperty, Q = J.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, X = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(l, e, r) {
  var o, n = {}, t = null, s = null;
  r !== void 0 && (t = "" + r), e.key !== void 0 && (t = "" + e.key), e.ref !== void 0 && (s = e.ref);
  for (o in e) Z.call(e, o) && !X.hasOwnProperty(o) && (n[o] = e[o]);
  if (l && l.defaultProps) for (o in e = l.defaultProps, e) n[o] === void 0 && (n[o] = e[o]);
  return {
    $$typeof: V,
    type: l,
    key: t,
    ref: s,
    props: n,
    _owner: Q.current
  };
}
w.Fragment = Y;
w.jsx = T;
w.jsxs = T;
O.exports = w;
var $ = O.exports;
const {
  SvelteComponent: ee,
  assign: I,
  binding_callbacks: x,
  check_outros: te,
  children: j,
  claim_element: D,
  claim_space: se,
  component_subscribe: S,
  compute_slots: ne,
  create_slot: oe,
  detach: u,
  element: L,
  empty: k,
  exclude_internal_props: C,
  get_all_dirty_from_scope: le,
  get_slot_changes: re,
  group_outros: ie,
  init: ae,
  insert_hydration: p,
  safe_not_equal: ce,
  set_custom_element_data: N,
  space: ue,
  transition_in: g,
  transition_out: h,
  update_slot_base: _e
} = window.__gradio__svelte__internal, {
  beforeUpdate: fe,
  getContext: de,
  onDestroy: me,
  setContext: pe
} = window.__gradio__svelte__internal;
function E(l) {
  let e, r;
  const o = (
    /*#slots*/
    l[7].default
  ), n = oe(
    o,
    l,
    /*$$scope*/
    l[6],
    null
  );
  return {
    c() {
      e = L("svelte-slot"), n && n.c(), this.h();
    },
    l(t) {
      e = D(t, "SVELTE-SLOT", {
        class: !0
      });
      var s = j(e);
      n && n.l(s), s.forEach(u), this.h();
    },
    h() {
      N(e, "class", "svelte-1rt0kpf");
    },
    m(t, s) {
      p(t, e, s), n && n.m(e, null), l[9](e), r = !0;
    },
    p(t, s) {
      n && n.p && (!r || s & /*$$scope*/
      64) && _e(
        n,
        o,
        t,
        /*$$scope*/
        t[6],
        r ? re(
          o,
          /*$$scope*/
          t[6],
          s,
          null
        ) : le(
          /*$$scope*/
          t[6]
        ),
        null
      );
    },
    i(t) {
      r || (g(n, t), r = !0);
    },
    o(t) {
      h(n, t), r = !1;
    },
    d(t) {
      t && u(e), n && n.d(t), l[9](null);
    }
  };
}
function ge(l) {
  let e, r, o, n, t = (
    /*$$slots*/
    l[4].default && E(l)
  );
  return {
    c() {
      e = L("react-portal-target"), r = ue(), t && t.c(), o = k(), this.h();
    },
    l(s) {
      e = D(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(e).forEach(u), r = se(s), t && t.l(s), o = k(), this.h();
    },
    h() {
      N(e, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      p(s, e, a), l[8](e), p(s, r, a), t && t.m(s, a), p(s, o, a), n = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? t ? (t.p(s, a), a & /*$$slots*/
      16 && g(t, 1)) : (t = E(s), t.c(), g(t, 1), t.m(o.parentNode, o)) : t && (ie(), h(t, 1, 1, () => {
        t = null;
      }), te());
    },
    i(s) {
      n || (g(t), n = !0);
    },
    o(s) {
      h(t), n = !1;
    },
    d(s) {
      s && (u(e), u(r), u(o)), l[8](null), t && t.d(s);
    }
  };
}
function R(l) {
  const {
    svelteInit: e,
    ...r
  } = l;
  return r;
}
function we(l, e, r) {
  let o, n, {
    $$slots: t = {},
    $$scope: s
  } = e;
  const a = ne(t);
  let {
    svelteInit: c
  } = e;
  const _ = m(R(e)), f = m();
  S(l, f, (i) => r(0, o = i));
  const d = m();
  S(l, d, (i) => r(1, n = i));
  const v = [], z = de("$$ms-gr-react-wrapper"), {
    slotKey: A,
    slotIndex: q,
    subSlotIndex: K
  } = B() || {}, U = c({
    parent: z,
    props: _,
    target: f,
    slot: d,
    slotKey: A,
    slotIndex: q,
    subSlotIndex: K,
    onDestroy(i) {
      v.push(i);
    }
  });
  pe("$$ms-gr-react-wrapper", U), fe(() => {
    _.set(R(e));
  }), me(() => {
    v.forEach((i) => i());
  });
  function F(i) {
    x[i ? "unshift" : "push"](() => {
      o = i, f.set(o);
    });
  }
  function M(i) {
    x[i ? "unshift" : "push"](() => {
      n = i, d.set(n);
    });
  }
  return l.$$set = (i) => {
    r(17, e = I(I({}, e), C(i))), "svelteInit" in i && r(5, c = i.svelteInit), "$$scope" in i && r(6, s = i.$$scope);
  }, e = C(e), [o, n, f, d, a, c, s, t, F, M];
}
class be extends ee {
  constructor(e) {
    super(), ae(this, e, we, ge, ce, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Ie
} = window.__gradio__svelte__internal, P = window.ms_globals.rerender, b = window.ms_globals.tree;
function he(l, e = {}) {
  function r(o) {
    const n = m(), t = new be({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: l,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: e.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, c = s.parent ?? b;
          return c.nodes = [...c.nodes, a], P({
            createPortal: y,
            node: b
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((_) => _.svelteInstance !== n), P({
              createPortal: y,
              node: b
            });
          }), a;
        },
        ...o.props
      }
    });
    return n.set(t), t;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((n) => {
      window.ms_globals.initialize = () => {
        n();
      };
    })), window.ms_globals.initializePromise.then(() => {
      o(r);
    });
  });
}
const {
  useItems: xe,
  withItemsContextProvider: Se,
  ItemHandler: ve
} = H("antd-menu-items"), ke = he((l) => /* @__PURE__ */ $.jsx(ve, {
  ...l,
  allowedSlots: ["default"],
  itemProps: (e, r) => ({
    ...e,
    className: G(e.className, e.type ? `ms-gr-antd-menu-item-${e.type}` : "ms-gr-antd-menu-item", r.default.length > 0 ? "ms-gr-antd-menu-item-submenu" : "")
  }),
  itemChildren: (e) => e.default.length > 0 ? e.default : void 0
}));
export {
  ke as MenuItem,
  ke as default
};
