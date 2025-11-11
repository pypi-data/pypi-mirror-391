import { i as le, a as W, r as ce, Z as k, g as ae, b as ue } from "./Index-CFqiE2cf.js";
const v = window.ms_globals.React, ne = window.ms_globals.React.forwardRef, re = window.ms_globals.React.useRef, oe = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, se = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, de = window.ms_globals.internalContext.useContextPropsContext, fe = window.ms_globals.antd.FloatButton;
var me = /\s/;
function _e(e) {
  for (var t = e.length; t-- && me.test(e.charAt(t)); )
    ;
  return t;
}
var pe = /^\s+/;
function ge(e) {
  return e && e.slice(0, _e(e) + 1).replace(pe, "");
}
var z = NaN, he = /^[-+]0x[0-9a-f]+$/i, we = /^0b[01]+$/i, be = /^0o[0-7]+$/i, ye = parseInt;
function D(e) {
  if (typeof e == "number")
    return e;
  if (le(e))
    return z;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ge(e);
  var o = we.test(e);
  return o || be.test(e) ? ye(e.slice(2), o ? 2 : 8) : he.test(e) ? z : +e;
}
var F = function() {
  return ce.Date.now();
}, Ee = "Expected a function", ve = Math.max, xe = Math.min;
function Ce(e, t, o) {
  var s, i, n, r, l, d, p = 0, g = !1, c = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(Ee);
  t = D(t) || 0, W(o) && (g = !!o.leading, c = "maxWait" in o, n = c ? ve(D(o.maxWait) || 0, t) : n, h = "trailing" in o ? !!o.trailing : h);
  function m(u) {
    var b = s, R = i;
    return s = i = void 0, p = u, r = e.apply(R, b), r;
  }
  function E(u) {
    return p = u, l = setTimeout(_, t), g ? m(u) : r;
  }
  function x(u) {
    var b = u - d, R = u - p, M = t - b;
    return c ? xe(M, n - R) : M;
  }
  function f(u) {
    var b = u - d, R = u - p;
    return d === void 0 || b >= t || b < 0 || c && R >= n;
  }
  function _() {
    var u = F();
    if (f(u))
      return w(u);
    l = setTimeout(_, x(u));
  }
  function w(u) {
    return l = void 0, h && s ? m(u) : (s = i = void 0, r);
  }
  function S() {
    l !== void 0 && clearTimeout(l), p = 0, s = d = i = l = void 0;
  }
  function a() {
    return l === void 0 ? r : w(F());
  }
  function C() {
    var u = F(), b = f(u);
    if (s = arguments, i = this, d = u, b) {
      if (l === void 0)
        return E(d);
      if (c)
        return clearTimeout(l), l = setTimeout(_, t), m(d);
    }
    return l === void 0 && (l = setTimeout(_, t)), r;
  }
  return C.cancel = S, C.flush = a, C;
}
var Y = {
  exports: {}
}, L = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ie = v, Se = Symbol.for("react.element"), Re = Symbol.for("react.fragment"), Te = Object.prototype.hasOwnProperty, ke = Ie.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Oe = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Z(e, t, o) {
  var s, i = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) Te.call(t, s) && !Oe.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: Se,
    type: e,
    key: n,
    ref: r,
    props: i,
    _owner: ke.current
  };
}
L.Fragment = Re;
L.jsx = Z;
L.jsxs = Z;
Y.exports = L;
var y = Y.exports;
const {
  SvelteComponent: Pe,
  assign: U,
  binding_callbacks: G,
  check_outros: Le,
  children: Q,
  claim_element: $,
  claim_space: Fe,
  component_subscribe: H,
  compute_slots: je,
  create_slot: Ne,
  detach: I,
  element: ee,
  empty: K,
  exclude_internal_props: q,
  get_all_dirty_from_scope: We,
  get_slot_changes: Ae,
  group_outros: Be,
  init: Me,
  insert_hydration: O,
  safe_not_equal: ze,
  set_custom_element_data: te,
  space: De,
  transition_in: P,
  transition_out: A,
  update_slot_base: Ue
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ge,
  getContext: He,
  onDestroy: Ke,
  setContext: qe
} = window.__gradio__svelte__internal;
function V(e) {
  let t, o;
  const s = (
    /*#slots*/
    e[7].default
  ), i = Ne(
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
      64) && Ue(
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
        ) : We(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (P(i, n), o = !0);
    },
    o(n) {
      A(i, n), o = !1;
    },
    d(n) {
      n && I(t), i && i.d(n), e[9](null);
    }
  };
}
function Ve(e) {
  let t, o, s, i, n = (
    /*$$slots*/
    e[4].default && V(e)
  );
  return {
    c() {
      t = ee("react-portal-target"), o = De(), n && n.c(), s = K(), this.h();
    },
    l(r) {
      t = $(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), Q(t).forEach(I), o = Fe(r), n && n.l(r), s = K(), this.h();
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
      16 && P(n, 1)) : (n = V(r), n.c(), P(n, 1), n.m(s.parentNode, s)) : n && (Be(), A(n, 1, 1, () => {
        n = null;
      }), Le());
    },
    i(r) {
      i || (P(n), i = !0);
    },
    o(r) {
      A(n), i = !1;
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
function Je(e, t, o) {
  let s, i, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = je(n);
  let {
    svelteInit: d
  } = t;
  const p = k(J(t)), g = k();
  H(e, g, (a) => o(0, s = a));
  const c = k();
  H(e, c, (a) => o(1, i = a));
  const h = [], m = He("$$ms-gr-react-wrapper"), {
    slotKey: E,
    slotIndex: x,
    subSlotIndex: f
  } = ae() || {}, _ = d({
    parent: m,
    props: p,
    target: g,
    slot: c,
    slotKey: E,
    slotIndex: x,
    subSlotIndex: f,
    onDestroy(a) {
      h.push(a);
    }
  });
  qe("$$ms-gr-react-wrapper", _), Ge(() => {
    p.set(J(t));
  }), Ke(() => {
    h.forEach((a) => a());
  });
  function w(a) {
    G[a ? "unshift" : "push"](() => {
      s = a, g.set(s);
    });
  }
  function S(a) {
    G[a ? "unshift" : "push"](() => {
      i = a, c.set(i);
    });
  }
  return e.$$set = (a) => {
    o(17, t = U(U({}, t), q(a))), "svelteInit" in a && o(5, d = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = q(t), [s, i, g, c, l, d, r, n, w, S];
}
class Xe extends Pe {
  constructor(t) {
    super(), Me(this, t, Je, Ve, ze, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: it
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, j = window.ms_globals.tree;
function Ye(e, t = {}) {
  function o(s) {
    const i = k(), n = new Xe({
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
            createPortal: N,
            node: j
          }), r.onDestroy(() => {
            d.nodes = d.nodes.filter((p) => p.svelteInstance !== i), X({
              createPortal: N,
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
const Ze = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Qe(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const s = e[o];
    return t[o] = $e(o, s), t;
  }, {}) : {};
}
function $e(e, t) {
  return typeof t == "number" && !Ze.includes(e) ? t + "px" : t;
}
function B(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const i = v.Children.toArray(e._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = B(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...v.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(N(v.cloneElement(e._reactElement, {
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
      } = B(n);
      t.push(...l), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function et(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const T = ne(({
  slot: e,
  clone: t,
  className: o,
  style: s,
  observeAttributes: i
}, n) => {
  const r = re(), [l, d] = oe([]), {
    forceClone: p
  } = de(), g = p ? !0 : t;
  return ie(() => {
    var x;
    if (!r.current || !e)
      return;
    let c = e;
    function h() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), et(n, f), o && f.classList.add(...o.split(" ")), s) {
        const _ = Qe(s);
        Object.keys(_).forEach((w) => {
          f.style[w] = _[w];
        });
      }
    }
    let m = null, E = null;
    if (g && window.MutationObserver) {
      let f = function() {
        var a, C, u;
        (a = r.current) != null && a.contains(c) && ((C = r.current) == null || C.removeChild(c));
        const {
          portals: w,
          clonedElement: S
        } = B(e);
        c = S, d(w), c.style.display = "contents", E && clearTimeout(E), E = setTimeout(() => {
          h();
        }, 50), (u = r.current) == null || u.appendChild(c);
      };
      f();
      const _ = Ce(() => {
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
      c.style.display = "contents", h(), (x = r.current) == null || x.appendChild(c);
    return () => {
      var f, _;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((_ = r.current) == null || _.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, g, o, s, n, i, p]), v.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function tt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function nt(e, t = !1) {
  try {
    if (ue(e))
      return e;
    if (t && !tt(e))
      return;
    if (typeof e == "string") {
      let o = e.trim();
      return o.startsWith(";") && (o = o.slice(1)), o.endsWith(";") && (o = o.slice(0, -1)), new Function(`return (...args) => (${o})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function rt(e, t) {
  return se(() => nt(e, t), [e, t]);
}
const st = Ye(({
  slots: e,
  children: t,
  target: o,
  ...s
}) => {
  var n;
  const i = rt(o);
  return /* @__PURE__ */ y.jsxs(y.Fragment, {
    children: [/* @__PURE__ */ y.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ y.jsx(fe.BackTop, {
      ...s,
      target: i,
      icon: e.icon ? /* @__PURE__ */ y.jsx(T, {
        clone: !0,
        slot: e.icon
      }) : s.icon,
      description: e.description ? /* @__PURE__ */ y.jsx(T, {
        clone: !0,
        slot: e.description
      }) : s.description,
      tooltip: e.tooltip ? /* @__PURE__ */ y.jsx(T, {
        clone: !0,
        slot: e.tooltip
      }) : s.tooltip,
      badge: {
        ...s.badge,
        count: e["badge.count"] ? /* @__PURE__ */ y.jsx(T, {
          slot: e["badge.count"]
        }) : (n = s.badge) == null ? void 0 : n.count
      }
    })]
  });
});
export {
  st as FloatButtonBackTop,
  st as default
};
