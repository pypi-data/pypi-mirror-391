import { i as le, a as W, r as ce, Z as k, g as ae, c as ue } from "./Index-DFfBIkgA.js";
const E = window.ms_globals.React, ne = window.ms_globals.React.forwardRef, re = window.ms_globals.React.useRef, oe = window.ms_globals.React.useState, se = window.ms_globals.React.useEffect, ie = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, de = window.ms_globals.internalContext.useContextPropsContext, fe = window.ms_globals.antd.theme, me = window.ms_globals.antd.FloatButton;
var pe = /\s/;
function _e(e) {
  for (var t = e.length; t-- && pe.test(e.charAt(t)); )
    ;
  return t;
}
var ge = /^\s+/;
function he(e) {
  return e && e.slice(0, _e(e) + 1).replace(ge, "");
}
var B = NaN, be = /^[-+]0x[0-9a-f]+$/i, we = /^0b[01]+$/i, ye = /^0o[0-7]+$/i, Ee = parseInt;
function D(e) {
  if (typeof e == "number")
    return e;
  if (le(e))
    return B;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = he(e);
  var s = we.test(e);
  return s || ye.test(e) ? Ee(e.slice(2), s ? 2 : 8) : be.test(e) ? B : +e;
}
var j = function() {
  return ce.Date.now();
}, Ce = "Expected a function", xe = Math.max, ve = Math.min;
function Ie(e, t, s) {
  var i, o, n, r, l, u, p = 0, g = !1, c = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(Ce);
  t = D(t) || 0, W(s) && (g = !!s.leading, c = "maxWait" in s, n = c ? xe(D(s.maxWait) || 0, t) : n, h = "trailing" in s ? !!s.trailing : h);
  function m(d) {
    var y = i, R = o;
    return i = o = void 0, p = d, r = e.apply(R, y), r;
  }
  function C(d) {
    return p = d, l = setTimeout(_, t), g ? m(d) : r;
  }
  function x(d) {
    var y = d - u, R = d - p, z = t - y;
    return c ? ve(z, n - R) : z;
  }
  function f(d) {
    var y = d - u, R = d - p;
    return u === void 0 || y >= t || y < 0 || c && R >= n;
  }
  function _() {
    var d = j();
    if (f(d))
      return b(d);
    l = setTimeout(_, x(d));
  }
  function b(d) {
    return l = void 0, h && i ? m(d) : (i = o = void 0, r);
  }
  function S() {
    l !== void 0 && clearTimeout(l), p = 0, i = u = o = l = void 0;
  }
  function a() {
    return l === void 0 ? r : b(j());
  }
  function v() {
    var d = j(), y = f(d);
    if (i = arguments, o = this, u = d, y) {
      if (l === void 0)
        return C(u);
      if (c)
        return clearTimeout(l), l = setTimeout(_, t), m(u);
    }
    return l === void 0 && (l = setTimeout(_, t)), r;
  }
  return v.cancel = S, v.flush = a, v;
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
var Se = E, Re = Symbol.for("react.element"), Te = Symbol.for("react.fragment"), ke = Object.prototype.hasOwnProperty, Oe = Se.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Pe = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Z(e, t, s) {
  var i, o = {}, n = null, r = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) ke.call(t, i) && !Pe.hasOwnProperty(i) && (o[i] = t[i]);
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
L.Fragment = Te;
L.jsx = Z;
L.jsxs = Z;
Y.exports = L;
var w = Y.exports;
const {
  SvelteComponent: Le,
  assign: G,
  binding_callbacks: U,
  check_outros: je,
  children: Q,
  claim_element: $,
  claim_space: Ne,
  component_subscribe: H,
  compute_slots: Ae,
  create_slot: We,
  detach: I,
  element: ee,
  empty: K,
  exclude_internal_props: q,
  get_all_dirty_from_scope: Fe,
  get_slot_changes: Me,
  group_outros: ze,
  init: Be,
  insert_hydration: O,
  safe_not_equal: De,
  set_custom_element_data: te,
  space: Ge,
  transition_in: P,
  transition_out: F,
  update_slot_base: Ue
} = window.__gradio__svelte__internal, {
  beforeUpdate: He,
  getContext: Ke,
  onDestroy: qe,
  setContext: Ve
} = window.__gradio__svelte__internal;
function V(e) {
  let t, s;
  const i = (
    /*#slots*/
    e[7].default
  ), o = We(
    i,
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
      var r = Q(t);
      o && o.l(r), r.forEach(I), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), o && o.m(t, null), e[9](t), s = !0;
    },
    p(n, r) {
      o && o.p && (!s || r & /*$$scope*/
      64) && Ue(
        o,
        i,
        n,
        /*$$scope*/
        n[6],
        s ? Me(
          i,
          /*$$scope*/
          n[6],
          r,
          null
        ) : Fe(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      s || (P(o, n), s = !0);
    },
    o(n) {
      F(o, n), s = !1;
    },
    d(n) {
      n && I(t), o && o.d(n), e[9](null);
    }
  };
}
function Je(e) {
  let t, s, i, o, n = (
    /*$$slots*/
    e[4].default && V(e)
  );
  return {
    c() {
      t = ee("react-portal-target"), s = Ge(), n && n.c(), i = K(), this.h();
    },
    l(r) {
      t = $(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), Q(t).forEach(I), s = Ne(r), n && n.l(r), i = K(), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      O(r, t, l), e[8](t), O(r, s, l), n && n.m(r, l), O(r, i, l), o = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && P(n, 1)) : (n = V(r), n.c(), P(n, 1), n.m(i.parentNode, i)) : n && (ze(), F(n, 1, 1, () => {
        n = null;
      }), je());
    },
    i(r) {
      o || (P(n), o = !0);
    },
    o(r) {
      F(n), o = !1;
    },
    d(r) {
      r && (I(t), I(s), I(i)), e[8](null), n && n.d(r);
    }
  };
}
function J(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function Xe(e, t, s) {
  let i, o, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Ae(n);
  let {
    svelteInit: u
  } = t;
  const p = k(J(t)), g = k();
  H(e, g, (a) => s(0, i = a));
  const c = k();
  H(e, c, (a) => s(1, o = a));
  const h = [], m = Ke("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: x,
    subSlotIndex: f
  } = ae() || {}, _ = u({
    parent: m,
    props: p,
    target: g,
    slot: c,
    slotKey: C,
    slotIndex: x,
    subSlotIndex: f,
    onDestroy(a) {
      h.push(a);
    }
  });
  Ve("$$ms-gr-react-wrapper", _), He(() => {
    p.set(J(t));
  }), qe(() => {
    h.forEach((a) => a());
  });
  function b(a) {
    U[a ? "unshift" : "push"](() => {
      i = a, g.set(i);
    });
  }
  function S(a) {
    U[a ? "unshift" : "push"](() => {
      o = a, c.set(o);
    });
  }
  return e.$$set = (a) => {
    s(17, t = G(G({}, t), q(a))), "svelteInit" in a && s(5, u = a.svelteInit), "$$scope" in a && s(6, r = a.$$scope);
  }, t = q(t), [i, o, g, c, l, u, r, n, b, S];
}
class Ye extends Le {
  constructor(t) {
    super(), Be(this, t, Xe, Je, De, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ot
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, N = window.ms_globals.tree;
function Ze(e, t = {}) {
  function s(i) {
    const o = k(), n = new Ye({
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
          return u.nodes = [...u.nodes, l], X({
            createPortal: A,
            node: N
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((p) => p.svelteInstance !== o), X({
              createPortal: A,
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
const Qe = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function $e(e) {
  return e ? Object.keys(e).reduce((t, s) => {
    const i = e[s];
    return t[s] = et(s, i), t;
  }, {}) : {};
}
function et(e, t) {
  return typeof t == "number" && !Qe.includes(e) ? t + "px" : t;
}
function M(e) {
  const t = [], s = e.cloneNode(!1);
  if (e._reactElement) {
    const o = E.Children.toArray(e._reactElement.props.children).map((n) => {
      if (E.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = M(n.props.el);
        return E.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...E.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(A(E.cloneElement(e._reactElement, {
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
      } = M(n);
      t.push(...l), s.appendChild(r);
    } else n.nodeType === 3 && s.appendChild(n.cloneNode());
  }
  return {
    clonedElement: s,
    portals: t
  };
}
function tt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const T = ne(({
  slot: e,
  clone: t,
  className: s,
  style: i,
  observeAttributes: o
}, n) => {
  const r = re(), [l, u] = oe([]), {
    forceClone: p
  } = de(), g = p ? !0 : t;
  return se(() => {
    var x;
    if (!r.current || !e)
      return;
    let c = e;
    function h() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), tt(n, f), s && f.classList.add(...s.split(" ")), i) {
        const _ = $e(i);
        Object.keys(_).forEach((b) => {
          f.style[b] = _[b];
        });
      }
    }
    let m = null, C = null;
    if (g && window.MutationObserver) {
      let f = function() {
        var a, v, d;
        (a = r.current) != null && a.contains(c) && ((v = r.current) == null || v.removeChild(c));
        const {
          portals: b,
          clonedElement: S
        } = M(e);
        c = S, u(b), c.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          h();
        }, 50), (d = r.current) == null || d.appendChild(c);
      };
      f();
      const _ = Ie(() => {
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
      c.style.display = "contents", h(), (x = r.current) == null || x.appendChild(c);
    return () => {
      var f, _;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((_ = r.current) == null || _.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, g, s, i, n, o, p]), E.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function nt(e) {
  return ie(() => {
    const t = E.Children.toArray(e), s = [], i = [];
    return t.forEach((o) => {
      o.props.node && o.props.nodeSlotKey ? s.push(o) : i.push(o);
    }), [s, i];
  }, [e]);
}
const st = Ze(({
  children: e,
  slots: t,
  style: s,
  shape: i = "circle",
  className: o,
  ...n
}) => {
  var p;
  const {
    token: r
  } = fe.useToken(), [l, u] = nt(e);
  return /* @__PURE__ */ w.jsxs(w.Fragment, {
    children: [/* @__PURE__ */ w.jsx("div", {
      style: {
        display: "none"
      },
      children: l
    }), /* @__PURE__ */ w.jsx(me.Group, {
      ...n,
      shape: i,
      className: ue(o, `ms-gr-antd-float-button-group-${i}`),
      style: {
        ...s,
        "--ms-gr-antd-border-radius-lg": r.borderRadiusLG + "px"
      },
      closeIcon: t.closeIcon ? /* @__PURE__ */ w.jsx(T, {
        clone: !0,
        slot: t.closeIcon
      }) : n.closeIcon,
      icon: t.icon ? /* @__PURE__ */ w.jsx(T, {
        clone: !0,
        slot: t.icon
      }) : n.icon,
      description: t.description ? /* @__PURE__ */ w.jsx(T, {
        clone: !0,
        slot: t.description
      }) : n.description,
      tooltip: t.tooltip ? /* @__PURE__ */ w.jsx(T, {
        clone: !0,
        slot: t.tooltip
      }) : n.tooltip,
      badge: {
        ...n.badge,
        count: t["badge.count"] ? /* @__PURE__ */ w.jsx(T, {
          slot: t["badge.count"]
        }) : (p = n.badge) == null ? void 0 : p.count
      },
      children: u
    })]
  });
});
export {
  st as FloatButtonGroup,
  st as default
};
