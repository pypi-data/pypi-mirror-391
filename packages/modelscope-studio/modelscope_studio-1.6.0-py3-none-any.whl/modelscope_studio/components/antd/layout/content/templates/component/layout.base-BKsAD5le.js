import { Z as p, g as H, c as J } from "./Index-CqdDFMhv.js";
const W = window.ms_globals.React, G = window.ms_globals.React.useMemo, I = window.ms_globals.ReactDOM.createPortal, _ = window.ms_globals.antd.Layout;
var L = {
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
var V = W, Y = Symbol.for("react.element"), Z = Symbol.for("react.fragment"), Q = Object.prototype.hasOwnProperty, X = V.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, $ = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(r, t, l) {
  var n, o = {}, e = null, s = null;
  l !== void 0 && (e = "" + l), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) Q.call(t, n) && !$.hasOwnProperty(n) && (o[n] = t[n]);
  if (r && r.defaultProps) for (n in t = r.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: Y,
    type: r,
    key: e,
    ref: s,
    props: o,
    _owner: X.current
  };
}
b.Fragment = Z;
b.jsx = T;
b.jsxs = T;
L.exports = b;
var ee = L.exports;
const {
  SvelteComponent: te,
  assign: k,
  binding_callbacks: R,
  check_outros: se,
  children: j,
  claim_element: D,
  claim_space: oe,
  component_subscribe: S,
  compute_slots: ne,
  create_slot: re,
  detach: c,
  element: N,
  empty: E,
  exclude_internal_props: P,
  get_all_dirty_from_scope: le,
  get_slot_changes: ae,
  group_outros: ie,
  init: ue,
  insert_hydration: w,
  safe_not_equal: ce,
  set_custom_element_data: z,
  space: _e,
  transition_in: g,
  transition_out: h,
  update_slot_base: fe
} = window.__gradio__svelte__internal, {
  beforeUpdate: de,
  getContext: me,
  onDestroy: pe,
  setContext: we
} = window.__gradio__svelte__internal;
function x(r) {
  let t, l;
  const n = (
    /*#slots*/
    r[7].default
  ), o = re(
    n,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      t = N("svelte-slot"), o && o.c(), this.h();
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
      w(e, t, s), o && o.m(t, null), r[9](t), l = !0;
    },
    p(e, s) {
      o && o.p && (!l || s & /*$$scope*/
      64) && fe(
        o,
        n,
        e,
        /*$$scope*/
        e[6],
        l ? ae(
          n,
          /*$$scope*/
          e[6],
          s,
          null
        ) : le(
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
      h(o, e), l = !1;
    },
    d(e) {
      e && c(t), o && o.d(e), r[9](null);
    }
  };
}
function ge(r) {
  let t, l, n, o, e = (
    /*$$slots*/
    r[4].default && x(r)
  );
  return {
    c() {
      t = N("react-portal-target"), l = _e(), e && e.c(), n = E(), this.h();
    },
    l(s) {
      t = D(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(c), l = oe(s), e && e.l(s), n = E(), this.h();
    },
    h() {
      z(t, "class", "svelte-1rt0kpf");
    },
    m(s, i) {
      w(s, t, i), r[8](t), w(s, l, i), e && e.m(s, i), w(s, n, i), o = !0;
    },
    p(s, [i]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, i), i & /*$$slots*/
      16 && g(e, 1)) : (e = x(s), e.c(), g(e, 1), e.m(n.parentNode, n)) : e && (ie(), h(e, 1, 1, () => {
        e = null;
      }), se());
    },
    i(s) {
      o || (g(e), o = !0);
    },
    o(s) {
      h(e), o = !1;
    },
    d(s) {
      s && (c(t), c(l), c(n)), r[8](null), e && e.d(s);
    }
  };
}
function C(r) {
  const {
    svelteInit: t,
    ...l
  } = r;
  return l;
}
function be(r, t, l) {
  let n, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const i = ne(e);
  let {
    svelteInit: u
  } = t;
  const f = p(C(t)), d = p();
  S(r, d, (a) => l(0, n = a));
  const m = p();
  S(r, m, (a) => l(1, o = a));
  const v = [], A = me("$$ms-gr-react-wrapper"), {
    slotKey: q,
    slotIndex: F,
    subSlotIndex: K
  } = H() || {}, M = u({
    parent: A,
    props: f,
    target: d,
    slot: m,
    slotKey: q,
    slotIndex: F,
    subSlotIndex: K,
    onDestroy(a) {
      v.push(a);
    }
  });
  we("$$ms-gr-react-wrapper", M), de(() => {
    f.set(C(t));
  }), pe(() => {
    v.forEach((a) => a());
  });
  function U(a) {
    R[a ? "unshift" : "push"](() => {
      n = a, d.set(n);
    });
  }
  function B(a) {
    R[a ? "unshift" : "push"](() => {
      o = a, m.set(o);
    });
  }
  return r.$$set = (a) => {
    l(17, t = k(k({}, t), P(a))), "svelteInit" in a && l(5, u = a.svelteInit), "$$scope" in a && l(6, s = a.$$scope);
  }, t = P(t), [n, o, d, m, i, u, s, e, U, B];
}
class ye extends te {
  constructor(t) {
    super(), ue(this, t, be, ge, ce, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Ie
} = window.__gradio__svelte__internal, O = window.ms_globals.rerender, y = window.ms_globals.tree;
function he(r, t = {}) {
  function l(n) {
    const o = p(), e = new ye({
      ...n,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const i = {
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
          }, u = s.parent ?? y;
          return u.nodes = [...u.nodes, i], O({
            createPortal: I,
            node: y
          }), s.onDestroy(() => {
            u.nodes = u.nodes.filter((f) => f.svelteInstance !== o), O({
              createPortal: I,
              node: y
            });
          }), i;
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
const ke = he(({
  component: r,
  className: t,
  ...l
}) => {
  const n = G(() => {
    switch (r) {
      case "content":
        return _.Content;
      case "footer":
        return _.Footer;
      case "header":
        return _.Header;
      case "layout":
        return _;
      default:
        return _;
    }
  }, [r]);
  return /* @__PURE__ */ ee.jsx(n, {
    ...l,
    className: J(t, r === "layout" ? null : `ms-gr-antd-layout-${r}`)
  });
});
export {
  ke as Base,
  ke as default
};
