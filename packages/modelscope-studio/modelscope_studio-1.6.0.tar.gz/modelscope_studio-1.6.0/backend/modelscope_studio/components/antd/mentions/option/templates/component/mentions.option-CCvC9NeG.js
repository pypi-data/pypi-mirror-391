import { Z as m, g as B } from "./Index-BVT9AUVL.js";
const W = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal, G = window.ms_globals.createItemsContext.createItemsContext;
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
var H = W, J = Symbol.for("react.element"), V = Symbol.for("react.fragment"), Y = Object.prototype.hasOwnProperty, Z = H.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Q = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(l, e, r) {
  var s, n = {}, t = null, o = null;
  r !== void 0 && (t = "" + r), e.key !== void 0 && (t = "" + e.key), e.ref !== void 0 && (o = e.ref);
  for (s in e) Y.call(e, s) && !Q.hasOwnProperty(s) && (n[s] = e[s]);
  if (l && l.defaultProps) for (s in e = l.defaultProps, e) n[s] === void 0 && (n[s] = e[s]);
  return {
    $$typeof: J,
    type: l,
    key: t,
    ref: o,
    props: n,
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
  binding_callbacks: x,
  check_outros: ee,
  children: j,
  claim_element: D,
  claim_space: te,
  component_subscribe: C,
  compute_slots: oe,
  create_slot: ne,
  detach: c,
  element: L,
  empty: S,
  exclude_internal_props: k,
  get_all_dirty_from_scope: se,
  get_slot_changes: le,
  group_outros: re,
  init: ie,
  insert_hydration: p,
  safe_not_equal: ae,
  set_custom_element_data: z,
  space: _e,
  transition_in: g,
  transition_out: h,
  update_slot_base: ce
} = window.__gradio__svelte__internal, {
  beforeUpdate: ue,
  getContext: fe,
  onDestroy: de,
  setContext: me
} = window.__gradio__svelte__internal;
function E(l) {
  let e, r;
  const s = (
    /*#slots*/
    l[7].default
  ), n = ne(
    s,
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
      var o = j(e);
      n && n.l(o), o.forEach(c), this.h();
    },
    h() {
      z(e, "class", "svelte-1rt0kpf");
    },
    m(t, o) {
      p(t, e, o), n && n.m(e, null), l[9](e), r = !0;
    },
    p(t, o) {
      n && n.p && (!r || o & /*$$scope*/
      64) && ce(
        n,
        s,
        t,
        /*$$scope*/
        t[6],
        r ? le(
          s,
          /*$$scope*/
          t[6],
          o,
          null
        ) : se(
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
      t && c(e), n && n.d(t), l[9](null);
    }
  };
}
function pe(l) {
  let e, r, s, n, t = (
    /*$$slots*/
    l[4].default && E(l)
  );
  return {
    c() {
      e = L("react-portal-target"), r = _e(), t && t.c(), s = S(), this.h();
    },
    l(o) {
      e = D(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(e).forEach(c), r = te(o), t && t.l(o), s = S(), this.h();
    },
    h() {
      z(e, "class", "svelte-1rt0kpf");
    },
    m(o, a) {
      p(o, e, a), l[8](e), p(o, r, a), t && t.m(o, a), p(o, s, a), n = !0;
    },
    p(o, [a]) {
      /*$$slots*/
      o[4].default ? t ? (t.p(o, a), a & /*$$slots*/
      16 && g(t, 1)) : (t = E(o), t.c(), g(t, 1), t.m(s.parentNode, s)) : t && (re(), h(t, 1, 1, () => {
        t = null;
      }), ee());
    },
    i(o) {
      n || (g(t), n = !0);
    },
    o(o) {
      h(t), n = !1;
    },
    d(o) {
      o && (c(e), c(r), c(s)), l[8](null), t && t.d(o);
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
  let s, n, {
    $$slots: t = {},
    $$scope: o
  } = e;
  const a = oe(t);
  let {
    svelteInit: _
  } = e;
  const u = m(P(e)), f = m();
  C(l, f, (i) => r(0, s = i));
  const d = m();
  C(l, d, (i) => r(1, n = i));
  const v = [], A = fe("$$ms-gr-react-wrapper"), {
    slotKey: K,
    slotIndex: N,
    subSlotIndex: q
  } = B() || {}, U = _({
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
    x[i ? "unshift" : "push"](() => {
      s = i, f.set(s);
    });
  }
  function M(i) {
    x[i ? "unshift" : "push"](() => {
      n = i, d.set(n);
    });
  }
  return l.$$set = (i) => {
    r(17, e = I(I({}, e), k(i))), "svelteInit" in i && r(5, _ = i.svelteInit), "$$scope" in i && r(6, o = i.$$scope);
  }, e = k(e), [s, n, f, d, a, _, o, t, F, M];
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
  function r(s) {
    const n = m(), t = new we({
      ...s,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: l,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: e.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, _ = o.parent ?? b;
          return _.nodes = [..._.nodes, a], R({
            createPortal: y,
            node: b
          }), o.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== n), R({
              createPortal: y,
              node: b
            });
          }), a;
        },
        ...s.props
      }
    });
    return n.set(t), t;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((n) => {
      window.ms_globals.initialize = () => {
        n();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(r);
    });
  });
}
const {
  useItems: Ie,
  withItemsContextProvider: xe,
  ItemHandler: he
} = G("antd-mentions-options"), Ce = be((l) => /* @__PURE__ */ X.jsx(he, {
  ...l,
  allowedSlots: ["default", "options"],
  itemChildrenKey: "options",
  itemChildren: (e) => e.options.length > 0 ? e.options : e.default.length > 0 ? e.default : void 0
}));
export {
  Ce as MentionsOption,
  Ce as default
};
