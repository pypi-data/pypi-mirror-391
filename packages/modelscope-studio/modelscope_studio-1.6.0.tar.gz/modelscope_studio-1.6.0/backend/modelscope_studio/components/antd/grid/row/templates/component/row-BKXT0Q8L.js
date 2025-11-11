import { i as ie, a as A, r as le, Z as T, g as ae } from "./Index-CxNLPxvs.js";
const E = window.ms_globals.React, te = window.ms_globals.React.forwardRef, ne = window.ms_globals.React.useRef, re = window.ms_globals.React.useState, oe = window.ms_globals.React.useEffect, se = window.ms_globals.React.createElement, j = window.ms_globals.ReactDOM.createPortal, ce = window.ms_globals.internalContext.useContextPropsContext, de = window.ms_globals.antd.Row, ue = window.ms_globals.antd.Col, fe = window.ms_globals.createItemsContext.createItemsContext;
var me = /\s/;
function pe(e) {
  for (var t = e.length; t-- && me.test(e.charAt(t)); )
    ;
  return t;
}
var _e = /^\s+/;
function he(e) {
  return e && e.slice(0, pe(e) + 1).replace(_e, "");
}
var F = NaN, ge = /^[-+]0x[0-9a-f]+$/i, we = /^0b[01]+$/i, be = /^0o[0-7]+$/i, ye = parseInt;
function M(e) {
  if (typeof e == "number")
    return e;
  if (ie(e))
    return F;
  if (A(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = A(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = he(e);
  var s = we.test(e);
  return s || be.test(e) ? ye(e.slice(2), s ? 2 : 8) : ge.test(e) ? F : +e;
}
var L = function() {
  return le.Date.now();
}, Ee = "Expected a function", Ce = Math.max, ve = Math.min;
function xe(e, t, s) {
  var i, o, n, r, l, u, _ = 0, h = !1, a = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(Ee);
  t = M(t) || 0, A(s) && (h = !!s.leading, a = "maxWait" in s, n = a ? Ce(M(s.maxWait) || 0, t) : n, g = "trailing" in s ? !!s.trailing : g);
  function m(d) {
    var b = i, R = o;
    return i = o = void 0, _ = d, r = e.apply(R, b), r;
  }
  function y(d) {
    return _ = d, l = setTimeout(p, t), h ? m(d) : r;
  }
  function C(d) {
    var b = d - u, R = d - _, D = t - b;
    return a ? ve(D, n - R) : D;
  }
  function f(d) {
    var b = d - u, R = d - _;
    return u === void 0 || b >= t || b < 0 || a && R >= n;
  }
  function p() {
    var d = L();
    if (f(d))
      return w(d);
    l = setTimeout(p, C(d));
  }
  function w(d) {
    return l = void 0, g && i ? m(d) : (i = o = void 0, r);
  }
  function I() {
    l !== void 0 && clearTimeout(l), _ = 0, i = u = o = l = void 0;
  }
  function c() {
    return l === void 0 ? r : w(L());
  }
  function v() {
    var d = L(), b = f(d);
    if (i = arguments, o = this, u = d, b) {
      if (l === void 0)
        return y(u);
      if (a)
        return clearTimeout(l), l = setTimeout(p, t), m(u);
    }
    return l === void 0 && (l = setTimeout(p, t)), r;
  }
  return v.cancel = I, v.flush = c, v;
}
var X = {
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
var Ie = E, Re = Symbol.for("react.element"), Se = Symbol.for("react.fragment"), Te = Object.prototype.hasOwnProperty, Oe = Ie.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ke = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Y(e, t, s) {
  var i, o = {}, n = null, r = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) Te.call(t, i) && !ke.hasOwnProperty(i) && (o[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) o[i] === void 0 && (o[i] = t[i]);
  return {
    $$typeof: Re,
    type: e,
    key: n,
    ref: r,
    props: o,
    _owner: Oe.current
  };
}
P.Fragment = Se;
P.jsx = Y;
P.jsxs = Y;
X.exports = P;
var S = X.exports;
const {
  SvelteComponent: Pe,
  assign: U,
  binding_callbacks: H,
  check_outros: Le,
  children: Z,
  claim_element: Q,
  claim_space: Ne,
  component_subscribe: B,
  compute_slots: je,
  create_slot: Ae,
  detach: x,
  element: $,
  empty: G,
  exclude_internal_props: K,
  get_all_dirty_from_scope: We,
  get_slot_changes: ze,
  group_outros: De,
  init: Fe,
  insert_hydration: O,
  safe_not_equal: Me,
  set_custom_element_data: ee,
  space: Ue,
  transition_in: k,
  transition_out: W,
  update_slot_base: He
} = window.__gradio__svelte__internal, {
  beforeUpdate: Be,
  getContext: Ge,
  onDestroy: Ke,
  setContext: qe
} = window.__gradio__svelte__internal;
function q(e) {
  let t, s;
  const i = (
    /*#slots*/
    e[7].default
  ), o = Ae(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = $("svelte-slot"), o && o.c(), this.h();
    },
    l(n) {
      t = Q(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = Z(t);
      o && o.l(r), r.forEach(x), this.h();
    },
    h() {
      ee(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), o && o.m(t, null), e[9](t), s = !0;
    },
    p(n, r) {
      o && o.p && (!s || r & /*$$scope*/
      64) && He(
        o,
        i,
        n,
        /*$$scope*/
        n[6],
        s ? ze(
          i,
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
      s || (k(o, n), s = !0);
    },
    o(n) {
      W(o, n), s = !1;
    },
    d(n) {
      n && x(t), o && o.d(n), e[9](null);
    }
  };
}
function Ve(e) {
  let t, s, i, o, n = (
    /*$$slots*/
    e[4].default && q(e)
  );
  return {
    c() {
      t = $("react-portal-target"), s = Ue(), n && n.c(), i = G(), this.h();
    },
    l(r) {
      t = Q(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), Z(t).forEach(x), s = Ne(r), n && n.l(r), i = G(), this.h();
    },
    h() {
      ee(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      O(r, t, l), e[8](t), O(r, s, l), n && n.m(r, l), O(r, i, l), o = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = q(r), n.c(), k(n, 1), n.m(i.parentNode, i)) : n && (De(), W(n, 1, 1, () => {
        n = null;
      }), Le());
    },
    i(r) {
      o || (k(n), o = !0);
    },
    o(r) {
      W(n), o = !1;
    },
    d(r) {
      r && (x(t), x(s), x(i)), e[8](null), n && n.d(r);
    }
  };
}
function V(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function Je(e, t, s) {
  let i, o, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = je(n);
  let {
    svelteInit: u
  } = t;
  const _ = T(V(t)), h = T();
  B(e, h, (c) => s(0, i = c));
  const a = T();
  B(e, a, (c) => s(1, o = c));
  const g = [], m = Ge("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: C,
    subSlotIndex: f
  } = ae() || {}, p = u({
    parent: m,
    props: _,
    target: h,
    slot: a,
    slotKey: y,
    slotIndex: C,
    subSlotIndex: f,
    onDestroy(c) {
      g.push(c);
    }
  });
  qe("$$ms-gr-react-wrapper", p), Be(() => {
    _.set(V(t));
  }), Ke(() => {
    g.forEach((c) => c());
  });
  function w(c) {
    H[c ? "unshift" : "push"](() => {
      i = c, h.set(i);
    });
  }
  function I(c) {
    H[c ? "unshift" : "push"](() => {
      o = c, a.set(o);
    });
  }
  return e.$$set = (c) => {
    s(17, t = U(U({}, t), K(c))), "svelteInit" in c && s(5, u = c.svelteInit), "$$scope" in c && s(6, r = c.$$scope);
  }, t = K(t), [i, o, h, a, l, u, r, n, w, I];
}
class Xe extends Pe {
  constructor(t) {
    super(), Fe(this, t, Je, Ve, Me, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: st
} = window.__gradio__svelte__internal, J = window.ms_globals.rerender, N = window.ms_globals.tree;
function Ye(e, t = {}) {
  function s(i) {
    const o = T(), n = new Xe({
      ...i,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, u = r.parent ?? N;
          return u.nodes = [...u.nodes, l], J({
            createPortal: j,
            node: N
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== o), J({
              createPortal: j,
              node: N
            });
          }), l;
        },
        ...i.props
      }
    });
    return o.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      i(s);
    });
  });
}
const Ze = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Qe(e) {
  return e ? Object.keys(e).reduce((t, s) => {
    const i = e[s];
    return t[s] = $e(s, i), t;
  }, {}) : {};
}
function $e(e, t) {
  return typeof t == "number" && !Ze.includes(e) ? t + "px" : t;
}
function z(e) {
  const t = [], s = e.cloneNode(!1);
  if (e._reactElement) {
    const o = E.Children.toArray(e._reactElement.props.children).map((n) => {
      if (E.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = z(n.props.el);
        return E.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...E.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(j(E.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), s)), {
      clonedElement: s,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: r,
      type: l,
      useCapture: u
    }) => {
      s.addEventListener(l, r, u);
    });
  });
  const i = Array.from(e.childNodes);
  for (let o = 0; o < i.length; o++) {
    const n = i[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = z(n);
      t.push(...l), s.appendChild(r);
    } else n.nodeType === 3 && s.appendChild(n.cloneNode());
  }
  return {
    clonedElement: s,
    portals: t
  };
}
function et(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const tt = te(({
  slot: e,
  clone: t,
  className: s,
  style: i,
  observeAttributes: o
}, n) => {
  const r = ne(), [l, u] = re([]), {
    forceClone: _
  } = ce(), h = _ ? !0 : t;
  return oe(() => {
    var C;
    if (!r.current || !e)
      return;
    let a = e;
    function g() {
      let f = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (f = a.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), et(n, f), s && f.classList.add(...s.split(" ")), i) {
        const p = Qe(i);
        Object.keys(p).forEach((w) => {
          f.style[w] = p[w];
        });
      }
    }
    let m = null, y = null;
    if (h && window.MutationObserver) {
      let f = function() {
        var c, v, d;
        (c = r.current) != null && c.contains(a) && ((v = r.current) == null || v.removeChild(a));
        const {
          portals: w,
          clonedElement: I
        } = z(e);
        a = I, u(w), a.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          g();
        }, 50), (d = r.current) == null || d.appendChild(a);
      };
      f();
      const p = xe(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      m = new window.MutationObserver(p), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", g(), (C = r.current) == null || C.appendChild(a);
    return () => {
      var f, p;
      a.style.display = "", (f = r.current) != null && f.contains(a) && ((p = r.current) == null || p.removeChild(a)), m == null || m.disconnect();
    };
  }, [e, h, s, i, n, o, _]), E.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
}), {
  withItemsContextProvider: nt,
  useItems: rt,
  ItemHandler: it
} = fe("antd-grid-cols"), lt = Ye(nt(["default"], ({
  children: e,
  ...t
}) => {
  const {
    items: {
      default: s
    }
  } = rt();
  return /* @__PURE__ */ S.jsxs(S.Fragment, {
    children: [/* @__PURE__ */ S.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ S.jsx(de, {
      ...t,
      children: s == null ? void 0 : s.map((i, o) => {
        if (!i)
          return;
        const {
          el: n,
          props: r
        } = i;
        return /* @__PURE__ */ se(ue, {
          ...r,
          key: o
        }, n && /* @__PURE__ */ S.jsx(tt, {
          slot: n
        }));
      })
    })]
  });
}));
export {
  lt as Row,
  lt as default
};
