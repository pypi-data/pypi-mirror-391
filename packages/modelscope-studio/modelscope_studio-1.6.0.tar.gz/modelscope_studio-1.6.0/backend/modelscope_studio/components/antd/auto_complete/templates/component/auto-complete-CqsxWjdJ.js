import { i as me, a as z, r as _e, b as he, Z as j, g as ge, c as pe } from "./Index-DwWgR96E.js";
const v = window.ms_globals.React, re = window.ms_globals.React.forwardRef, W = window.ms_globals.React.useRef, le = window.ms_globals.React.useState, N = window.ms_globals.React.useEffect, B = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, we = window.ms_globals.internalContext.useContextPropsContext, D = window.ms_globals.internalContext.ContextPropsProvider, Ce = window.ms_globals.internalContext.AutoCompleteContext, xe = window.ms_globals.antd.AutoComplete, be = window.ms_globals.createItemsContext.createItemsContext;
var ye = /\s/;
function ve(t) {
  for (var e = t.length; e-- && ye.test(t.charAt(e)); )
    ;
  return e;
}
var Ee = /^\s+/;
function Ie(t) {
  return t && t.slice(0, ve(t) + 1).replace(Ee, "");
}
var q = NaN, Re = /^[-+]0x[0-9a-f]+$/i, Se = /^0b[01]+$/i, Pe = /^0o[0-7]+$/i, ke = parseInt;
function G(t) {
  if (typeof t == "number")
    return t;
  if (me(t))
    return q;
  if (z(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = z(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ie(t);
  var l = Se.test(t);
  return l || Pe.test(t) ? ke(t.slice(2), l ? 2 : 8) : Re.test(t) ? q : +t;
}
var A = function() {
  return _e.Date.now();
}, je = "Expected a function", Oe = Math.max, Te = Math.min;
function Fe(t, e, l) {
  var s, r, n, o, c, a, w = 0, x = !1, i = !1, p = !0;
  if (typeof t != "function")
    throw new TypeError(je);
  e = G(e) || 0, z(l) && (x = !!l.leading, i = "maxWait" in l, n = i ? Oe(G(l.maxWait) || 0, e) : n, p = "trailing" in l ? !!l.trailing : p);
  function d(h) {
    var I = s, P = r;
    return s = r = void 0, w = h, o = t.apply(P, I), o;
  }
  function C(h) {
    return w = h, c = setTimeout(m, e), x ? d(h) : o;
  }
  function b(h) {
    var I = h - a, P = h - w, H = e - I;
    return i ? Te(H, n - P) : H;
  }
  function f(h) {
    var I = h - a, P = h - w;
    return a === void 0 || I >= e || I < 0 || i && P >= n;
  }
  function m() {
    var h = A();
    if (f(h))
      return _(h);
    c = setTimeout(m, b(h));
  }
  function _(h) {
    return c = void 0, p && s ? d(h) : (s = r = void 0, o);
  }
  function y() {
    c !== void 0 && clearTimeout(c), w = 0, s = a = r = c = void 0;
  }
  function u() {
    return c === void 0 ? o : _(A());
  }
  function E() {
    var h = A(), I = f(h);
    if (s = arguments, r = this, a = h, I) {
      if (c === void 0)
        return C(a);
      if (i)
        return clearTimeout(c), c = setTimeout(m, e), d(a);
    }
    return c === void 0 && (c = setTimeout(m, e)), o;
  }
  return E.cancel = y, E.flush = u, E;
}
function Ae(t, e) {
  return he(t, e);
}
var oe = {
  exports: {}
}, F = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Le = v, We = Symbol.for("react.element"), Ne = Symbol.for("react.fragment"), Me = Object.prototype.hasOwnProperty, ze = Le.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, De = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function se(t, e, l) {
  var s, r = {}, n = null, o = null;
  l !== void 0 && (n = "" + l), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (o = e.ref);
  for (s in e) Me.call(e, s) && !De.hasOwnProperty(s) && (r[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) r[s] === void 0 && (r[s] = e[s]);
  return {
    $$typeof: We,
    type: t,
    key: n,
    ref: o,
    props: r,
    _owner: ze.current
  };
}
F.Fragment = Ne;
F.jsx = se;
F.jsxs = se;
oe.exports = F;
var g = oe.exports;
const {
  SvelteComponent: Ve,
  assign: J,
  binding_callbacks: X,
  check_outros: Ue,
  children: ce,
  claim_element: ie,
  claim_space: Be,
  component_subscribe: Y,
  compute_slots: He,
  create_slot: qe,
  detach: S,
  element: ae,
  empty: Z,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Ge,
  get_slot_changes: Je,
  group_outros: Xe,
  init: Ye,
  insert_hydration: O,
  safe_not_equal: Ze,
  set_custom_element_data: ue,
  space: Ke,
  transition_in: T,
  transition_out: V,
  update_slot_base: Qe
} = window.__gradio__svelte__internal, {
  beforeUpdate: $e,
  getContext: et,
  onDestroy: tt,
  setContext: nt
} = window.__gradio__svelte__internal;
function Q(t) {
  let e, l;
  const s = (
    /*#slots*/
    t[7].default
  ), r = qe(
    s,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = ae("svelte-slot"), r && r.c(), this.h();
    },
    l(n) {
      e = ie(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = ce(e);
      r && r.l(o), o.forEach(S), this.h();
    },
    h() {
      ue(e, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      O(n, e, o), r && r.m(e, null), t[9](e), l = !0;
    },
    p(n, o) {
      r && r.p && (!l || o & /*$$scope*/
      64) && Qe(
        r,
        s,
        n,
        /*$$scope*/
        n[6],
        l ? Je(
          s,
          /*$$scope*/
          n[6],
          o,
          null
        ) : Ge(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      l || (T(r, n), l = !0);
    },
    o(n) {
      V(r, n), l = !1;
    },
    d(n) {
      n && S(e), r && r.d(n), t[9](null);
    }
  };
}
function rt(t) {
  let e, l, s, r, n = (
    /*$$slots*/
    t[4].default && Q(t)
  );
  return {
    c() {
      e = ae("react-portal-target"), l = Ke(), n && n.c(), s = Z(), this.h();
    },
    l(o) {
      e = ie(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), ce(e).forEach(S), l = Be(o), n && n.l(o), s = Z(), this.h();
    },
    h() {
      ue(e, "class", "svelte-1rt0kpf");
    },
    m(o, c) {
      O(o, e, c), t[8](e), O(o, l, c), n && n.m(o, c), O(o, s, c), r = !0;
    },
    p(o, [c]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, c), c & /*$$slots*/
      16 && T(n, 1)) : (n = Q(o), n.c(), T(n, 1), n.m(s.parentNode, s)) : n && (Xe(), V(n, 1, 1, () => {
        n = null;
      }), Ue());
    },
    i(o) {
      r || (T(n), r = !0);
    },
    o(o) {
      V(n), r = !1;
    },
    d(o) {
      o && (S(e), S(l), S(s)), t[8](null), n && n.d(o);
    }
  };
}
function $(t) {
  const {
    svelteInit: e,
    ...l
  } = t;
  return l;
}
function lt(t, e, l) {
  let s, r, {
    $$slots: n = {},
    $$scope: o
  } = e;
  const c = He(n);
  let {
    svelteInit: a
  } = e;
  const w = j($(e)), x = j();
  Y(t, x, (u) => l(0, s = u));
  const i = j();
  Y(t, i, (u) => l(1, r = u));
  const p = [], d = et("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: b,
    subSlotIndex: f
  } = ge() || {}, m = a({
    parent: d,
    props: w,
    target: x,
    slot: i,
    slotKey: C,
    slotIndex: b,
    subSlotIndex: f,
    onDestroy(u) {
      p.push(u);
    }
  });
  nt("$$ms-gr-react-wrapper", m), $e(() => {
    w.set($(e));
  }), tt(() => {
    p.forEach((u) => u());
  });
  function _(u) {
    X[u ? "unshift" : "push"](() => {
      s = u, x.set(s);
    });
  }
  function y(u) {
    X[u ? "unshift" : "push"](() => {
      r = u, i.set(r);
    });
  }
  return t.$$set = (u) => {
    l(17, e = J(J({}, e), K(u))), "svelteInit" in u && l(5, a = u.svelteInit), "$$scope" in u && l(6, o = u.$$scope);
  }, e = K(e), [s, r, x, i, c, a, o, n, _, y];
}
class ot extends Ve {
  constructor(e) {
    super(), Ye(this, e, lt, rt, Ze, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Ct
} = window.__gradio__svelte__internal, ee = window.ms_globals.rerender, L = window.ms_globals.tree;
function st(t, e = {}) {
  function l(s) {
    const r = j(), n = new ot({
      ...s,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: t,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: e.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, a = o.parent ?? L;
          return a.nodes = [...a.nodes, c], ee({
            createPortal: M,
            node: L
          }), o.onDestroy(() => {
            a.nodes = a.nodes.filter((w) => w.svelteInstance !== r), ee({
              createPortal: M,
              node: L
            });
          }), c;
        },
        ...s.props
      }
    });
    return r.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((r) => {
      window.ms_globals.initialize = () => {
        r();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(l);
    });
  });
}
const ct = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function it(t) {
  return t ? Object.keys(t).reduce((e, l) => {
    const s = t[l];
    return e[l] = at(l, s), e;
  }, {}) : {};
}
function at(t, e) {
  return typeof e == "number" && !ct.includes(t) ? e + "px" : e;
}
function U(t) {
  const e = [], l = t.cloneNode(!1);
  if (t._reactElement) {
    const r = v.Children.toArray(t._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: c
        } = U(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: c,
          children: [...v.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(M(v.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: r
    }), l)), {
      clonedElement: l,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((r) => {
    t.getEventListeners(r).forEach(({
      listener: o,
      type: c,
      useCapture: a
    }) => {
      l.addEventListener(c, o, a);
    });
  });
  const s = Array.from(t.childNodes);
  for (let r = 0; r < s.length; r++) {
    const n = s[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: c
      } = U(n);
      e.push(...c), l.appendChild(o);
    } else n.nodeType === 3 && l.appendChild(n.cloneNode());
  }
  return {
    clonedElement: l,
    portals: e
  };
}
function ut(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const R = re(({
  slot: t,
  clone: e,
  className: l,
  style: s,
  observeAttributes: r
}, n) => {
  const o = W(), [c, a] = le([]), {
    forceClone: w
  } = we(), x = w ? !0 : e;
  return N(() => {
    var b;
    if (!o.current || !t)
      return;
    let i = t;
    function p() {
      let f = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (f = i.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), ut(n, f), l && f.classList.add(...l.split(" ")), s) {
        const m = it(s);
        Object.keys(m).forEach((_) => {
          f.style[_] = m[_];
        });
      }
    }
    let d = null, C = null;
    if (x && window.MutationObserver) {
      let f = function() {
        var u, E, h;
        (u = o.current) != null && u.contains(i) && ((E = o.current) == null || E.removeChild(i));
        const {
          portals: _,
          clonedElement: y
        } = U(t);
        i = y, a(_), i.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          p();
        }, 50), (h = o.current) == null || h.appendChild(i);
      };
      f();
      const m = Fe(() => {
        f(), d == null || d.disconnect(), d == null || d.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      d = new window.MutationObserver(m), d.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", p(), (b = o.current) == null || b.appendChild(i);
    return () => {
      var f, m;
      i.style.display = "", (f = o.current) != null && f.contains(i) && ((m = o.current) == null || m.removeChild(i)), d == null || d.disconnect();
    };
  }, [t, x, l, s, n, r, w]), v.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...c);
});
function dt(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function ft(t, e = !1) {
  try {
    if (pe(t))
      return t;
    if (e && !dt(t))
      return;
    if (typeof t == "string") {
      let l = t.trim();
      return l.startsWith(";") && (l = l.slice(1)), l.endsWith(";") && (l = l.slice(0, -1)), new Function(`return (...args) => (${l})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function k(t, e) {
  return B(() => ft(t, e), [t, e]);
}
function mt({
  value: t,
  onValueChange: e
}) {
  const [l, s] = le(t), r = W(e);
  r.current = e;
  const n = W(l);
  return n.current = l, N(() => {
    r.current(l);
  }, [l]), N(() => {
    Ae(t, n.current) || s(t);
  }, [t]), [l, s];
}
const _t = ({
  children: t,
  ...e
}) => /* @__PURE__ */ g.jsx(g.Fragment, {
  children: t(e)
});
function de(t) {
  return v.createElement(_t, {
    children: t
  });
}
function fe(t, e, l) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((r, n) => {
      var w, x;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const o = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((w = r.props) == null ? void 0 : w.key) ?? (l ? `${l}-${n}` : `${n}`)
      }) : {
        ...r.props,
        key: ((x = r.props) == null ? void 0 : x.key) ?? (l ? `${l}-${n}` : `${n}`)
      };
      let c = o;
      Object.keys(r.slots).forEach((i) => {
        if (!r.slots[i] || !(r.slots[i] instanceof Element) && !r.slots[i].el)
          return;
        const p = i.split(".");
        p.forEach((_, y) => {
          c[_] || (c[_] = {}), y !== p.length - 1 && (c = o[_]);
        });
        const d = r.slots[i];
        let C, b, f = (e == null ? void 0 : e.clone) ?? !1, m = e == null ? void 0 : e.forceClone;
        d instanceof Element ? C = d : (C = d.el, b = d.callback, f = d.clone ?? f, m = d.forceClone ?? m), m = m ?? !!b, c[p[p.length - 1]] = C ? b ? (..._) => (b(p[p.length - 1], _), /* @__PURE__ */ g.jsx(D, {
          ...r.ctx,
          params: _,
          forceClone: m,
          children: /* @__PURE__ */ g.jsx(R, {
            slot: C,
            clone: f
          })
        })) : de((_) => /* @__PURE__ */ g.jsx(D, {
          ...r.ctx,
          forceClone: m,
          children: /* @__PURE__ */ g.jsx(R, {
            ..._,
            slot: C,
            clone: f
          })
        })) : c[p[p.length - 1]], c = o;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return r[a] ? o[a] = fe(r[a], e, `${n}`) : e != null && e.children && (o[a] = void 0, Reflect.deleteProperty(o, a)), o;
    });
}
function te(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? de((l) => /* @__PURE__ */ g.jsx(D, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ g.jsx(R, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...l
    })
  })) : /* @__PURE__ */ g.jsx(R, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function ne({
  key: t,
  slots: e,
  targets: l
}, s) {
  return e[t] ? (...r) => l ? l.map((n, o) => /* @__PURE__ */ g.jsx(v.Fragment, {
    children: te(n, {
      clone: !0,
      params: r,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }, o)) : /* @__PURE__ */ g.jsx(g.Fragment, {
    children: te(e[t], {
      clone: !0,
      params: r,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: ht,
  withItemsContextProvider: gt,
  ItemHandler: xt
} = be("antd-auto-complete-options"), pt = re(({
  children: t,
  ...e
}, l) => /* @__PURE__ */ g.jsx(Ce.Provider, {
  value: B(() => ({
    ...e,
    elRef: l
  }), [e, l]),
  children: t
})), bt = st(gt(["options", "default"], ({
  slots: t,
  children: e,
  onValueChange: l,
  filterOption: s,
  onChange: r,
  options: n,
  getPopupContainer: o,
  dropdownRender: c,
  popupRender: a,
  elRef: w,
  setSlotParams: x,
  ...i
}) => {
  const p = k(o), d = k(s), C = k(c), b = k(a), [f, m] = mt({
    onValueChange: l,
    value: i.value
  }), {
    items: _
  } = ht(), y = _.options.length > 0 ? _.options : _.default;
  return /* @__PURE__ */ g.jsxs(g.Fragment, {
    children: [t.children ? null : /* @__PURE__ */ g.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ g.jsx(xe, {
      ...i,
      value: f,
      ref: w,
      allowClear: t["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ g.jsx(R, {
          slot: t["allowClear.clearIcon"]
        })
      } : i.allowClear,
      options: B(() => n || fe(y, {
        children: "options"
        // clone: true,
      }), [y, n]),
      onChange: (u, ...E) => {
        r == null || r(u, ...E), m(u);
      },
      notFoundContent: t.notFoundContent ? /* @__PURE__ */ g.jsx(R, {
        slot: t.notFoundContent
      }) : i.notFoundContent,
      filterOption: d || s,
      getPopupContainer: p,
      popupRender: t.popupRender ? ne({
        slots: t,
        key: "popupRender"
      }, {}) : b,
      dropdownRender: t.dropdownRender ? ne({
        slots: t,
        key: "dropdownRender"
      }, {}) : C,
      children: t.children ? /* @__PURE__ */ g.jsxs(pt, {
        children: [/* @__PURE__ */ g.jsx("div", {
          style: {
            display: "none"
          },
          children: e
        }), /* @__PURE__ */ g.jsx(R, {
          slot: t.children
        })]
      }) : null
    })]
  });
}));
export {
  bt as AutoComplete,
  bt as default
};
