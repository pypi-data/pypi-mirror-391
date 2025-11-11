import { i as ae, a as W, r as ue, Z as k, g as de, b as fe } from "./Index-Dyh12G6-.js";
const C = window.ms_globals.React, oe = window.ms_globals.React.forwardRef, ie = window.ms_globals.React.useRef, le = window.ms_globals.React.useState, ce = window.ms_globals.React.useEffect, Q = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, me = window.ms_globals.internalContext.useContextPropsContext, _e = window.ms_globals.internalContext.ContextPropsProvider, pe = window.ms_globals.antd.Slider, he = window.ms_globals.createItemsContext.createItemsContext;
var ge = /\s/;
function we(e) {
  for (var t = e.length; t-- && ge.test(e.charAt(t)); )
    ;
  return t;
}
var be = /^\s+/;
function xe(e) {
  return e && e.slice(0, we(e) + 1).replace(be, "");
}
var D = NaN, Ce = /^[-+]0x[0-9a-f]+$/i, ye = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Se = parseInt;
function U(e) {
  if (typeof e == "number")
    return e;
  if (ae(e))
    return D;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = xe(e);
  var n = ye.test(e);
  return n || Ee.test(e) ? Se(e.slice(2), n ? 2 : 8) : Ce.test(e) ? D : +e;
}
var F = function() {
  return ue.Date.now();
}, Ie = "Expected a function", Pe = Math.max, Re = Math.min;
function ke(e, t, n) {
  var i, o, r, s, l, d, _ = 0, g = !1, c = !1, w = !0;
  if (typeof e != "function")
    throw new TypeError(Ie);
  t = U(t) || 0, W(n) && (g = !!n.leading, c = "maxWait" in n, r = c ? Pe(U(n.maxWait) || 0, t) : r, w = "trailing" in n ? !!n.trailing : w);
  function f(u) {
    var y = i, R = o;
    return i = o = void 0, _ = u, s = e.apply(R, y), s;
  }
  function b(u) {
    return _ = u, l = setTimeout(p, t), g ? f(u) : s;
  }
  function E(u) {
    var y = u - d, R = u - _, z = t - y;
    return c ? Re(z, r - R) : z;
  }
  function m(u) {
    var y = u - d, R = u - _;
    return d === void 0 || y >= t || y < 0 || c && R >= r;
  }
  function p() {
    var u = F();
    if (m(u))
      return x(u);
    l = setTimeout(p, E(u));
  }
  function x(u) {
    return l = void 0, w && i ? f(u) : (i = o = void 0, s);
  }
  function P() {
    l !== void 0 && clearTimeout(l), _ = 0, i = d = o = l = void 0;
  }
  function a() {
    return l === void 0 ? s : x(F());
  }
  function S() {
    var u = F(), y = m(u);
    if (i = arguments, o = this, d = u, y) {
      if (l === void 0)
        return b(d);
      if (c)
        return clearTimeout(l), l = setTimeout(p, t), f(d);
    }
    return l === void 0 && (l = setTimeout(p, t)), s;
  }
  return S.cancel = P, S.flush = a, S;
}
var $ = {
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
var Te = C, Oe = Symbol.for("react.element"), ve = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Fe = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Le = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ee(e, t, n) {
  var i, o = {}, r = null, s = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (i in t) je.call(t, i) && !Le.hasOwnProperty(i) && (o[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) o[i] === void 0 && (o[i] = t[i]);
  return {
    $$typeof: Oe,
    type: e,
    key: r,
    ref: s,
    props: o,
    _owner: Fe.current
  };
}
j.Fragment = ve;
j.jsx = ee;
j.jsxs = ee;
$.exports = j;
var h = $.exports;
const {
  SvelteComponent: Ne,
  assign: G,
  binding_callbacks: H,
  check_outros: We,
  children: te,
  claim_element: ne,
  claim_space: Ae,
  component_subscribe: B,
  compute_slots: Me,
  create_slot: ze,
  detach: I,
  element: re,
  empty: K,
  exclude_internal_props: q,
  get_all_dirty_from_scope: De,
  get_slot_changes: Ue,
  group_outros: Ge,
  init: He,
  insert_hydration: T,
  safe_not_equal: Be,
  set_custom_element_data: se,
  space: Ke,
  transition_in: O,
  transition_out: A,
  update_slot_base: qe
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ve,
  getContext: Je,
  onDestroy: Xe,
  setContext: Ye
} = window.__gradio__svelte__internal;
function V(e) {
  let t, n;
  const i = (
    /*#slots*/
    e[7].default
  ), o = ze(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = re("svelte-slot"), o && o.c(), this.h();
    },
    l(r) {
      t = ne(r, "SVELTE-SLOT", {
        class: !0
      });
      var s = te(t);
      o && o.l(s), s.forEach(I), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(r, s) {
      T(r, t, s), o && o.m(t, null), e[9](t), n = !0;
    },
    p(r, s) {
      o && o.p && (!n || s & /*$$scope*/
      64) && qe(
        o,
        i,
        r,
        /*$$scope*/
        r[6],
        n ? Ue(
          i,
          /*$$scope*/
          r[6],
          s,
          null
        ) : De(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      n || (O(o, r), n = !0);
    },
    o(r) {
      A(o, r), n = !1;
    },
    d(r) {
      r && I(t), o && o.d(r), e[9](null);
    }
  };
}
function Ze(e) {
  let t, n, i, o, r = (
    /*$$slots*/
    e[4].default && V(e)
  );
  return {
    c() {
      t = re("react-portal-target"), n = Ke(), r && r.c(), i = K(), this.h();
    },
    l(s) {
      t = ne(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), te(t).forEach(I), n = Ae(s), r && r.l(s), i = K(), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(s, l) {
      T(s, t, l), e[8](t), T(s, n, l), r && r.m(s, l), T(s, i, l), o = !0;
    },
    p(s, [l]) {
      /*$$slots*/
      s[4].default ? r ? (r.p(s, l), l & /*$$slots*/
      16 && O(r, 1)) : (r = V(s), r.c(), O(r, 1), r.m(i.parentNode, i)) : r && (Ge(), A(r, 1, 1, () => {
        r = null;
      }), We());
    },
    i(s) {
      o || (O(r), o = !0);
    },
    o(s) {
      A(r), o = !1;
    },
    d(s) {
      s && (I(t), I(n), I(i)), e[8](null), r && r.d(s);
    }
  };
}
function J(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function Qe(e, t, n) {
  let i, o, {
    $$slots: r = {},
    $$scope: s
  } = t;
  const l = Me(r);
  let {
    svelteInit: d
  } = t;
  const _ = k(J(t)), g = k();
  B(e, g, (a) => n(0, i = a));
  const c = k();
  B(e, c, (a) => n(1, o = a));
  const w = [], f = Je("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: E,
    subSlotIndex: m
  } = de() || {}, p = d({
    parent: f,
    props: _,
    target: g,
    slot: c,
    slotKey: b,
    slotIndex: E,
    subSlotIndex: m,
    onDestroy(a) {
      w.push(a);
    }
  });
  Ye("$$ms-gr-react-wrapper", p), Ve(() => {
    _.set(J(t));
  }), Xe(() => {
    w.forEach((a) => a());
  });
  function x(a) {
    H[a ? "unshift" : "push"](() => {
      i = a, g.set(i);
    });
  }
  function P(a) {
    H[a ? "unshift" : "push"](() => {
      o = a, c.set(o);
    });
  }
  return e.$$set = (a) => {
    n(17, t = G(G({}, t), q(a))), "svelteInit" in a && n(5, d = a.svelteInit), "$$scope" in a && n(6, s = a.$$scope);
  }, t = q(t), [i, o, g, c, l, d, s, r, x, P];
}
class $e extends Ne {
  constructor(t) {
    super(), He(this, t, Qe, Ze, Be, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, L = window.ms_globals.tree;
function et(e, t = {}) {
  function n(i) {
    const o = k(), r = new $e({
      ...i,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, d = s.parent ?? L;
          return d.nodes = [...d.nodes, l], X({
            createPortal: N,
            node: L
          }), s.onDestroy(() => {
            d.nodes = d.nodes.filter((_) => _.svelteInstance !== o), X({
              createPortal: N,
              node: L
            });
          }), l;
        },
        ...i.props
      }
    });
    return o.set(r), r;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      i(n);
    });
  });
}
const tt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function nt(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const i = e[n];
    return t[n] = rt(n, i), t;
  }, {}) : {};
}
function rt(e, t) {
  return typeof t == "number" && !tt.includes(e) ? t + "px" : t;
}
function M(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const o = C.Children.toArray(e._reactElement.props.children).map((r) => {
      if (C.isValidElement(r) && r.props.__slot__) {
        const {
          portals: s,
          clonedElement: l
        } = M(r.props.el);
        return C.cloneElement(r, {
          ...r.props,
          el: l,
          children: [...C.Children.toArray(r.props.children), ...s]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(N(C.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: s,
      type: l,
      useCapture: d
    }) => {
      n.addEventListener(l, s, d);
    });
  });
  const i = Array.from(e.childNodes);
  for (let o = 0; o < i.length; o++) {
    const r = i[o];
    if (r.nodeType === 1) {
      const {
        clonedElement: s,
        portals: l
      } = M(r);
      t.push(...l), n.appendChild(s);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function st(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const v = oe(({
  slot: e,
  clone: t,
  className: n,
  style: i,
  observeAttributes: o
}, r) => {
  const s = ie(), [l, d] = le([]), {
    forceClone: _
  } = me(), g = _ ? !0 : t;
  return ce(() => {
    var E;
    if (!s.current || !e)
      return;
    let c = e;
    function w() {
      let m = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (m = c.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), st(r, m), n && m.classList.add(...n.split(" ")), i) {
        const p = nt(i);
        Object.keys(p).forEach((x) => {
          m.style[x] = p[x];
        });
      }
    }
    let f = null, b = null;
    if (g && window.MutationObserver) {
      let m = function() {
        var a, S, u;
        (a = s.current) != null && a.contains(c) && ((S = s.current) == null || S.removeChild(c));
        const {
          portals: x,
          clonedElement: P
        } = M(e);
        c = P, d(x), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          w();
        }, 50), (u = s.current) == null || u.appendChild(c);
      };
      m();
      const p = ke(() => {
        m(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      f = new window.MutationObserver(p), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", w(), (E = s.current) == null || E.appendChild(c);
    return () => {
      var m, p;
      c.style.display = "", (m = s.current) != null && m.contains(c) && ((p = s.current) == null || p.removeChild(c)), f == null || f.disconnect();
    };
  }, [e, g, n, i, r, o, _]), C.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...l);
});
function ot(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function it(e, t = !1) {
  try {
    if (fe(e))
      return e;
    if (t && !ot(e))
      return;
    if (typeof e == "string") {
      let n = e.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function Y(e, t) {
  return Q(() => it(e, t), [e, t]);
}
const lt = ({
  children: e,
  ...t
}) => /* @__PURE__ */ h.jsx(h.Fragment, {
  children: e(t)
});
function ct(e) {
  return C.createElement(lt, {
    children: e
  });
}
function Z(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ct((n) => /* @__PURE__ */ h.jsx(_e, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ h.jsx(v, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ h.jsx(v, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function at({
  key: e,
  slots: t,
  targets: n
}, i) {
  return t[e] ? (...o) => n ? n.map((r, s) => /* @__PURE__ */ h.jsx(C.Fragment, {
    children: Z(r, {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ h.jsx(h.Fragment, {
    children: Z(t[e], {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: ut,
  useItems: dt,
  ItemHandler: pt
} = he("antd-slider-marks"), ft = (e) => e.reduce((t, n) => {
  const i = n == null ? void 0 : n.props.number;
  return i !== void 0 && (t[i] = (n == null ? void 0 : n.slots.label) instanceof Element ? {
    ...n.props,
    label: /* @__PURE__ */ h.jsx(v, {
      slot: n == null ? void 0 : n.slots.label
    })
  } : (n == null ? void 0 : n.slots.children) instanceof Element ? /* @__PURE__ */ h.jsx(v, {
    slot: n == null ? void 0 : n.slots.children
  }) : {
    ...n == null ? void 0 : n.props
  }), t;
}, {}), ht = et(ut(["marks"], ({
  marks: e,
  children: t,
  onValueChange: n,
  onChange: i,
  elRef: o,
  tooltip: r,
  step: s,
  slots: l,
  setSlotParams: d,
  ..._
}) => {
  const g = (b) => {
    i == null || i(b), n(b);
  }, c = Y(r == null ? void 0 : r.getPopupContainer), w = Y(r == null ? void 0 : r.formatter), {
    items: {
      marks: f
    }
  } = dt();
  return /* @__PURE__ */ h.jsxs(h.Fragment, {
    children: [/* @__PURE__ */ h.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ h.jsx(pe, {
      ..._,
      tooltip: {
        ...r,
        getPopupContainer: c,
        formatter: l["tooltip.formatter"] ? at({
          key: "tooltip.formatter",
          slots: l
        }) : w
      },
      marks: Q(() => e || ft(f), [f, e]),
      step: s === void 0 ? null : s,
      ref: o,
      onChange: g
    })]
  });
}));
export {
  ht as Slider,
  ht as default
};
