import { Z as m, g as G } from "./Index-BlZyqKln.js";
const B = window.ms_globals.React, h = window.ms_globals.ReactDOM.createPortal, J = window.ms_globals.antd.Form;
var T = {
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
var M = B, Y = Symbol.for("react.element"), Z = Symbol.for("react.fragment"), H = Object.prototype.hasOwnProperty, Q = M.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, X = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function j(r, s, n) {
  var l, o = {}, e = null, t = null;
  n !== void 0 && (e = "" + n), s.key !== void 0 && (e = "" + s.key), s.ref !== void 0 && (t = s.ref);
  for (l in s) H.call(s, l) && !X.hasOwnProperty(l) && (o[l] = s[l]);
  if (r && r.defaultProps) for (l in s = r.defaultProps, s) o[l] === void 0 && (o[l] = s[l]);
  return {
    $$typeof: Y,
    type: r,
    key: e,
    ref: t,
    props: o,
    _owner: Q.current
  };
}
g.Fragment = Z;
g.jsx = j;
g.jsxs = j;
T.exports = g;
var F = T.exports;
const {
  SvelteComponent: $,
  assign: k,
  binding_callbacks: I,
  check_outros: ee,
  children: C,
  claim_element: D,
  claim_space: te,
  component_subscribe: P,
  compute_slots: se,
  create_slot: oe,
  detach: c,
  element: L,
  empty: S,
  exclude_internal_props: E,
  get_all_dirty_from_scope: le,
  get_slot_changes: re,
  group_outros: ne,
  init: ie,
  insert_hydration: p,
  safe_not_equal: ae,
  set_custom_element_data: z,
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
function R(r) {
  let s, n;
  const l = (
    /*#slots*/
    r[7].default
  ), o = oe(
    l,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      s = L("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      s = D(e, "SVELTE-SLOT", {
        class: !0
      });
      var t = C(s);
      o && o.l(t), t.forEach(c), this.h();
    },
    h() {
      z(s, "class", "svelte-1rt0kpf");
    },
    m(e, t) {
      p(e, s, t), o && o.m(s, null), r[9](s), n = !0;
    },
    p(e, t) {
      o && o.p && (!n || t & /*$$scope*/
      64) && ce(
        o,
        l,
        e,
        /*$$scope*/
        e[6],
        n ? re(
          l,
          /*$$scope*/
          e[6],
          t,
          null
        ) : le(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      n || (w(o, e), n = !0);
    },
    o(e) {
      v(o, e), n = !1;
    },
    d(e) {
      e && c(s), o && o.d(e), r[9](null);
    }
  };
}
function pe(r) {
  let s, n, l, o, e = (
    /*$$slots*/
    r[4].default && R(r)
  );
  return {
    c() {
      s = L("react-portal-target"), n = _e(), e && e.c(), l = S(), this.h();
    },
    l(t) {
      s = D(t, "REACT-PORTAL-TARGET", {
        class: !0
      }), C(s).forEach(c), n = te(t), e && e.l(t), l = S(), this.h();
    },
    h() {
      z(s, "class", "svelte-1rt0kpf");
    },
    m(t, a) {
      p(t, s, a), r[8](s), p(t, n, a), e && e.m(t, a), p(t, l, a), o = !0;
    },
    p(t, [a]) {
      /*$$slots*/
      t[4].default ? e ? (e.p(t, a), a & /*$$slots*/
      16 && w(e, 1)) : (e = R(t), e.c(), w(e, 1), e.m(l.parentNode, l)) : e && (ne(), v(e, 1, 1, () => {
        e = null;
      }), ee());
    },
    i(t) {
      o || (w(e), o = !0);
    },
    o(t) {
      v(e), o = !1;
    },
    d(t) {
      t && (c(s), c(n), c(l)), r[8](null), e && e.d(t);
    }
  };
}
function O(r) {
  const {
    svelteInit: s,
    ...n
  } = r;
  return n;
}
function we(r, s, n) {
  let l, o, {
    $$slots: e = {},
    $$scope: t
  } = s;
  const a = se(e);
  let {
    svelteInit: _
  } = s;
  const u = m(O(s)), f = m();
  P(r, f, (i) => n(0, l = i));
  const d = m();
  P(r, d, (i) => n(1, o = i));
  const y = [], A = fe("$$ms-gr-react-wrapper"), {
    slotKey: N,
    slotIndex: q,
    subSlotIndex: K
  } = G() || {}, U = _({
    parent: A,
    props: u,
    target: f,
    slot: d,
    slotKey: N,
    slotIndex: q,
    subSlotIndex: K,
    onDestroy(i) {
      y.push(i);
    }
  });
  me("$$ms-gr-react-wrapper", U), ue(() => {
    u.set(O(s));
  }), de(() => {
    y.forEach((i) => i());
  });
  function V(i) {
    I[i ? "unshift" : "push"](() => {
      l = i, f.set(l);
    });
  }
  function W(i) {
    I[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return r.$$set = (i) => {
    n(17, s = k(k({}, s), E(i))), "svelteInit" in i && n(5, _ = i.svelteInit), "$$scope" in i && n(6, t = i.$$scope);
  }, s = E(s), [l, o, f, d, a, _, t, e, V, W];
}
class ge extends $ {
  constructor(s) {
    super(), ie(this, s, we, pe, ae, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ye
} = window.__gradio__svelte__internal, x = window.ms_globals.rerender, b = window.ms_globals.tree;
function be(r, s = {}) {
  function n(l) {
    const o = m(), e = new ge({
      ...l,
      props: {
        svelteInit(t) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: r,
            props: t.props,
            slot: t.slot,
            target: t.target,
            slotIndex: t.slotIndex,
            subSlotIndex: t.subSlotIndex,
            ignore: s.ignore,
            slotKey: t.slotKey,
            nodes: []
          }, _ = t.parent ?? b;
          return _.nodes = [..._.nodes, a], x({
            createPortal: h,
            node: b
          }), t.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== o), x({
              createPortal: h,
              node: b
            });
          }), a;
        },
        ...l.props
      }
    });
    return o.set(e), e;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      l(n);
    });
  });
}
const he = be(({
  onFormChange: r,
  onFormFinish: s,
  ...n
}) => /* @__PURE__ */ F.jsx(J.Provider, {
  ...n,
  onFormChange: (l, o) => {
    r == null || r(l, {
      ...o,
      forms: Object.keys(o.forms).reduce((e, t) => ({
        ...e,
        [t]: o.forms[t].getFieldsValue()
      }), {})
    });
  },
  onFormFinish: (l, o) => {
    s == null || s(l, {
      ...o,
      forms: Object.keys(o.forms).reduce((e, t) => ({
        ...e,
        [t]: o.forms[t].getFieldsValue()
      }), {})
    });
  }
}));
export {
  he as FormProvider,
  he as default
};
