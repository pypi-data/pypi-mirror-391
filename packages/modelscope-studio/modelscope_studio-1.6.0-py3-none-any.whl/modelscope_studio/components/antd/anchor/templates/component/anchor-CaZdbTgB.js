import { i as ue, a as F, r as de, Z as R, g as fe, b as me } from "./Index-tXcwJW5g.js";
const v = window.ms_globals.React, Q = window.ms_globals.React.useMemo, le = window.ms_globals.React.forwardRef, ie = window.ms_globals.React.useRef, ce = window.ms_globals.React.useState, ae = window.ms_globals.React.useEffect, A = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, z = window.ms_globals.internalContext.ContextPropsProvider, he = window.ms_globals.antd.Anchor, pe = window.ms_globals.createItemsContext.createItemsContext;
var ge = /\s/;
function we(t) {
  for (var e = t.length; e-- && ge.test(t.charAt(e)); )
    ;
  return e;
}
var be = /^\s+/;
function xe(t) {
  return t && t.slice(0, we(t) + 1).replace(be, "");
}
var D = NaN, Ce = /^[-+]0x[0-9a-f]+$/i, ye = /^0b[01]+$/i, ve = /^0o[0-7]+$/i, Ee = parseInt;
function U(t) {
  if (typeof t == "number")
    return t;
  if (ue(t))
    return D;
  if (F(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = F(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = xe(t);
  var o = ye.test(t);
  return o || ve.test(t) ? Ee(t.slice(2), o ? 2 : 8) : Ce.test(t) ? D : +t;
}
var j = function() {
  return de.Date.now();
}, Ie = "Expected a function", Se = Math.max, Pe = Math.min;
function Re(t, e, o) {
  var l, s, n, r, i, a, g = 0, w = !1, c = !1, h = !0;
  if (typeof t != "function")
    throw new TypeError(Ie);
  e = U(e) || 0, F(o) && (w = !!o.leading, c = "maxWait" in o, n = c ? Se(U(o.maxWait) || 0, e) : n, h = "trailing" in o ? !!o.trailing : h);
  function u(m) {
    var y = l, P = s;
    return l = s = void 0, g = m, r = t.apply(P, y), r;
  }
  function b(m) {
    return g = m, i = setTimeout(_, e), w ? u(m) : r;
  }
  function x(m) {
    var y = m - a, P = m - g, M = e - y;
    return c ? Pe(M, n - P) : M;
  }
  function d(m) {
    var y = m - a, P = m - g;
    return a === void 0 || y >= e || y < 0 || c && P >= n;
  }
  function _() {
    var m = j();
    if (d(m))
      return p(m);
    i = setTimeout(_, x(m));
  }
  function p(m) {
    return i = void 0, h && l ? u(m) : (l = s = void 0, r);
  }
  function E() {
    i !== void 0 && clearTimeout(i), g = 0, l = a = s = i = void 0;
  }
  function f() {
    return i === void 0 ? r : p(j());
  }
  function I() {
    var m = j(), y = d(m);
    if (l = arguments, s = this, a = m, y) {
      if (i === void 0)
        return b(a);
      if (c)
        return clearTimeout(i), i = setTimeout(_, e), u(a);
    }
    return i === void 0 && (i = setTimeout(_, e)), r;
  }
  return I.cancel = E, I.flush = f, I;
}
var $ = {
  exports: {}
}, O = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ke = v, Te = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Le = ke.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ae = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ee(t, e, o) {
  var l, s = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (r = e.ref);
  for (l in e) je.call(e, l) && !Ae.hasOwnProperty(l) && (s[l] = e[l]);
  if (t && t.defaultProps) for (l in e = t.defaultProps, e) s[l] === void 0 && (s[l] = e[l]);
  return {
    $$typeof: Te,
    type: t,
    key: n,
    ref: r,
    props: s,
    _owner: Le.current
  };
}
O.Fragment = Oe;
O.jsx = ee;
O.jsxs = ee;
$.exports = O;
var C = $.exports;
const {
  SvelteComponent: Fe,
  assign: B,
  binding_callbacks: H,
  check_outros: Ne,
  children: te,
  claim_element: ne,
  claim_space: We,
  component_subscribe: G,
  compute_slots: Me,
  create_slot: ze,
  detach: S,
  element: re,
  empty: q,
  exclude_internal_props: V,
  get_all_dirty_from_scope: De,
  get_slot_changes: Ue,
  group_outros: Be,
  init: He,
  insert_hydration: k,
  safe_not_equal: Ge,
  set_custom_element_data: se,
  space: qe,
  transition_in: T,
  transition_out: N,
  update_slot_base: Ve
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function J(t) {
  let e, o;
  const l = (
    /*#slots*/
    t[7].default
  ), s = ze(
    l,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = re("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      e = ne(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = te(e);
      s && s.l(r), r.forEach(S), this.h();
    },
    h() {
      se(e, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      k(n, e, r), s && s.m(e, null), t[9](e), o = !0;
    },
    p(n, r) {
      s && s.p && (!o || r & /*$$scope*/
      64) && Ve(
        s,
        l,
        n,
        /*$$scope*/
        n[6],
        o ? Ue(
          l,
          /*$$scope*/
          n[6],
          r,
          null
        ) : De(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (T(s, n), o = !0);
    },
    o(n) {
      N(s, n), o = !1;
    },
    d(n) {
      n && S(e), s && s.d(n), t[9](null);
    }
  };
}
function Ke(t) {
  let e, o, l, s, n = (
    /*$$slots*/
    t[4].default && J(t)
  );
  return {
    c() {
      e = re("react-portal-target"), o = qe(), n && n.c(), l = q(), this.h();
    },
    l(r) {
      e = ne(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), te(e).forEach(S), o = We(r), n && n.l(r), l = q(), this.h();
    },
    h() {
      se(e, "class", "svelte-1rt0kpf");
    },
    m(r, i) {
      k(r, e, i), t[8](e), k(r, o, i), n && n.m(r, i), k(r, l, i), s = !0;
    },
    p(r, [i]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, i), i & /*$$slots*/
      16 && T(n, 1)) : (n = J(r), n.c(), T(n, 1), n.m(l.parentNode, l)) : n && (Be(), N(n, 1, 1, () => {
        n = null;
      }), Ne());
    },
    i(r) {
      s || (T(n), s = !0);
    },
    o(r) {
      N(n), s = !1;
    },
    d(r) {
      r && (S(e), S(o), S(l)), t[8](null), n && n.d(r);
    }
  };
}
function X(t) {
  const {
    svelteInit: e,
    ...o
  } = t;
  return o;
}
function Qe(t, e, o) {
  let l, s, {
    $$slots: n = {},
    $$scope: r
  } = e;
  const i = Me(n);
  let {
    svelteInit: a
  } = e;
  const g = R(X(e)), w = R();
  G(t, w, (f) => o(0, l = f));
  const c = R();
  G(t, c, (f) => o(1, s = f));
  const h = [], u = Xe("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: x,
    subSlotIndex: d
  } = fe() || {}, _ = a({
    parent: u,
    props: g,
    target: w,
    slot: c,
    slotKey: b,
    slotIndex: x,
    subSlotIndex: d,
    onDestroy(f) {
      h.push(f);
    }
  });
  Ze("$$ms-gr-react-wrapper", _), Je(() => {
    g.set(X(e));
  }), Ye(() => {
    h.forEach((f) => f());
  });
  function p(f) {
    H[f ? "unshift" : "push"](() => {
      l = f, w.set(l);
    });
  }
  function E(f) {
    H[f ? "unshift" : "push"](() => {
      s = f, c.set(s);
    });
  }
  return t.$$set = (f) => {
    o(17, e = B(B({}, e), V(f))), "svelteInit" in f && o(5, a = f.svelteInit), "$$scope" in f && o(6, r = f.$$scope);
  }, e = V(e), [l, s, w, c, i, a, r, n, p, E];
}
class $e extends Fe {
  constructor(e) {
    super(), He(this, e, Qe, Ke, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ft
} = window.__gradio__svelte__internal, Y = window.ms_globals.rerender, L = window.ms_globals.tree;
function et(t, e = {}) {
  function o(l) {
    const s = R(), n = new $e({
      ...l,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const i = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: t,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: e.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, a = r.parent ?? L;
          return a.nodes = [...a.nodes, i], Y({
            createPortal: A,
            node: L
          }), r.onDestroy(() => {
            a.nodes = a.nodes.filter((g) => g.svelteInstance !== s), Y({
              createPortal: A,
              node: L
            });
          }), i;
        },
        ...l.props
      }
    });
    return s.set(n), n;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((s) => {
      window.ms_globals.initialize = () => {
        s();
      };
    })), window.ms_globals.initializePromise.then(() => {
      l(o);
    });
  });
}
function tt(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function nt(t, e = !1) {
  try {
    if (me(t))
      return t;
    if (e && !tt(t))
      return;
    if (typeof t == "string") {
      let o = t.trim();
      return o.startsWith(";") && (o = o.slice(1)), o.endsWith(";") && (o = o.slice(0, -1)), new Function(`return (...args) => (${o})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function Z(t, e) {
  return Q(() => nt(t, e), [t, e]);
}
const rt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function st(t) {
  return t ? Object.keys(t).reduce((e, o) => {
    const l = t[o];
    return e[o] = ot(o, l), e;
  }, {}) : {};
}
function ot(t, e) {
  return typeof e == "number" && !rt.includes(t) ? e + "px" : e;
}
function W(t) {
  const e = [], o = t.cloneNode(!1);
  if (t._reactElement) {
    const s = v.Children.toArray(t._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: i
        } = W(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...v.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return s.originalChildren = t._reactElement.props.children, e.push(A(v.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: s
    }), o)), {
      clonedElement: o,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((s) => {
    t.getEventListeners(s).forEach(({
      listener: r,
      type: i,
      useCapture: a
    }) => {
      o.addEventListener(i, r, a);
    });
  });
  const l = Array.from(t.childNodes);
  for (let s = 0; s < l.length; s++) {
    const n = l[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: i
      } = W(n);
      e.push(...i), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: e
  };
}
function lt(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const K = le(({
  slot: t,
  clone: e,
  className: o,
  style: l,
  observeAttributes: s
}, n) => {
  const r = ie(), [i, a] = ce([]), {
    forceClone: g
  } = _e(), w = g ? !0 : e;
  return ae(() => {
    var x;
    if (!r.current || !t)
      return;
    let c = t;
    function h() {
      let d = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (d = c.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), lt(n, d), o && d.classList.add(...o.split(" ")), l) {
        const _ = st(l);
        Object.keys(_).forEach((p) => {
          d.style[p] = _[p];
        });
      }
    }
    let u = null, b = null;
    if (w && window.MutationObserver) {
      let d = function() {
        var f, I, m;
        (f = r.current) != null && f.contains(c) && ((I = r.current) == null || I.removeChild(c));
        const {
          portals: p,
          clonedElement: E
        } = W(t);
        c = E, a(p), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          h();
        }, 50), (m = r.current) == null || m.appendChild(c);
      };
      d();
      const _ = Re(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      u = new window.MutationObserver(_), u.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", h(), (x = r.current) == null || x.appendChild(c);
    return () => {
      var d, _;
      c.style.display = "", (d = r.current) != null && d.contains(c) && ((_ = r.current) == null || _.removeChild(c)), u == null || u.disconnect();
    };
  }, [t, w, o, l, n, s, g]), v.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...i);
}), it = ({
  children: t,
  ...e
}) => /* @__PURE__ */ C.jsx(C.Fragment, {
  children: t(e)
});
function ct(t) {
  return v.createElement(it, {
    children: t
  });
}
function oe(t, e, o) {
  const l = t.filter(Boolean);
  if (l.length !== 0)
    return l.map((s, n) => {
      var g, w;
      if (typeof s != "object")
        return e != null && e.fallback ? e.fallback(s) : s;
      const r = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...s.props,
        key: ((g = s.props) == null ? void 0 : g.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...s.props,
        key: ((w = s.props) == null ? void 0 : w.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let i = r;
      Object.keys(s.slots).forEach((c) => {
        if (!s.slots[c] || !(s.slots[c] instanceof Element) && !s.slots[c].el)
          return;
        const h = c.split(".");
        h.forEach((p, E) => {
          i[p] || (i[p] = {}), E !== h.length - 1 && (i = r[p]);
        });
        const u = s.slots[c];
        let b, x, d = (e == null ? void 0 : e.clone) ?? !1, _ = e == null ? void 0 : e.forceClone;
        u instanceof Element ? b = u : (b = u.el, x = u.callback, d = u.clone ?? d, _ = u.forceClone ?? _), _ = _ ?? !!x, i[h[h.length - 1]] = b ? x ? (...p) => (x(h[h.length - 1], p), /* @__PURE__ */ C.jsx(z, {
          ...s.ctx,
          params: p,
          forceClone: _,
          children: /* @__PURE__ */ C.jsx(K, {
            slot: b,
            clone: d
          })
        })) : ct((p) => /* @__PURE__ */ C.jsx(z, {
          ...s.ctx,
          forceClone: _,
          children: /* @__PURE__ */ C.jsx(K, {
            ...p,
            slot: b,
            clone: d
          })
        })) : i[h[h.length - 1]], i = r;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return s[a] ? r[a] = oe(s[a], e, `${n}`) : e != null && e.children && (r[a] = void 0, Reflect.deleteProperty(r, a)), r;
    });
}
const {
  useItems: at,
  withItemsContextProvider: ut,
  ItemHandler: mt
} = pe("antd-anchor-items"), _t = et(ut(["items", "default"], ({
  getContainer: t,
  getCurrentAnchor: e,
  children: o,
  items: l,
  ...s
}) => {
  const n = Z(t), r = Z(e), {
    items: i
  } = at(), a = i.items.length > 0 ? i.items : i.default;
  return /* @__PURE__ */ C.jsxs(C.Fragment, {
    children: [/* @__PURE__ */ C.jsx("div", {
      style: {
        display: "none"
      },
      children: o
    }), /* @__PURE__ */ C.jsx(he, {
      ...s,
      items: Q(() => l || oe(a, {
        clone: !0
      }), [l, a]),
      getContainer: n,
      getCurrentAnchor: r
    })]
  });
}));
export {
  _t as Anchor,
  _t as default
};
