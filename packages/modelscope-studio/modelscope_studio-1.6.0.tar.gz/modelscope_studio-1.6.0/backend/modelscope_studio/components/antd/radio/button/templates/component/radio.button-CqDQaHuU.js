import { Z as m, g as G } from "./Index-y09EcMN7.js";
const F = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal, J = window.ms_globals.antd.theme, M = window.ms_globals.antd.Radio;
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
var V = F, Y = Symbol.for("react.element"), Z = Symbol.for("react.fragment"), H = Object.prototype.hasOwnProperty, Q = V.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, X = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function C(l, t, r) {
  var n, o = {}, e = null, s = null;
  r !== void 0 && (e = "" + r), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) H.call(t, n) && !X.hasOwnProperty(n) && (o[n] = t[n]);
  if (l && l.defaultProps) for (n in t = l.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: Y,
    type: l,
    key: e,
    ref: s,
    props: o,
    _owner: Q.current
  };
}
g.Fragment = Z;
g.jsx = C;
g.jsxs = C;
T.exports = g;
var $ = T.exports;
const {
  SvelteComponent: ee,
  assign: k,
  binding_callbacks: I,
  check_outros: te,
  children: j,
  claim_element: D,
  claim_space: se,
  component_subscribe: R,
  compute_slots: oe,
  create_slot: ne,
  detach: c,
  element: L,
  empty: S,
  exclude_internal_props: E,
  get_all_dirty_from_scope: le,
  get_slot_changes: re,
  group_outros: ie,
  init: ae,
  insert_hydration: p,
  safe_not_equal: _e,
  set_custom_element_data: z,
  space: ce,
  transition_in: w,
  transition_out: h,
  update_slot_base: ue
} = window.__gradio__svelte__internal, {
  beforeUpdate: fe,
  getContext: de,
  onDestroy: me,
  setContext: pe
} = window.__gradio__svelte__internal;
function x(l) {
  let t, r;
  const n = (
    /*#slots*/
    l[7].default
  ), o = ne(
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
      64) && ue(
        o,
        n,
        e,
        /*$$scope*/
        e[6],
        r ? re(
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
      r || (w(o, e), r = !0);
    },
    o(e) {
      h(o, e), r = !1;
    },
    d(e) {
      e && c(t), o && o.d(e), l[9](null);
    }
  };
}
function we(l) {
  let t, r, n, o, e = (
    /*$$slots*/
    l[4].default && x(l)
  );
  return {
    c() {
      t = L("react-portal-target"), r = ce(), e && e.c(), n = S(), this.h();
    },
    l(s) {
      t = D(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(c), r = se(s), e && e.l(s), n = S(), this.h();
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
      16 && w(e, 1)) : (e = x(s), e.c(), w(e, 1), e.m(n.parentNode, n)) : e && (ie(), h(e, 1, 1, () => {
        e = null;
      }), te());
    },
    i(s) {
      o || (w(e), o = !0);
    },
    o(s) {
      h(e), o = !1;
    },
    d(s) {
      s && (c(t), c(r), c(n)), l[8](null), e && e.d(s);
    }
  };
}
function P(l) {
  const {
    svelteInit: t,
    ...r
  } = l;
  return r;
}
function ge(l, t, r) {
  let n, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const a = oe(e);
  let {
    svelteInit: _
  } = t;
  const u = m(P(t)), f = m();
  R(l, f, (i) => r(0, n = i));
  const d = m();
  R(l, d, (i) => r(1, o = i));
  const v = [], A = de("$$ms-gr-react-wrapper"), {
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
      v.push(i);
    }
  });
  pe("$$ms-gr-react-wrapper", U), fe(() => {
    u.set(P(t));
  }), me(() => {
    v.forEach((i) => i());
  });
  function W(i) {
    I[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function B(i) {
    I[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return l.$$set = (i) => {
    r(17, t = k(k({}, t), E(i))), "svelteInit" in i && r(5, _ = i.svelteInit), "$$scope" in i && r(6, s = i.$$scope);
  }, t = E(t), [n, o, f, d, a, _, s, e, W, B];
}
class be extends ee {
  constructor(t) {
    super(), ae(this, t, ge, we, _e, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ye
} = window.__gradio__svelte__internal, O = window.ms_globals.rerender, b = window.ms_globals.tree;
function he(l, t = {}) {
  function r(n) {
    const o = m(), e = new be({
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
const ke = he(({
  onValueChange: l,
  onChange: t,
  elRef: r,
  style: n,
  ...o
}) => {
  const {
    token: e
  } = J.useToken();
  return /* @__PURE__ */ $.jsx(M.Button, {
    ...o,
    style: {
      ...n,
      "--ms-gr-antd-line-width": e.lineWidth + "px"
    },
    ref: r,
    onChange: (s) => {
      t == null || t(s), l(s.target.checked);
    }
  });
});
export {
  ke as Radio,
  ke as default
};
