import { i as se, a as W, r as le, Z as R, g as ae } from "./Index-0aRxzgKl.js";
const E = window.ms_globals.React, ne = window.ms_globals.React.forwardRef, re = window.ms_globals.React.useRef, oe = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, A = window.ms_globals.ReactDOM.createPortal, ce = window.ms_globals.internalContext.useContextPropsContext, ue = window.ms_globals.antd.Statistic;
var de = /\s/;
function fe(e) {
  for (var t = e.length; t-- && de.test(e.charAt(t)); )
    ;
  return t;
}
var me = /^\s+/;
function _e(e) {
  return e && e.slice(0, fe(e) + 1).replace(me, "");
}
var M = NaN, pe = /^[-+]0x[0-9a-f]+$/i, he = /^0b[01]+$/i, ge = /^0o[0-7]+$/i, we = parseInt;
function U(e) {
  if (typeof e == "number")
    return e;
  if (se(e))
    return M;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = _e(e);
  var o = he.test(e);
  return o || ge.test(e) ? we(e.slice(2), o ? 2 : 8) : pe.test(e) ? M : +e;
}
var L = function() {
  return le.Date.now();
}, be = "Expected a function", xe = Math.max, ye = Math.min;
function Ee(e, t, o) {
  var s, i, n, r, l, d, p = 0, h = !1, a = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(be);
  t = U(t) || 0, W(o) && (h = !!o.leading, a = "maxWait" in o, n = a ? xe(U(o.maxWait) || 0, t) : n, g = "trailing" in o ? !!o.trailing : g);
  function m(u) {
    var b = s, T = i;
    return s = i = void 0, p = u, r = e.apply(T, b), r;
  }
  function x(u) {
    return p = u, l = setTimeout(_, t), h ? m(u) : r;
  }
  function v(u) {
    var b = u - d, T = u - p, F = t - b;
    return a ? ye(F, n - T) : F;
  }
  function f(u) {
    var b = u - d, T = u - p;
    return d === void 0 || b >= t || b < 0 || a && T >= n;
  }
  function _() {
    var u = L();
    if (f(u))
      return w(u);
    l = setTimeout(_, v(u));
  }
  function w(u) {
    return l = void 0, g && s ? m(u) : (s = i = void 0, r);
  }
  function S() {
    l !== void 0 && clearTimeout(l), p = 0, s = d = i = l = void 0;
  }
  function c() {
    return l === void 0 ? r : w(L());
  }
  function C() {
    var u = L(), b = f(u);
    if (s = arguments, i = this, d = u, b) {
      if (l === void 0)
        return x(d);
      if (a)
        return clearTimeout(l), l = setTimeout(_, t), m(d);
    }
    return l === void 0 && (l = setTimeout(_, t)), r;
  }
  return C.cancel = S, C.flush = c, C;
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
var ve = E, Ce = Symbol.for("react.element"), Ie = Symbol.for("react.fragment"), Se = Object.prototype.hasOwnProperty, Te = ve.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Re = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Z(e, t, o) {
  var s, i = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) Se.call(t, s) && !Re.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: Ce,
    type: e,
    key: n,
    ref: r,
    props: i,
    _owner: Te.current
  };
}
P.Fragment = Ie;
P.jsx = Z;
P.jsxs = Z;
Y.exports = P;
var y = Y.exports;
const {
  SvelteComponent: Oe,
  assign: B,
  binding_callbacks: G,
  check_outros: ke,
  children: Q,
  claim_element: $,
  claim_space: Pe,
  component_subscribe: H,
  compute_slots: Le,
  create_slot: je,
  detach: I,
  element: ee,
  empty: K,
  exclude_internal_props: q,
  get_all_dirty_from_scope: Ne,
  get_slot_changes: Ae,
  group_outros: We,
  init: ze,
  insert_hydration: O,
  safe_not_equal: De,
  set_custom_element_data: te,
  space: Fe,
  transition_in: k,
  transition_out: z,
  update_slot_base: Me
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ue,
  getContext: Be,
  onDestroy: Ge,
  setContext: He
} = window.__gradio__svelte__internal;
function V(e) {
  let t, o;
  const s = (
    /*#slots*/
    e[7].default
  ), i = je(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ee("svelte-slot"), i && i.c(), this.h();
    },
    l(n) {
      t = $(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = Q(t);
      i && i.l(r), r.forEach(I), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), i && i.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      i && i.p && (!o || r & /*$$scope*/
      64) && Me(
        i,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Ae(
          s,
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
      o || (k(i, n), o = !0);
    },
    o(n) {
      z(i, n), o = !1;
    },
    d(n) {
      n && I(t), i && i.d(n), e[9](null);
    }
  };
}
function Ke(e) {
  let t, o, s, i, n = (
    /*$$slots*/
    e[4].default && V(e)
  );
  return {
    c() {
      t = ee("react-portal-target"), o = Fe(), n && n.c(), s = K(), this.h();
    },
    l(r) {
      t = $(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), Q(t).forEach(I), o = Pe(r), n && n.l(r), s = K(), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      O(r, t, l), e[8](t), O(r, o, l), n && n.m(r, l), O(r, s, l), i = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = V(r), n.c(), k(n, 1), n.m(s.parentNode, s)) : n && (We(), z(n, 1, 1, () => {
        n = null;
      }), ke());
    },
    i(r) {
      i || (k(n), i = !0);
    },
    o(r) {
      z(n), i = !1;
    },
    d(r) {
      r && (I(t), I(o), I(s)), e[8](null), n && n.d(r);
    }
  };
}
function J(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function qe(e, t, o) {
  let s, i, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Le(n);
  let {
    svelteInit: d
  } = t;
  const p = R(J(t)), h = R();
  H(e, h, (c) => o(0, s = c));
  const a = R();
  H(e, a, (c) => o(1, i = c));
  const g = [], m = Be("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: v,
    subSlotIndex: f
  } = ae() || {}, _ = d({
    parent: m,
    props: p,
    target: h,
    slot: a,
    slotKey: x,
    slotIndex: v,
    subSlotIndex: f,
    onDestroy(c) {
      g.push(c);
    }
  });
  He("$$ms-gr-react-wrapper", _), Ue(() => {
    p.set(J(t));
  }), Ge(() => {
    g.forEach((c) => c());
  });
  function w(c) {
    G[c ? "unshift" : "push"](() => {
      s = c, h.set(s);
    });
  }
  function S(c) {
    G[c ? "unshift" : "push"](() => {
      i = c, a.set(i);
    });
  }
  return e.$$set = (c) => {
    o(17, t = B(B({}, t), q(c))), "svelteInit" in c && o(5, d = c.svelteInit), "$$scope" in c && o(6, r = c.$$scope);
  }, t = q(t), [s, i, h, a, l, d, r, n, w, S];
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
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, j = window.ms_globals.tree;
function Je(e, t = {}) {
  function o(s) {
    const i = R(), n = new Ve({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, d = r.parent ?? j;
          return d.nodes = [...d.nodes, l], X({
            createPortal: A,
            node: j
          }), r.onDestroy(() => {
            d.nodes = d.nodes.filter((p) => p.svelteInstance !== i), X({
              createPortal: A,
              node: j
            });
          }), l;
        },
        ...s.props
      }
    });
    return i.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((i) => {
      window.ms_globals.initialize = () => {
        i();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(o);
    });
  });
}
const Xe = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ye(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const s = e[o];
    return t[o] = Ze(o, s), t;
  }, {}) : {};
}
function Ze(e, t) {
  return typeof t == "number" && !Xe.includes(e) ? t + "px" : t;
}
function D(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const i = E.Children.toArray(e._reactElement.props.children).map((n) => {
      if (E.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = D(n.props.el);
        return E.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...E.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(A(E.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: i
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((i) => {
    e.getEventListeners(i).forEach(({
      listener: r,
      type: l,
      useCapture: d
    }) => {
      o.addEventListener(l, r, d);
    });
  });
  const s = Array.from(e.childNodes);
  for (let i = 0; i < s.length; i++) {
    const n = s[i];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = D(n);
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
const N = ne(({
  slot: e,
  clone: t,
  className: o,
  style: s,
  observeAttributes: i
}, n) => {
  const r = re(), [l, d] = oe([]), {
    forceClone: p
  } = ce(), h = p ? !0 : t;
  return ie(() => {
    var v;
    if (!r.current || !e)
      return;
    let a = e;
    function g() {
      let f = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (f = a.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), Qe(n, f), o && f.classList.add(...o.split(" ")), s) {
        const _ = Ye(s);
        Object.keys(_).forEach((w) => {
          f.style[w] = _[w];
        });
      }
    }
    let m = null, x = null;
    if (h && window.MutationObserver) {
      let f = function() {
        var c, C, u;
        (c = r.current) != null && c.contains(a) && ((C = r.current) == null || C.removeChild(a));
        const {
          portals: w,
          clonedElement: S
        } = D(e);
        a = S, d(w), a.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          g();
        }, 50), (u = r.current) == null || u.appendChild(a);
      };
      f();
      const _ = Ee(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      m = new window.MutationObserver(_), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", g(), (v = r.current) == null || v.appendChild(a);
    return () => {
      var f, _;
      a.style.display = "", (f = r.current) != null && f.contains(a) && ((_ = r.current) == null || _.removeChild(a)), m == null || m.disconnect();
    };
  }, [e, h, o, s, n, i, p]), E.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
}), tt = Je(({
  children: e,
  value: t,
  slots: o,
  ...s
}) => /* @__PURE__ */ y.jsxs(y.Fragment, {
  children: [/* @__PURE__ */ y.jsx("div", {
    style: {
      display: "none"
    },
    children: e
  }), /* @__PURE__ */ y.jsx(ue.Timer, {
    ...s,
    value: typeof t == "number" ? t * 1e3 : t,
    title: o.title ? /* @__PURE__ */ y.jsx(N, {
      slot: o.title
    }) : s.title,
    prefix: o.prefix ? /* @__PURE__ */ y.jsx(N, {
      slot: o.prefix
    }) : s.prefix,
    suffix: o.suffix ? /* @__PURE__ */ y.jsx(N, {
      slot: o.suffix
    }) : s.suffix
  })]
}));
export {
  tt as StatisticTimer,
  tt as default
};
