import { i as he, a as D, r as _e, Z as O, g as ge, b as we } from "./Index-CTo42Ypd.js";
const T = window.ms_globals.React, ue = window.ms_globals.React.forwardRef, fe = window.ms_globals.React.useRef, de = window.ms_globals.React.useState, me = window.ms_globals.React.useEffect, te = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, be = window.ms_globals.internalContext.useContextPropsContext, M = window.ms_globals.internalContext.ContextPropsProvider, H = window.ms_globals.antd.Tree, ye = window.ms_globals.createItemsContext.createItemsContext;
var ve = /\s/;
function xe(t) {
  for (var e = t.length; e-- && ve.test(t.charAt(e)); )
    ;
  return e;
}
var pe = /^\s+/;
function Ce(t) {
  return t && t.slice(0, xe(t) + 1).replace(pe, "");
}
var G = NaN, Ie = /^[-+]0x[0-9a-f]+$/i, Ee = /^0b[01]+$/i, Te = /^0o[0-7]+$/i, Re = parseInt;
function q(t) {
  if (typeof t == "number")
    return t;
  if (he(t))
    return G;
  if (D(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = D(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ce(t);
  var o = Ee.test(t);
  return o || Te.test(t) ? Re(t.slice(2), o ? 2 : 8) : Ie.test(t) ? G : +t;
}
var N = function() {
  return _e.Date.now();
}, Se = "Expected a function", ke = Math.max, Pe = Math.min;
function Oe(t, e, o) {
  var s, l, n, r, i, u, b = 0, v = !1, c = !1, g = !0;
  if (typeof t != "function")
    throw new TypeError(Se);
  e = q(e) || 0, D(o) && (v = !!o.leading, c = "maxWait" in o, n = c ? ke(q(o.maxWait) || 0, e) : n, g = "trailing" in o ? !!o.trailing : g);
  function a(h) {
    var _ = s, C = l;
    return s = l = void 0, b = h, r = t.apply(C, _), r;
  }
  function x(h) {
    return b = h, i = setTimeout(m, e), v ? a(h) : r;
  }
  function p(h) {
    var _ = h - u, C = h - b, B = e - _;
    return c ? Pe(B, n - C) : B;
  }
  function d(h) {
    var _ = h - u, C = h - b;
    return u === void 0 || _ >= e || _ < 0 || c && C >= n;
  }
  function m() {
    var h = N();
    if (d(h))
      return w(h);
    i = setTimeout(m, p(h));
  }
  function w(h) {
    return i = void 0, g && s ? a(h) : (s = l = void 0, r);
  }
  function I() {
    i !== void 0 && clearTimeout(i), b = 0, s = u = l = i = void 0;
  }
  function f() {
    return i === void 0 ? r : w(N());
  }
  function E() {
    var h = N(), _ = d(h);
    if (s = arguments, l = this, u = h, _) {
      if (i === void 0)
        return x(u);
      if (c)
        return clearTimeout(i), i = setTimeout(m, e), a(u);
    }
    return i === void 0 && (i = setTimeout(m, e)), r;
  }
  return E.cancel = I, E.flush = f, E;
}
var ne = {
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
var je = T, Le = Symbol.for("react.element"), Fe = Symbol.for("react.fragment"), Ne = Object.prototype.hasOwnProperty, We = je.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ae = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function re(t, e, o) {
  var s, l = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (r = e.ref);
  for (s in e) Ne.call(e, s) && !Ae.hasOwnProperty(s) && (l[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) l[s] === void 0 && (l[s] = e[s]);
  return {
    $$typeof: Le,
    type: t,
    key: n,
    ref: r,
    props: l,
    _owner: We.current
  };
}
F.Fragment = Fe;
F.jsx = re;
F.jsxs = re;
ne.exports = F;
var y = ne.exports;
const {
  SvelteComponent: De,
  assign: V,
  binding_callbacks: J,
  check_outros: Me,
  children: le,
  claim_element: oe,
  claim_space: ze,
  component_subscribe: X,
  compute_slots: Ue,
  create_slot: Be,
  detach: R,
  element: se,
  empty: Y,
  exclude_internal_props: Z,
  get_all_dirty_from_scope: He,
  get_slot_changes: Ge,
  group_outros: qe,
  init: Ve,
  insert_hydration: j,
  safe_not_equal: Je,
  set_custom_element_data: ie,
  space: Xe,
  transition_in: L,
  transition_out: z,
  update_slot_base: Ye
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ze,
  getContext: Ke,
  onDestroy: Qe,
  setContext: $e
} = window.__gradio__svelte__internal;
function K(t) {
  let e, o;
  const s = (
    /*#slots*/
    t[7].default
  ), l = Be(
    s,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = se("svelte-slot"), l && l.c(), this.h();
    },
    l(n) {
      e = oe(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = le(e);
      l && l.l(r), r.forEach(R), this.h();
    },
    h() {
      ie(e, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      j(n, e, r), l && l.m(e, null), t[9](e), o = !0;
    },
    p(n, r) {
      l && l.p && (!o || r & /*$$scope*/
      64) && Ye(
        l,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Ge(
          s,
          /*$$scope*/
          n[6],
          r,
          null
        ) : He(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (L(l, n), o = !0);
    },
    o(n) {
      z(l, n), o = !1;
    },
    d(n) {
      n && R(e), l && l.d(n), t[9](null);
    }
  };
}
function et(t) {
  let e, o, s, l, n = (
    /*$$slots*/
    t[4].default && K(t)
  );
  return {
    c() {
      e = se("react-portal-target"), o = Xe(), n && n.c(), s = Y(), this.h();
    },
    l(r) {
      e = oe(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), le(e).forEach(R), o = ze(r), n && n.l(r), s = Y(), this.h();
    },
    h() {
      ie(e, "class", "svelte-1rt0kpf");
    },
    m(r, i) {
      j(r, e, i), t[8](e), j(r, o, i), n && n.m(r, i), j(r, s, i), l = !0;
    },
    p(r, [i]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, i), i & /*$$slots*/
      16 && L(n, 1)) : (n = K(r), n.c(), L(n, 1), n.m(s.parentNode, s)) : n && (qe(), z(n, 1, 1, () => {
        n = null;
      }), Me());
    },
    i(r) {
      l || (L(n), l = !0);
    },
    o(r) {
      z(n), l = !1;
    },
    d(r) {
      r && (R(e), R(o), R(s)), t[8](null), n && n.d(r);
    }
  };
}
function Q(t) {
  const {
    svelteInit: e,
    ...o
  } = t;
  return o;
}
function tt(t, e, o) {
  let s, l, {
    $$slots: n = {},
    $$scope: r
  } = e;
  const i = Ue(n);
  let {
    svelteInit: u
  } = e;
  const b = O(Q(e)), v = O();
  X(t, v, (f) => o(0, s = f));
  const c = O();
  X(t, c, (f) => o(1, l = f));
  const g = [], a = Ke("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: p,
    subSlotIndex: d
  } = ge() || {}, m = u({
    parent: a,
    props: b,
    target: v,
    slot: c,
    slotKey: x,
    slotIndex: p,
    subSlotIndex: d,
    onDestroy(f) {
      g.push(f);
    }
  });
  $e("$$ms-gr-react-wrapper", m), Ze(() => {
    b.set(Q(e));
  }), Qe(() => {
    g.forEach((f) => f());
  });
  function w(f) {
    J[f ? "unshift" : "push"](() => {
      s = f, v.set(s);
    });
  }
  function I(f) {
    J[f ? "unshift" : "push"](() => {
      l = f, c.set(l);
    });
  }
  return t.$$set = (f) => {
    o(17, e = V(V({}, e), Z(f))), "svelteInit" in f && o(5, u = f.svelteInit), "$$scope" in f && o(6, r = f.$$scope);
  }, e = Z(e), [s, l, v, c, i, u, r, n, w, I];
}
class nt extends De {
  constructor(e) {
    super(), Ve(this, e, tt, et, Je, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, $ = window.ms_globals.rerender, W = window.ms_globals.tree;
function rt(t, e = {}) {
  function o(s) {
    const l = O(), n = new nt({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const i = {
            key: window.ms_globals.autokey,
            svelteInstance: l,
            reactComponent: t,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: e.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, u = r.parent ?? W;
          return u.nodes = [...u.nodes, i], $({
            createPortal: A,
            node: W
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((b) => b.svelteInstance !== l), $({
              createPortal: A,
              node: W
            });
          }), i;
        },
        ...s.props
      }
    });
    return l.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((l) => {
      window.ms_globals.initialize = () => {
        l();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(o);
    });
  });
}
const lt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ot(t) {
  return t ? Object.keys(t).reduce((e, o) => {
    const s = t[o];
    return e[o] = st(o, s), e;
  }, {}) : {};
}
function st(t, e) {
  return typeof e == "number" && !lt.includes(t) ? e + "px" : e;
}
function U(t) {
  const e = [], o = t.cloneNode(!1);
  if (t._reactElement) {
    const l = T.Children.toArray(t._reactElement.props.children).map((n) => {
      if (T.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: i
        } = U(n.props.el);
        return T.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...T.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return l.originalChildren = t._reactElement.props.children, e.push(A(T.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: l
    }), o)), {
      clonedElement: o,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((l) => {
    t.getEventListeners(l).forEach(({
      listener: r,
      type: i,
      useCapture: u
    }) => {
      o.addEventListener(i, r, u);
    });
  });
  const s = Array.from(t.childNodes);
  for (let l = 0; l < s.length; l++) {
    const n = s[l];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: i
      } = U(n);
      e.push(...i), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: e
  };
}
function it(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const S = ue(({
  slot: t,
  clone: e,
  className: o,
  style: s,
  observeAttributes: l
}, n) => {
  const r = fe(), [i, u] = de([]), {
    forceClone: b
  } = be(), v = b ? !0 : e;
  return me(() => {
    var p;
    if (!r.current || !t)
      return;
    let c = t;
    function g() {
      let d = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (d = c.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), it(n, d), o && d.classList.add(...o.split(" ")), s) {
        const m = ot(s);
        Object.keys(m).forEach((w) => {
          d.style[w] = m[w];
        });
      }
    }
    let a = null, x = null;
    if (v && window.MutationObserver) {
      let d = function() {
        var f, E, h;
        (f = r.current) != null && f.contains(c) && ((E = r.current) == null || E.removeChild(c));
        const {
          portals: w,
          clonedElement: I
        } = U(t);
        c = I, u(w), c.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          g();
        }, 50), (h = r.current) == null || h.appendChild(c);
      };
      d();
      const m = Oe(() => {
        d(), a == null || a.disconnect(), a == null || a.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      a = new window.MutationObserver(m), a.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (p = r.current) == null || p.appendChild(c);
    return () => {
      var d, m;
      c.style.display = "", (d = r.current) != null && d.contains(c) && ((m = r.current) == null || m.removeChild(c)), a == null || a.disconnect();
    };
  }, [t, v, o, s, n, l, b]), T.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...i);
});
function ct(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function at(t, e = !1) {
  try {
    if (we(t))
      return t;
    if (e && !ct(t))
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
function k(t, e) {
  return te(() => at(t, e), [t, e]);
}
function ut(t, e) {
  return Object.keys(t).reduce((o, s) => (t[s] !== void 0 && (o[s] = t[s]), o), {});
}
const ft = ({
  children: t,
  ...e
}) => /* @__PURE__ */ y.jsx(y.Fragment, {
  children: t(e)
});
function ce(t) {
  return T.createElement(ft, {
    children: t
  });
}
function ae(t, e, o) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((l, n) => {
      var b, v;
      if (typeof l != "object")
        return e != null && e.fallback ? e.fallback(l) : l;
      const r = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...l.props,
        key: ((b = l.props) == null ? void 0 : b.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...l.props,
        key: ((v = l.props) == null ? void 0 : v.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let i = r;
      Object.keys(l.slots).forEach((c) => {
        if (!l.slots[c] || !(l.slots[c] instanceof Element) && !l.slots[c].el)
          return;
        const g = c.split(".");
        g.forEach((w, I) => {
          i[w] || (i[w] = {}), I !== g.length - 1 && (i = r[w]);
        });
        const a = l.slots[c];
        let x, p, d = (e == null ? void 0 : e.clone) ?? !1, m = e == null ? void 0 : e.forceClone;
        a instanceof Element ? x = a : (x = a.el, p = a.callback, d = a.clone ?? d, m = a.forceClone ?? m), m = m ?? !!p, i[g[g.length - 1]] = x ? p ? (...w) => (p(g[g.length - 1], w), /* @__PURE__ */ y.jsx(M, {
          ...l.ctx,
          params: w,
          forceClone: m,
          children: /* @__PURE__ */ y.jsx(S, {
            slot: x,
            clone: d
          })
        })) : ce((w) => /* @__PURE__ */ y.jsx(M, {
          ...l.ctx,
          forceClone: m,
          children: /* @__PURE__ */ y.jsx(S, {
            ...w,
            slot: x,
            clone: d
          })
        })) : i[g[g.length - 1]], i = r;
      });
      const u = (e == null ? void 0 : e.children) || "children";
      return l[u] ? r[u] = ae(l[u], e, `${n}`) : e != null && e.children && (r[u] = void 0, Reflect.deleteProperty(r, u)), r;
    });
}
function ee(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? ce((o) => /* @__PURE__ */ y.jsx(M, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ y.jsx(S, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...o
    })
  })) : /* @__PURE__ */ y.jsx(S, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function P({
  key: t,
  slots: e,
  targets: o
}, s) {
  return e[t] ? (...l) => o ? o.map((n, r) => /* @__PURE__ */ y.jsx(T.Fragment, {
    children: ee(n, {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }, r)) : /* @__PURE__ */ y.jsx(y.Fragment, {
    children: ee(e[t], {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: dt,
  useItems: mt,
  ItemHandler: gt
} = ye("antd-tree-tree-nodes"), wt = rt(dt(["default", "treeData"], ({
  slots: t,
  filterTreeNode: e,
  treeData: o,
  draggable: s,
  allowDrop: l,
  onCheck: n,
  onSelect: r,
  onExpand: i,
  children: u,
  directory: b,
  setSlotParams: v,
  onLoadData: c,
  titleRender: g,
  ...a
}) => {
  const x = k(e), p = k(s), d = k(g), m = k(typeof s == "object" ? s.nodeDraggable : void 0), w = k(l), I = b ? H.DirectoryTree : H, {
    items: f
  } = mt(), E = f.treeData.length > 0 ? f.treeData : f.default, h = te(() => ({
    ...a,
    treeData: o || ae(E, {
      clone: !0,
      itemPropsTransformer: (_) => _.value && _.key && _.value !== _.key ? {
        ..._,
        key: void 0
      } : _
    }),
    showLine: t["showLine.showLeafIcon"] ? {
      showLeafIcon: P({
        slots: t,
        key: "showLine.showLeafIcon"
      })
    } : a.showLine,
    icon: t.icon ? P({
      slots: t,
      key: "icon"
    }) : a.icon,
    switcherLoadingIcon: t.switcherLoadingIcon ? /* @__PURE__ */ y.jsx(S, {
      slot: t.switcherLoadingIcon
    }) : a.switcherLoadingIcon,
    switcherIcon: t.switcherIcon ? P({
      slots: t,
      key: "switcherIcon"
    }) : a.switcherIcon,
    titleRender: t.titleRender ? P({
      slots: t,
      key: "titleRender"
    }) : d,
    draggable: t["draggable.icon"] || m ? {
      icon: t["draggable.icon"] ? /* @__PURE__ */ y.jsx(S, {
        slot: t["draggable.icon"]
      }) : typeof s == "object" ? s.icon : void 0,
      nodeDraggable: m
    } : p || s,
    // eslint-disable-next-line require-await
    loadData: async (..._) => c == null ? void 0 : c(..._)
  }), [a, o, E, t, v, m, s, d, p, c]);
  return /* @__PURE__ */ y.jsxs(y.Fragment, {
    children: [/* @__PURE__ */ y.jsx("div", {
      style: {
        display: "none"
      },
      children: u
    }), /* @__PURE__ */ y.jsx(I, {
      ...ut(h),
      filterTreeNode: x,
      allowDrop: w,
      onSelect: (_, ...C) => {
        r == null || r(_, ...C);
      },
      onExpand: (_, ...C) => {
        i == null || i(_, ...C);
      },
      onCheck: (_, ...C) => {
        n == null || n(_, ...C);
      }
    })]
  });
}));
export {
  wt as Tree,
  wt as default
};
