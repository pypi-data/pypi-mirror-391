import { Z as m, g as V, i as Y } from "./Index-BGAMtROE.js";
const U = window.ms_globals.React, B = window.ms_globals.React.useMemo, G = window.ms_globals.React.useState, J = window.ms_globals.React.useEffect, y = window.ms_globals.ReactDOM.createPortal, Z = window.ms_globals.internalContext.useContextPropsContext, H = window.ms_globals.internalContext.ContextPropsProvider;
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
var Q = U, X = Symbol.for("react.element"), $ = Symbol.for("react.fragment"), ee = Object.prototype.hasOwnProperty, te = Q.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function F(s, e, o) {
  var l, r = {}, t = null, n = null;
  o !== void 0 && (t = "" + o), e.key !== void 0 && (t = "" + e.key), e.ref !== void 0 && (n = e.ref);
  for (l in e) ee.call(e, l) && !ne.hasOwnProperty(l) && (r[l] = e[l]);
  if (s && s.defaultProps) for (l in e = s.defaultProps, e) r[l] === void 0 && (r[l] = e[l]);
  return {
    $$typeof: X,
    type: s,
    key: t,
    ref: n,
    props: r,
    _owner: te.current
  };
}
g.Fragment = $;
g.jsx = F;
g.jsxs = F;
O.exports = g;
var se = O.exports;
const {
  SvelteComponent: oe,
  assign: x,
  binding_callbacks: C,
  check_outros: re,
  children: T,
  claim_element: j,
  claim_space: le,
  component_subscribe: P,
  compute_slots: ie,
  create_slot: ce,
  detach: u,
  element: D,
  empty: R,
  exclude_internal_props: S,
  get_all_dirty_from_scope: ae,
  get_slot_changes: ue,
  group_outros: fe,
  init: _e,
  insert_hydration: p,
  safe_not_equal: de,
  set_custom_element_data: L,
  space: me,
  transition_in: w,
  transition_out: v,
  update_slot_base: pe
} = window.__gradio__svelte__internal, {
  beforeUpdate: we,
  getContext: ge,
  onDestroy: be,
  setContext: ve
} = window.__gradio__svelte__internal;
function E(s) {
  let e, o;
  const l = (
    /*#slots*/
    s[7].default
  ), r = ce(
    l,
    s,
    /*$$scope*/
    s[6],
    null
  );
  return {
    c() {
      e = D("svelte-slot"), r && r.c(), this.h();
    },
    l(t) {
      e = j(t, "SVELTE-SLOT", {
        class: !0
      });
      var n = T(e);
      r && r.l(n), n.forEach(u), this.h();
    },
    h() {
      L(e, "class", "svelte-1rt0kpf");
    },
    m(t, n) {
      p(t, e, n), r && r.m(e, null), s[9](e), o = !0;
    },
    p(t, n) {
      r && r.p && (!o || n & /*$$scope*/
      64) && pe(
        r,
        l,
        t,
        /*$$scope*/
        t[6],
        o ? ue(
          l,
          /*$$scope*/
          t[6],
          n,
          null
        ) : ae(
          /*$$scope*/
          t[6]
        ),
        null
      );
    },
    i(t) {
      o || (w(r, t), o = !0);
    },
    o(t) {
      v(r, t), o = !1;
    },
    d(t) {
      t && u(e), r && r.d(t), s[9](null);
    }
  };
}
function he(s) {
  let e, o, l, r, t = (
    /*$$slots*/
    s[4].default && E(s)
  );
  return {
    c() {
      e = D("react-portal-target"), o = me(), t && t.c(), l = R(), this.h();
    },
    l(n) {
      e = j(n, "REACT-PORTAL-TARGET", {
        class: !0
      }), T(e).forEach(u), o = le(n), t && t.l(n), l = R(), this.h();
    },
    h() {
      L(e, "class", "svelte-1rt0kpf");
    },
    m(n, c) {
      p(n, e, c), s[8](e), p(n, o, c), t && t.m(n, c), p(n, l, c), r = !0;
    },
    p(n, [c]) {
      /*$$slots*/
      n[4].default ? t ? (t.p(n, c), c & /*$$slots*/
      16 && w(t, 1)) : (t = E(n), t.c(), w(t, 1), t.m(l.parentNode, l)) : t && (fe(), v(t, 1, 1, () => {
        t = null;
      }), re());
    },
    i(n) {
      r || (w(t), r = !0);
    },
    o(n) {
      v(t), r = !1;
    },
    d(n) {
      n && (u(e), u(o), u(l)), s[8](null), t && t.d(n);
    }
  };
}
function k(s) {
  const {
    svelteInit: e,
    ...o
  } = s;
  return o;
}
function ye(s, e, o) {
  let l, r, {
    $$slots: t = {},
    $$scope: n
  } = e;
  const c = ie(t);
  let {
    svelteInit: a
  } = e;
  const f = m(k(e)), _ = m();
  P(s, _, (i) => o(0, l = i));
  const d = m();
  P(s, d, (i) => o(1, r = i));
  const h = [], z = ge("$$ms-gr-react-wrapper"), {
    slotKey: A,
    slotIndex: M,
    subSlotIndex: N
  } = V() || {}, W = a({
    parent: z,
    props: f,
    target: _,
    slot: d,
    slotKey: A,
    slotIndex: M,
    subSlotIndex: N,
    onDestroy(i) {
      h.push(i);
    }
  });
  ve("$$ms-gr-react-wrapper", W), we(() => {
    f.set(k(e));
  }), be(() => {
    h.forEach((i) => i());
  });
  function q(i) {
    C[i ? "unshift" : "push"](() => {
      l = i, _.set(l);
    });
  }
  function K(i) {
    C[i ? "unshift" : "push"](() => {
      r = i, d.set(r);
    });
  }
  return s.$$set = (i) => {
    o(17, e = x(x({}, e), S(i))), "svelteInit" in i && o(5, a = i.svelteInit), "$$scope" in i && o(6, n = i.$$scope);
  }, e = S(e), [l, r, _, d, c, a, n, t, q, K];
}
class xe extends oe {
  constructor(e) {
    super(), _e(this, e, ye, he, de, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ke
} = window.__gradio__svelte__internal, I = window.ms_globals.rerender, b = window.ms_globals.tree;
function Ce(s, e = {}) {
  function o(l) {
    const r = m(), t = new xe({
      ...l,
      props: {
        svelteInit(n) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: s,
            props: n.props,
            slot: n.slot,
            target: n.target,
            slotIndex: n.slotIndex,
            subSlotIndex: n.subSlotIndex,
            ignore: e.ignore,
            slotKey: n.slotKey,
            nodes: []
          }, a = n.parent ?? b;
          return a.nodes = [...a.nodes, c], I({
            createPortal: y,
            node: b
          }), n.onDestroy(() => {
            a.nodes = a.nodes.filter((f) => f.svelteInstance !== r), I({
              createPortal: y,
              node: b
            });
          }), c;
        },
        ...l.props
      }
    });
    return r.set(t), t;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((r) => {
      window.ms_globals.initialize = () => {
        r();
      };
    })), window.ms_globals.initializePromise.then(() => {
      l(o);
    });
  });
}
function Pe(s) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(s.trim());
}
function Re(s, e = !1) {
  try {
    if (Y(s))
      return s;
    if (e && !Pe(s))
      return;
    if (typeof s == "string") {
      let o = s.trim();
      return o.startsWith(";") && (o = o.slice(1)), o.endsWith(";") && (o = o.slice(0, -1)), new Function(`return (...args) => (${o})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function Se(s, e) {
  return B(() => Re(s, e), [s, e]);
}
const Ie = Ce(({
  children: s,
  paramsMapping: e,
  asItem: o
}) => {
  const l = Se(e), [r, t] = G(void 0), {
    forceClone: n,
    ctx: c
  } = Z();
  return J(() => {
    l ? t(l(c)) : o && t(c == null ? void 0 : c[o]);
  }, [o, c, l]), /* @__PURE__ */ se.jsx(H, {
    forceClone: n,
    ctx: r,
    mergeContext: !1,
    children: s
  });
});
export {
  Ie as Filter,
  Ie as default
};
