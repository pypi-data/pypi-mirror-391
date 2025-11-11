import { Z as m, g as F } from "./Index-DYqvMLKQ.js";
const W = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal, J = window.ms_globals.antd.theme, M = window.ms_globals.antd.Button;
var C = {
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
var V = W, Y = Symbol.for("react.element"), Z = Symbol.for("react.fragment"), H = Object.prototype.hasOwnProperty, Q = V.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, X = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(l, t, r) {
  var n, s = {}, e = null, o = null;
  r !== void 0 && (e = "" + r), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (n in t) H.call(t, n) && !X.hasOwnProperty(n) && (s[n] = t[n]);
  if (l && l.defaultProps) for (n in t = l.defaultProps, t) s[n] === void 0 && (s[n] = t[n]);
  return {
    $$typeof: Y,
    type: l,
    key: e,
    ref: o,
    props: s,
    _owner: Q.current
  };
}
g.Fragment = Z;
g.jsx = T;
g.jsxs = T;
C.exports = g;
var $ = C.exports;
const {
  SvelteComponent: ee,
  assign: k,
  binding_callbacks: I,
  check_outros: te,
  children: j,
  claim_element: D,
  claim_space: oe,
  component_subscribe: S,
  compute_slots: se,
  create_slot: ne,
  detach: c,
  element: L,
  empty: E,
  exclude_internal_props: R,
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
  ), s = ne(
    n,
    l,
    /*$$scope*/
    l[6],
    null
  );
  return {
    c() {
      t = L("svelte-slot"), s && s.c(), this.h();
    },
    l(e) {
      t = D(e, "SVELTE-SLOT", {
        class: !0
      });
      var o = j(t);
      s && s.l(o), o.forEach(c), this.h();
    },
    h() {
      z(t, "class", "svelte-1rt0kpf");
    },
    m(e, o) {
      p(e, t, o), s && s.m(t, null), l[9](t), r = !0;
    },
    p(e, o) {
      s && s.p && (!r || o & /*$$scope*/
      64) && ue(
        s,
        n,
        e,
        /*$$scope*/
        e[6],
        r ? re(
          n,
          /*$$scope*/
          e[6],
          o,
          null
        ) : le(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      r || (w(s, e), r = !0);
    },
    o(e) {
      h(s, e), r = !1;
    },
    d(e) {
      e && c(t), s && s.d(e), l[9](null);
    }
  };
}
function we(l) {
  let t, r, n, s, e = (
    /*$$slots*/
    l[4].default && x(l)
  );
  return {
    c() {
      t = L("react-portal-target"), r = ce(), e && e.c(), n = E(), this.h();
    },
    l(o) {
      t = D(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(c), r = oe(o), e && e.l(o), n = E(), this.h();
    },
    h() {
      z(t, "class", "svelte-1rt0kpf");
    },
    m(o, a) {
      p(o, t, a), l[8](t), p(o, r, a), e && e.m(o, a), p(o, n, a), s = !0;
    },
    p(o, [a]) {
      /*$$slots*/
      o[4].default ? e ? (e.p(o, a), a & /*$$slots*/
      16 && w(e, 1)) : (e = x(o), e.c(), w(e, 1), e.m(n.parentNode, n)) : e && (ie(), h(e, 1, 1, () => {
        e = null;
      }), te());
    },
    i(o) {
      s || (w(e), s = !0);
    },
    o(o) {
      h(e), s = !1;
    },
    d(o) {
      o && (c(t), c(r), c(n)), l[8](null), e && e.d(o);
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
  let n, s, {
    $$slots: e = {},
    $$scope: o
  } = t;
  const a = se(e);
  let {
    svelteInit: _
  } = t;
  const u = m(P(t)), f = m();
  S(l, f, (i) => r(0, n = i));
  const d = m();
  S(l, d, (i) => r(1, s = i));
  const v = [], A = de("$$ms-gr-react-wrapper"), {
    slotKey: B,
    slotIndex: N,
    subSlotIndex: q
  } = F() || {}, G = _({
    parent: A,
    props: u,
    target: f,
    slot: d,
    slotKey: B,
    slotIndex: N,
    subSlotIndex: q,
    onDestroy(i) {
      v.push(i);
    }
  });
  pe("$$ms-gr-react-wrapper", G), fe(() => {
    u.set(P(t));
  }), me(() => {
    v.forEach((i) => i());
  });
  function K(i) {
    I[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function U(i) {
    I[i ? "unshift" : "push"](() => {
      s = i, d.set(s);
    });
  }
  return l.$$set = (i) => {
    r(17, t = k(k({}, t), R(i))), "svelteInit" in i && r(5, _ = i.svelteInit), "$$scope" in i && r(6, o = i.$$scope);
  }, t = R(t), [n, s, f, d, a, _, o, e, K, U];
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
    const s = m(), e = new be({
      ...n,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: l,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, _ = o.parent ?? b;
          return _.nodes = [..._.nodes, a], O({
            createPortal: y,
            node: b
          }), o.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== s), O({
              createPortal: y,
              node: b
            });
          }), a;
        },
        ...n.props
      }
    });
    return s.set(e), e;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((s) => {
      window.ms_globals.initialize = () => {
        s();
      };
    })), window.ms_globals.initializePromise.then(() => {
      n(r);
    });
  });
}
const ke = he(({
  style: l,
  ...t
}) => {
  const {
    token: r
  } = J.useToken();
  return /* @__PURE__ */ $.jsx(M.Group, {
    ...t,
    style: {
      ...l,
      "--ms-gr-antd-line-width": r.lineWidth + "px"
    }
  });
});
export {
  ke as ButtonGroup,
  ke as default
};
