import { i as ae, a as W, r as de, Z as P, g as ue } from "./Index-Nmz8KFIS.js";
const y = window.ms_globals.React, oe = window.ms_globals.React.forwardRef, se = window.ms_globals.React.useRef, le = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, ce = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, z = window.ms_globals.internalContext.ContextPropsProvider, me = window.ms_globals.antd.Timeline, pe = window.ms_globals.createItemsContext.createItemsContext;
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
var U = NaN, be = /^[-+]0x[0-9a-f]+$/i, xe = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Ce = parseInt;
function B(e) {
  if (typeof e == "number")
    return e;
  if (ae(e))
    return U;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = we(e);
  var s = xe.test(e);
  return s || Ee.test(e) ? Ce(e.slice(2), s ? 2 : 8) : be.test(e) ? U : +e;
}
var L = function() {
  return de.Date.now();
}, ye = "Expected a function", ve = Math.max, Ie = Math.min;
function Se(e, t, s) {
  var l, r, n, o, i, d, _ = 0, h = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(ye);
  t = B(t) || 0, W(s) && (h = !!s.leading, c = "maxWait" in s, n = c ? ve(B(s.maxWait) || 0, t) : n, g = "trailing" in s ? !!s.trailing : g);
  function f(p) {
    var C = l, T = r;
    return l = r = void 0, _ = p, o = e.apply(T, C), o;
  }
  function w(p) {
    return _ = p, i = setTimeout(m, t), h ? f(p) : o;
  }
  function x(p) {
    var C = p - d, T = p - _, F = t - C;
    return c ? Ie(F, n - T) : F;
  }
  function a(p) {
    var C = p - d, T = p - _;
    return d === void 0 || C >= t || C < 0 || c && T >= n;
  }
  function m() {
    var p = L();
    if (a(p))
      return E(p);
    i = setTimeout(m, x(p));
  }
  function E(p) {
    return i = void 0, g && l ? f(p) : (l = r = void 0, o);
  }
  function S() {
    i !== void 0 && clearTimeout(i), _ = 0, l = d = r = i = void 0;
  }
  function u() {
    return i === void 0 ? o : E(L());
  }
  function v() {
    var p = L(), C = a(p);
    if (l = arguments, r = this, d = p, C) {
      if (i === void 0)
        return w(d);
      if (c)
        return clearTimeout(i), i = setTimeout(m, t), f(d);
    }
    return i === void 0 && (i = setTimeout(m, t)), o;
  }
  return v.cancel = S, v.flush = u, v;
}
var K = {
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
var Te = y, Pe = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), Re = Object.prototype.hasOwnProperty, ke = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, je = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(e, t, s) {
  var l, r = {}, n = null, o = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (l in t) Re.call(t, l) && !je.hasOwnProperty(l) && (r[l] = t[l]);
  if (e && e.defaultProps) for (l in t = e.defaultProps, t) r[l] === void 0 && (r[l] = t[l]);
  return {
    $$typeof: Pe,
    type: e,
    key: n,
    ref: o,
    props: r,
    _owner: ke.current
  };
}
j.Fragment = Oe;
j.jsx = Q;
j.jsxs = Q;
K.exports = j;
var b = K.exports;
const {
  SvelteComponent: Le,
  assign: H,
  binding_callbacks: G,
  check_outros: Ne,
  children: $,
  claim_element: ee,
  claim_space: Ae,
  component_subscribe: q,
  compute_slots: We,
  create_slot: De,
  detach: I,
  element: te,
  empty: V,
  exclude_internal_props: J,
  get_all_dirty_from_scope: Me,
  get_slot_changes: Fe,
  group_outros: ze,
  init: Ue,
  insert_hydration: O,
  safe_not_equal: Be,
  set_custom_element_data: ne,
  space: He,
  transition_in: R,
  transition_out: D,
  update_slot_base: Ge
} = window.__gradio__svelte__internal, {
  beforeUpdate: qe,
  getContext: Ve,
  onDestroy: Je,
  setContext: Xe
} = window.__gradio__svelte__internal;
function X(e) {
  let t, s;
  const l = (
    /*#slots*/
    e[7].default
  ), r = De(
    l,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = te("svelte-slot"), r && r.c(), this.h();
    },
    l(n) {
      t = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = $(t);
      r && r.l(o), o.forEach(I), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      O(n, t, o), r && r.m(t, null), e[9](t), s = !0;
    },
    p(n, o) {
      r && r.p && (!s || o & /*$$scope*/
      64) && Ge(
        r,
        l,
        n,
        /*$$scope*/
        n[6],
        s ? Fe(
          l,
          /*$$scope*/
          n[6],
          o,
          null
        ) : Me(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      s || (R(r, n), s = !0);
    },
    o(n) {
      D(r, n), s = !1;
    },
    d(n) {
      n && I(t), r && r.d(n), e[9](null);
    }
  };
}
function Ye(e) {
  let t, s, l, r, n = (
    /*$$slots*/
    e[4].default && X(e)
  );
  return {
    c() {
      t = te("react-portal-target"), s = He(), n && n.c(), l = V(), this.h();
    },
    l(o) {
      t = ee(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(t).forEach(I), s = Ae(o), n && n.l(o), l = V(), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(o, i) {
      O(o, t, i), e[8](t), O(o, s, i), n && n.m(o, i), O(o, l, i), r = !0;
    },
    p(o, [i]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, i), i & /*$$slots*/
      16 && R(n, 1)) : (n = X(o), n.c(), R(n, 1), n.m(l.parentNode, l)) : n && (ze(), D(n, 1, 1, () => {
        n = null;
      }), Ne());
    },
    i(o) {
      r || (R(n), r = !0);
    },
    o(o) {
      D(n), r = !1;
    },
    d(o) {
      o && (I(t), I(s), I(l)), e[8](null), n && n.d(o);
    }
  };
}
function Y(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function Ze(e, t, s) {
  let l, r, {
    $$slots: n = {},
    $$scope: o
  } = t;
  const i = We(n);
  let {
    svelteInit: d
  } = t;
  const _ = P(Y(t)), h = P();
  q(e, h, (u) => s(0, l = u));
  const c = P();
  q(e, c, (u) => s(1, r = u));
  const g = [], f = Ve("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: x,
    subSlotIndex: a
  } = ue() || {}, m = d({
    parent: f,
    props: _,
    target: h,
    slot: c,
    slotKey: w,
    slotIndex: x,
    subSlotIndex: a,
    onDestroy(u) {
      g.push(u);
    }
  });
  Xe("$$ms-gr-react-wrapper", m), qe(() => {
    _.set(Y(t));
  }), Je(() => {
    g.forEach((u) => u());
  });
  function E(u) {
    G[u ? "unshift" : "push"](() => {
      l = u, h.set(l);
    });
  }
  function S(u) {
    G[u ? "unshift" : "push"](() => {
      r = u, c.set(r);
    });
  }
  return e.$$set = (u) => {
    s(17, t = H(H({}, t), J(u))), "svelteInit" in u && s(5, d = u.svelteInit), "$$scope" in u && s(6, o = u.$$scope);
  }, t = J(t), [l, r, h, c, i, d, o, n, E, S];
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
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, N = window.ms_globals.tree;
function Qe(e, t = {}) {
  function s(l) {
    const r = P(), n = new Ke({
      ...l,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const i = {
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
          }, d = o.parent ?? N;
          return d.nodes = [...d.nodes, i], Z({
            createPortal: A,
            node: N
          }), o.onDestroy(() => {
            d.nodes = d.nodes.filter((_) => _.svelteInstance !== r), Z({
              createPortal: A,
              node: N
            });
          }), i;
        },
        ...l.props
      }
    });
    return r.set(n), n;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((r) => {
      window.ms_globals.initialize = () => {
        r();
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
    const r = y.Children.toArray(e._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: i
        } = M(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...y.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(A(y.cloneElement(e._reactElement, {
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
      type: i,
      useCapture: d
    }) => {
      s.addEventListener(i, o, d);
    });
  });
  const l = Array.from(e.childNodes);
  for (let r = 0; r < l.length; r++) {
    const n = l[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: i
      } = M(n);
      t.push(...i), s.appendChild(o);
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
const k = oe(({
  slot: e,
  clone: t,
  className: s,
  style: l,
  observeAttributes: r
}, n) => {
  const o = se(), [i, d] = le([]), {
    forceClone: _
  } = fe(), h = _ ? !0 : t;
  return ie(() => {
    var x;
    if (!o.current || !e)
      return;
    let c = e;
    function g() {
      let a = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (a = c.children[0], a.tagName.toLowerCase() === "react-portal-target" && a.children[0] && (a = a.children[0])), nt(n, a), s && a.classList.add(...s.split(" ")), l) {
        const m = et(l);
        Object.keys(m).forEach((E) => {
          a.style[E] = m[E];
        });
      }
    }
    let f = null, w = null;
    if (h && window.MutationObserver) {
      let a = function() {
        var u, v, p;
        (u = o.current) != null && u.contains(c) && ((v = o.current) == null || v.removeChild(c));
        const {
          portals: E,
          clonedElement: S
        } = M(e);
        c = S, d(E), c.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          g();
        }, 50), (p = o.current) == null || p.appendChild(c);
      };
      a();
      const m = Se(() => {
        a(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      f = new window.MutationObserver(m), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (x = o.current) == null || x.appendChild(c);
    return () => {
      var a, m;
      c.style.display = "", (a = o.current) != null && a.contains(c) && ((m = o.current) == null || m.removeChild(c)), f == null || f.disconnect();
    };
  }, [e, h, s, l, n, r, _]), y.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...i);
}), rt = ({
  children: e,
  ...t
}) => /* @__PURE__ */ b.jsx(b.Fragment, {
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
    return l.map((r, n) => {
      var _;
      if (typeof r != "object")
        return r;
      const o = {
        ...r.props,
        key: ((_ = r.props) == null ? void 0 : _.key) ?? (s ? `${s}-${n}` : `${n}`)
      };
      let i = o;
      Object.keys(r.slots).forEach((h) => {
        if (!r.slots[h] || !(r.slots[h] instanceof Element) && !r.slots[h].el)
          return;
        const c = h.split(".");
        c.forEach((m, E) => {
          i[m] || (i[m] = {}), E !== c.length - 1 && (i = o[m]);
        });
        const g = r.slots[h];
        let f, w, x = !1, a = t == null ? void 0 : t.forceClone;
        g instanceof Element ? f = g : (f = g.el, w = g.callback, x = g.clone ?? x, a = g.forceClone ?? a), a = a ?? !!w, i[c[c.length - 1]] = f ? w ? (...m) => (w(c[c.length - 1], m), /* @__PURE__ */ b.jsx(z, {
          ...r.ctx,
          params: m,
          forceClone: a,
          children: /* @__PURE__ */ b.jsx(k, {
            slot: f,
            clone: x
          })
        })) : ot((m) => /* @__PURE__ */ b.jsx(z, {
          ...r.ctx,
          forceClone: a,
          children: /* @__PURE__ */ b.jsx(k, {
            ...m,
            slot: f,
            clone: x
          })
        })) : i[c[c.length - 1]], i = o;
      });
      const d = "children";
      return r[d] && (o[d] = re(r[d], t, `${n}`)), o;
    });
}
const {
  withItemsContextProvider: st,
  useItems: lt,
  ItemHandler: at
} = pe("antd-timeline-items"), dt = Qe(st(["items", "default"], ({
  slots: e,
  items: t,
  children: s,
  ...l
}) => {
  const {
    items: r
  } = lt(), n = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ b.jsxs(b.Fragment, {
    children: [/* @__PURE__ */ b.jsx("div", {
      style: {
        display: "none"
      },
      children: s
    }), /* @__PURE__ */ b.jsx(me, {
      ...l,
      items: ce(() => t || re(n), [t, n]),
      pending: e.pending ? /* @__PURE__ */ b.jsx(k, {
        slot: e.pending
      }) : l.pending,
      pendingDot: e.pendingDot ? /* @__PURE__ */ b.jsx(k, {
        slot: e.pendingDot
      }) : l.pendingDot
    })]
  });
}));
export {
  dt as Timeline,
  dt as default
};
