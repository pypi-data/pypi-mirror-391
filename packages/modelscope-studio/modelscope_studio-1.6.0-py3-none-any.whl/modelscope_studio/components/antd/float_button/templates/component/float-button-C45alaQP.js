import { i as ce, a as A, r as ae, Z as T, g as ue, b as de } from "./Index-CqtPaMG_.js";
const E = window.ms_globals.React, re = window.ms_globals.React.forwardRef, oe = window.ms_globals.React.useRef, ie = window.ms_globals.React.useState, se = window.ms_globals.React.useEffect, le = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, me = window.ms_globals.antd.FloatButton;
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
var B = NaN, be = /^[-+]0x[0-9a-f]+$/i, we = /^0b[01]+$/i, ye = /^0o[0-7]+$/i, Ce = parseInt;
function D(e) {
  if (typeof e == "number")
    return e;
  if (ce(e))
    return B;
  if (A(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = A(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = he(e);
  var o = we.test(e);
  return o || ye.test(e) ? Ce(e.slice(2), o ? 2 : 8) : be.test(e) ? B : +e;
}
var L = function() {
  return ae.Date.now();
}, Ee = "Expected a function", xe = Math.max, ve = Math.min;
function Ie(e, t, o) {
  var s, i, n, r, l, u, _ = 0, g = !1, c = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(Ee);
  t = D(t) || 0, A(o) && (g = !!o.leading, c = "maxWait" in o, n = c ? xe(D(o.maxWait) || 0, t) : n, h = "trailing" in o ? !!o.trailing : h);
  function m(d) {
    var y = s, R = i;
    return s = i = void 0, _ = d, r = e.apply(R, y), r;
  }
  function C(d) {
    return _ = d, l = setTimeout(p, t), g ? m(d) : r;
  }
  function x(d) {
    var y = d - u, R = d - _, z = t - y;
    return c ? ve(z, n - R) : z;
  }
  function f(d) {
    var y = d - u, R = d - _;
    return u === void 0 || y >= t || y < 0 || c && R >= n;
  }
  function p() {
    var d = L();
    if (f(d))
      return b(d);
    l = setTimeout(p, x(d));
  }
  function b(d) {
    return l = void 0, h && s ? m(d) : (s = i = void 0, r);
  }
  function S() {
    l !== void 0 && clearTimeout(l), _ = 0, s = u = i = l = void 0;
  }
  function a() {
    return l === void 0 ? r : b(L());
  }
  function v() {
    var d = L(), y = f(d);
    if (s = arguments, i = this, u = d, y) {
      if (l === void 0)
        return C(u);
      if (c)
        return clearTimeout(l), l = setTimeout(p, t), m(u);
    }
    return l === void 0 && (l = setTimeout(p, t)), r;
  }
  return v.cancel = S, v.flush = a, v;
}
var Z = {
  exports: {}
}, j = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Se = E, Re = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), Te = Object.prototype.hasOwnProperty, Pe = Se.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ke = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(e, t, o) {
  var s, i = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) Te.call(t, s) && !ke.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: Re,
    type: e,
    key: n,
    ref: r,
    props: i,
    _owner: Pe.current
  };
}
j.Fragment = Oe;
j.jsx = Q;
j.jsxs = Q;
Z.exports = j;
var w = Z.exports;
const {
  SvelteComponent: je,
  assign: U,
  binding_callbacks: G,
  check_outros: Le,
  children: $,
  claim_element: ee,
  claim_space: Fe,
  component_subscribe: H,
  compute_slots: Ne,
  create_slot: Ae,
  detach: I,
  element: te,
  empty: K,
  exclude_internal_props: q,
  get_all_dirty_from_scope: We,
  get_slot_changes: Me,
  group_outros: ze,
  init: Be,
  insert_hydration: P,
  safe_not_equal: De,
  set_custom_element_data: ne,
  space: Ue,
  transition_in: k,
  transition_out: W,
  update_slot_base: Ge
} = window.__gradio__svelte__internal, {
  beforeUpdate: He,
  getContext: Ke,
  onDestroy: qe,
  setContext: Ve
} = window.__gradio__svelte__internal;
function V(e) {
  let t, o;
  const s = (
    /*#slots*/
    e[7].default
  ), i = Ae(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = te("svelte-slot"), i && i.c(), this.h();
    },
    l(n) {
      t = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = $(t);
      i && i.l(r), r.forEach(I), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      P(n, t, r), i && i.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      i && i.p && (!o || r & /*$$scope*/
      64) && Ge(
        i,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Me(
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
      o || (k(i, n), o = !0);
    },
    o(n) {
      W(i, n), o = !1;
    },
    d(n) {
      n && I(t), i && i.d(n), e[9](null);
    }
  };
}
function Je(e) {
  let t, o, s, i, n = (
    /*$$slots*/
    e[4].default && V(e)
  );
  return {
    c() {
      t = te("react-portal-target"), o = Ue(), n && n.c(), s = K(), this.h();
    },
    l(r) {
      t = ee(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(t).forEach(I), o = Fe(r), n && n.l(r), s = K(), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      P(r, t, l), e[8](t), P(r, o, l), n && n.m(r, l), P(r, s, l), i = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = V(r), n.c(), k(n, 1), n.m(s.parentNode, s)) : n && (ze(), W(n, 1, 1, () => {
        n = null;
      }), Le());
    },
    i(r) {
      i || (k(n), i = !0);
    },
    o(r) {
      W(n), i = !1;
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
function Xe(e, t, o) {
  let s, i, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Ne(n);
  let {
    svelteInit: u
  } = t;
  const _ = T(J(t)), g = T();
  H(e, g, (a) => o(0, s = a));
  const c = T();
  H(e, c, (a) => o(1, i = a));
  const h = [], m = Ke("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: x,
    subSlotIndex: f
  } = ue() || {}, p = u({
    parent: m,
    props: _,
    target: g,
    slot: c,
    slotKey: C,
    slotIndex: x,
    subSlotIndex: f,
    onDestroy(a) {
      h.push(a);
    }
  });
  Ve("$$ms-gr-react-wrapper", p), He(() => {
    _.set(J(t));
  }), qe(() => {
    h.forEach((a) => a());
  });
  function b(a) {
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
    o(17, t = U(U({}, t), q(a))), "svelteInit" in a && o(5, u = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = q(t), [s, i, g, c, l, u, r, n, b, S];
}
class Ye extends je {
  constructor(t) {
    super(), Be(this, t, Xe, Je, De, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: st
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, F = window.ms_globals.tree;
function Ze(e, t = {}) {
  function o(s) {
    const i = T(), n = new Ye({
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
          }, u = r.parent ?? F;
          return u.nodes = [...u.nodes, l], X({
            createPortal: N,
            node: F
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== i), X({
              createPortal: N,
              node: F
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
const Qe = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function $e(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const s = e[o];
    return t[o] = et(o, s), t;
  }, {}) : {};
}
function et(e, t) {
  return typeof t == "number" && !Qe.includes(e) ? t + "px" : t;
}
function M(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const i = E.Children.toArray(e._reactElement.props.children).map((n) => {
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
    return i.originalChildren = e._reactElement.props.children, t.push(N(E.cloneElement(e._reactElement, {
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
      useCapture: u
    }) => {
      o.addEventListener(l, r, u);
    });
  });
  const s = Array.from(e.childNodes);
  for (let i = 0; i < s.length; i++) {
    const n = s[i];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = M(n);
      t.push(...l), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function tt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const O = re(({
  slot: e,
  clone: t,
  className: o,
  style: s,
  observeAttributes: i
}, n) => {
  const r = oe(), [l, u] = ie([]), {
    forceClone: _
  } = fe(), g = _ ? !0 : t;
  return se(() => {
    var x;
    if (!r.current || !e)
      return;
    let c = e;
    function h() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), tt(n, f), o && f.classList.add(...o.split(" ")), s) {
        const p = $e(s);
        Object.keys(p).forEach((b) => {
          f.style[b] = p[b];
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
      const p = Ie(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      m = new window.MutationObserver(p), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", h(), (x = r.current) == null || x.appendChild(c);
    return () => {
      var f, p;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((p = r.current) == null || p.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, g, o, s, n, i, _]), E.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function nt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function rt(e, t = !1) {
  try {
    if (de(e))
      return e;
    if (t && !nt(e))
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
function Y(e, t) {
  return le(() => rt(e, t), [e, t]);
}
function ot(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const lt = Ze(({
  slots: e,
  children: t,
  tooltip: o,
  ...s
}) => {
  var u;
  const i = e["tooltip.title"] || typeof o == "object", n = ot(o), r = Y(n.afterOpenChange), l = Y(n.getPopupContainer);
  return /* @__PURE__ */ w.jsxs(w.Fragment, {
    children: [/* @__PURE__ */ w.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ w.jsx(me, {
      ...s,
      icon: e.icon ? /* @__PURE__ */ w.jsx(O, {
        clone: !0,
        slot: e.icon
      }) : s.icon,
      description: e.description ? /* @__PURE__ */ w.jsx(O, {
        clone: !0,
        slot: e.description
      }) : s.description,
      tooltip: e.tooltip ? /* @__PURE__ */ w.jsx(O, {
        slot: e.tooltip
      }) : i ? {
        ...n,
        afterOpenChange: r,
        getPopupContainer: l,
        title: e["tooltip.title"] ? /* @__PURE__ */ w.jsx(O, {
          slot: e["tooltip.title"]
        }) : n.title
      } : o,
      badge: {
        ...s.badge,
        count: e["badge.count"] ? /* @__PURE__ */ w.jsx(O, {
          slot: e["badge.count"]
        }) : (u = s.badge) == null ? void 0 : u.count
      }
    })]
  });
});
export {
  lt as FloatButton,
  lt as default
};
