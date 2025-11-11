import { Z as m, g as G } from "./Index-W-3v1tk0.js";
const B = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal;
var C = {
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
var J = B, M = Symbol.for("react.element"), V = Symbol.for("react.fragment"), Y = Object.prototype.hasOwnProperty, Z = J.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, H = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(l, t, r) {
  var n, o = {}, e = null, s = null;
  r !== void 0 && (e = "" + r), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) Y.call(t, n) && !H.hasOwnProperty(n) && (o[n] = t[n]);
  if (l && l.defaultProps) for (n in t = l.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: M,
    type: l,
    key: e,
    ref: s,
    props: o,
    _owner: Z.current
  };
}
w.Fragment = V;
w.jsx = T;
w.jsxs = T;
C.exports = w;
var we = C.exports;
const {
  SvelteComponent: Q,
  assign: I,
  binding_callbacks: k,
  check_outros: X,
  children: j,
  claim_element: D,
  claim_space: $,
  component_subscribe: R,
  compute_slots: ee,
  create_slot: te,
  detach: c,
  element: L,
  empty: S,
  exclude_internal_props: E,
  get_all_dirty_from_scope: se,
  get_slot_changes: oe,
  group_outros: ne,
  init: le,
  insert_hydration: p,
  safe_not_equal: re,
  set_custom_element_data: z,
  space: ie,
  transition_in: g,
  transition_out: v,
  update_slot_base: ae
} = window.__gradio__svelte__internal, {
  beforeUpdate: _e,
  getContext: ce,
  onDestroy: ue,
  setContext: fe
} = window.__gradio__svelte__internal;
function P(l) {
  let t, r;
  const n = (
    /*#slots*/
    l[7].default
  ), o = te(
    n,
    l,
    /*$$scope*/
    l[6],
    null
  );
  return {
    c() {
      t = L("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      t = D(e, "SVELTE-SLOT", {
        class: !0
      });
      var s = j(t);
      o && o.l(s), s.forEach(c), this.h();
    },
    h() {
      z(t, "class", "svelte-1rt0kpf");
    },
    m(e, s) {
      p(e, t, s), o && o.m(t, null), l[9](t), r = !0;
    },
    p(e, s) {
      o && o.p && (!r || s & /*$$scope*/
      64) && ae(
        o,
        n,
        e,
        /*$$scope*/
        e[6],
        r ? oe(
          n,
          /*$$scope*/
          e[6],
          s,
          null
        ) : se(
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
      v(o, e), r = !1;
    },
    d(e) {
      e && c(t), o && o.d(e), l[9](null);
    }
  };
}
function de(l) {
  let t, r, n, o, e = (
    /*$$slots*/
    l[4].default && P(l)
  );
  return {
    c() {
      t = L("react-portal-target"), r = ie(), e && e.c(), n = S(), this.h();
    },
    l(s) {
      t = D(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(c), r = $(s), e && e.l(s), n = S(), this.h();
    },
    h() {
      z(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      p(s, t, a), l[8](t), p(s, r, a), e && e.m(s, a), p(s, n, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, a), a & /*$$slots*/
      16 && g(e, 1)) : (e = P(s), e.c(), g(e, 1), e.m(n.parentNode, n)) : e && (ne(), v(e, 1, 1, () => {
        e = null;
      }), X());
    },
    i(s) {
      o || (g(e), o = !0);
    },
    o(s) {
      v(e), o = !1;
    },
    d(s) {
      s && (c(t), c(r), c(n)), l[8](null), e && e.d(s);
    }
  };
}
function x(l) {
  const {
    svelteInit: t,
    ...r
  } = l;
  return r;
}
function me(l, t, r) {
  let n, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const a = ee(e);
  let {
    svelteInit: _
  } = t;
  const u = m(x(t)), f = m();
  R(l, f, (i) => r(0, n = i));
  const d = m();
  R(l, d, (i) => r(1, o = i));
  const h = [], A = ce("$$ms-gr-react-wrapper"), {
    slotKey: N,
    slotIndex: K,
    subSlotIndex: U
  } = G() || {}, q = _({
    parent: A,
    props: u,
    target: f,
    slot: d,
    slotKey: N,
    slotIndex: K,
    subSlotIndex: U,
    onDestroy(i) {
      h.push(i);
    }
  });
  fe("$$ms-gr-react-wrapper", q), _e(() => {
    u.set(x(t));
  }), ue(() => {
    h.forEach((i) => i());
  });
  function F(i) {
    k[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function W(i) {
    k[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return l.$$set = (i) => {
    r(17, t = I(I({}, t), E(i))), "svelteInit" in i && r(5, _ = i.svelteInit), "$$scope" in i && r(6, s = i.$$scope);
  }, t = E(t), [n, o, f, d, a, _, s, e, F, W];
}
class pe extends Q {
  constructor(t) {
    super(), le(this, t, me, de, re, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: be
} = window.__gradio__svelte__internal, O = window.ms_globals.rerender, b = window.ms_globals.tree;
function ve(l, t = {}) {
  function r(n) {
    const o = m(), e = new pe({
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
          }, _ = s.parent ?? b;
          return _.nodes = [..._.nodes, a], O({
            createPortal: y,
            node: b
          }), s.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== o), O({
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
      n(r);
    });
  });
}
export {
  we as j,
  ve as s
};
