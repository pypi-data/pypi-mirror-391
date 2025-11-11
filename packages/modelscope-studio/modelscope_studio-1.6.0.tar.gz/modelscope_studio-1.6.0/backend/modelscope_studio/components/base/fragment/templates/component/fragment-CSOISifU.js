import { Z as m, g as J } from "./Index-C5BkFZGP.js";
const G = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal;
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
function j(r, t, l) {
  var n, o = {}, e = null, s = null;
  l !== void 0 && (e = "" + l), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) Z.call(t, n) && !Q.hasOwnProperty(n) && (o[n] = t[n]);
  if (r && r.defaultProps) for (n in t = r.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: V,
    type: r,
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
var I = T.exports;
const {
  SvelteComponent: X,
  assign: k,
  binding_callbacks: S,
  check_outros: $,
  children: D,
  claim_element: L,
  claim_space: ee,
  component_subscribe: E,
  compute_slots: te,
  create_slot: se,
  detach: c,
  element: z,
  empty: R,
  exclude_internal_props: P,
  get_all_dirty_from_scope: oe,
  get_slot_changes: ne,
  group_outros: re,
  init: le,
  insert_hydration: p,
  safe_not_equal: ie,
  set_custom_element_data: A,
  space: ae,
  transition_in: g,
  transition_out: v,
  update_slot_base: _e
} = window.__gradio__svelte__internal, {
  beforeUpdate: ce,
  getContext: ue,
  onDestroy: fe,
  setContext: de
} = window.__gradio__svelte__internal;
function x(r) {
  let t, l;
  const n = (
    /*#slots*/
    r[7].default
  ), o = se(
    n,
    r,
    /*$$scope*/
    r[6],
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
      p(e, t, s), o && o.m(t, null), r[9](t), l = !0;
    },
    p(e, s) {
      o && o.p && (!l || s & /*$$scope*/
      64) && _e(
        o,
        n,
        e,
        /*$$scope*/
        e[6],
        l ? ne(
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
function me(r) {
  let t, l, n, o, e = (
    /*$$slots*/
    r[4].default && x(r)
  );
  return {
    c() {
      t = z("react-portal-target"), l = ae(), e && e.c(), n = R(), this.h();
    },
    l(s) {
      t = L(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), D(t).forEach(c), l = ee(s), e && e.l(s), n = R(), this.h();
    },
    h() {
      A(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      p(s, t, a), r[8](t), p(s, l, a), e && e.m(s, a), p(s, n, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, a), a & /*$$slots*/
      16 && g(e, 1)) : (e = x(s), e.c(), g(e, 1), e.m(n.parentNode, n)) : e && (re(), v(e, 1, 1, () => {
        e = null;
      }), $());
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
function pe(r, t, l) {
  let n, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const a = te(e);
  let {
    svelteInit: _
  } = t;
  const u = m(O(t)), f = m();
  E(r, f, (i) => l(0, n = i));
  const d = m();
  E(r, d, (i) => l(1, o = i));
  const h = [], F = ue("$$ms-gr-react-wrapper"), {
    slotKey: N,
    slotIndex: q,
    subSlotIndex: K
  } = J() || {}, U = _({
    parent: F,
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
  de("$$ms-gr-react-wrapper", U), ce(() => {
    u.set(O(t));
  }), fe(() => {
    h.forEach((i) => i());
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
  return r.$$set = (i) => {
    l(17, t = k(k({}, t), P(i))), "svelteInit" in i && l(5, _ = i.svelteInit), "$$scope" in i && l(6, s = i.$$scope);
  }, t = P(t), [n, o, f, d, a, _, s, e, W, B];
}
class ge extends X {
  constructor(t) {
    super(), le(this, t, pe, me, ie, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ve
} = window.__gradio__svelte__internal, C = window.ms_globals.rerender, b = window.ms_globals.tree;
function we(r, t = {}) {
  function l(n) {
    const o = m(), e = new ge({
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
          return _.nodes = [..._.nodes, a], C({
            createPortal: y,
            node: b
          }), s.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== o), C({
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
const he = we(({
  children: r
}) => /* @__PURE__ */ I.jsx(I.Fragment, {
  children: r
}));
export {
  he as Fragment,
  he as default
};
