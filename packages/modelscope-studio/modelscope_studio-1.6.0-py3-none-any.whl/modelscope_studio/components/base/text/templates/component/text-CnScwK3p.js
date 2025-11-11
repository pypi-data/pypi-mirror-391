import { Z as m, g as J } from "./Index-CFqGfTxl.js";
const G = window.ms_globals.React, I = window.ms_globals.ReactDOM.createPortal;
var T = {
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
var M = G, V = Symbol.for("react.element"), Y = Symbol.for("react.fragment"), Z = Object.prototype.hasOwnProperty, H = M.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Q = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function j(l, t, r) {
  var n, o = {}, e = null, s = null;
  r !== void 0 && (e = "" + r), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) Z.call(t, n) && !Q.hasOwnProperty(n) && (o[n] = t[n]);
  if (l && l.defaultProps) for (n in t = l.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: V,
    type: l,
    key: e,
    ref: s,
    props: o,
    _owner: H.current
  };
}
w.Fragment = Y;
w.jsx = j;
w.jsxs = j;
T.exports = w;
var b = T.exports;
const {
  SvelteComponent: X,
  assign: k,
  binding_callbacks: S,
  check_outros: $,
  children: D,
  claim_element: L,
  claim_space: ee,
  component_subscribe: x,
  compute_slots: te,
  create_slot: se,
  detach: c,
  element: z,
  empty: E,
  exclude_internal_props: R,
  get_all_dirty_from_scope: oe,
  get_slot_changes: ne,
  group_outros: le,
  init: re,
  insert_hydration: p,
  safe_not_equal: ie,
  set_custom_element_data: A,
  space: ae,
  transition_in: g,
  transition_out: h,
  update_slot_base: _e
} = window.__gradio__svelte__internal, {
  beforeUpdate: ce,
  getContext: ue,
  onDestroy: fe,
  setContext: de
} = window.__gradio__svelte__internal;
function P(l) {
  let t, r;
  const n = (
    /*#slots*/
    l[7].default
  ), o = se(
    n,
    l,
    /*$$scope*/
    l[6],
    null
  );
  return {
    c() {
      t = z("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      t = L(e, "SVELTE-SLOT", {
        class: !0
      });
      var s = D(t);
      o && o.l(s), s.forEach(c), this.h();
    },
    h() {
      A(t, "class", "svelte-1rt0kpf");
    },
    m(e, s) {
      p(e, t, s), o && o.m(t, null), l[9](t), r = !0;
    },
    p(e, s) {
      o && o.p && (!r || s & /*$$scope*/
      64) && _e(
        o,
        n,
        e,
        /*$$scope*/
        e[6],
        r ? ne(
          n,
          /*$$scope*/
          e[6],
          s,
          null
        ) : oe(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      r || (g(o, e), r = !0);
    },
    o(e) {
      h(o, e), r = !1;
    },
    d(e) {
      e && c(t), o && o.d(e), l[9](null);
    }
  };
}
function me(l) {
  let t, r, n, o, e = (
    /*$$slots*/
    l[4].default && P(l)
  );
  return {
    c() {
      t = z("react-portal-target"), r = ae(), e && e.c(), n = E(), this.h();
    },
    l(s) {
      t = L(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), D(t).forEach(c), r = ee(s), e && e.l(s), n = E(), this.h();
    },
    h() {
      A(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      p(s, t, a), l[8](t), p(s, r, a), e && e.m(s, a), p(s, n, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, a), a & /*$$slots*/
      16 && g(e, 1)) : (e = P(s), e.c(), g(e, 1), e.m(n.parentNode, n)) : e && (le(), h(e, 1, 1, () => {
        e = null;
      }), $());
    },
    i(s) {
      o || (g(e), o = !0);
    },
    o(s) {
      h(e), o = !1;
    },
    d(s) {
      s && (c(t), c(r), c(n)), l[8](null), e && e.d(s);
    }
  };
}
function O(l) {
  const {
    svelteInit: t,
    ...r
  } = l;
  return r;
}
function pe(l, t, r) {
  let n, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const a = te(e);
  let {
    svelteInit: _
  } = t;
  const u = m(O(t)), f = m();
  x(l, f, (i) => r(0, n = i));
  const d = m();
  x(l, d, (i) => r(1, o = i));
  const y = [], N = ue("$$ms-gr-react-wrapper"), {
    slotKey: q,
    slotIndex: F,
    subSlotIndex: K
  } = J() || {}, U = _({
    parent: N,
    props: u,
    target: f,
    slot: d,
    slotKey: q,
    slotIndex: F,
    subSlotIndex: K,
    onDestroy(i) {
      y.push(i);
    }
  });
  de("$$ms-gr-react-wrapper", U), ce(() => {
    u.set(O(t));
  }), fe(() => {
    y.forEach((i) => i());
  });
  function W(i) {
    S[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function B(i) {
    S[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return l.$$set = (i) => {
    r(17, t = k(k({}, t), R(i))), "svelteInit" in i && r(5, _ = i.svelteInit), "$$scope" in i && r(6, s = i.$$scope);
  }, t = R(t), [n, o, f, d, a, _, s, e, W, B];
}
class ge extends X {
  constructor(t) {
    super(), re(this, t, pe, me, ie, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ve
} = window.__gradio__svelte__internal, C = window.ms_globals.rerender, v = window.ms_globals.tree;
function we(l, t = {}) {
  function r(n) {
    const o = m(), e = new ge({
      ...n,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: l,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, _ = s.parent ?? v;
          return _.nodes = [..._.nodes, a], C({
            createPortal: I,
            node: v
          }), s.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== o), C({
              createPortal: I,
              node: v
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
      n(r);
    });
  });
}
const he = we(({
  value: l
}) => /* @__PURE__ */ b.jsx(b.Fragment, {
  children: l || /* @__PURE__ */ b.jsx("span", {})
}));
export {
  he as Text,
  he as default
};
