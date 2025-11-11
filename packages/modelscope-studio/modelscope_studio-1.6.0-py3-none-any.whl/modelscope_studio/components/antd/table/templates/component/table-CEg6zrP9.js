import { i as Ge, a as q, r as Je, Z as W, g as Qe, b as Xe } from "./Index-Bcc4uA6R.js";
const O = window.ms_globals.React, He = window.ms_globals.React.forwardRef, De = window.ms_globals.React.useRef, Be = window.ms_globals.React.useState, ze = window.ms_globals.React.useEffect, N = window.ms_globals.React.useMemo, X = window.ms_globals.ReactDOM.createPortal, qe = window.ms_globals.internalContext.useContextPropsContext, V = window.ms_globals.internalContext.ContextPropsProvider, j = window.ms_globals.antd.Table, z = window.ms_globals.createItemsContext.createItemsContext;
var Ve = /\s/;
function Ke(t) {
  for (var e = t.length; e-- && Ve.test(t.charAt(e)); )
    ;
  return e;
}
var Ye = /^\s+/;
function Ze(t) {
  return t && t.slice(0, Ke(t) + 1).replace(Ye, "");
}
var ce = NaN, $e = /^[-+]0x[0-9a-f]+$/i, et = /^0b[01]+$/i, tt = /^0o[0-7]+$/i, rt = parseInt;
function ue(t) {
  if (typeof t == "number")
    return t;
  if (Ge(t))
    return ce;
  if (q(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = q(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ze(t);
  var n = et.test(t);
  return n || tt.test(t) ? rt(t.slice(2), n ? 2 : 8) : $e.test(t) ? ce : +t;
}
var J = function() {
  return Je.Date.now();
}, nt = "Expected a function", lt = Math.max, it = Math.min;
function ot(t, e, n) {
  var o, l, r, i, s, u, C = 0, b = !1, c = !1, _ = !0;
  if (typeof t != "function")
    throw new TypeError(nt);
  e = ue(e) || 0, q(n) && (b = !!n.leading, c = "maxWait" in n, r = c ? lt(ue(n.maxWait) || 0, e) : r, _ = "trailing" in n ? !!n.trailing : _);
  function d(m) {
    var v = o, T = l;
    return o = l = void 0, C = m, i = t.apply(T, v), i;
  }
  function x(m) {
    return C = m, s = setTimeout(h, e), b ? d(m) : i;
  }
  function y(m) {
    var v = m - u, T = m - C, L = e - v;
    return c ? it(L, r - T) : L;
  }
  function a(m) {
    var v = m - u, T = m - C;
    return u === void 0 || v >= e || v < 0 || c && T >= r;
  }
  function h() {
    var m = J();
    if (a(m))
      return g(m);
    s = setTimeout(h, y(m));
  }
  function g(m) {
    return s = void 0, _ && o ? d(m) : (o = l = void 0, i);
  }
  function E() {
    s !== void 0 && clearTimeout(s), C = 0, o = u = l = s = void 0;
  }
  function f() {
    return s === void 0 ? i : g(J());
  }
  function P() {
    var m = J(), v = a(m);
    if (o = arguments, l = this, u = m, v) {
      if (s === void 0)
        return x(u);
      if (c)
        return clearTimeout(s), s = setTimeout(h, e), d(u);
    }
    return s === void 0 && (s = setTimeout(h, e)), i;
  }
  return P.cancel = E, P.flush = f, P;
}
var pe = {
  exports: {}
}, G = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var at = O, st = Symbol.for("react.element"), ct = Symbol.for("react.fragment"), ut = Object.prototype.hasOwnProperty, dt = at.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ft = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function xe(t, e, n) {
  var o, l = {}, r = null, i = null;
  n !== void 0 && (r = "" + n), e.key !== void 0 && (r = "" + e.key), e.ref !== void 0 && (i = e.ref);
  for (o in e) ut.call(e, o) && !ft.hasOwnProperty(o) && (l[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) l[o] === void 0 && (l[o] = e[o]);
  return {
    $$typeof: st,
    type: t,
    key: r,
    ref: i,
    props: l,
    _owner: dt.current
  };
}
G.Fragment = ct;
G.jsx = xe;
G.jsxs = xe;
pe.exports = G;
var w = pe.exports;
const {
  SvelteComponent: mt,
  assign: de,
  binding_callbacks: fe,
  check_outros: ht,
  children: ye,
  claim_element: Ie,
  claim_space: gt,
  component_subscribe: me,
  compute_slots: _t,
  create_slot: wt,
  detach: k,
  element: Ee,
  empty: he,
  exclude_internal_props: ge,
  get_all_dirty_from_scope: Ct,
  get_slot_changes: bt,
  group_outros: pt,
  init: xt,
  insert_hydration: H,
  safe_not_equal: yt,
  set_custom_element_data: ve,
  space: It,
  transition_in: D,
  transition_out: K,
  update_slot_base: Et
} = window.__gradio__svelte__internal, {
  beforeUpdate: vt,
  getContext: St,
  onDestroy: Pt,
  setContext: Tt
} = window.__gradio__svelte__internal;
function _e(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), l = wt(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = Ee("svelte-slot"), l && l.c(), this.h();
    },
    l(r) {
      e = Ie(r, "SVELTE-SLOT", {
        class: !0
      });
      var i = ye(e);
      l && l.l(i), i.forEach(k), this.h();
    },
    h() {
      ve(e, "class", "svelte-1rt0kpf");
    },
    m(r, i) {
      H(r, e, i), l && l.m(e, null), t[9](e), n = !0;
    },
    p(r, i) {
      l && l.p && (!n || i & /*$$scope*/
      64) && Et(
        l,
        o,
        r,
        /*$$scope*/
        r[6],
        n ? bt(
          o,
          /*$$scope*/
          r[6],
          i,
          null
        ) : Ct(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      n || (D(l, r), n = !0);
    },
    o(r) {
      K(l, r), n = !1;
    },
    d(r) {
      r && k(e), l && l.d(r), t[9](null);
    }
  };
}
function Ot(t) {
  let e, n, o, l, r = (
    /*$$slots*/
    t[4].default && _e(t)
  );
  return {
    c() {
      e = Ee("react-portal-target"), n = It(), r && r.c(), o = he(), this.h();
    },
    l(i) {
      e = Ie(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), ye(e).forEach(k), n = gt(i), r && r.l(i), o = he(), this.h();
    },
    h() {
      ve(e, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      H(i, e, s), t[8](e), H(i, n, s), r && r.m(i, s), H(i, o, s), l = !0;
    },
    p(i, [s]) {
      /*$$slots*/
      i[4].default ? r ? (r.p(i, s), s & /*$$slots*/
      16 && D(r, 1)) : (r = _e(i), r.c(), D(r, 1), r.m(o.parentNode, o)) : r && (pt(), K(r, 1, 1, () => {
        r = null;
      }), ht());
    },
    i(i) {
      l || (D(r), l = !0);
    },
    o(i) {
      K(r), l = !1;
    },
    d(i) {
      i && (k(e), k(n), k(o)), t[8](null), r && r.d(i);
    }
  };
}
function we(t) {
  const {
    svelteInit: e,
    ...n
  } = t;
  return n;
}
function Rt(t, e, n) {
  let o, l, {
    $$slots: r = {},
    $$scope: i
  } = e;
  const s = _t(r);
  let {
    svelteInit: u
  } = e;
  const C = W(we(e)), b = W();
  me(t, b, (f) => n(0, o = f));
  const c = W();
  me(t, c, (f) => n(1, l = f));
  const _ = [], d = St("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: y,
    subSlotIndex: a
  } = Qe() || {}, h = u({
    parent: d,
    props: C,
    target: b,
    slot: c,
    slotKey: x,
    slotIndex: y,
    subSlotIndex: a,
    onDestroy(f) {
      _.push(f);
    }
  });
  Tt("$$ms-gr-react-wrapper", h), vt(() => {
    C.set(we(e));
  }), Pt(() => {
    _.forEach((f) => f());
  });
  function g(f) {
    fe[f ? "unshift" : "push"](() => {
      o = f, b.set(o);
    });
  }
  function E(f) {
    fe[f ? "unshift" : "push"](() => {
      l = f, c.set(l);
    });
  }
  return t.$$set = (f) => {
    n(17, e = de(de({}, e), ge(f))), "svelteInit" in f && n(5, u = f.svelteInit), "$$scope" in f && n(6, i = f.$$scope);
  }, e = ge(e), [o, l, b, c, s, u, i, r, g, E];
}
class kt extends mt {
  constructor(e) {
    super(), xt(this, e, Rt, Ot, yt, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Xt
} = window.__gradio__svelte__internal, Ce = window.ms_globals.rerender, Q = window.ms_globals.tree;
function jt(t, e = {}) {
  function n(o) {
    const l = W(), r = new kt({
      ...o,
      props: {
        svelteInit(i) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: l,
            reactComponent: t,
            props: i.props,
            slot: i.slot,
            target: i.target,
            slotIndex: i.slotIndex,
            subSlotIndex: i.subSlotIndex,
            ignore: e.ignore,
            slotKey: i.slotKey,
            nodes: []
          }, u = i.parent ?? Q;
          return u.nodes = [...u.nodes, s], Ce({
            createPortal: X,
            node: Q
          }), i.onDestroy(() => {
            u.nodes = u.nodes.filter((C) => C.svelteInstance !== l), Ce({
              createPortal: X,
              node: Q
            });
          }), s;
        },
        ...o.props
      }
    });
    return l.set(r), r;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((l) => {
      window.ms_globals.initialize = () => {
        l();
      };
    })), window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
const Nt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Lt(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = Ft(n, o), e;
  }, {}) : {};
}
function Ft(t, e) {
  return typeof e == "number" && !Nt.includes(t) ? e + "px" : e;
}
function Y(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const l = O.Children.toArray(t._reactElement.props.children).map((r) => {
      if (O.isValidElement(r) && r.props.__slot__) {
        const {
          portals: i,
          clonedElement: s
        } = Y(r.props.el);
        return O.cloneElement(r, {
          ...r.props,
          el: s,
          children: [...O.Children.toArray(r.props.children), ...i]
        });
      }
      return null;
    });
    return l.originalChildren = t._reactElement.props.children, e.push(X(O.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: l
    }), n)), {
      clonedElement: n,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((l) => {
    t.getEventListeners(l).forEach(({
      listener: i,
      type: s,
      useCapture: u
    }) => {
      n.addEventListener(s, i, u);
    });
  });
  const o = Array.from(t.childNodes);
  for (let l = 0; l < o.length; l++) {
    const r = o[l];
    if (r.nodeType === 1) {
      const {
        clonedElement: i,
        portals: s
      } = Y(r);
      e.push(...s), n.appendChild(i);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function At(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const R = He(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: l
}, r) => {
  const i = De(), [s, u] = Be([]), {
    forceClone: C
  } = qe(), b = C ? !0 : e;
  return ze(() => {
    var y;
    if (!i.current || !t)
      return;
    let c = t;
    function _() {
      let a = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (a = c.children[0], a.tagName.toLowerCase() === "react-portal-target" && a.children[0] && (a = a.children[0])), At(r, a), n && a.classList.add(...n.split(" ")), o) {
        const h = Lt(o);
        Object.keys(h).forEach((g) => {
          a.style[g] = h[g];
        });
      }
    }
    let d = null, x = null;
    if (b && window.MutationObserver) {
      let a = function() {
        var f, P, m;
        (f = i.current) != null && f.contains(c) && ((P = i.current) == null || P.removeChild(c));
        const {
          portals: g,
          clonedElement: E
        } = Y(t);
        c = E, u(g), c.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          _();
        }, 50), (m = i.current) == null || m.appendChild(c);
      };
      a();
      const h = ot(() => {
        a(), d == null || d.disconnect(), d == null || d.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      d = new window.MutationObserver(h), d.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", _(), (y = i.current) == null || y.appendChild(c);
    return () => {
      var a, h;
      c.style.display = "", (a = i.current) != null && a.contains(c) && ((h = i.current) == null || h.removeChild(c)), d == null || d.disconnect();
    };
  }, [t, b, n, o, r, l, C]), O.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...s);
});
function Mt(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function S(t, e = !1) {
  try {
    if (Xe(t))
      return t;
    if (e && !Mt(t))
      return;
    if (typeof t == "string") {
      let n = t.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function I(t, e) {
  return N(() => S(t, e), [t, e]);
}
function Ut(t, e) {
  return Object.keys(t).reduce((n, o) => (t[o] !== void 0 && (n[o] = t[o]), n), {});
}
const Wt = ({
  children: t,
  ...e
}) => /* @__PURE__ */ w.jsx(w.Fragment, {
  children: t(e)
});
function Se(t) {
  return O.createElement(Wt, {
    children: t
  });
}
function B(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((l, r) => {
      var C, b;
      if (typeof l != "object")
        return e != null && e.fallback ? e.fallback(l) : l;
      const i = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...l.props,
        key: ((C = l.props) == null ? void 0 : C.key) ?? (n ? `${n}-${r}` : `${r}`)
      }) : {
        ...l.props,
        key: ((b = l.props) == null ? void 0 : b.key) ?? (n ? `${n}-${r}` : `${r}`)
      };
      let s = i;
      Object.keys(l.slots).forEach((c) => {
        if (!l.slots[c] || !(l.slots[c] instanceof Element) && !l.slots[c].el)
          return;
        const _ = c.split(".");
        _.forEach((g, E) => {
          s[g] || (s[g] = {}), E !== _.length - 1 && (s = i[g]);
        });
        const d = l.slots[c];
        let x, y, a = (e == null ? void 0 : e.clone) ?? !1, h = e == null ? void 0 : e.forceClone;
        d instanceof Element ? x = d : (x = d.el, y = d.callback, a = d.clone ?? a, h = d.forceClone ?? h), h = h ?? !!y, s[_[_.length - 1]] = x ? y ? (...g) => (y(_[_.length - 1], g), /* @__PURE__ */ w.jsx(V, {
          ...l.ctx,
          params: g,
          forceClone: h,
          children: /* @__PURE__ */ w.jsx(R, {
            slot: x,
            clone: a
          })
        })) : Se((g) => /* @__PURE__ */ w.jsx(V, {
          ...l.ctx,
          forceClone: h,
          children: /* @__PURE__ */ w.jsx(R, {
            ...g,
            slot: x,
            clone: a
          })
        })) : s[_[_.length - 1]], s = i;
      });
      const u = (e == null ? void 0 : e.children) || "children";
      return l[u] ? i[u] = B(l[u], e, `${r}`) : e != null && e.children && (i[u] = void 0, Reflect.deleteProperty(i, u)), i;
    });
}
function be(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? Se((n) => /* @__PURE__ */ w.jsx(V, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ w.jsx(R, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...n
    })
  })) : /* @__PURE__ */ w.jsx(R, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function M({
  key: t,
  slots: e,
  targets: n
}, o) {
  return e[t] ? (...l) => n ? n.map((r, i) => /* @__PURE__ */ w.jsx(O.Fragment, {
    children: be(r, {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }, i)) : /* @__PURE__ */ w.jsx(w.Fragment, {
    children: be(e[t], {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }) : void 0;
}
const {
  useItems: Ht,
  withItemsContextProvider: Dt,
  ItemHandler: qt
} = z("antd-table-columns"), {
  useItems: Vt,
  withItemsContextProvider: Kt,
  ItemHandler: Yt
} = z("antd-table-row-selection-selections"), {
  useItems: Bt,
  withItemsContextProvider: zt,
  ItemHandler: Zt
} = z("antd-table-row-selection"), {
  useItems: Gt,
  withItemsContextProvider: Jt,
  ItemHandler: $t
} = z("antd-table-expandable");
function U(t) {
  return typeof t == "object" && t !== null ? t : {};
}
const er = jt(zt(["rowSelection"], Jt(["expandable"], Dt(["default"], ({
  children: t,
  slots: e,
  columns: n,
  getPopupContainer: o,
  pagination: l,
  loading: r,
  rowKey: i,
  rowClassName: s,
  summary: u,
  rowSelection: C,
  expandable: b,
  sticky: c,
  footer: _,
  showSorterTooltip: d,
  onRow: x,
  onHeaderRow: y,
  components: a,
  setSlotParams: h,
  ...g
}) => {
  const {
    items: {
      default: E
    }
  } = Ht(), {
    items: {
      expandable: f
    }
  } = Gt(), {
    items: {
      rowSelection: P
    }
  } = Bt(), m = I(o), v = e["loading.tip"] || e["loading.indicator"], T = U(r), L = e["pagination.showQuickJumper.goButton"] || e["pagination.itemRender"], F = U(l), Pe = I(F.showTotal), Te = I(s), Oe = I(i, !0), Re = e["showSorterTooltip.title"] || typeof d == "object", A = U(d), ke = I(A.afterOpenChange), je = I(A.getPopupContainer), Ne = typeof c == "object", Z = U(c), Le = I(Z.getContainer), Fe = I(x), Ae = I(y), Me = I(u), Ue = I(_), We = N(() => {
    var re, ne, le, ie, oe, ae, se;
    const p = S((re = a == null ? void 0 : a.header) == null ? void 0 : re.table), $ = S((ne = a == null ? void 0 : a.header) == null ? void 0 : ne.row), ee = S((le = a == null ? void 0 : a.header) == null ? void 0 : le.cell), te = S((ie = a == null ? void 0 : a.header) == null ? void 0 : ie.wrapper);
    return {
      table: S(a == null ? void 0 : a.table),
      header: p || $ || ee || te ? {
        table: p,
        row: $,
        cell: ee,
        wrapper: te
      } : void 0,
      body: typeof (a == null ? void 0 : a.body) == "object" ? {
        wrapper: S((oe = a == null ? void 0 : a.body) == null ? void 0 : oe.wrapper),
        row: S((ae = a == null ? void 0 : a.body) == null ? void 0 : ae.row),
        cell: S((se = a == null ? void 0 : a.body) == null ? void 0 : se.cell)
      } : S(a == null ? void 0 : a.body)
    };
  }, [a]);
  return /* @__PURE__ */ w.jsxs(w.Fragment, {
    children: [/* @__PURE__ */ w.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ w.jsx(j, {
      ...g,
      components: We,
      columns: N(() => (n == null ? void 0 : n.map((p) => p === "EXPAND_COLUMN" ? j.EXPAND_COLUMN : p === "SELECTION_COLUMN" ? j.SELECTION_COLUMN : p)) || B(E, {
        fallback: (p) => p === "EXPAND_COLUMN" ? j.EXPAND_COLUMN : p === "SELECTION_COLUMN" ? j.SELECTION_COLUMN : p
      }), [E, n]),
      onRow: Fe,
      onHeaderRow: Ae,
      summary: e.summary ? M({
        slots: e,
        key: "summary"
      }) : Me,
      rowSelection: N(() => {
        var p;
        return C || ((p = B(P)) == null ? void 0 : p[0]);
      }, [C, P]),
      expandable: N(() => {
        var p;
        return b || ((p = B(f)) == null ? void 0 : p[0]);
      }, [b, f]),
      rowClassName: Te,
      rowKey: Oe || i,
      sticky: Ne ? {
        ...Z,
        getContainer: Le
      } : c,
      showSorterTooltip: Re ? {
        ...A,
        afterOpenChange: ke,
        getPopupContainer: je,
        title: e["showSorterTooltip.title"] ? /* @__PURE__ */ w.jsx(R, {
          slot: e["showSorterTooltip.title"]
        }) : A.title
      } : d,
      pagination: L ? Ut({
        ...F,
        showTotal: Pe,
        showQuickJumper: e["pagination.showQuickJumper.goButton"] ? {
          goButton: /* @__PURE__ */ w.jsx(R, {
            slot: e["pagination.showQuickJumper.goButton"]
          })
        } : F.showQuickJumper,
        itemRender: e["pagination.itemRender"] ? M({
          slots: e,
          key: "pagination.itemRender"
        }) : F.itemRender
      }) : l,
      getPopupContainer: m,
      loading: v ? {
        ...T,
        tip: e["loading.tip"] ? /* @__PURE__ */ w.jsx(R, {
          slot: e["loading.tip"]
        }) : T.tip,
        indicator: e["loading.indicator"] ? /* @__PURE__ */ w.jsx(R, {
          slot: e["loading.indicator"]
        }) : T.indicator
      } : r,
      footer: e.footer ? M({
        slots: e,
        key: "footer"
      }) : Ue,
      title: e.title ? M({
        slots: e,
        key: "title"
      }) : g.title
    })]
  });
}))));
export {
  er as Table,
  er as default
};
