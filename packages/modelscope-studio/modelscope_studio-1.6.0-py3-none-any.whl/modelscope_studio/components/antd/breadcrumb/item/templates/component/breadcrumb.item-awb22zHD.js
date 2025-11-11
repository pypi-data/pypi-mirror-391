import { i as me, a as B, r as he, Z as k, g as pe, b as _e } from "./Index-BXAGP9AJ.js";
const C = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, de = window.ms_globals.React.useRef, ue = window.ms_globals.React.useState, fe = window.ms_globals.React.useEffect, A = window.ms_globals.ReactDOM.createPortal, we = window.ms_globals.internalContext.useContextPropsContext, M = window.ms_globals.internalContext.ContextPropsProvider, ne = window.ms_globals.createItemsContext.createItemsContext;
var ge = /\s/;
function ve(n) {
  for (var e = n.length; e-- && ge.test(n.charAt(e)); )
    ;
  return e;
}
var be = /^\s+/;
function xe(n) {
  return n && n.slice(0, ve(n) + 1).replace(be, "");
}
var G = NaN, Ie = /^[-+]0x[0-9a-f]+$/i, Ce = /^0b[01]+$/i, ye = /^0o[0-7]+$/i, Ee = parseInt;
function q(n) {
  if (typeof n == "number")
    return n;
  if (me(n))
    return G;
  if (B(n)) {
    var e = typeof n.valueOf == "function" ? n.valueOf() : n;
    n = B(e) ? e + "" : e;
  }
  if (typeof n != "string")
    return n === 0 ? n : +n;
  n = xe(n);
  var l = Ce.test(n);
  return l || ye.test(n) ? Ee(n.slice(2), l ? 2 : 8) : Ie.test(n) ? G : +n;
}
var W = function() {
  return he.Date.now();
}, Pe = "Expected a function", Se = Math.max, Re = Math.min;
function ke(n, e, l) {
  var s, t, r, o, c, a, w = 0, g = !1, i = !1, p = !0;
  if (typeof n != "function")
    throw new TypeError(Pe);
  e = q(e) || 0, B(l) && (g = !!l.leading, i = "maxWait" in l, r = i ? Se(q(l.maxWait) || 0, e) : r, p = "trailing" in l ? !!l.trailing : p);
  function d(h) {
    var y = s, S = t;
    return s = t = void 0, w = h, o = n.apply(S, y), o;
  }
  function v(h) {
    return w = h, c = setTimeout(m, e), g ? d(h) : o;
  }
  function b(h) {
    var y = h - a, S = h - w, U = e - y;
    return i ? Re(U, r - S) : U;
  }
  function u(h) {
    var y = h - a, S = h - w;
    return a === void 0 || y >= e || y < 0 || i && S >= r;
  }
  function m() {
    var h = W();
    if (u(h))
      return _(h);
    c = setTimeout(m, b(h));
  }
  function _(h) {
    return c = void 0, p && s ? d(h) : (s = t = void 0, o);
  }
  function I() {
    c !== void 0 && clearTimeout(c), w = 0, s = a = t = c = void 0;
  }
  function f() {
    return c === void 0 ? o : _(W());
  }
  function E() {
    var h = W(), y = u(h);
    if (s = arguments, t = this, a = h, y) {
      if (c === void 0)
        return v(a);
      if (i)
        return clearTimeout(c), c = setTimeout(m, e), d(a);
    }
    return c === void 0 && (c = setTimeout(m, e)), o;
  }
  return E.cancel = I, E.flush = f, E;
}
var re = {
  exports: {}
}, N = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Oe = C, Te = Symbol.for("react.element"), je = Symbol.for("react.fragment"), Le = Object.prototype.hasOwnProperty, Ne = Oe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, We = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function te(n, e, l) {
  var s, t = {}, r = null, o = null;
  l !== void 0 && (r = "" + l), e.key !== void 0 && (r = "" + e.key), e.ref !== void 0 && (o = e.ref);
  for (s in e) Le.call(e, s) && !We.hasOwnProperty(s) && (t[s] = e[s]);
  if (n && n.defaultProps) for (s in e = n.defaultProps, e) t[s] === void 0 && (t[s] = e[s]);
  return {
    $$typeof: Te,
    type: n,
    key: r,
    ref: o,
    props: t,
    _owner: Ne.current
  };
}
N.Fragment = je;
N.jsx = te;
N.jsxs = te;
re.exports = N;
var x = re.exports;
const {
  SvelteComponent: Fe,
  assign: V,
  binding_callbacks: J,
  check_outros: Ae,
  children: oe,
  claim_element: le,
  claim_space: Be,
  component_subscribe: X,
  compute_slots: Me,
  create_slot: ze,
  detach: P,
  element: se,
  empty: Y,
  exclude_internal_props: Z,
  get_all_dirty_from_scope: De,
  get_slot_changes: He,
  group_outros: Ue,
  init: Ge,
  insert_hydration: O,
  safe_not_equal: qe,
  set_custom_element_data: ce,
  space: Ve,
  transition_in: T,
  transition_out: z,
  update_slot_base: Je
} = window.__gradio__svelte__internal, {
  beforeUpdate: Xe,
  getContext: Ye,
  onDestroy: Ze,
  setContext: Ke
} = window.__gradio__svelte__internal;
function K(n) {
  let e, l;
  const s = (
    /*#slots*/
    n[7].default
  ), t = ze(
    s,
    n,
    /*$$scope*/
    n[6],
    null
  );
  return {
    c() {
      e = se("svelte-slot"), t && t.c(), this.h();
    },
    l(r) {
      e = le(r, "SVELTE-SLOT", {
        class: !0
      });
      var o = oe(e);
      t && t.l(o), o.forEach(P), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(r, o) {
      O(r, e, o), t && t.m(e, null), n[9](e), l = !0;
    },
    p(r, o) {
      t && t.p && (!l || o & /*$$scope*/
      64) && Je(
        t,
        s,
        r,
        /*$$scope*/
        r[6],
        l ? He(
          s,
          /*$$scope*/
          r[6],
          o,
          null
        ) : De(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      l || (T(t, r), l = !0);
    },
    o(r) {
      z(t, r), l = !1;
    },
    d(r) {
      r && P(e), t && t.d(r), n[9](null);
    }
  };
}
function Qe(n) {
  let e, l, s, t, r = (
    /*$$slots*/
    n[4].default && K(n)
  );
  return {
    c() {
      e = se("react-portal-target"), l = Ve(), r && r.c(), s = Y(), this.h();
    },
    l(o) {
      e = le(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), oe(e).forEach(P), l = Be(o), r && r.l(o), s = Y(), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(o, c) {
      O(o, e, c), n[8](e), O(o, l, c), r && r.m(o, c), O(o, s, c), t = !0;
    },
    p(o, [c]) {
      /*$$slots*/
      o[4].default ? r ? (r.p(o, c), c & /*$$slots*/
      16 && T(r, 1)) : (r = K(o), r.c(), T(r, 1), r.m(s.parentNode, s)) : r && (Ue(), z(r, 1, 1, () => {
        r = null;
      }), Ae());
    },
    i(o) {
      t || (T(r), t = !0);
    },
    o(o) {
      z(r), t = !1;
    },
    d(o) {
      o && (P(e), P(l), P(s)), n[8](null), r && r.d(o);
    }
  };
}
function Q(n) {
  const {
    svelteInit: e,
    ...l
  } = n;
  return l;
}
function $e(n, e, l) {
  let s, t, {
    $$slots: r = {},
    $$scope: o
  } = e;
  const c = Me(r);
  let {
    svelteInit: a
  } = e;
  const w = k(Q(e)), g = k();
  X(n, g, (f) => l(0, s = f));
  const i = k();
  X(n, i, (f) => l(1, t = f));
  const p = [], d = Ye("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: b,
    subSlotIndex: u
  } = pe() || {}, m = a({
    parent: d,
    props: w,
    target: g,
    slot: i,
    slotKey: v,
    slotIndex: b,
    subSlotIndex: u,
    onDestroy(f) {
      p.push(f);
    }
  });
  Ke("$$ms-gr-react-wrapper", m), Xe(() => {
    w.set(Q(e));
  }), Ze(() => {
    p.forEach((f) => f());
  });
  function _(f) {
    J[f ? "unshift" : "push"](() => {
      s = f, g.set(s);
    });
  }
  function I(f) {
    J[f ? "unshift" : "push"](() => {
      t = f, i.set(t);
    });
  }
  return n.$$set = (f) => {
    l(17, e = V(V({}, e), Z(f))), "svelteInit" in f && l(5, a = f.svelteInit), "$$scope" in f && l(6, o = f.$$scope);
  }, e = Z(e), [s, t, g, i, c, a, o, r, _, I];
}
class en extends Fe {
  constructor(e) {
    super(), Ge(this, e, $e, Qe, qe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: mn
} = window.__gradio__svelte__internal, $ = window.ms_globals.rerender, F = window.ms_globals.tree;
function nn(n, e = {}) {
  function l(s) {
    const t = k(), r = new en({
      ...s,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: t,
            reactComponent: n,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: e.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, a = o.parent ?? F;
          return a.nodes = [...a.nodes, c], $({
            createPortal: A,
            node: F
          }), o.onDestroy(() => {
            a.nodes = a.nodes.filter((w) => w.svelteInstance !== t), $({
              createPortal: A,
              node: F
            });
          }), c;
        },
        ...s.props
      }
    });
    return t.set(r), r;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((t) => {
      window.ms_globals.initialize = () => {
        t();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(l);
    });
  });
}
function rn(n) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(n.trim());
}
function ee(n, e = !1) {
  try {
    if (_e(n))
      return n;
    if (e && !rn(n))
      return;
    if (typeof n == "string") {
      let l = n.trim();
      return l.startsWith(";") && (l = l.slice(1)), l.endsWith(";") && (l = l.slice(0, -1)), new Function(`return (...args) => (${l})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
const tn = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function on(n) {
  return n ? Object.keys(n).reduce((e, l) => {
    const s = n[l];
    return e[l] = ln(l, s), e;
  }, {}) : {};
}
function ln(n, e) {
  return typeof e == "number" && !tn.includes(n) ? e + "px" : e;
}
function D(n) {
  const e = [], l = n.cloneNode(!1);
  if (n._reactElement) {
    const t = C.Children.toArray(n._reactElement.props.children).map((r) => {
      if (C.isValidElement(r) && r.props.__slot__) {
        const {
          portals: o,
          clonedElement: c
        } = D(r.props.el);
        return C.cloneElement(r, {
          ...r.props,
          el: c,
          children: [...C.Children.toArray(r.props.children), ...o]
        });
      }
      return null;
    });
    return t.originalChildren = n._reactElement.props.children, e.push(A(C.cloneElement(n._reactElement, {
      ...n._reactElement.props,
      children: t
    }), l)), {
      clonedElement: l,
      portals: e
    };
  }
  Object.keys(n.getEventListeners()).forEach((t) => {
    n.getEventListeners(t).forEach(({
      listener: o,
      type: c,
      useCapture: a
    }) => {
      l.addEventListener(c, o, a);
    });
  });
  const s = Array.from(n.childNodes);
  for (let t = 0; t < s.length; t++) {
    const r = s[t];
    if (r.nodeType === 1) {
      const {
        clonedElement: o,
        portals: c
      } = D(r);
      e.push(...c), l.appendChild(o);
    } else r.nodeType === 3 && l.appendChild(r.cloneNode());
  }
  return {
    clonedElement: l,
    portals: e
  };
}
function sn(n, e) {
  n && (typeof n == "function" ? n(e) : n.current = e);
}
const j = ae(({
  slot: n,
  clone: e,
  className: l,
  style: s,
  observeAttributes: t
}, r) => {
  const o = de(), [c, a] = ue([]), {
    forceClone: w
  } = we(), g = w ? !0 : e;
  return fe(() => {
    var b;
    if (!o.current || !n)
      return;
    let i = n;
    function p() {
      let u = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (u = i.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), sn(r, u), l && u.classList.add(...l.split(" ")), s) {
        const m = on(s);
        Object.keys(m).forEach((_) => {
          u.style[_] = m[_];
        });
      }
    }
    let d = null, v = null;
    if (g && window.MutationObserver) {
      let u = function() {
        var f, E, h;
        (f = o.current) != null && f.contains(i) && ((E = o.current) == null || E.removeChild(i));
        const {
          portals: _,
          clonedElement: I
        } = D(n);
        i = I, a(_), i.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          p();
        }, 50), (h = o.current) == null || h.appendChild(i);
      };
      u();
      const m = ke(() => {
        u(), d == null || d.disconnect(), d == null || d.observe(n, {
          childList: !0,
          subtree: !0,
          attributes: t
        });
      }, 50);
      d = new window.MutationObserver(m), d.observe(n, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", p(), (b = o.current) == null || b.appendChild(i);
    return () => {
      var u, m;
      i.style.display = "", (u = o.current) != null && u.contains(i) && ((m = o.current) == null || m.removeChild(i)), d == null || d.disconnect();
    };
  }, [n, g, l, s, r, t, w]), C.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...c);
}), cn = ({
  children: n,
  ...e
}) => /* @__PURE__ */ x.jsx(x.Fragment, {
  children: n(e)
});
function ie(n) {
  return C.createElement(cn, {
    children: n
  });
}
function H(n, e, l) {
  const s = n.filter(Boolean);
  if (s.length !== 0)
    return s.map((t, r) => {
      var w, g;
      if (typeof t != "object")
        return e != null && e.fallback ? e.fallback(t) : t;
      const o = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...t.props,
        key: ((w = t.props) == null ? void 0 : w.key) ?? (l ? `${l}-${r}` : `${r}`)
      }) : {
        ...t.props,
        key: ((g = t.props) == null ? void 0 : g.key) ?? (l ? `${l}-${r}` : `${r}`)
      };
      let c = o;
      Object.keys(t.slots).forEach((i) => {
        if (!t.slots[i] || !(t.slots[i] instanceof Element) && !t.slots[i].el)
          return;
        const p = i.split(".");
        p.forEach((_, I) => {
          c[_] || (c[_] = {}), I !== p.length - 1 && (c = o[_]);
        });
        const d = t.slots[i];
        let v, b, u = (e == null ? void 0 : e.clone) ?? !1, m = e == null ? void 0 : e.forceClone;
        d instanceof Element ? v = d : (v = d.el, b = d.callback, u = d.clone ?? u, m = d.forceClone ?? m), m = m ?? !!b, c[p[p.length - 1]] = v ? b ? (..._) => (b(p[p.length - 1], _), /* @__PURE__ */ x.jsx(M, {
          ...t.ctx,
          params: _,
          forceClone: m,
          children: /* @__PURE__ */ x.jsx(j, {
            slot: v,
            clone: u
          })
        })) : ie((_) => /* @__PURE__ */ x.jsx(M, {
          ...t.ctx,
          forceClone: m,
          children: /* @__PURE__ */ x.jsx(j, {
            ..._,
            slot: v,
            clone: u
          })
        })) : c[p[p.length - 1]], c = o;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return t[a] ? o[a] = H(t[a], e, `${r}`) : e != null && e.children && (o[a] = void 0, Reflect.deleteProperty(o, a)), o;
    });
}
function L(n, e) {
  return n ? e != null && e.forceClone || e != null && e.params ? ie((l) => /* @__PURE__ */ x.jsx(M, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ x.jsx(j, {
      slot: n,
      clone: e == null ? void 0 : e.clone,
      ...l
    })
  })) : /* @__PURE__ */ x.jsx(j, {
    slot: n,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function R({
  key: n,
  slots: e,
  targets: l
}, s) {
  return e[n] ? (...t) => l ? l.map((r, o) => /* @__PURE__ */ x.jsx(C.Fragment, {
    children: L(r, {
      clone: !0,
      params: t,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }, o)) : /* @__PURE__ */ x.jsx(x.Fragment, {
    children: L(e[n], {
      clone: !0,
      params: t,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: an,
  withItemsContextProvider: dn,
  ItemHandler: hn
} = ne("antd-menu-items"), {
  useItems: pn,
  withItemsContextProvider: _n,
  ItemHandler: un
} = ne("antd-breadcrumb-items"), wn = nn(dn(["menu.items", "dropdownProps.menu.items"], ({
  setSlotParams: n,
  itemSlots: e,
  ...l
}) => {
  const {
    items: {
      "menu.items": s,
      "dropdownProps.menu.items": t
    }
  } = an();
  return /* @__PURE__ */ x.jsx(un, {
    ...l,
    itemProps: (r) => {
      var w, g, i, p, d, v, b, u, m, _, I, f;
      const o = {
        ...r.menu || {},
        items: (w = r.menu) != null && w.items || s.length > 0 ? H(s, {
          clone: !0
        }) : void 0,
        expandIcon: R({
          slots: e,
          key: "menu.expandIcon"
        }, {}) || ((g = r.menu) == null ? void 0 : g.expandIcon),
        overflowedIndicator: L(e["menu.overflowedIndicator"]) || ((i = r.menu) == null ? void 0 : i.overflowedIndicator)
      }, c = {
        ...((p = r.dropdownProps) == null ? void 0 : p.menu) || {},
        items: (v = (d = r.dropdownProps) == null ? void 0 : d.menu) != null && v.items || t.length > 0 ? H(t, {
          clone: !0
        }) : void 0,
        expandIcon: R({
          slots: e,
          key: "dropdownProps.menu.expandIcon"
        }, {}) || ((u = (b = r.dropdownProps) == null ? void 0 : b.menu) == null ? void 0 : u.expandIcon),
        overflowedIndicator: L(e["dropdownProps.menu.overflowedIndicator"]) || ((_ = (m = r.dropdownProps) == null ? void 0 : m.menu) == null ? void 0 : _.overflowedIndicator)
      }, a = {
        ...r.dropdownProps || {},
        dropdownRender: e["dropdownProps.dropdownRender"] ? R({
          slots: e,
          key: "dropdownProps.dropdownRender"
        }, {}) : ee((I = r.dropdownProps) == null ? void 0 : I.dropdownRender),
        popupRender: e["dropdownProps.popupRender"] ? R({
          slots: e,
          key: "dropdownProps.popupRender"
        }, {}) : ee((f = r.dropdownProps) == null ? void 0 : f.popupRender),
        menu: Object.values(c).filter(Boolean).length > 0 ? c : void 0
      };
      return {
        ...r,
        menu: Object.values(o).filter(Boolean).length > 0 ? o : void 0,
        dropdownProps: Object.values(a).filter(Boolean).length > 0 ? a : void 0
      };
    }
  });
}));
export {
  wn as BreadcrumbItem,
  wn as default
};
