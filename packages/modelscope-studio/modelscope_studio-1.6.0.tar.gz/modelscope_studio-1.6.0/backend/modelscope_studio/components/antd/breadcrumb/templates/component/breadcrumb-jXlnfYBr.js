import { i as de, a as W, r as fe, Z as T, g as me } from "./Index-rOKSEzoB.js";
const E = window.ms_globals.React, oe = window.ms_globals.React.forwardRef, ae = window.ms_globals.React.useRef, ce = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, ue = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, F = window.ms_globals.internalContext.ContextPropsProvider, he = window.ms_globals.antd.Breadcrumb, ge = window.ms_globals.createItemsContext.createItemsContext;
var be = /\s/;
function we(t) {
  for (var e = t.length; e-- && be.test(t.charAt(e)); )
    ;
  return e;
}
var xe = /^\s+/;
function pe(t) {
  return t && t.slice(0, we(t) + 1).replace(xe, "");
}
var D = NaN, Ce = /^[-+]0x[0-9a-f]+$/i, Ee = /^0b[01]+$/i, ve = /^0o[0-7]+$/i, ye = parseInt;
function U(t) {
  if (typeof t == "number")
    return t;
  if (de(t))
    return D;
  if (W(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = W(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = pe(t);
  var s = Ee.test(t);
  return s || ve.test(t) ? ye(t.slice(2), s ? 2 : 8) : Ce.test(t) ? D : +t;
}
var L = function() {
  return fe.Date.now();
}, Ie = "Expected a function", Se = Math.max, Pe = Math.min;
function Re(t, e, s) {
  var o, n, r, l, a, i, w = 0, x = !1, c = !1, h = !0;
  if (typeof t != "function")
    throw new TypeError(Ie);
  e = U(e) || 0, W(s) && (x = !!s.leading, c = "maxWait" in s, r = c ? Se(U(s.maxWait) || 0, e) : r, h = "trailing" in s ? !!s.trailing : h);
  function u(m) {
    var v = o, P = n;
    return o = n = void 0, w = m, l = t.apply(P, v), l;
  }
  function p(m) {
    return w = m, a = setTimeout(_, e), x ? u(m) : l;
  }
  function C(m) {
    var v = m - i, P = m - w, z = e - v;
    return c ? Pe(z, r - P) : z;
  }
  function d(m) {
    var v = m - i, P = m - w;
    return i === void 0 || v >= e || v < 0 || c && P >= r;
  }
  function _() {
    var m = L();
    if (d(m))
      return g(m);
    a = setTimeout(_, C(m));
  }
  function g(m) {
    return a = void 0, h && o ? u(m) : (o = n = void 0, l);
  }
  function y() {
    a !== void 0 && clearTimeout(a), w = 0, o = i = n = a = void 0;
  }
  function f() {
    return a === void 0 ? l : g(L());
  }
  function I() {
    var m = L(), v = d(m);
    if (o = arguments, n = this, i = m, v) {
      if (a === void 0)
        return p(i);
      if (c)
        return clearTimeout(a), a = setTimeout(_, e), u(i);
    }
    return a === void 0 && (a = setTimeout(_, e)), l;
  }
  return I.cancel = y, I.flush = f, I;
}
var Q = {
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
var Te = E, ke = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Le = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function $(t, e, s) {
  var o, n = {}, r = null, l = null;
  s !== void 0 && (r = "" + s), e.key !== void 0 && (r = "" + e.key), e.ref !== void 0 && (l = e.ref);
  for (o in e) je.call(e, o) && !Ne.hasOwnProperty(o) && (n[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) n[o] === void 0 && (n[o] = e[o]);
  return {
    $$typeof: ke,
    type: t,
    key: r,
    ref: l,
    props: n,
    _owner: Le.current
  };
}
j.Fragment = Oe;
j.jsx = $;
j.jsxs = $;
Q.exports = j;
var b = Q.exports;
const {
  SvelteComponent: Ae,
  assign: H,
  binding_callbacks: G,
  check_outros: We,
  children: ee,
  claim_element: te,
  claim_space: Fe,
  component_subscribe: q,
  compute_slots: Me,
  create_slot: Be,
  detach: S,
  element: re,
  empty: V,
  exclude_internal_props: J,
  get_all_dirty_from_scope: ze,
  get_slot_changes: De,
  group_outros: Ue,
  init: He,
  insert_hydration: k,
  safe_not_equal: Ge,
  set_custom_element_data: ne,
  space: qe,
  transition_in: O,
  transition_out: M,
  update_slot_base: Ve
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function X(t) {
  let e, s;
  const o = (
    /*#slots*/
    t[7].default
  ), n = Be(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = re("svelte-slot"), n && n.c(), this.h();
    },
    l(r) {
      e = te(r, "SVELTE-SLOT", {
        class: !0
      });
      var l = ee(e);
      n && n.l(l), l.forEach(S), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      k(r, e, l), n && n.m(e, null), t[9](e), s = !0;
    },
    p(r, l) {
      n && n.p && (!s || l & /*$$scope*/
      64) && Ve(
        n,
        o,
        r,
        /*$$scope*/
        r[6],
        s ? De(
          o,
          /*$$scope*/
          r[6],
          l,
          null
        ) : ze(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      s || (O(n, r), s = !0);
    },
    o(r) {
      M(n, r), s = !1;
    },
    d(r) {
      r && S(e), n && n.d(r), t[9](null);
    }
  };
}
function Ke(t) {
  let e, s, o, n, r = (
    /*$$slots*/
    t[4].default && X(t)
  );
  return {
    c() {
      e = re("react-portal-target"), s = qe(), r && r.c(), o = V(), this.h();
    },
    l(l) {
      e = te(l, "REACT-PORTAL-TARGET", {
        class: !0
      }), ee(e).forEach(S), s = Fe(l), r && r.l(l), o = V(), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(l, a) {
      k(l, e, a), t[8](e), k(l, s, a), r && r.m(l, a), k(l, o, a), n = !0;
    },
    p(l, [a]) {
      /*$$slots*/
      l[4].default ? r ? (r.p(l, a), a & /*$$slots*/
      16 && O(r, 1)) : (r = X(l), r.c(), O(r, 1), r.m(o.parentNode, o)) : r && (Ue(), M(r, 1, 1, () => {
        r = null;
      }), We());
    },
    i(l) {
      n || (O(r), n = !0);
    },
    o(l) {
      M(r), n = !1;
    },
    d(l) {
      l && (S(e), S(s), S(o)), t[8](null), r && r.d(l);
    }
  };
}
function Y(t) {
  const {
    svelteInit: e,
    ...s
  } = t;
  return s;
}
function Qe(t, e, s) {
  let o, n, {
    $$slots: r = {},
    $$scope: l
  } = e;
  const a = Me(r);
  let {
    svelteInit: i
  } = e;
  const w = T(Y(e)), x = T();
  q(t, x, (f) => s(0, o = f));
  const c = T();
  q(t, c, (f) => s(1, n = f));
  const h = [], u = Xe("$$ms-gr-react-wrapper"), {
    slotKey: p,
    slotIndex: C,
    subSlotIndex: d
  } = me() || {}, _ = i({
    parent: u,
    props: w,
    target: x,
    slot: c,
    slotKey: p,
    slotIndex: C,
    subSlotIndex: d,
    onDestroy(f) {
      h.push(f);
    }
  });
  Ze("$$ms-gr-react-wrapper", _), Je(() => {
    w.set(Y(e));
  }), Ye(() => {
    h.forEach((f) => f());
  });
  function g(f) {
    G[f ? "unshift" : "push"](() => {
      o = f, x.set(o);
    });
  }
  function y(f) {
    G[f ? "unshift" : "push"](() => {
      n = f, c.set(n);
    });
  }
  return t.$$set = (f) => {
    s(17, e = H(H({}, e), J(f))), "svelteInit" in f && s(5, i = f.svelteInit), "$$scope" in f && s(6, l = f.$$scope);
  }, e = J(e), [o, n, x, c, a, i, l, r, g, y];
}
class $e extends Ae {
  constructor(e) {
    super(), He(this, e, Qe, Ke, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ut
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, N = window.ms_globals.tree;
function et(t, e = {}) {
  function s(o) {
    const n = T(), r = new $e({
      ...o,
      props: {
        svelteInit(l) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: t,
            props: l.props,
            slot: l.slot,
            target: l.target,
            slotIndex: l.slotIndex,
            subSlotIndex: l.subSlotIndex,
            ignore: e.ignore,
            slotKey: l.slotKey,
            nodes: []
          }, i = l.parent ?? N;
          return i.nodes = [...i.nodes, a], Z({
            createPortal: A,
            node: N
          }), l.onDestroy(() => {
            i.nodes = i.nodes.filter((w) => w.svelteInstance !== n), Z({
              createPortal: A,
              node: N
            });
          }), a;
        },
        ...o.props
      }
    });
    return n.set(r), r;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((n) => {
      window.ms_globals.initialize = () => {
        n();
      };
    })), window.ms_globals.initializePromise.then(() => {
      o(s);
    });
  });
}
const tt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function rt(t) {
  return t ? Object.keys(t).reduce((e, s) => {
    const o = t[s];
    return e[s] = nt(s, o), e;
  }, {}) : {};
}
function nt(t, e) {
  return typeof e == "number" && !tt.includes(t) ? e + "px" : e;
}
function B(t) {
  const e = [], s = t.cloneNode(!1);
  if (t._reactElement) {
    const n = E.Children.toArray(t._reactElement.props.children).map((r) => {
      if (E.isValidElement(r) && r.props.__slot__) {
        const {
          portals: l,
          clonedElement: a
        } = B(r.props.el);
        return E.cloneElement(r, {
          ...r.props,
          el: a,
          children: [...E.Children.toArray(r.props.children), ...l]
        });
      }
      return null;
    });
    return n.originalChildren = t._reactElement.props.children, e.push(A(E.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: n
    }), s)), {
      clonedElement: s,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((n) => {
    t.getEventListeners(n).forEach(({
      listener: l,
      type: a,
      useCapture: i
    }) => {
      s.addEventListener(a, l, i);
    });
  });
  const o = Array.from(t.childNodes);
  for (let n = 0; n < o.length; n++) {
    const r = o[n];
    if (r.nodeType === 1) {
      const {
        clonedElement: l,
        portals: a
      } = B(r);
      e.push(...a), s.appendChild(l);
    } else r.nodeType === 3 && s.appendChild(r.cloneNode());
  }
  return {
    clonedElement: s,
    portals: e
  };
}
function lt(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const R = oe(({
  slot: t,
  clone: e,
  className: s,
  style: o,
  observeAttributes: n
}, r) => {
  const l = ae(), [a, i] = ce([]), {
    forceClone: w
  } = _e(), x = w ? !0 : e;
  return ie(() => {
    var C;
    if (!l.current || !t)
      return;
    let c = t;
    function h() {
      let d = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (d = c.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), lt(r, d), s && d.classList.add(...s.split(" ")), o) {
        const _ = rt(o);
        Object.keys(_).forEach((g) => {
          d.style[g] = _[g];
        });
      }
    }
    let u = null, p = null;
    if (x && window.MutationObserver) {
      let d = function() {
        var f, I, m;
        (f = l.current) != null && f.contains(c) && ((I = l.current) == null || I.removeChild(c));
        const {
          portals: g,
          clonedElement: y
        } = B(t);
        c = y, i(g), c.style.display = "contents", p && clearTimeout(p), p = setTimeout(() => {
          h();
        }, 50), (m = l.current) == null || m.appendChild(c);
      };
      d();
      const _ = Re(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: n
        });
      }, 50);
      u = new window.MutationObserver(_), u.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", h(), (C = l.current) == null || C.appendChild(c);
    return () => {
      var d, _;
      c.style.display = "", (d = l.current) != null && d.contains(c) && ((_ = l.current) == null || _.removeChild(c)), u == null || u.disconnect();
    };
  }, [t, x, s, o, r, n, w]), E.createElement("react-child", {
    ref: l,
    style: {
      display: "contents"
    }
  }, ...a);
}), st = ({
  children: t,
  ...e
}) => /* @__PURE__ */ b.jsx(b.Fragment, {
  children: t(e)
});
function le(t) {
  return E.createElement(st, {
    children: t
  });
}
function se(t, e, s) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((n, r) => {
      var w, x;
      if (typeof n != "object")
        return e != null && e.fallback ? e.fallback(n) : n;
      const l = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...n.props,
        key: ((w = n.props) == null ? void 0 : w.key) ?? (s ? `${s}-${r}` : `${r}`)
      }) : {
        ...n.props,
        key: ((x = n.props) == null ? void 0 : x.key) ?? (s ? `${s}-${r}` : `${r}`)
      };
      let a = l;
      Object.keys(n.slots).forEach((c) => {
        if (!n.slots[c] || !(n.slots[c] instanceof Element) && !n.slots[c].el)
          return;
        const h = c.split(".");
        h.forEach((g, y) => {
          a[g] || (a[g] = {}), y !== h.length - 1 && (a = l[g]);
        });
        const u = n.slots[c];
        let p, C, d = (e == null ? void 0 : e.clone) ?? !1, _ = e == null ? void 0 : e.forceClone;
        u instanceof Element ? p = u : (p = u.el, C = u.callback, d = u.clone ?? d, _ = u.forceClone ?? _), _ = _ ?? !!C, a[h[h.length - 1]] = p ? C ? (...g) => (C(h[h.length - 1], g), /* @__PURE__ */ b.jsx(F, {
          ...n.ctx,
          params: g,
          forceClone: _,
          children: /* @__PURE__ */ b.jsx(R, {
            slot: p,
            clone: d
          })
        })) : le((g) => /* @__PURE__ */ b.jsx(F, {
          ...n.ctx,
          forceClone: _,
          children: /* @__PURE__ */ b.jsx(R, {
            ...g,
            slot: p,
            clone: d
          })
        })) : a[h[h.length - 1]], a = l;
      });
      const i = (e == null ? void 0 : e.children) || "children";
      return n[i] ? l[i] = se(n[i], e, `${r}`) : e != null && e.children && (l[i] = void 0, Reflect.deleteProperty(l, i)), l;
    });
}
function K(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? le((s) => /* @__PURE__ */ b.jsx(F, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ b.jsx(R, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...s
    })
  })) : /* @__PURE__ */ b.jsx(R, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function ot({
  key: t,
  slots: e,
  targets: s
}, o) {
  return e[t] ? (...n) => s ? s.map((r, l) => /* @__PURE__ */ b.jsx(E.Fragment, {
    children: K(r, {
      clone: !0,
      params: n,
      forceClone: (o == null ? void 0 : o.forceClone) ?? !0
    })
  }, l)) : /* @__PURE__ */ b.jsx(b.Fragment, {
    children: K(e[t], {
      clone: !0,
      params: n,
      forceClone: (o == null ? void 0 : o.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: at,
  withItemsContextProvider: ct,
  ItemHandler: dt
} = ge("antd-breadcrumb-items"), ft = et(ct(["default", "items"], ({
  slots: t,
  items: e,
  setSlotParams: s,
  children: o,
  ...n
}) => {
  const {
    items: r
  } = at(), l = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ b.jsxs(b.Fragment, {
    children: [/* @__PURE__ */ b.jsx("div", {
      style: {
        display: "none"
      },
      children: o
    }), /* @__PURE__ */ b.jsx(he, {
      ...n,
      itemRender: t.itemRender ? ot({
        slots: t,
        key: "itemRender"
      }, {}) : n.itemRender,
      items: ue(() => e || se(l, {
        // clone: true,
      }), [e, l]),
      separator: t.separator ? /* @__PURE__ */ b.jsx(R, {
        slot: t.separator,
        clone: !0
      }) : n.separator
    })]
  });
}));
export {
  ft as Breadcrumb,
  ft as default
};
