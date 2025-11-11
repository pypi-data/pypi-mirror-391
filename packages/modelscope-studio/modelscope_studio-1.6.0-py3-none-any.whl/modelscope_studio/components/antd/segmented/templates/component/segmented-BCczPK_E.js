import { i as ae, a as A, r as ue, Z as O, g as de } from "./Index-Cdv_7f8n.js";
const v = window.ms_globals.React, oe = window.ms_globals.React.forwardRef, se = window.ms_globals.React.useRef, le = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, ce = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, z = window.ms_globals.internalContext.ContextPropsProvider, me = window.ms_globals.antd.Segmented, pe = window.ms_globals.createItemsContext.createItemsContext;
var _e = /\s/;
function he(e) {
  for (var t = e.length; t-- && _e.test(e.charAt(t)); )
    ;
  return t;
}
var ge = /^\s+/;
function we(e) {
  return e && e.slice(0, he(e) + 1).replace(ge, "");
}
var D = NaN, be = /^[-+]0x[0-9a-f]+$/i, xe = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, ye = parseInt;
function U(e) {
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
  e = we(e);
  var s = xe.test(e);
  return s || Ee.test(e) ? ye(e.slice(2), s ? 2 : 8) : be.test(e) ? D : +e;
}
var j = function() {
  return ue.Date.now();
}, ve = "Expected a function", Ce = Math.max, Ie = Math.min;
function Se(e, t, s) {
  var l, o, n, r, i, u, _ = 0, h = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(ve);
  t = U(t) || 0, A(s) && (h = !!s.leading, c = "maxWait" in s, n = c ? Ce(U(s.maxWait) || 0, t) : n, g = "trailing" in s ? !!s.trailing : g);
  function f(p) {
    var y = l, P = o;
    return l = o = void 0, _ = p, r = e.apply(P, y), r;
  }
  function w(p) {
    return _ = p, i = setTimeout(m, t), h ? f(p) : r;
  }
  function b(p) {
    var y = p - u, P = p - _, F = t - y;
    return c ? Ie(F, n - P) : F;
  }
  function a(p) {
    var y = p - u, P = p - _;
    return u === void 0 || y >= t || y < 0 || c && P >= n;
  }
  function m() {
    var p = j();
    if (a(p))
      return x(p);
    i = setTimeout(m, b(p));
  }
  function x(p) {
    return i = void 0, g && l ? f(p) : (l = o = void 0, r);
  }
  function S() {
    i !== void 0 && clearTimeout(i), _ = 0, l = u = o = i = void 0;
  }
  function d() {
    return i === void 0 ? r : x(j());
  }
  function C() {
    var p = j(), y = a(p);
    if (l = arguments, o = this, u = p, y) {
      if (i === void 0)
        return w(u);
      if (c)
        return clearTimeout(i), i = setTimeout(m, t), f(u);
    }
    return i === void 0 && (i = setTimeout(m, t)), r;
  }
  return C.cancel = S, C.flush = d, C;
}
var K = {
  exports: {}
}, k = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Pe = v, Oe = Symbol.for("react.element"), Re = Symbol.for("react.fragment"), Te = Object.prototype.hasOwnProperty, ke = Pe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, je = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(e, t, s) {
  var l, o = {}, n = null, r = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (l in t) Te.call(t, l) && !je.hasOwnProperty(l) && (o[l] = t[l]);
  if (e && e.defaultProps) for (l in t = e.defaultProps, t) o[l] === void 0 && (o[l] = t[l]);
  return {
    $$typeof: Oe,
    type: e,
    key: n,
    ref: r,
    props: o,
    _owner: ke.current
  };
}
k.Fragment = Re;
k.jsx = Q;
k.jsxs = Q;
K.exports = k;
var E = K.exports;
const {
  SvelteComponent: Le,
  assign: B,
  binding_callbacks: H,
  check_outros: Ne,
  children: $,
  claim_element: ee,
  claim_space: Ae,
  component_subscribe: G,
  compute_slots: We,
  create_slot: Me,
  detach: I,
  element: te,
  empty: q,
  exclude_internal_props: V,
  get_all_dirty_from_scope: Fe,
  get_slot_changes: ze,
  group_outros: De,
  init: Ue,
  insert_hydration: R,
  safe_not_equal: Be,
  set_custom_element_data: ne,
  space: He,
  transition_in: T,
  transition_out: W,
  update_slot_base: Ge
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
      R(n, t, r), o && o.m(t, null), e[9](t), s = !0;
    },
    p(n, r) {
      o && o.p && (!s || r & /*$$scope*/
      64) && Ge(
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
      s || (T(o, n), s = !0);
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
      t = te("react-portal-target"), s = He(), n && n.c(), l = q(), this.h();
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
      R(r, t, i), e[8](t), R(r, s, i), n && n.m(r, i), R(r, l, i), o = !0;
    },
    p(r, [i]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, i), i & /*$$slots*/
      16 && T(n, 1)) : (n = J(r), n.c(), T(n, 1), n.m(l.parentNode, l)) : n && (De(), W(n, 1, 1, () => {
        n = null;
      }), Ne());
    },
    i(r) {
      o || (T(n), o = !0);
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
    svelteInit: u
  } = t;
  const _ = O(X(t)), h = O();
  G(e, h, (d) => s(0, l = d));
  const c = O();
  G(e, c, (d) => s(1, o = d));
  const g = [], f = Ve("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: b,
    subSlotIndex: a
  } = de() || {}, m = u({
    parent: f,
    props: _,
    target: h,
    slot: c,
    slotKey: w,
    slotIndex: b,
    subSlotIndex: a,
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
    H[d ? "unshift" : "push"](() => {
      l = d, h.set(l);
    });
  }
  function S(d) {
    H[d ? "unshift" : "push"](() => {
      o = d, c.set(o);
    });
  }
  return e.$$set = (d) => {
    s(17, t = B(B({}, t), V(d))), "svelteInit" in d && s(5, u = d.svelteInit), "$$scope" in d && s(6, r = d.$$scope);
  }, t = V(t), [l, o, h, c, i, u, r, n, x, S];
}
class Ke extends Le {
  constructor(t) {
    super(), Ue(this, t, Ze, Ye, Be, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ct
} = window.__gradio__svelte__internal, Y = window.ms_globals.rerender, L = window.ms_globals.tree;
function Qe(e, t = {}) {
  function s(l) {
    const o = O(), n = new Ke({
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
          }, u = r.parent ?? L;
          return u.nodes = [...u.nodes, i], Y({
            createPortal: N,
            node: L
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== o), Y({
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
    const o = v.Children.toArray(e._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: i
        } = M(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...v.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(N(v.cloneElement(e._reactElement, {
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
      useCapture: u
    }) => {
      s.addEventListener(i, r, u);
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
  const r = se(), [i, u] = le([]), {
    forceClone: _
  } = fe(), h = _ ? !0 : t;
  return ie(() => {
    var b;
    if (!r.current || !e)
      return;
    let c = e;
    function g() {
      let a = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (a = c.children[0], a.tagName.toLowerCase() === "react-portal-target" && a.children[0] && (a = a.children[0])), nt(n, a), s && a.classList.add(...s.split(" ")), l) {
        const m = et(l);
        Object.keys(m).forEach((x) => {
          a.style[x] = m[x];
        });
      }
    }
    let f = null, w = null;
    if (h && window.MutationObserver) {
      let a = function() {
        var d, C, p;
        (d = r.current) != null && d.contains(c) && ((C = r.current) == null || C.removeChild(c));
        const {
          portals: x,
          clonedElement: S
        } = M(e);
        c = S, u(x), c.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          g();
        }, 50), (p = r.current) == null || p.appendChild(c);
      };
      a();
      const m = Se(() => {
        a(), f == null || f.disconnect(), f == null || f.observe(e, {
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
      c.style.display = "contents", g(), (b = r.current) == null || b.appendChild(c);
    return () => {
      var a, m;
      c.style.display = "", (a = r.current) != null && a.contains(c) && ((m = r.current) == null || m.removeChild(c)), f == null || f.disconnect();
    };
  }, [e, h, s, l, n, o, _]), v.createElement("react-child", {
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
  return v.createElement(rt, {
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
        let f, w, b = !1, a = t == null ? void 0 : t.forceClone;
        g instanceof Element ? f = g : (f = g.el, w = g.callback, b = g.clone ?? b, a = g.forceClone ?? a), a = a ?? !!w, i[c[c.length - 1]] = f ? w ? (...m) => (w(c[c.length - 1], m), /* @__PURE__ */ E.jsx(z, {
          ...o.ctx,
          params: m,
          forceClone: a,
          children: /* @__PURE__ */ E.jsx(Z, {
            slot: f,
            clone: b
          })
        })) : ot((m) => /* @__PURE__ */ E.jsx(z, {
          ...o.ctx,
          forceClone: a,
          children: /* @__PURE__ */ E.jsx(Z, {
            ...m,
            slot: f,
            clone: b
          })
        })) : i[c[c.length - 1]], i = r;
      });
      const u = "children";
      return o[u] && (r[u] = re(o[u], t, `${n}`)), r;
    });
}
const {
  withItemsContextProvider: st,
  useItems: lt,
  ItemHandler: at
} = pe("antd-segmented-options"), ut = Qe(st(["options", "default"], ({
  options: e,
  onChange: t,
  onValueChange: s,
  children: l,
  ...o
}) => {
  const {
    items: n
  } = lt(), r = n.options.length > 0 ? n.options : n.default;
  return /* @__PURE__ */ E.jsxs(E.Fragment, {
    children: [/* @__PURE__ */ E.jsx("div", {
      style: {
        display: "none"
      },
      children: l
    }), /* @__PURE__ */ E.jsx(me, {
      ...o,
      onChange: (i) => {
        t == null || t(i), s(i);
      },
      options: ce(() => e || re(r), [e, r])
    })]
  });
}));
export {
  ut as Segmented,
  ut as default
};
