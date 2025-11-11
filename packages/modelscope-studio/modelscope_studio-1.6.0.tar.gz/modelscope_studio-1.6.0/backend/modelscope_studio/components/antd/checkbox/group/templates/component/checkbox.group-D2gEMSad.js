import { i as ae, a as A, r as ue, Z as P, g as de } from "./Index-8IWM2Mvk.js";
const y = window.ms_globals.React, oe = window.ms_globals.React.forwardRef, se = window.ms_globals.React.useRef, le = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, ce = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, z = window.ms_globals.internalContext.ContextPropsProvider, me = window.ms_globals.antd.Checkbox, pe = window.ms_globals.createItemsContext.createItemsContext;
var _e = /\s/;
function he(e) {
  for (var t = e.length; t-- && _e.test(e.charAt(t)); )
    ;
  return t;
}
var ge = /^\s+/;
function be(e) {
  return e && e.slice(0, he(e) + 1).replace(ge, "");
}
var D = NaN, we = /^[-+]0x[0-9a-f]+$/i, xe = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Ce = parseInt;
function G(e) {
  if (typeof e == "number")
    return e;
  if (ae(e))
    return D;
  if (A(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = A(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = be(e);
  var s = xe.test(e);
  return s || Ee.test(e) ? Ce(e.slice(2), s ? 2 : 8) : we.test(e) ? D : +e;
}
var j = function() {
  return ue.Date.now();
}, ye = "Expected a function", ve = Math.max, Ie = Math.min;
function Se(e, t, s) {
  var l, o, n, r, i, a, _ = 0, h = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(ye);
  t = G(t) || 0, A(s) && (h = !!s.leading, c = "maxWait" in s, n = c ? ve(G(s.maxWait) || 0, t) : n, g = "trailing" in s ? !!s.trailing : g);
  function f(p) {
    var C = l, k = o;
    return l = o = void 0, _ = p, r = e.apply(k, C), r;
  }
  function b(p) {
    return _ = p, i = setTimeout(m, t), h ? f(p) : r;
  }
  function w(p) {
    var C = p - a, k = p - _, F = t - C;
    return c ? Ie(F, n - k) : F;
  }
  function u(p) {
    var C = p - a, k = p - _;
    return a === void 0 || C >= t || C < 0 || c && k >= n;
  }
  function m() {
    var p = j();
    if (u(p))
      return x(p);
    i = setTimeout(m, w(p));
  }
  function x(p) {
    return i = void 0, g && l ? f(p) : (l = o = void 0, r);
  }
  function S() {
    i !== void 0 && clearTimeout(i), _ = 0, l = a = o = i = void 0;
  }
  function d() {
    return i === void 0 ? r : x(j());
  }
  function v() {
    var p = j(), C = u(p);
    if (l = arguments, o = this, a = p, C) {
      if (i === void 0)
        return b(a);
      if (c)
        return clearTimeout(i), i = setTimeout(m, t), f(a);
    }
    return i === void 0 && (i = setTimeout(m, t)), r;
  }
  return v.cancel = S, v.flush = d, v;
}
var K = {
  exports: {}
}, T = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ke = y, Pe = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), Re = Object.prototype.hasOwnProperty, Te = ke.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, je = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(e, t, s) {
  var l, o = {}, n = null, r = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (l in t) Re.call(t, l) && !je.hasOwnProperty(l) && (o[l] = t[l]);
  if (e && e.defaultProps) for (l in t = e.defaultProps, t) o[l] === void 0 && (o[l] = t[l]);
  return {
    $$typeof: Pe,
    type: e,
    key: n,
    ref: r,
    props: o,
    _owner: Te.current
  };
}
T.Fragment = Oe;
T.jsx = Q;
T.jsxs = Q;
K.exports = T;
var E = K.exports;
const {
  SvelteComponent: Le,
  assign: U,
  binding_callbacks: B,
  check_outros: Ne,
  children: $,
  claim_element: ee,
  claim_space: Ae,
  component_subscribe: H,
  compute_slots: We,
  create_slot: Me,
  detach: I,
  element: te,
  empty: q,
  exclude_internal_props: V,
  get_all_dirty_from_scope: Fe,
  get_slot_changes: ze,
  group_outros: De,
  init: Ge,
  insert_hydration: O,
  safe_not_equal: Ue,
  set_custom_element_data: ne,
  space: Be,
  transition_in: R,
  transition_out: W,
  update_slot_base: He
} = window.__gradio__svelte__internal, {
  beforeUpdate: qe,
  getContext: Ve,
  onDestroy: Je,
  setContext: Xe
} = window.__gradio__svelte__internal;
function J(e) {
  let t, s;
  const l = (
    /*#slots*/
    e[7].default
  ), o = Me(
    l,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = te("svelte-slot"), o && o.c(), this.h();
    },
    l(n) {
      t = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = $(t);
      o && o.l(r), r.forEach(I), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), o && o.m(t, null), e[9](t), s = !0;
    },
    p(n, r) {
      o && o.p && (!s || r & /*$$scope*/
      64) && He(
        o,
        l,
        n,
        /*$$scope*/
        n[6],
        s ? ze(
          l,
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
      s || (R(o, n), s = !0);
    },
    o(n) {
      W(o, n), s = !1;
    },
    d(n) {
      n && I(t), o && o.d(n), e[9](null);
    }
  };
}
function Ye(e) {
  let t, s, l, o, n = (
    /*$$slots*/
    e[4].default && J(e)
  );
  return {
    c() {
      t = te("react-portal-target"), s = Be(), n && n.c(), l = q(), this.h();
    },
    l(r) {
      t = ee(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(t).forEach(I), s = Ae(r), n && n.l(r), l = q(), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(r, i) {
      O(r, t, i), e[8](t), O(r, s, i), n && n.m(r, i), O(r, l, i), o = !0;
    },
    p(r, [i]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, i), i & /*$$slots*/
      16 && R(n, 1)) : (n = J(r), n.c(), R(n, 1), n.m(l.parentNode, l)) : n && (De(), W(n, 1, 1, () => {
        n = null;
      }), Ne());
    },
    i(r) {
      o || (R(n), o = !0);
    },
    o(r) {
      W(n), o = !1;
    },
    d(r) {
      r && (I(t), I(s), I(l)), e[8](null), n && n.d(r);
    }
  };
}
function X(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function Ze(e, t, s) {
  let l, o, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const i = We(n);
  let {
    svelteInit: a
  } = t;
  const _ = P(X(t)), h = P();
  H(e, h, (d) => s(0, l = d));
  const c = P();
  H(e, c, (d) => s(1, o = d));
  const g = [], f = Ve("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: w,
    subSlotIndex: u
  } = de() || {}, m = a({
    parent: f,
    props: _,
    target: h,
    slot: c,
    slotKey: b,
    slotIndex: w,
    subSlotIndex: u,
    onDestroy(d) {
      g.push(d);
    }
  });
  Xe("$$ms-gr-react-wrapper", m), qe(() => {
    _.set(X(t));
  }), Je(() => {
    g.forEach((d) => d());
  });
  function x(d) {
    B[d ? "unshift" : "push"](() => {
      l = d, h.set(l);
    });
  }
  function S(d) {
    B[d ? "unshift" : "push"](() => {
      o = d, c.set(o);
    });
  }
  return e.$$set = (d) => {
    s(17, t = U(U({}, t), V(d))), "svelteInit" in d && s(5, a = d.svelteInit), "$$scope" in d && s(6, r = d.$$scope);
  }, t = V(t), [l, o, h, c, i, a, r, n, x, S];
}
class Ke extends Le {
  constructor(t) {
    super(), Ge(this, t, Ze, Ye, Ue, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ct
} = window.__gradio__svelte__internal, Y = window.ms_globals.rerender, L = window.ms_globals.tree;
function Qe(e, t = {}) {
  function s(l) {
    const o = P(), n = new Ke({
      ...l,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const i = {
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
          }, a = r.parent ?? L;
          return a.nodes = [...a.nodes, i], Y({
            createPortal: N,
            node: L
          }), r.onDestroy(() => {
            a.nodes = a.nodes.filter((_) => _.svelteInstance !== o), Y({
              createPortal: N,
              node: L
            });
          }), i;
        },
        ...l.props
      }
    });
    return o.set(n), n;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      l(s);
    });
  });
}
const $e = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function et(e) {
  return e ? Object.keys(e).reduce((t, s) => {
    const l = e[s];
    return t[s] = tt(s, l), t;
  }, {}) : {};
}
function tt(e, t) {
  return typeof t == "number" && !$e.includes(e) ? t + "px" : t;
}
function M(e) {
  const t = [], s = e.cloneNode(!1);
  if (e._reactElement) {
    const o = y.Children.toArray(e._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: i
        } = M(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...y.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(N(y.cloneElement(e._reactElement, {
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
      type: i,
      useCapture: a
    }) => {
      s.addEventListener(i, r, a);
    });
  });
  const l = Array.from(e.childNodes);
  for (let o = 0; o < l.length; o++) {
    const n = l[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: i
      } = M(n);
      t.push(...i), s.appendChild(r);
    } else n.nodeType === 3 && s.appendChild(n.cloneNode());
  }
  return {
    clonedElement: s,
    portals: t
  };
}
function nt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Z = oe(({
  slot: e,
  clone: t,
  className: s,
  style: l,
  observeAttributes: o
}, n) => {
  const r = se(), [i, a] = le([]), {
    forceClone: _
  } = fe(), h = _ ? !0 : t;
  return ie(() => {
    var w;
    if (!r.current || !e)
      return;
    let c = e;
    function g() {
      let u = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (u = c.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), nt(n, u), s && u.classList.add(...s.split(" ")), l) {
        const m = et(l);
        Object.keys(m).forEach((x) => {
          u.style[x] = m[x];
        });
      }
    }
    let f = null, b = null;
    if (h && window.MutationObserver) {
      let u = function() {
        var d, v, p;
        (d = r.current) != null && d.contains(c) && ((v = r.current) == null || v.removeChild(c));
        const {
          portals: x,
          clonedElement: S
        } = M(e);
        c = S, a(x), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          g();
        }, 50), (p = r.current) == null || p.appendChild(c);
      };
      u();
      const m = Se(() => {
        u(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      f = new window.MutationObserver(m), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (w = r.current) == null || w.appendChild(c);
    return () => {
      var u, m;
      c.style.display = "", (u = r.current) != null && u.contains(c) && ((m = r.current) == null || m.removeChild(c)), f == null || f.disconnect();
    };
  }, [e, h, s, l, n, o, _]), y.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...i);
}), rt = ({
  children: e,
  ...t
}) => /* @__PURE__ */ E.jsx(E.Fragment, {
  children: e(t)
});
function ot(e) {
  return y.createElement(rt, {
    children: e
  });
}
function re(e, t, s) {
  const l = e.filter(Boolean);
  if (l.length !== 0)
    return l.map((o, n) => {
      var _;
      if (typeof o != "object")
        return o;
      const r = {
        ...o.props,
        key: ((_ = o.props) == null ? void 0 : _.key) ?? (s ? `${s}-${n}` : `${n}`)
      };
      let i = r;
      Object.keys(o.slots).forEach((h) => {
        if (!o.slots[h] || !(o.slots[h] instanceof Element) && !o.slots[h].el)
          return;
        const c = h.split(".");
        c.forEach((m, x) => {
          i[m] || (i[m] = {}), x !== c.length - 1 && (i = r[m]);
        });
        const g = o.slots[h];
        let f, b, w = !1, u = t == null ? void 0 : t.forceClone;
        g instanceof Element ? f = g : (f = g.el, b = g.callback, w = g.clone ?? w, u = g.forceClone ?? u), u = u ?? !!b, i[c[c.length - 1]] = f ? b ? (...m) => (b(c[c.length - 1], m), /* @__PURE__ */ E.jsx(z, {
          ...o.ctx,
          params: m,
          forceClone: u,
          children: /* @__PURE__ */ E.jsx(Z, {
            slot: f,
            clone: w
          })
        })) : ot((m) => /* @__PURE__ */ E.jsx(z, {
          ...o.ctx,
          forceClone: u,
          children: /* @__PURE__ */ E.jsx(Z, {
            ...m,
            slot: f,
            clone: w
          })
        })) : i[c[c.length - 1]], i = r;
      });
      const a = "children";
      return o[a] && (r[a] = re(o[a], t, `${n}`)), r;
    });
}
const {
  withItemsContextProvider: st,
  useItems: lt,
  ItemHandler: at
} = pe("antd-checkbox-group-options"), ut = Qe(st(["default", "options"], ({
  onValueChange: e,
  onChange: t,
  elRef: s,
  options: l,
  children: o,
  ...n
}) => {
  const {
    items: r
  } = lt(), i = r.options.length > 0 ? r.options : r.default;
  return /* @__PURE__ */ E.jsxs(E.Fragment, {
    children: [/* @__PURE__ */ E.jsx("div", {
      style: {
        display: "none"
      },
      children: o
    }), /* @__PURE__ */ E.jsx(me.Group, {
      ...n,
      ref: s,
      options: ce(() => l || re(i), [i, l]),
      onChange: (a) => {
        t == null || t(a), e(a);
      }
    })]
  });
}));
export {
  ut as CheckboxGroup,
  ut as default
};
