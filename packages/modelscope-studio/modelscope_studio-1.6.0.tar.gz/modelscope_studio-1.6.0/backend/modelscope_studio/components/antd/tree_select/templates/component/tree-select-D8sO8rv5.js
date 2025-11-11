import { i as _e, a as z, r as he, Z as j, g as ge, b as we } from "./Index-CT39uA6k.js";
const R = window.ms_globals.React, ue = window.ms_globals.React.forwardRef, de = window.ms_globals.React.useRef, fe = window.ms_globals.React.useState, me = window.ms_globals.React.useEffect, ee = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, pe = window.ms_globals.internalContext.useContextPropsContext, U = window.ms_globals.internalContext.ContextPropsProvider, xe = window.ms_globals.antd.TreeSelect, be = window.ms_globals.createItemsContext.createItemsContext;
var Ce = /\s/;
function ye(t) {
  for (var e = t.length; e-- && Ce.test(t.charAt(e)); )
    ;
  return e;
}
var ve = /^\s+/;
function Ie(t) {
  return t && t.slice(0, ye(t) + 1).replace(ve, "");
}
var H = NaN, Ee = /^[-+]0x[0-9a-f]+$/i, Re = /^0b[01]+$/i, Se = /^0o[0-7]+$/i, Te = parseInt;
function G(t) {
  if (typeof t == "number")
    return t;
  if (_e(t))
    return H;
  if (z(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = z(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ie(t);
  var o = Re.test(t);
  return o || Se.test(t) ? Te(t.slice(2), o ? 2 : 8) : Ee.test(t) ? H : +t;
}
var L = function() {
  return he.Date.now();
}, ke = "Expected a function", Pe = Math.max, Oe = Math.min;
function je(t, e, o) {
  var c, r, n, l, s, a, g = 0, C = !1, i = !1, w = !0;
  if (typeof t != "function")
    throw new TypeError(ke);
  e = G(e) || 0, z(o) && (C = !!o.leading, i = "maxWait" in o, n = i ? Pe(G(o.maxWait) || 0, e) : n, w = "trailing" in o ? !!o.trailing : w);
  function f(m) {
    var v = c, T = r;
    return c = r = void 0, g = m, l = t.apply(T, v), l;
  }
  function b(m) {
    return g = m, s = setTimeout(_, e), C ? f(m) : l;
  }
  function x(m) {
    var v = m - a, T = m - g, y = e - v;
    return i ? Oe(y, n - T) : y;
  }
  function u(m) {
    var v = m - a, T = m - g;
    return a === void 0 || v >= e || v < 0 || i && T >= n;
  }
  function _() {
    var m = L();
    if (u(m))
      return h(m);
    s = setTimeout(_, x(m));
  }
  function h(m) {
    return s = void 0, w && c ? f(m) : (c = r = void 0, l);
  }
  function I() {
    s !== void 0 && clearTimeout(s), g = 0, c = a = r = s = void 0;
  }
  function d() {
    return s === void 0 ? l : h(L());
  }
  function E() {
    var m = L(), v = u(m);
    if (c = arguments, r = this, a = m, v) {
      if (s === void 0)
        return b(a);
      if (i)
        return clearTimeout(s), s = setTimeout(_, e), f(a);
    }
    return s === void 0 && (s = setTimeout(_, e)), l;
  }
  return E.cancel = I, E.flush = d, E;
}
var te = {
  exports: {}
}, W = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Fe = R, Ne = Symbol.for("react.element"), We = Symbol.for("react.fragment"), Le = Object.prototype.hasOwnProperty, Ae = Fe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Me = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(t, e, o) {
  var c, r = {}, n = null, l = null;
  o !== void 0 && (n = "" + o), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (l = e.ref);
  for (c in e) Le.call(e, c) && !Me.hasOwnProperty(c) && (r[c] = e[c]);
  if (t && t.defaultProps) for (c in e = t.defaultProps, e) r[c] === void 0 && (r[c] = e[c]);
  return {
    $$typeof: Ne,
    type: t,
    key: n,
    ref: l,
    props: r,
    _owner: Ae.current
  };
}
W.Fragment = We;
W.jsx = ne;
W.jsxs = ne;
te.exports = W;
var p = te.exports;
const {
  SvelteComponent: ze,
  assign: q,
  binding_callbacks: V,
  check_outros: Ue,
  children: re,
  claim_element: le,
  claim_space: De,
  component_subscribe: J,
  compute_slots: Be,
  create_slot: He,
  detach: O,
  element: oe,
  empty: X,
  exclude_internal_props: Y,
  get_all_dirty_from_scope: Ge,
  get_slot_changes: qe,
  group_outros: Ve,
  init: Je,
  insert_hydration: F,
  safe_not_equal: Xe,
  set_custom_element_data: ce,
  space: Ye,
  transition_in: N,
  transition_out: D,
  update_slot_base: Ze
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ke,
  getContext: Qe,
  onDestroy: $e,
  setContext: et
} = window.__gradio__svelte__internal;
function Z(t) {
  let e, o;
  const c = (
    /*#slots*/
    t[7].default
  ), r = He(
    c,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = oe("svelte-slot"), r && r.c(), this.h();
    },
    l(n) {
      e = le(n, "SVELTE-SLOT", {
        class: !0
      });
      var l = re(e);
      r && r.l(l), l.forEach(O), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(n, l) {
      F(n, e, l), r && r.m(e, null), t[9](e), o = !0;
    },
    p(n, l) {
      r && r.p && (!o || l & /*$$scope*/
      64) && Ze(
        r,
        c,
        n,
        /*$$scope*/
        n[6],
        o ? qe(
          c,
          /*$$scope*/
          n[6],
          l,
          null
        ) : Ge(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (N(r, n), o = !0);
    },
    o(n) {
      D(r, n), o = !1;
    },
    d(n) {
      n && O(e), r && r.d(n), t[9](null);
    }
  };
}
function tt(t) {
  let e, o, c, r, n = (
    /*$$slots*/
    t[4].default && Z(t)
  );
  return {
    c() {
      e = oe("react-portal-target"), o = Ye(), n && n.c(), c = X(), this.h();
    },
    l(l) {
      e = le(l, "REACT-PORTAL-TARGET", {
        class: !0
      }), re(e).forEach(O), o = De(l), n && n.l(l), c = X(), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(l, s) {
      F(l, e, s), t[8](e), F(l, o, s), n && n.m(l, s), F(l, c, s), r = !0;
    },
    p(l, [s]) {
      /*$$slots*/
      l[4].default ? n ? (n.p(l, s), s & /*$$slots*/
      16 && N(n, 1)) : (n = Z(l), n.c(), N(n, 1), n.m(c.parentNode, c)) : n && (Ve(), D(n, 1, 1, () => {
        n = null;
      }), Ue());
    },
    i(l) {
      r || (N(n), r = !0);
    },
    o(l) {
      D(n), r = !1;
    },
    d(l) {
      l && (O(e), O(o), O(c)), t[8](null), n && n.d(l);
    }
  };
}
function K(t) {
  const {
    svelteInit: e,
    ...o
  } = t;
  return o;
}
function nt(t, e, o) {
  let c, r, {
    $$slots: n = {},
    $$scope: l
  } = e;
  const s = Be(n);
  let {
    svelteInit: a
  } = e;
  const g = j(K(e)), C = j();
  J(t, C, (d) => o(0, c = d));
  const i = j();
  J(t, i, (d) => o(1, r = d));
  const w = [], f = Qe("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: x,
    subSlotIndex: u
  } = ge() || {}, _ = a({
    parent: f,
    props: g,
    target: C,
    slot: i,
    slotKey: b,
    slotIndex: x,
    subSlotIndex: u,
    onDestroy(d) {
      w.push(d);
    }
  });
  et("$$ms-gr-react-wrapper", _), Ke(() => {
    g.set(K(e));
  }), $e(() => {
    w.forEach((d) => d());
  });
  function h(d) {
    V[d ? "unshift" : "push"](() => {
      c = d, C.set(c);
    });
  }
  function I(d) {
    V[d ? "unshift" : "push"](() => {
      r = d, i.set(r);
    });
  }
  return t.$$set = (d) => {
    o(17, e = q(q({}, e), Y(d))), "svelteInit" in d && o(5, a = d.svelteInit), "$$scope" in d && o(6, l = d.$$scope);
  }, e = Y(e), [c, r, C, i, s, a, l, n, h, I];
}
class rt extends ze {
  constructor(e) {
    super(), Je(this, e, nt, tt, Xe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: gt
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, A = window.ms_globals.tree;
function lt(t, e = {}) {
  function o(c) {
    const r = j(), n = new rt({
      ...c,
      props: {
        svelteInit(l) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: t,
            props: l.props,
            slot: l.slot,
            target: l.target,
            slotIndex: l.slotIndex,
            subSlotIndex: l.subSlotIndex,
            ignore: e.ignore,
            slotKey: l.slotKey,
            nodes: []
          }, a = l.parent ?? A;
          return a.nodes = [...a.nodes, s], Q({
            createPortal: M,
            node: A
          }), l.onDestroy(() => {
            a.nodes = a.nodes.filter((g) => g.svelteInstance !== r), Q({
              createPortal: M,
              node: A
            });
          }), s;
        },
        ...c.props
      }
    });
    return r.set(n), n;
  }
  return new Promise((c) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((r) => {
      window.ms_globals.initialize = () => {
        r();
      };
    })), window.ms_globals.initializePromise.then(() => {
      c(o);
    });
  });
}
const ot = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ct(t) {
  return t ? Object.keys(t).reduce((e, o) => {
    const c = t[o];
    return e[o] = st(o, c), e;
  }, {}) : {};
}
function st(t, e) {
  return typeof e == "number" && !ot.includes(t) ? e + "px" : e;
}
function B(t) {
  const e = [], o = t.cloneNode(!1);
  if (t._reactElement) {
    const r = R.Children.toArray(t._reactElement.props.children).map((n) => {
      if (R.isValidElement(n) && n.props.__slot__) {
        const {
          portals: l,
          clonedElement: s
        } = B(n.props.el);
        return R.cloneElement(n, {
          ...n.props,
          el: s,
          children: [...R.Children.toArray(n.props.children), ...l]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(M(R.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: r
    }), o)), {
      clonedElement: o,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((r) => {
    t.getEventListeners(r).forEach(({
      listener: l,
      type: s,
      useCapture: a
    }) => {
      o.addEventListener(s, l, a);
    });
  });
  const c = Array.from(t.childNodes);
  for (let r = 0; r < c.length; r++) {
    const n = c[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: l,
        portals: s
      } = B(n);
      e.push(...s), o.appendChild(l);
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
  style: c,
  observeAttributes: r
}, n) => {
  const l = de(), [s, a] = fe([]), {
    forceClone: g
  } = pe(), C = g ? !0 : e;
  return me(() => {
    var x;
    if (!l.current || !t)
      return;
    let i = t;
    function w() {
      let u = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (u = i.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), it(n, u), o && u.classList.add(...o.split(" ")), c) {
        const _ = ct(c);
        Object.keys(_).forEach((h) => {
          u.style[h] = _[h];
        });
      }
    }
    let f = null, b = null;
    if (C && window.MutationObserver) {
      let u = function() {
        var d, E, m;
        (d = l.current) != null && d.contains(i) && ((E = l.current) == null || E.removeChild(i));
        const {
          portals: h,
          clonedElement: I
        } = B(t);
        i = I, a(h), i.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          w();
        }, 50), (m = l.current) == null || m.appendChild(i);
      };
      u();
      const _ = je(() => {
        u(), f == null || f.disconnect(), f == null || f.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      f = new window.MutationObserver(_), f.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", w(), (x = l.current) == null || x.appendChild(i);
    return () => {
      var u, _;
      i.style.display = "", (u = l.current) != null && u.contains(i) && ((_ = l.current) == null || _.removeChild(i)), f == null || f.disconnect();
    };
  }, [t, C, o, c, n, r, g]), R.createElement("react-child", {
    ref: l,
    style: {
      display: "contents"
    }
  }, ...s);
});
function at(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function ut(t, e = !1) {
  try {
    if (we(t))
      return t;
    if (e && !at(t))
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
  return ee(() => ut(t, e), [t, e]);
}
function dt(t, e) {
  return Object.keys(t).reduce((o, c) => (t[c] !== void 0 && (o[c] = t[c]), o), {});
}
const ft = ({
  children: t,
  ...e
}) => /* @__PURE__ */ p.jsx(p.Fragment, {
  children: t(e)
});
function se(t) {
  return R.createElement(ft, {
    children: t
  });
}
function ie(t, e, o) {
  const c = t.filter(Boolean);
  if (c.length !== 0)
    return c.map((r, n) => {
      var g, C;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const l = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((g = r.props) == null ? void 0 : g.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...r.props,
        key: ((C = r.props) == null ? void 0 : C.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let s = l;
      Object.keys(r.slots).forEach((i) => {
        if (!r.slots[i] || !(r.slots[i] instanceof Element) && !r.slots[i].el)
          return;
        const w = i.split(".");
        w.forEach((h, I) => {
          s[h] || (s[h] = {}), I !== w.length - 1 && (s = l[h]);
        });
        const f = r.slots[i];
        let b, x, u = (e == null ? void 0 : e.clone) ?? !1, _ = e == null ? void 0 : e.forceClone;
        f instanceof Element ? b = f : (b = f.el, x = f.callback, u = f.clone ?? u, _ = f.forceClone ?? _), _ = _ ?? !!x, s[w[w.length - 1]] = b ? x ? (...h) => (x(w[w.length - 1], h), /* @__PURE__ */ p.jsx(U, {
          ...r.ctx,
          params: h,
          forceClone: _,
          children: /* @__PURE__ */ p.jsx(S, {
            slot: b,
            clone: u
          })
        })) : se((h) => /* @__PURE__ */ p.jsx(U, {
          ...r.ctx,
          forceClone: _,
          children: /* @__PURE__ */ p.jsx(S, {
            ...h,
            slot: b,
            clone: u
          })
        })) : s[w[w.length - 1]], s = l;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return r[a] ? l[a] = ie(r[a], e, `${n}`) : e != null && e.children && (l[a] = void 0, Reflect.deleteProperty(l, a)), l;
    });
}
function $(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? se((o) => /* @__PURE__ */ p.jsx(U, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ p.jsx(S, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...o
    })
  })) : /* @__PURE__ */ p.jsx(S, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function P({
  key: t,
  slots: e,
  targets: o
}, c) {
  return e[t] ? (...r) => o ? o.map((n, l) => /* @__PURE__ */ p.jsx(R.Fragment, {
    children: $(n, {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }, l)) : /* @__PURE__ */ p.jsx(p.Fragment, {
    children: $(e[t], {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: mt,
  useItems: _t,
  ItemHandler: wt
} = be("antd-tree-select-tree-nodes"), pt = lt(mt(["default", "treeData"], ({
  slots: t,
  filterTreeNode: e,
  getPopupContainer: o,
  dropdownRender: c,
  popupRender: r,
  tagRender: n,
  treeTitleRender: l,
  treeData: s,
  onValueChange: a,
  onChange: g,
  children: C,
  maxTagPlaceholder: i,
  elRef: w,
  setSlotParams: f,
  onLoadData: b,
  ...x
}) => {
  const u = k(e), _ = k(o), h = k(n), I = k(c), d = k(r), E = k(l), {
    items: m
  } = _t(), v = m.treeData.length > 0 ? m.treeData : m.default, T = ee(() => ({
    ...x,
    // eslint-disable-next-line require-await
    loadData: async (...y) => b == null ? void 0 : b(...y),
    treeData: s || ie(v, {
      clone: !0,
      itemPropsTransformer: (y) => y.value && y.key && y.value !== y.key ? {
        ...y,
        key: void 0
      } : y
    }),
    dropdownRender: t.dropdownRender ? P({
      slots: t,
      key: "dropdownRender"
    }) : I,
    popupRender: t.popupRender ? P({
      slots: t,
      key: "popupRender"
    }) : d,
    allowClear: t["allowClear.clearIcon"] ? {
      clearIcon: /* @__PURE__ */ p.jsx(S, {
        slot: t["allowClear.clearIcon"]
      })
    } : x.allowClear,
    suffixIcon: t.suffixIcon ? /* @__PURE__ */ p.jsx(S, {
      slot: t.suffixIcon
    }) : x.suffixIcon,
    prefix: t.prefix ? /* @__PURE__ */ p.jsx(S, {
      slot: t.prefix
    }) : x.prefix,
    switcherIcon: t.switcherIcon ? P({
      slots: t,
      key: "switcherIcon"
    }) : x.switcherIcon,
    getPopupContainer: _,
    tagRender: t.tagRender ? P({
      slots: t,
      key: "tagRender"
    }) : h,
    treeTitleRender: t.treeTitleRender ? P({
      slots: t,
      key: "treeTitleRender"
    }) : E,
    filterTreeNode: u || e,
    maxTagPlaceholder: t.maxTagPlaceholder ? P({
      slots: t,
      key: "maxTagPlaceholder"
    }) : i,
    notFoundContent: t.notFoundContent ? /* @__PURE__ */ p.jsx(S, {
      slot: t.notFoundContent
    }) : x.notFoundContent
  }), [I, d, e, u, _, i, b, x, f, v, t, h, s, E]);
  return /* @__PURE__ */ p.jsxs(p.Fragment, {
    children: [/* @__PURE__ */ p.jsx("div", {
      style: {
        display: "none"
      },
      children: C
    }), /* @__PURE__ */ p.jsx(xe, {
      ...dt(T),
      ref: w,
      onChange: (y, ...ae) => {
        g == null || g(y, ...ae), a(y);
      }
    })]
  });
}));
export {
  pt as TreeSelect,
  pt as default
};
