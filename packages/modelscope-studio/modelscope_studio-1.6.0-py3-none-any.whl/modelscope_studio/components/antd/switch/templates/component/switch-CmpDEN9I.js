import { i as se, a as A, r as le, Z as T, g as ce } from "./Index-bYkIJ7Ef.js";
const E = window.ms_globals.React, ne = window.ms_globals.React.forwardRef, re = window.ms_globals.React.useRef, oe = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, j = window.ms_globals.ReactDOM.createPortal, ae = window.ms_globals.internalContext.useContextPropsContext, de = window.ms_globals.antd.Switch;
var ue = /\s/;
function fe(e) {
  for (var t = e.length; t-- && ue.test(e.charAt(t)); )
    ;
  return t;
}
var me = /^\s+/;
function _e(e) {
  return e && e.slice(0, fe(e) + 1).replace(me, "");
}
var F = NaN, pe = /^[-+]0x[0-9a-f]+$/i, he = /^0b[01]+$/i, ge = /^0o[0-7]+$/i, we = parseInt;
function M(e) {
  if (typeof e == "number")
    return e;
  if (se(e))
    return F;
  if (A(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = A(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = _e(e);
  var i = he.test(e);
  return i || ge.test(e) ? we(e.slice(2), i ? 2 : 8) : pe.test(e) ? F : +e;
}
var L = function() {
  return le.Date.now();
}, be = "Expected a function", ye = Math.max, Ee = Math.min;
function Ce(e, t, i) {
  var s, o, n, r, l, u, p = 0, h = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(be);
  t = M(t) || 0, A(i) && (h = !!i.leading, c = "maxWait" in i, n = c ? ye(M(i.maxWait) || 0, t) : n, g = "trailing" in i ? !!i.trailing : g);
  function m(d) {
    var b = s, k = o;
    return s = o = void 0, p = d, r = e.apply(k, b), r;
  }
  function y(d) {
    return p = d, l = setTimeout(_, t), h ? m(d) : r;
  }
  function C(d) {
    var b = d - u, k = d - p, D = t - b;
    return c ? Ee(D, n - k) : D;
  }
  function f(d) {
    var b = d - u, k = d - p;
    return u === void 0 || b >= t || b < 0 || c && k >= n;
  }
  function _() {
    var d = L();
    if (f(d))
      return w(d);
    l = setTimeout(_, C(d));
  }
  function w(d) {
    return l = void 0, g && s ? m(d) : (s = o = void 0, r);
  }
  function S() {
    l !== void 0 && clearTimeout(l), p = 0, s = u = o = l = void 0;
  }
  function a() {
    return l === void 0 ? r : w(L());
  }
  function v() {
    var d = L(), b = f(d);
    if (s = arguments, o = this, u = d, b) {
      if (l === void 0)
        return y(u);
      if (c)
        return clearTimeout(l), l = setTimeout(_, t), m(u);
    }
    return l === void 0 && (l = setTimeout(_, t)), r;
  }
  return v.cancel = S, v.flush = a, v;
}
var Z = {
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
var ve = E, xe = Symbol.for("react.element"), Ie = Symbol.for("react.fragment"), Se = Object.prototype.hasOwnProperty, ke = ve.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Te = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(e, t, i) {
  var s, o = {}, n = null, r = null;
  i !== void 0 && (n = "" + i), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) Se.call(t, s) && !Te.hasOwnProperty(s) && (o[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) o[s] === void 0 && (o[s] = t[s]);
  return {
    $$typeof: xe,
    type: e,
    key: n,
    ref: r,
    props: o,
    _owner: ke.current
  };
}
P.Fragment = Ie;
P.jsx = Q;
P.jsxs = Q;
Z.exports = P;
var x = Z.exports;
const {
  SvelteComponent: Re,
  assign: U,
  binding_callbacks: B,
  check_outros: Oe,
  children: V,
  claim_element: $,
  claim_space: Pe,
  component_subscribe: G,
  compute_slots: Le,
  create_slot: Ne,
  detach: I,
  element: ee,
  empty: H,
  exclude_internal_props: K,
  get_all_dirty_from_scope: je,
  get_slot_changes: Ae,
  group_outros: We,
  init: ze,
  insert_hydration: R,
  safe_not_equal: De,
  set_custom_element_data: te,
  space: Fe,
  transition_in: O,
  transition_out: W,
  update_slot_base: Me
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ue,
  getContext: Be,
  onDestroy: Ge,
  setContext: He
} = window.__gradio__svelte__internal;
function q(e) {
  let t, i;
  const s = (
    /*#slots*/
    e[7].default
  ), o = Ne(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ee("svelte-slot"), o && o.c(), this.h();
    },
    l(n) {
      t = $(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = V(t);
      o && o.l(r), r.forEach(I), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      R(n, t, r), o && o.m(t, null), e[9](t), i = !0;
    },
    p(n, r) {
      o && o.p && (!i || r & /*$$scope*/
      64) && Me(
        o,
        s,
        n,
        /*$$scope*/
        n[6],
        i ? Ae(
          s,
          /*$$scope*/
          n[6],
          r,
          null
        ) : je(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      i || (O(o, n), i = !0);
    },
    o(n) {
      W(o, n), i = !1;
    },
    d(n) {
      n && I(t), o && o.d(n), e[9](null);
    }
  };
}
function Ke(e) {
  let t, i, s, o, n = (
    /*$$slots*/
    e[4].default && q(e)
  );
  return {
    c() {
      t = ee("react-portal-target"), i = Fe(), n && n.c(), s = H(), this.h();
    },
    l(r) {
      t = $(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), V(t).forEach(I), i = Pe(r), n && n.l(r), s = H(), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      R(r, t, l), e[8](t), R(r, i, l), n && n.m(r, l), R(r, s, l), o = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && O(n, 1)) : (n = q(r), n.c(), O(n, 1), n.m(s.parentNode, s)) : n && (We(), W(n, 1, 1, () => {
        n = null;
      }), Oe());
    },
    i(r) {
      o || (O(n), o = !0);
    },
    o(r) {
      W(n), o = !1;
    },
    d(r) {
      r && (I(t), I(i), I(s)), e[8](null), n && n.d(r);
    }
  };
}
function J(e) {
  const {
    svelteInit: t,
    ...i
  } = e;
  return i;
}
function qe(e, t, i) {
  let s, o, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Le(n);
  let {
    svelteInit: u
  } = t;
  const p = T(J(t)), h = T();
  G(e, h, (a) => i(0, s = a));
  const c = T();
  G(e, c, (a) => i(1, o = a));
  const g = [], m = Be("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: C,
    subSlotIndex: f
  } = ce() || {}, _ = u({
    parent: m,
    props: p,
    target: h,
    slot: c,
    slotKey: y,
    slotIndex: C,
    subSlotIndex: f,
    onDestroy(a) {
      g.push(a);
    }
  });
  He("$$ms-gr-react-wrapper", _), Ue(() => {
    p.set(J(t));
  }), Ge(() => {
    g.forEach((a) => a());
  });
  function w(a) {
    B[a ? "unshift" : "push"](() => {
      s = a, h.set(s);
    });
  }
  function S(a) {
    B[a ? "unshift" : "push"](() => {
      o = a, c.set(o);
    });
  }
  return e.$$set = (a) => {
    i(17, t = U(U({}, t), K(a))), "svelteInit" in a && i(5, u = a.svelteInit), "$$scope" in a && i(6, r = a.$$scope);
  }, t = K(t), [s, o, h, c, l, u, r, n, w, S];
}
class Je extends Re {
  constructor(t) {
    super(), ze(this, t, qe, Ke, De, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: et
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, N = window.ms_globals.tree;
function Xe(e, t = {}) {
  function i(s) {
    const o = T(), n = new Je({
      ...s,
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
          return u.nodes = [...u.nodes, l], X({
            createPortal: j,
            node: N
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((p) => p.svelteInstance !== o), X({
              createPortal: j,
              node: N
            });
          }), l;
        },
        ...s.props
      }
    });
    return o.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(i);
    });
  });
}
const Ye = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ze(e) {
  return e ? Object.keys(e).reduce((t, i) => {
    const s = e[i];
    return t[i] = Qe(i, s), t;
  }, {}) : {};
}
function Qe(e, t) {
  return typeof t == "number" && !Ye.includes(e) ? t + "px" : t;
}
function z(e) {
  const t = [], i = e.cloneNode(!1);
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
    }), i)), {
      clonedElement: i,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: r,
      type: l,
      useCapture: u
    }) => {
      i.addEventListener(l, r, u);
    });
  });
  const s = Array.from(e.childNodes);
  for (let o = 0; o < s.length; o++) {
    const n = s[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = z(n);
      t.push(...l), i.appendChild(r);
    } else n.nodeType === 3 && i.appendChild(n.cloneNode());
  }
  return {
    clonedElement: i,
    portals: t
  };
}
function Ve(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Y = ne(({
  slot: e,
  clone: t,
  className: i,
  style: s,
  observeAttributes: o
}, n) => {
  const r = re(), [l, u] = oe([]), {
    forceClone: p
  } = ae(), h = p ? !0 : t;
  return ie(() => {
    var C;
    if (!r.current || !e)
      return;
    let c = e;
    function g() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), Ve(n, f), i && f.classList.add(...i.split(" ")), s) {
        const _ = Ze(s);
        Object.keys(_).forEach((w) => {
          f.style[w] = _[w];
        });
      }
    }
    let m = null, y = null;
    if (h && window.MutationObserver) {
      let f = function() {
        var a, v, d;
        (a = r.current) != null && a.contains(c) && ((v = r.current) == null || v.removeChild(c));
        const {
          portals: w,
          clonedElement: S
        } = z(e);
        c = S, u(w), c.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          g();
        }, 50), (d = r.current) == null || d.appendChild(c);
      };
      f();
      const _ = Ce(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      m = new window.MutationObserver(_), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (C = r.current) == null || C.appendChild(c);
    return () => {
      var f, _;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((_ = r.current) == null || _.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, h, i, s, n, o, p]), E.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
}), tt = Xe(({
  slots: e,
  children: t,
  onValueChange: i,
  onChange: s,
  ...o
}) => /* @__PURE__ */ x.jsxs(x.Fragment, {
  children: [/* @__PURE__ */ x.jsx("div", {
    style: {
      display: "none"
    },
    children: t
  }), /* @__PURE__ */ x.jsx(de, {
    ...o,
    onChange: (n, ...r) => {
      i == null || i(n), s == null || s(n, ...r);
    },
    checkedChildren: e.checkedChildren ? /* @__PURE__ */ x.jsx(Y, {
      slot: e.checkedChildren
    }) : o.checkedChildren,
    unCheckedChildren: e.unCheckedChildren ? /* @__PURE__ */ x.jsx(Y, {
      slot: e.unCheckedChildren
    }) : o.unCheckedChildren
  })]
}));
export {
  tt as Switch,
  tt as default
};
