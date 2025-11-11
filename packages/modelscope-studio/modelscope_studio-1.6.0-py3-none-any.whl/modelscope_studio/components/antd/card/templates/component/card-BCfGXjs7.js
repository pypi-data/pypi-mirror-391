import { i as pe, a as z, r as _e, Z as B, g as he, t as xe, s as T, b as ge } from "./Index-CrS4O249.js";
const v = window.ms_globals.React, k = window.ms_globals.React.useMemo, ne = window.ms_globals.React.useState, re = window.ms_globals.React.useEffect, fe = window.ms_globals.React.forwardRef, me = window.ms_globals.React.useRef, W = window.ms_globals.ReactDOM.createPortal, be = window.ms_globals.internalContext.useContextPropsContext, M = window.ms_globals.internalContext.ContextPropsProvider, H = window.ms_globals.antd.Card, Ce = window.ms_globals.createItemsContext.createItemsContext;
var Ee = /\s/;
function we(e) {
  for (var t = e.length; t-- && Ee.test(e.charAt(t)); )
    ;
  return t;
}
var ve = /^\s+/;
function Ie(e) {
  return e && e.slice(0, we(e) + 1).replace(ve, "");
}
var V = NaN, ye = /^[-+]0x[0-9a-f]+$/i, Se = /^0b[01]+$/i, Pe = /^0o[0-7]+$/i, je = parseInt;
function q(e) {
  if (typeof e == "number")
    return e;
  if (pe(e))
    return V;
  if (z(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = z(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Ie(e);
  var n = Se.test(e);
  return n || Pe.test(e) ? je(e.slice(2), n ? 2 : 8) : ye.test(e) ? V : +e;
}
var F = function() {
  return _e.Date.now();
}, Te = "Expected a function", Be = Math.max, Re = Math.min;
function Oe(e, t, n) {
  var i, o, r, s, l, c, h = 0, d = !1, a = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(Te);
  t = q(t) || 0, z(n) && (d = !!n.leading, a = "maxWait" in n, r = a ? Be(q(n.maxWait) || 0, t) : r, g = "trailing" in n ? !!n.trailing : g);
  function m(x) {
    var I = i, j = o;
    return i = o = void 0, h = x, s = e.apply(j, I), s;
  }
  function C(x) {
    return h = x, l = setTimeout(_, t), d ? m(x) : s;
  }
  function E(x) {
    var I = x - c, j = x - h, G = t - I;
    return a ? Re(G, r - j) : G;
  }
  function u(x) {
    var I = x - c, j = x - h;
    return c === void 0 || I >= t || I < 0 || a && j >= r;
  }
  function _() {
    var x = F();
    if (u(x))
      return w(x);
    l = setTimeout(_, E(x));
  }
  function w(x) {
    return l = void 0, g && i ? m(x) : (i = o = void 0, s);
  }
  function P() {
    l !== void 0 && clearTimeout(l), h = 0, i = c = o = l = void 0;
  }
  function p() {
    return l === void 0 ? s : w(F());
  }
  function y() {
    var x = F(), I = u(x);
    if (i = arguments, o = this, c = x, I) {
      if (l === void 0)
        return C(c);
      if (a)
        return clearTimeout(l), l = setTimeout(_, t), m(c);
    }
    return l === void 0 && (l = setTimeout(_, t)), s;
  }
  return y.cancel = P, y.flush = p, y;
}
var oe = {
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
var ke = v, Le = Symbol.for("react.element"), Fe = Symbol.for("react.fragment"), Ae = Object.prototype.hasOwnProperty, Ne = ke.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, We = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function se(e, t, n) {
  var i, o = {}, r = null, s = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (i in t) Ae.call(t, i) && !We.hasOwnProperty(i) && (o[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) o[i] === void 0 && (o[i] = t[i]);
  return {
    $$typeof: Le,
    type: e,
    key: r,
    ref: s,
    props: o,
    _owner: Ne.current
  };
}
L.Fragment = Fe;
L.jsx = se;
L.jsxs = se;
oe.exports = L;
var f = oe.exports;
const {
  SvelteComponent: ze,
  assign: J,
  binding_callbacks: X,
  check_outros: Me,
  children: ie,
  claim_element: le,
  claim_space: De,
  component_subscribe: Y,
  compute_slots: Ue,
  create_slot: Ge,
  detach: S,
  element: ae,
  empty: Z,
  exclude_internal_props: K,
  get_all_dirty_from_scope: He,
  get_slot_changes: Ve,
  group_outros: qe,
  init: Je,
  insert_hydration: R,
  safe_not_equal: Xe,
  set_custom_element_data: ce,
  space: Ye,
  transition_in: O,
  transition_out: D,
  update_slot_base: Ze
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ke,
  getContext: Qe,
  onDestroy: $e,
  setContext: et
} = window.__gradio__svelte__internal;
function Q(e) {
  let t, n;
  const i = (
    /*#slots*/
    e[7].default
  ), o = Ge(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ae("svelte-slot"), o && o.c(), this.h();
    },
    l(r) {
      t = le(r, "SVELTE-SLOT", {
        class: !0
      });
      var s = ie(t);
      o && o.l(s), s.forEach(S), this.h();
    },
    h() {
      ce(t, "class", "svelte-1rt0kpf");
    },
    m(r, s) {
      R(r, t, s), o && o.m(t, null), e[9](t), n = !0;
    },
    p(r, s) {
      o && o.p && (!n || s & /*$$scope*/
      64) && Ze(
        o,
        i,
        r,
        /*$$scope*/
        r[6],
        n ? Ve(
          i,
          /*$$scope*/
          r[6],
          s,
          null
        ) : He(
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
      D(o, r), n = !1;
    },
    d(r) {
      r && S(t), o && o.d(r), e[9](null);
    }
  };
}
function tt(e) {
  let t, n, i, o, r = (
    /*$$slots*/
    e[4].default && Q(e)
  );
  return {
    c() {
      t = ae("react-portal-target"), n = Ye(), r && r.c(), i = Z(), this.h();
    },
    l(s) {
      t = le(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), ie(t).forEach(S), n = De(s), r && r.l(s), i = Z(), this.h();
    },
    h() {
      ce(t, "class", "svelte-1rt0kpf");
    },
    m(s, l) {
      R(s, t, l), e[8](t), R(s, n, l), r && r.m(s, l), R(s, i, l), o = !0;
    },
    p(s, [l]) {
      /*$$slots*/
      s[4].default ? r ? (r.p(s, l), l & /*$$slots*/
      16 && O(r, 1)) : (r = Q(s), r.c(), O(r, 1), r.m(i.parentNode, i)) : r && (qe(), D(r, 1, 1, () => {
        r = null;
      }), Me());
    },
    i(s) {
      o || (O(r), o = !0);
    },
    o(s) {
      D(r), o = !1;
    },
    d(s) {
      s && (S(t), S(n), S(i)), e[8](null), r && r.d(s);
    }
  };
}
function $(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function nt(e, t, n) {
  let i, o, {
    $$slots: r = {},
    $$scope: s
  } = t;
  const l = Ue(r);
  let {
    svelteInit: c
  } = t;
  const h = B($(t)), d = B();
  Y(e, d, (p) => n(0, i = p));
  const a = B();
  Y(e, a, (p) => n(1, o = p));
  const g = [], m = Qe("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: E,
    subSlotIndex: u
  } = he() || {}, _ = c({
    parent: m,
    props: h,
    target: d,
    slot: a,
    slotKey: C,
    slotIndex: E,
    subSlotIndex: u,
    onDestroy(p) {
      g.push(p);
    }
  });
  et("$$ms-gr-react-wrapper", _), Ke(() => {
    h.set($(t));
  }), $e(() => {
    g.forEach((p) => p());
  });
  function w(p) {
    X[p ? "unshift" : "push"](() => {
      i = p, d.set(i);
    });
  }
  function P(p) {
    X[p ? "unshift" : "push"](() => {
      o = p, a.set(o);
    });
  }
  return e.$$set = (p) => {
    n(17, t = J(J({}, t), K(p))), "svelteInit" in p && n(5, c = p.svelteInit), "$$scope" in p && n(6, s = p.$$scope);
  }, t = K(t), [i, o, d, a, l, c, s, r, w, P];
}
class rt extends ze {
  constructor(t) {
    super(), Je(this, t, nt, tt, Xe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Ct
} = window.__gradio__svelte__internal, ee = window.ms_globals.rerender, A = window.ms_globals.tree;
function ot(e, t = {}) {
  function n(i) {
    const o = B(), r = new rt({
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
          }, c = s.parent ?? A;
          return c.nodes = [...c.nodes, l], ee({
            createPortal: W,
            node: A
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((h) => h.svelteInstance !== o), ee({
              createPortal: W,
              node: A
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
function st(e) {
  const [t, n] = ne(() => T(e));
  return re(() => {
    let i = !0;
    return e.subscribe((r) => {
      i && (i = !1, r === t) || n(r);
    });
  }, [e]), t;
}
function it(e) {
  const t = k(() => xe(e, (n) => n), [e]);
  return st(t);
}
const lt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function at(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const i = e[n];
    return t[n] = ct(n, i), t;
  }, {}) : {};
}
function ct(e, t) {
  return typeof t == "number" && !lt.includes(e) ? t + "px" : t;
}
function U(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const o = v.Children.toArray(e._reactElement.props.children).map((r) => {
      if (v.isValidElement(r) && r.props.__slot__) {
        const {
          portals: s,
          clonedElement: l
        } = U(r.props.el);
        return v.cloneElement(r, {
          ...r.props,
          el: l,
          children: [...v.Children.toArray(r.props.children), ...s]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(W(v.cloneElement(e._reactElement, {
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
      useCapture: c
    }) => {
      n.addEventListener(l, s, c);
    });
  });
  const i = Array.from(e.childNodes);
  for (let o = 0; o < i.length; o++) {
    const r = i[o];
    if (r.nodeType === 1) {
      const {
        clonedElement: s,
        portals: l
      } = U(r);
      t.push(...l), n.appendChild(s);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function ut(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const b = fe(({
  slot: e,
  clone: t,
  className: n,
  style: i,
  observeAttributes: o
}, r) => {
  const s = me(), [l, c] = ne([]), {
    forceClone: h
  } = be(), d = h ? !0 : t;
  return re(() => {
    var E;
    if (!s.current || !e)
      return;
    let a = e;
    function g() {
      let u = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (u = a.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), ut(r, u), n && u.classList.add(...n.split(" ")), i) {
        const _ = at(i);
        Object.keys(_).forEach((w) => {
          u.style[w] = _[w];
        });
      }
    }
    let m = null, C = null;
    if (d && window.MutationObserver) {
      let u = function() {
        var p, y, x;
        (p = s.current) != null && p.contains(a) && ((y = s.current) == null || y.removeChild(a));
        const {
          portals: w,
          clonedElement: P
        } = U(e);
        a = P, c(w), a.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          g();
        }, 50), (x = s.current) == null || x.appendChild(a);
      };
      u();
      const _ = Oe(() => {
        u(), m == null || m.disconnect(), m == null || m.observe(e, {
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
      a.style.display = "contents", g(), (E = s.current) == null || E.appendChild(a);
    return () => {
      var u, _;
      a.style.display = "", (u = s.current) != null && u.contains(a) && ((_ = s.current) == null || _.removeChild(a)), m == null || m.disconnect();
    };
  }, [e, d, n, i, r, o, h]), v.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...l);
});
function dt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function ft(e, t = !1) {
  try {
    if (ge(e))
      return e;
    if (t && !dt(e))
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
function N(e, t) {
  return k(() => ft(e, t), [e, t]);
}
function mt(e, t) {
  const n = k(() => v.Children.toArray(e.originalChildren || e).filter((r) => r.props.node && !r.props.node.ignore && t === r.props.nodeSlotKey).sort((r, s) => {
    if (r.props.node.slotIndex && s.props.node.slotIndex) {
      const l = T(r.props.node.slotIndex) || 0, c = T(s.props.node.slotIndex) || 0;
      return l - c === 0 && r.props.node.subSlotIndex && s.props.node.subSlotIndex ? (T(r.props.node.subSlotIndex) || 0) - (T(s.props.node.subSlotIndex) || 0) : l - c;
    }
    return 0;
  }).map((r) => r.props.node.target), [e, t]);
  return it(n);
}
function pt(e, t) {
  return Object.keys(e).reduce((n, i) => (e[i] !== void 0 && (n[i] = e[i]), n), {});
}
const _t = ({
  children: e,
  ...t
}) => /* @__PURE__ */ f.jsx(f.Fragment, {
  children: e(t)
});
function ue(e) {
  return v.createElement(_t, {
    children: e
  });
}
function de(e, t, n) {
  const i = e.filter(Boolean);
  if (i.length !== 0)
    return i.map((o, r) => {
      var h;
      if (typeof o != "object")
        return o;
      const s = {
        ...o.props,
        key: ((h = o.props) == null ? void 0 : h.key) ?? (n ? `${n}-${r}` : `${r}`)
      };
      let l = s;
      Object.keys(o.slots).forEach((d) => {
        if (!o.slots[d] || !(o.slots[d] instanceof Element) && !o.slots[d].el)
          return;
        const a = d.split(".");
        a.forEach((_, w) => {
          l[_] || (l[_] = {}), w !== a.length - 1 && (l = s[_]);
        });
        const g = o.slots[d];
        let m, C, E = !1, u = t == null ? void 0 : t.forceClone;
        g instanceof Element ? m = g : (m = g.el, C = g.callback, E = g.clone ?? E, u = g.forceClone ?? u), u = u ?? !!C, l[a[a.length - 1]] = m ? C ? (..._) => (C(a[a.length - 1], _), /* @__PURE__ */ f.jsx(M, {
          ...o.ctx,
          params: _,
          forceClone: u,
          children: /* @__PURE__ */ f.jsx(b, {
            slot: m,
            clone: E
          })
        })) : ue((_) => /* @__PURE__ */ f.jsx(M, {
          ...o.ctx,
          forceClone: u,
          children: /* @__PURE__ */ f.jsx(b, {
            ..._,
            slot: m,
            clone: E
          })
        })) : l[a[a.length - 1]], l = s;
      });
      const c = "children";
      return o[c] && (s[c] = de(o[c], t, `${r}`)), s;
    });
}
function te(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ue((n) => /* @__PURE__ */ f.jsx(M, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ f.jsx(b, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ f.jsx(b, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function ht({
  key: e,
  slots: t,
  targets: n
}, i) {
  return t[e] ? (...o) => n ? n.map((r, s) => /* @__PURE__ */ f.jsx(v.Fragment, {
    children: te(r, {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ f.jsx(f.Fragment, {
    children: te(t[e], {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: xt,
  useItems: gt,
  ItemHandler: Et
} = Ce("antd-tabs-items"), wt = ot(xt(["tabList"], ({
  children: e,
  containsGrid: t,
  slots: n,
  tabList: i,
  tabProps: o,
  setSlotParams: r,
  ...s
}) => {
  const l = mt(e, "actions"), {
    items: {
      tabList: c
    }
  } = gt(), {
    indicator: h,
    more: d,
    renderTabBar: a
  } = o || {}, g = N(h == null ? void 0 : h.size), m = N(d == null ? void 0 : d.getPopupContainer), C = N(a);
  return /* @__PURE__ */ f.jsxs(H, {
    ...s,
    tabProps: {
      ...o || {},
      indicator: g ? {
        ...h,
        size: g
      } : h,
      renderTabBar: n["tabProps.renderTabBar"] ? ht({
        slots: n,
        key: "tabProps.renderTabBar"
      }) : C,
      more: pt({
        ...d || {},
        getPopupContainer: m || (d == null ? void 0 : d.getPopupContainer),
        icon: n["tabProps.more.icon"] ? /* @__PURE__ */ f.jsx(b, {
          slot: n["tabProps.more.icon"]
        }) : d == null ? void 0 : d.icon
      }),
      tabBarExtraContent: n["tabProps.tabBarExtraContent"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabProps.tabBarExtraContent"]
      }) : n["tabProps.tabBarExtraContent.left"] || n["tabProps.tabBarExtraContent.right"] ? {
        left: n["tabProps.tabBarExtraContent.left"] ? /* @__PURE__ */ f.jsx(b, {
          slot: n["tabProps.tabBarExtraContent.left"]
        }) : void 0,
        right: n["tabProps.tabBarExtraContent.right"] ? /* @__PURE__ */ f.jsx(b, {
          slot: n["tabProps.tabBarExtraContent.right"]
        }) : void 0
      } : o == null ? void 0 : o.tabBarExtraContent,
      addIcon: n["tabProps.addIcon"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabProps.addIcon"]
      }) : o == null ? void 0 : o.addIcon,
      removeIcon: n["tabProps.removeIcon"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabProps.removeIcon"]
      }) : o == null ? void 0 : o.removeIcon
    },
    tabList: k(() => i || de(c), [i, c]),
    title: n.title ? /* @__PURE__ */ f.jsx(b, {
      slot: n.title
    }) : s.title,
    extra: n.extra ? /* @__PURE__ */ f.jsx(b, {
      slot: n.extra
    }) : s.extra,
    cover: n.cover ? /* @__PURE__ */ f.jsx(b, {
      slot: n.cover
    }) : s.cover,
    tabBarExtraContent: n.tabBarExtraContent ? /* @__PURE__ */ f.jsx(b, {
      slot: n.tabBarExtraContent
    }) : n["tabBarExtraContent.left"] || n["tabBarExtraContent.right"] ? {
      left: n["tabBarExtraContent.left"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabBarExtraContent.left"]
      }) : void 0,
      right: n["tabBarExtraContent.right"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabBarExtraContent.right"]
      }) : void 0
    } : s.tabBarExtraContent,
    actions: l.length > 0 ? l.map((E, u) => /* @__PURE__ */ f.jsx(b, {
      slot: E
    }, u)) : s.actions,
    children: [t ? /* @__PURE__ */ f.jsx(H.Grid, {
      style: {
        display: "none"
      }
    }) : null, e]
  });
}));
export {
  wt as Card,
  wt as default
};
