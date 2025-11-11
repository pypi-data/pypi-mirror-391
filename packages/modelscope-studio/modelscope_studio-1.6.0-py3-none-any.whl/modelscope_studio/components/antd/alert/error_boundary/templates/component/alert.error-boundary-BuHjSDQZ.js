import { i as ie, a as j, r as le, Z as R, g as ae } from "./Index-CJ_rdyww.js";
const y = window.ms_globals.React, ne = window.ms_globals.React.forwardRef, re = window.ms_globals.React.useRef, oe = window.ms_globals.React.useState, se = window.ms_globals.React.useEffect, N = window.ms_globals.ReactDOM.createPortal, ce = window.ms_globals.internalContext.useContextPropsContext, ue = window.ms_globals.antd.Alert;
var de = /\s/;
function fe(e) {
  for (var t = e.length; t-- && de.test(e.charAt(t)); )
    ;
  return t;
}
var me = /^\s+/;
function pe(e) {
  return e && e.slice(0, fe(e) + 1).replace(me, "");
}
var F = NaN, _e = /^[-+]0x[0-9a-f]+$/i, ge = /^0b[01]+$/i, he = /^0o[0-7]+$/i, we = parseInt;
function M(e) {
  if (typeof e == "number")
    return e;
  if (ie(e))
    return F;
  if (j(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = j(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = pe(e);
  var o = ge.test(e);
  return o || he.test(e) ? we(e.slice(2), o ? 2 : 8) : _e.test(e) ? F : +e;
}
var L = function() {
  return le.Date.now();
}, be = "Expected a function", ye = Math.max, Ee = Math.min;
function ve(e, t, o) {
  var i, s, n, r, l, d, _ = 0, g = !1, a = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(be);
  t = M(t) || 0, j(o) && (g = !!o.leading, a = "maxWait" in o, n = a ? ye(M(o.maxWait) || 0, t) : n, h = "trailing" in o ? !!o.trailing : h);
  function m(u) {
    var b = i, S = s;
    return i = s = void 0, _ = u, r = e.apply(S, b), r;
  }
  function E(u) {
    return _ = u, l = setTimeout(p, t), g ? m(u) : r;
  }
  function v(u) {
    var b = u - d, S = u - _, D = t - b;
    return a ? Ee(D, n - S) : D;
  }
  function f(u) {
    var b = u - d, S = u - _;
    return d === void 0 || b >= t || b < 0 || a && S >= n;
  }
  function p() {
    var u = L();
    if (f(u))
      return w(u);
    l = setTimeout(p, v(u));
  }
  function w(u) {
    return l = void 0, h && i ? m(u) : (i = s = void 0, r);
  }
  function I() {
    l !== void 0 && clearTimeout(l), _ = 0, i = d = s = l = void 0;
  }
  function c() {
    return l === void 0 ? r : w(L());
  }
  function x() {
    var u = L(), b = f(u);
    if (i = arguments, s = this, d = u, b) {
      if (l === void 0)
        return E(d);
      if (a)
        return clearTimeout(l), l = setTimeout(p, t), m(d);
    }
    return l === void 0 && (l = setTimeout(p, t)), r;
  }
  return x.cancel = I, x.flush = c, x;
}
var Y = {
  exports: {}
}, P = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var xe = y, Ce = Symbol.for("react.element"), Ie = Symbol.for("react.fragment"), Se = Object.prototype.hasOwnProperty, Te = xe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Re = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Z(e, t, o) {
  var i, s = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) Se.call(t, i) && !Re.hasOwnProperty(i) && (s[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) s[i] === void 0 && (s[i] = t[i]);
  return {
    $$typeof: Ce,
    type: e,
    key: n,
    ref: r,
    props: s,
    _owner: Te.current
  };
}
P.Fragment = Ie;
P.jsx = Z;
P.jsxs = Z;
Y.exports = P;
var T = Y.exports;
const {
  SvelteComponent: Oe,
  assign: B,
  binding_callbacks: U,
  check_outros: ke,
  children: Q,
  claim_element: $,
  claim_space: Pe,
  component_subscribe: G,
  compute_slots: Le,
  create_slot: Ae,
  detach: C,
  element: ee,
  empty: H,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Ne,
  get_slot_changes: je,
  group_outros: We,
  init: ze,
  insert_hydration: O,
  safe_not_equal: De,
  set_custom_element_data: te,
  space: Fe,
  transition_in: k,
  transition_out: W,
  update_slot_base: Me
} = window.__gradio__svelte__internal, {
  beforeUpdate: Be,
  getContext: Ue,
  onDestroy: Ge,
  setContext: He
} = window.__gradio__svelte__internal;
function q(e) {
  let t, o;
  const i = (
    /*#slots*/
    e[7].default
  ), s = Ae(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ee("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      t = $(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = Q(t);
      s && s.l(r), r.forEach(C), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), s && s.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      s && s.p && (!o || r & /*$$scope*/
      64) && Me(
        s,
        i,
        n,
        /*$$scope*/
        n[6],
        o ? je(
          i,
          /*$$scope*/
          n[6],
          r,
          null
        ) : Ne(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (k(s, n), o = !0);
    },
    o(n) {
      W(s, n), o = !1;
    },
    d(n) {
      n && C(t), s && s.d(n), e[9](null);
    }
  };
}
function Ke(e) {
  let t, o, i, s, n = (
    /*$$slots*/
    e[4].default && q(e)
  );
  return {
    c() {
      t = ee("react-portal-target"), o = Fe(), n && n.c(), i = H(), this.h();
    },
    l(r) {
      t = $(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), Q(t).forEach(C), o = Pe(r), n && n.l(r), i = H(), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      O(r, t, l), e[8](t), O(r, o, l), n && n.m(r, l), O(r, i, l), s = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = q(r), n.c(), k(n, 1), n.m(i.parentNode, i)) : n && (We(), W(n, 1, 1, () => {
        n = null;
      }), ke());
    },
    i(r) {
      s || (k(n), s = !0);
    },
    o(r) {
      W(n), s = !1;
    },
    d(r) {
      r && (C(t), C(o), C(i)), e[8](null), n && n.d(r);
    }
  };
}
function V(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function qe(e, t, o) {
  let i, s, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Le(n);
  let {
    svelteInit: d
  } = t;
  const _ = R(V(t)), g = R();
  G(e, g, (c) => o(0, i = c));
  const a = R();
  G(e, a, (c) => o(1, s = c));
  const h = [], m = Ue("$$ms-gr-react-wrapper"), {
    slotKey: E,
    slotIndex: v,
    subSlotIndex: f
  } = ae() || {}, p = d({
    parent: m,
    props: _,
    target: g,
    slot: a,
    slotKey: E,
    slotIndex: v,
    subSlotIndex: f,
    onDestroy(c) {
      h.push(c);
    }
  });
  He("$$ms-gr-react-wrapper", p), Be(() => {
    _.set(V(t));
  }), Ge(() => {
    h.forEach((c) => c());
  });
  function w(c) {
    U[c ? "unshift" : "push"](() => {
      i = c, g.set(i);
    });
  }
  function I(c) {
    U[c ? "unshift" : "push"](() => {
      s = c, a.set(s);
    });
  }
  return e.$$set = (c) => {
    o(17, t = B(B({}, t), K(c))), "svelteInit" in c && o(5, d = c.svelteInit), "$$scope" in c && o(6, r = c.$$scope);
  }, t = K(t), [i, s, g, a, l, d, r, n, w, I];
}
class Ve extends Oe {
  constructor(t) {
    super(), ze(this, t, qe, Ke, De, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: et
} = window.__gradio__svelte__internal, J = window.ms_globals.rerender, A = window.ms_globals.tree;
function Je(e, t = {}) {
  function o(i) {
    const s = R(), n = new Ve({
      ...i,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, d = r.parent ?? A;
          return d.nodes = [...d.nodes, l], J({
            createPortal: N,
            node: A
          }), r.onDestroy(() => {
            d.nodes = d.nodes.filter((_) => _.svelteInstance !== s), J({
              createPortal: N,
              node: A
            });
          }), l;
        },
        ...i.props
      }
    });
    return s.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((s) => {
      window.ms_globals.initialize = () => {
        s();
      };
    })), window.ms_globals.initializePromise.then(() => {
      i(o);
    });
  });
}
const Xe = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ye(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const i = e[o];
    return t[o] = Ze(o, i), t;
  }, {}) : {};
}
function Ze(e, t) {
  return typeof t == "number" && !Xe.includes(e) ? t + "px" : t;
}
function z(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const s = y.Children.toArray(e._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = z(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...y.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return s.originalChildren = e._reactElement.props.children, t.push(N(y.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: s
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((s) => {
    e.getEventListeners(s).forEach(({
      listener: r,
      type: l,
      useCapture: d
    }) => {
      o.addEventListener(l, r, d);
    });
  });
  const i = Array.from(e.childNodes);
  for (let s = 0; s < i.length; s++) {
    const n = i[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = z(n);
      t.push(...l), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function Qe(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const X = ne(({
  slot: e,
  clone: t,
  className: o,
  style: i,
  observeAttributes: s
}, n) => {
  const r = re(), [l, d] = oe([]), {
    forceClone: _
  } = ce(), g = _ ? !0 : t;
  return se(() => {
    var v;
    if (!r.current || !e)
      return;
    let a = e;
    function h() {
      let f = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (f = a.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), Qe(n, f), o && f.classList.add(...o.split(" ")), i) {
        const p = Ye(i);
        Object.keys(p).forEach((w) => {
          f.style[w] = p[w];
        });
      }
    }
    let m = null, E = null;
    if (g && window.MutationObserver) {
      let f = function() {
        var c, x, u;
        (c = r.current) != null && c.contains(a) && ((x = r.current) == null || x.removeChild(a));
        const {
          portals: w,
          clonedElement: I
        } = z(e);
        a = I, d(w), a.style.display = "contents", E && clearTimeout(E), E = setTimeout(() => {
          h();
        }, 50), (u = r.current) == null || u.appendChild(a);
      };
      f();
      const p = ve(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      m = new window.MutationObserver(p), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", h(), (v = r.current) == null || v.appendChild(a);
    return () => {
      var f, p;
      a.style.display = "", (f = r.current) != null && f.contains(a) && ((p = r.current) == null || p.removeChild(a)), m == null || m.disconnect();
    };
  }, [e, g, o, i, n, s, _]), y.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
}), tt = Je(({
  slots: e,
  children: t,
  ...o
}) => /* @__PURE__ */ T.jsxs(T.Fragment, {
  children: [/* @__PURE__ */ T.jsx("div", {
    style: {
      display: "none"
    },
    children: t
  }), y.createElement(ue.ErrorBoundary, {
    ...o,
    description: e.description ? /* @__PURE__ */ T.jsx(X, {
      slot: e.description
    }) : o.description,
    message: e.message ? /* @__PURE__ */ T.jsx(X, {
      slot: e.message
    }) : o.message
  })]
}));
export {
  tt as AlertErrorBoundary,
  tt as default
};
