import { i as me, a as z, r as pe, Z as O, g as _e, b as he } from "./Index-CwFrpMi6.js";
const I = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, ue = window.ms_globals.React.useRef, fe = window.ms_globals.React.useState, de = window.ms_globals.React.useEffect, H = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, ge = window.ms_globals.internalContext.useContextPropsContext, V = window.ms_globals.internalContext.ContextPropsProvider, xe = window.ms_globals.internalContext.FormItemContext, we = window.ms_globals.antd.Form, be = window.ms_globals.createItemsContext.createItemsContext;
var Ce = /\s/;
function Ee(e) {
  for (var t = e.length; t-- && Ce.test(e.charAt(t)); )
    ;
  return t;
}
var ve = /^\s+/;
function ye(e) {
  return e && e.slice(0, Ee(e) + 1).replace(ve, "");
}
var B = NaN, Ie = /^[-+]0x[0-9a-f]+$/i, Re = /^0b[01]+$/i, Pe = /^0o[0-7]+$/i, Se = parseInt;
function G(e) {
  if (typeof e == "number")
    return e;
  if (me(e))
    return B;
  if (z(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = z(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ye(e);
  var s = Re.test(e);
  return s || Pe.test(e) ? Se(e.slice(2), s ? 2 : 8) : Ie.test(e) ? B : +e;
}
var W = function() {
  return pe.Date.now();
}, Fe = "Expected a function", Oe = Math.max, ke = Math.min;
function je(e, t, s) {
  var i, r, n, o, l, a, _ = 0, g = !1, c = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(Fe);
  t = G(t) || 0, z(s) && (g = !!s.leading, c = "maxWait" in s, n = c ? Oe(G(s.maxWait) || 0, t) : n, h = "trailing" in s ? !!s.trailing : h);
  function m(p) {
    var E = i, F = r;
    return i = r = void 0, _ = p, o = e.apply(F, E), o;
  }
  function b(p) {
    return _ = p, l = setTimeout(f, t), g ? m(p) : o;
  }
  function C(p) {
    var E = p - a, F = p - _, U = t - E;
    return c ? ke(U, n - F) : U;
  }
  function u(p) {
    var E = p - a, F = p - _;
    return a === void 0 || E >= t || E < 0 || c && F >= n;
  }
  function f() {
    var p = W();
    if (u(p))
      return x(p);
    l = setTimeout(f, C(p));
  }
  function x(p) {
    return l = void 0, h && i ? m(p) : (i = r = void 0, o);
  }
  function R() {
    l !== void 0 && clearTimeout(l), _ = 0, i = a = r = l = void 0;
  }
  function d() {
    return l === void 0 ? o : x(W());
  }
  function v() {
    var p = W(), E = u(p);
    if (i = arguments, r = this, a = p, E) {
      if (l === void 0)
        return b(a);
      if (c)
        return clearTimeout(l), l = setTimeout(f, t), m(a);
    }
    return l === void 0 && (l = setTimeout(f, t)), o;
  }
  return v.cancel = R, v.flush = d, v;
}
var ne = {
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
var Te = I, Le = Symbol.for("react.element"), We = Symbol.for("react.fragment"), Ne = Object.prototype.hasOwnProperty, Ae = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ze = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function re(e, t, s) {
  var i, r = {}, n = null, o = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (i in t) Ne.call(t, i) && !ze.hasOwnProperty(i) && (r[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) r[i] === void 0 && (r[i] = t[i]);
  return {
    $$typeof: Le,
    type: e,
    key: n,
    ref: o,
    props: r,
    _owner: Ae.current
  };
}
L.Fragment = We;
L.jsx = re;
L.jsxs = re;
ne.exports = L;
var w = ne.exports;
const {
  SvelteComponent: Me,
  assign: q,
  binding_callbacks: J,
  check_outros: De,
  children: oe,
  claim_element: se,
  claim_space: He,
  component_subscribe: X,
  compute_slots: Ue,
  create_slot: Ve,
  detach: S,
  element: ie,
  empty: Y,
  exclude_internal_props: Z,
  get_all_dirty_from_scope: Be,
  get_slot_changes: Ge,
  group_outros: qe,
  init: Je,
  insert_hydration: k,
  safe_not_equal: Xe,
  set_custom_element_data: le,
  space: Ye,
  transition_in: j,
  transition_out: M,
  update_slot_base: Ze
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ke,
  getContext: Qe,
  onDestroy: $e,
  setContext: et
} = window.__gradio__svelte__internal;
function K(e) {
  let t, s;
  const i = (
    /*#slots*/
    e[7].default
  ), r = Ve(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ie("svelte-slot"), r && r.c(), this.h();
    },
    l(n) {
      t = se(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = oe(t);
      r && r.l(o), o.forEach(S), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      k(n, t, o), r && r.m(t, null), e[9](t), s = !0;
    },
    p(n, o) {
      r && r.p && (!s || o & /*$$scope*/
      64) && Ze(
        r,
        i,
        n,
        /*$$scope*/
        n[6],
        s ? Ge(
          i,
          /*$$scope*/
          n[6],
          o,
          null
        ) : Be(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      s || (j(r, n), s = !0);
    },
    o(n) {
      M(r, n), s = !1;
    },
    d(n) {
      n && S(t), r && r.d(n), e[9](null);
    }
  };
}
function tt(e) {
  let t, s, i, r, n = (
    /*$$slots*/
    e[4].default && K(e)
  );
  return {
    c() {
      t = ie("react-portal-target"), s = Ye(), n && n.c(), i = Y(), this.h();
    },
    l(o) {
      t = se(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), oe(t).forEach(S), s = He(o), n && n.l(o), i = Y(), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      k(o, t, l), e[8](t), k(o, s, l), n && n.m(o, l), k(o, i, l), r = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, l), l & /*$$slots*/
      16 && j(n, 1)) : (n = K(o), n.c(), j(n, 1), n.m(i.parentNode, i)) : n && (qe(), M(n, 1, 1, () => {
        n = null;
      }), De());
    },
    i(o) {
      r || (j(n), r = !0);
    },
    o(o) {
      M(n), r = !1;
    },
    d(o) {
      o && (S(t), S(s), S(i)), e[8](null), n && n.d(o);
    }
  };
}
function Q(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function nt(e, t, s) {
  let i, r, {
    $$slots: n = {},
    $$scope: o
  } = t;
  const l = Ue(n);
  let {
    svelteInit: a
  } = t;
  const _ = O(Q(t)), g = O();
  X(e, g, (d) => s(0, i = d));
  const c = O();
  X(e, c, (d) => s(1, r = d));
  const h = [], m = Qe("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: C,
    subSlotIndex: u
  } = _e() || {}, f = a({
    parent: m,
    props: _,
    target: g,
    slot: c,
    slotKey: b,
    slotIndex: C,
    subSlotIndex: u,
    onDestroy(d) {
      h.push(d);
    }
  });
  et("$$ms-gr-react-wrapper", f), Ke(() => {
    _.set(Q(t));
  }), $e(() => {
    h.forEach((d) => d());
  });
  function x(d) {
    J[d ? "unshift" : "push"](() => {
      i = d, g.set(i);
    });
  }
  function R(d) {
    J[d ? "unshift" : "push"](() => {
      r = d, c.set(r);
    });
  }
  return e.$$set = (d) => {
    s(17, t = q(q({}, t), Z(d))), "svelteInit" in d && s(5, a = d.svelteInit), "$$scope" in d && s(6, o = d.$$scope);
  }, t = Z(t), [i, r, g, c, l, a, o, n, x, R];
}
class rt extends Me {
  constructor(t) {
    super(), Je(this, t, nt, tt, Xe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ht
} = window.__gradio__svelte__internal, $ = window.ms_globals.rerender, N = window.ms_globals.tree;
function ot(e, t = {}) {
  function s(i) {
    const r = O(), n = new rt({
      ...i,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, a = o.parent ?? N;
          return a.nodes = [...a.nodes, l], $({
            createPortal: A,
            node: N
          }), o.onDestroy(() => {
            a.nodes = a.nodes.filter((_) => _.svelteInstance !== r), $({
              createPortal: A,
              node: N
            });
          }), l;
        },
        ...i.props
      }
    });
    return r.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((r) => {
      window.ms_globals.initialize = () => {
        r();
      };
    })), window.ms_globals.initializePromise.then(() => {
      i(s);
    });
  });
}
const st = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function it(e) {
  return e ? Object.keys(e).reduce((t, s) => {
    const i = e[s];
    return t[s] = lt(s, i), t;
  }, {}) : {};
}
function lt(e, t) {
  return typeof t == "number" && !st.includes(e) ? t + "px" : t;
}
function D(e) {
  const t = [], s = e.cloneNode(!1);
  if (e._reactElement) {
    const r = I.Children.toArray(e._reactElement.props.children).map((n) => {
      if (I.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = D(n.props.el);
        return I.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...I.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(A(I.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: r
    }), s)), {
      clonedElement: s,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((r) => {
    e.getEventListeners(r).forEach(({
      listener: o,
      type: l,
      useCapture: a
    }) => {
      s.addEventListener(l, o, a);
    });
  });
  const i = Array.from(e.childNodes);
  for (let r = 0; r < i.length; r++) {
    const n = i[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: l
      } = D(n);
      t.push(...l), s.appendChild(o);
    } else n.nodeType === 3 && s.appendChild(n.cloneNode());
  }
  return {
    clonedElement: s,
    portals: t
  };
}
function ct(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const y = ae(({
  slot: e,
  clone: t,
  className: s,
  style: i,
  observeAttributes: r
}, n) => {
  const o = ue(), [l, a] = fe([]), {
    forceClone: _
  } = ge(), g = _ ? !0 : t;
  return de(() => {
    var C;
    if (!o.current || !e)
      return;
    let c = e;
    function h() {
      let u = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (u = c.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), ct(n, u), s && u.classList.add(...s.split(" ")), i) {
        const f = it(i);
        Object.keys(f).forEach((x) => {
          u.style[x] = f[x];
        });
      }
    }
    let m = null, b = null;
    if (g && window.MutationObserver) {
      let u = function() {
        var d, v, p;
        (d = o.current) != null && d.contains(c) && ((v = o.current) == null || v.removeChild(c));
        const {
          portals: x,
          clonedElement: R
        } = D(e);
        c = R, a(x), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          h();
        }, 50), (p = o.current) == null || p.appendChild(c);
      };
      u();
      const f = je(() => {
        u(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      m = new window.MutationObserver(f), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", h(), (C = o.current) == null || C.appendChild(c);
    return () => {
      var u, f;
      c.style.display = "", (u = o.current) != null && u.contains(c) && ((f = o.current) == null || f.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, g, s, i, n, r, _]), I.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
});
function at(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function T(e, t = !1) {
  try {
    if (he(e))
      return e;
    if (t && !at(e))
      return;
    if (typeof e == "string") {
      let s = e.trim();
      return s.startsWith(";") && (s = s.slice(1)), s.endsWith(";") && (s = s.slice(0, -1)), new Function(`return (...args) => (${s})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function P(e, t) {
  return H(() => T(e, t), [e, t]);
}
const ut = ({
  children: e,
  ...t
}) => /* @__PURE__ */ w.jsx(w.Fragment, {
  children: e(t)
});
function ft(e) {
  return I.createElement(ut, {
    children: e
  });
}
function ce(e, t, s) {
  const i = e.filter(Boolean);
  if (i.length !== 0)
    return i.map((r, n) => {
      var _;
      if (typeof r != "object")
        return r;
      const o = {
        ...r.props,
        key: ((_ = r.props) == null ? void 0 : _.key) ?? (s ? `${s}-${n}` : `${n}`)
      };
      let l = o;
      Object.keys(r.slots).forEach((g) => {
        if (!r.slots[g] || !(r.slots[g] instanceof Element) && !r.slots[g].el)
          return;
        const c = g.split(".");
        c.forEach((f, x) => {
          l[f] || (l[f] = {}), x !== c.length - 1 && (l = o[f]);
        });
        const h = r.slots[g];
        let m, b, C = !1, u = t == null ? void 0 : t.forceClone;
        h instanceof Element ? m = h : (m = h.el, b = h.callback, C = h.clone ?? C, u = h.forceClone ?? u), u = u ?? !!b, l[c[c.length - 1]] = m ? b ? (...f) => (b(c[c.length - 1], f), /* @__PURE__ */ w.jsx(V, {
          ...r.ctx,
          params: f,
          forceClone: u,
          children: /* @__PURE__ */ w.jsx(y, {
            slot: m,
            clone: C
          })
        })) : ft((f) => /* @__PURE__ */ w.jsx(V, {
          ...r.ctx,
          forceClone: u,
          children: /* @__PURE__ */ w.jsx(y, {
            ...f,
            slot: m,
            clone: C
          })
        })) : l[c[c.length - 1]], l = o;
      });
      const a = "children";
      return r[a] && (o[a] = ce(r[a], t, `${n}`)), o;
    });
}
const {
  withItemsContextProvider: dt,
  useItems: mt,
  ItemHandler: gt
} = be("antd-form-item-rules");
function pt(e) {
  const t = e.pattern;
  return {
    ...e,
    pattern: (() => {
      if (typeof t == "string" && t.startsWith("/")) {
        const s = t.match(/^\/(.+)\/([gimuy]*)$/);
        if (s) {
          const [, i, r] = s;
          return new RegExp(i, r);
        }
      }
      return typeof t == "string" ? new RegExp(t) : void 0;
    })() ? new RegExp(t) : void 0,
    defaultField: T(e.defaultField) || e.defaultField,
    transform: T(e.transform),
    validator: T(e.validator)
  };
}
function ee(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const te = ({
  children: e,
  ...t
}) => /* @__PURE__ */ w.jsx(xe.Provider, {
  value: H(() => t, [t]),
  children: e
}), xt = ot(dt(["rules"], ({
  slots: e,
  getValueFromEvent: t,
  getValueProps: s,
  normalize: i,
  shouldUpdate: r,
  tooltip: n,
  rules: o,
  children: l,
  hasFeedback: a,
  ..._
}) => {
  const g = e["tooltip.icon"] || e["tooltip.title"] || typeof n == "object", c = typeof a == "object", h = ee(a), m = P(h.icons), b = P(t), C = P(s), u = P(i), f = P(r), x = ee(n), R = P(x.afterOpenChange), d = P(x.getPopupContainer), {
    items: {
      rules: v
    }
  } = mt();
  return /* @__PURE__ */ w.jsx(we.Item, {
    ..._,
    hasFeedback: c ? {
      ...h,
      icons: m || h.icons
    } : a,
    getValueFromEvent: b,
    getValueProps: C,
    normalize: u,
    shouldUpdate: f || r,
    rules: H(() => {
      var p;
      return (p = o || ce(v)) == null ? void 0 : p.map((E) => pt(E));
    }, [v, o]),
    tooltip: e.tooltip ? /* @__PURE__ */ w.jsx(y, {
      slot: e.tooltip
    }) : g ? {
      ...x,
      afterOpenChange: R,
      getPopupContainer: d,
      icon: e["tooltip.icon"] ? /* @__PURE__ */ w.jsx(y, {
        slot: e["tooltip.icon"]
      }) : x.icon,
      title: e["tooltip.title"] ? /* @__PURE__ */ w.jsx(y, {
        slot: e["tooltip.title"]
      }) : x.title
    } : n,
    extra: e.extra ? /* @__PURE__ */ w.jsx(y, {
      slot: e.extra
    }) : _.extra,
    help: e.help ? /* @__PURE__ */ w.jsx(y, {
      slot: e.help
    }) : _.help,
    label: e.label ? /* @__PURE__ */ w.jsx(y, {
      slot: e.label
    }) : _.label,
    children: f || r ? () => /* @__PURE__ */ w.jsx(te, {
      children: l
    }) : /* @__PURE__ */ w.jsx(te, {
      children: l
    })
  });
}));
export {
  xt as FormItem,
  xt as default
};
