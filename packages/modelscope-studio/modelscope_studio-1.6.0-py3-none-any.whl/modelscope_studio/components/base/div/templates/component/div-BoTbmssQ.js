import { Z as m, g as Y, t as Z, s as _ } from "./Index-Bruf2ffQ.js";
const T = window.ms_globals.React, D = window.ms_globals.React.useMemo, G = window.ms_globals.React.useState, J = window.ms_globals.React.useEffect, S = window.ms_globals.ReactDOM.createPortal;
var j = {
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
var H = T, Q = Symbol.for("react.element"), X = Symbol.for("react.fragment"), $ = Object.prototype.hasOwnProperty, ee = H.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, te = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function A(n, t, l) {
  var r, o = {}, e = null, s = null;
  l !== void 0 && (e = "" + l), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (r in t) $.call(t, r) && !te.hasOwnProperty(r) && (o[r] = t[r]);
  if (n && n.defaultProps) for (r in t = n.defaultProps, t) o[r] === void 0 && (o[r] = t[r]);
  return {
    $$typeof: Q,
    type: n,
    key: e,
    ref: s,
    props: o,
    _owner: ee.current
  };
}
b.Fragment = X;
b.jsx = A;
b.jsxs = A;
j.exports = b;
var se = j.exports;
const {
  SvelteComponent: oe,
  assign: h,
  binding_callbacks: x,
  check_outros: ne,
  children: L,
  claim_element: z,
  claim_space: re,
  component_subscribe: R,
  compute_slots: le,
  create_slot: ie,
  detach: c,
  element: N,
  empty: E,
  exclude_internal_props: k,
  get_all_dirty_from_scope: ae,
  get_slot_changes: ue,
  group_outros: ce,
  init: _e,
  insert_hydration: g,
  safe_not_equal: fe,
  set_custom_element_data: q,
  space: de,
  transition_in: w,
  transition_out: I,
  update_slot_base: pe
} = window.__gradio__svelte__internal, {
  beforeUpdate: me,
  getContext: ge,
  onDestroy: we,
  setContext: be
} = window.__gradio__svelte__internal;
function P(n) {
  let t, l;
  const r = (
    /*#slots*/
    n[7].default
  ), o = ie(
    r,
    n,
    /*$$scope*/
    n[6],
    null
  );
  return {
    c() {
      t = N("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      t = z(e, "SVELTE-SLOT", {
        class: !0
      });
      var s = L(t);
      o && o.l(s), s.forEach(c), this.h();
    },
    h() {
      q(t, "class", "svelte-1rt0kpf");
    },
    m(e, s) {
      g(e, t, s), o && o.m(t, null), n[9](t), l = !0;
    },
    p(e, s) {
      o && o.p && (!l || s & /*$$scope*/
      64) && pe(
        o,
        r,
        e,
        /*$$scope*/
        e[6],
        l ? ue(
          r,
          /*$$scope*/
          e[6],
          s,
          null
        ) : ae(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      l || (w(o, e), l = !0);
    },
    o(e) {
      I(o, e), l = !1;
    },
    d(e) {
      e && c(t), o && o.d(e), n[9](null);
    }
  };
}
function ve(n) {
  let t, l, r, o, e = (
    /*$$slots*/
    n[4].default && P(n)
  );
  return {
    c() {
      t = N("react-portal-target"), l = de(), e && e.c(), r = E(), this.h();
    },
    l(s) {
      t = z(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), L(t).forEach(c), l = re(s), e && e.l(s), r = E(), this.h();
    },
    h() {
      q(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      g(s, t, a), n[8](t), g(s, l, a), e && e.m(s, a), g(s, r, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, a), a & /*$$slots*/
      16 && w(e, 1)) : (e = P(s), e.c(), w(e, 1), e.m(r.parentNode, r)) : e && (ce(), I(e, 1, 1, () => {
        e = null;
      }), ne());
    },
    i(s) {
      o || (w(e), o = !0);
    },
    o(s) {
      I(e), o = !1;
    },
    d(s) {
      s && (c(t), c(l), c(r)), n[8](null), e && e.d(s);
    }
  };
}
function C(n) {
  const {
    svelteInit: t,
    ...l
  } = n;
  return l;
}
function Ie(n, t, l) {
  let r, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const a = le(e);
  let {
    svelteInit: u
  } = t;
  const f = m(C(t)), d = m();
  R(n, d, (i) => l(0, r = i));
  const p = m();
  R(n, p, (i) => l(1, o = i));
  const y = [], K = ge("$$ms-gr-react-wrapper"), {
    slotKey: M,
    slotIndex: U,
    subSlotIndex: B
  } = Y() || {}, F = u({
    parent: K,
    props: f,
    target: d,
    slot: p,
    slotKey: M,
    slotIndex: U,
    subSlotIndex: B,
    onDestroy(i) {
      y.push(i);
    }
  });
  be("$$ms-gr-react-wrapper", F), me(() => {
    f.set(C(t));
  }), we(() => {
    y.forEach((i) => i());
  });
  function V(i) {
    x[i ? "unshift" : "push"](() => {
      r = i, d.set(r);
    });
  }
  function W(i) {
    x[i ? "unshift" : "push"](() => {
      o = i, p.set(o);
    });
  }
  return n.$$set = (i) => {
    l(17, t = h(h({}, t), k(i))), "svelteInit" in i && l(5, u = i.svelteInit), "$$scope" in i && l(6, s = i.$$scope);
  }, t = k(t), [r, o, d, p, a, u, s, e, V, W];
}
class ye extends oe {
  constructor(t) {
    super(), _e(this, t, Ie, ve, fe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ke
} = window.__gradio__svelte__internal, O = window.ms_globals.rerender, v = window.ms_globals.tree;
function Se(n, t = {}) {
  function l(r) {
    const o = m(), e = new ye({
      ...r,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: n,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, u = s.parent ?? v;
          return u.nodes = [...u.nodes, a], O({
            createPortal: S,
            node: v
          }), s.onDestroy(() => {
            u.nodes = u.nodes.filter((f) => f.svelteInstance !== o), O({
              createPortal: S,
              node: v
            });
          }), a;
        },
        ...r.props
      }
    });
    return o.set(e), e;
  }
  return new Promise((r) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      r(l);
    });
  });
}
function he(n) {
  const [t, l] = G(() => _(n));
  return J(() => {
    let r = !0;
    return n.subscribe((e) => {
      r && (r = !1, e === t) || l(e);
    });
  }, [n]), t;
}
function xe(n) {
  const t = D(() => Z(n, (l) => l), [n]);
  return he(t);
}
function Re(n, t) {
  const l = D(() => T.Children.toArray(n.originalChildren || n).filter((e) => e.props.node && !e.props.node.ignore && (!e.props.nodeSlotKey || t)).sort((e, s) => {
    if (e.props.node.slotIndex && s.props.node.slotIndex) {
      const a = _(e.props.node.slotIndex) || 0, u = _(s.props.node.slotIndex) || 0;
      return a - u === 0 && e.props.node.subSlotIndex && s.props.node.subSlotIndex ? (_(e.props.node.subSlotIndex) || 0) - (_(s.props.node.subSlotIndex) || 0) : a - u;
    }
    return 0;
  }).map((e) => e.props.node.target), [n, t]);
  return xe(l);
}
const Pe = Se(({
  slots: n,
  value: t,
  children: l,
  ...r
}) => {
  const o = Re(l);
  return /* @__PURE__ */ se.jsx("div", {
    ...r,
    children: o.length > 0 ? l : t || l
  });
});
export {
  Pe as Div,
  Pe as default
};
