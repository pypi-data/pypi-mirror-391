import { i as me, a as D, r as _e, Z as k, g as he, b as ge } from "./Index-BB0JzqpV.js";
const v = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, ue = window.ms_globals.React.useRef, de = window.ms_globals.React.useState, fe = window.ms_globals.React.useEffect, ee = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, we = window.ms_globals.internalContext.useContextPropsContext, M = window.ms_globals.internalContext.ContextPropsProvider, pe = window.ms_globals.antd.Dropdown, xe = window.ms_globals.createItemsContext.createItemsContext;
var be = /\s/;
function Ce(t) {
  for (var e = t.length; e-- && be.test(t.charAt(e)); )
    ;
  return e;
}
var ve = /^\s+/;
function ye(t) {
  return t && t.slice(0, Ce(t) + 1).replace(ve, "");
}
var H = NaN, Ee = /^[-+]0x[0-9a-f]+$/i, Ie = /^0b[01]+$/i, Re = /^0o[0-7]+$/i, Se = parseInt;
function G(t) {
  if (typeof t == "number")
    return t;
  if (me(t))
    return H;
  if (D(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = D(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = ye(t);
  var o = Ie.test(t);
  return o || Re.test(t) ? Se(t.slice(2), o ? 2 : 8) : Ee.test(t) ? H : +t;
}
var F = function() {
  return _e.Date.now();
}, Pe = "Expected a function", ke = Math.max, Te = Math.min;
function Oe(t, e, o) {
  var s, r, n, l, c, a, g = 0, b = !1, i = !1, _ = !0;
  if (typeof t != "function")
    throw new TypeError(Pe);
  e = G(e) || 0, D(o) && (b = !!o.leading, i = "maxWait" in o, n = i ? ke(G(o.maxWait) || 0, e) : n, _ = "trailing" in o ? !!o.trailing : _);
  function u(m) {
    var y = s, S = r;
    return s = r = void 0, g = m, l = t.apply(S, y), l;
  }
  function x(m) {
    return g = m, c = setTimeout(h, e), b ? u(m) : l;
  }
  function C(m) {
    var y = m - a, S = m - g, B = e - y;
    return i ? Te(B, n - S) : B;
  }
  function d(m) {
    var y = m - a, S = m - g;
    return a === void 0 || y >= e || y < 0 || i && S >= n;
  }
  function h() {
    var m = F();
    if (d(m))
      return w(m);
    c = setTimeout(h, C(m));
  }
  function w(m) {
    return c = void 0, _ && s ? u(m) : (s = r = void 0, l);
  }
  function E() {
    c !== void 0 && clearTimeout(c), g = 0, s = a = r = c = void 0;
  }
  function f() {
    return c === void 0 ? l : w(F());
  }
  function I() {
    var m = F(), y = d(m);
    if (s = arguments, r = this, a = m, y) {
      if (c === void 0)
        return x(a);
      if (i)
        return clearTimeout(c), c = setTimeout(h, e), u(a);
    }
    return c === void 0 && (c = setTimeout(h, e)), l;
  }
  return I.cancel = E, I.flush = f, I;
}
var te = {
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
var je = v, Fe = Symbol.for("react.element"), Le = Symbol.for("react.fragment"), Ne = Object.prototype.hasOwnProperty, We = je.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ae = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(t, e, o) {
  var s, r = {}, n = null, l = null;
  o !== void 0 && (n = "" + o), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (l = e.ref);
  for (s in e) Ne.call(e, s) && !Ae.hasOwnProperty(s) && (r[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) r[s] === void 0 && (r[s] = e[s]);
  return {
    $$typeof: Fe,
    type: t,
    key: n,
    ref: l,
    props: r,
    _owner: We.current
  };
}
j.Fragment = Le;
j.jsx = ne;
j.jsxs = ne;
te.exports = j;
var p = te.exports;
const {
  SvelteComponent: De,
  assign: q,
  binding_callbacks: V,
  check_outros: Me,
  children: re,
  claim_element: le,
  claim_space: ze,
  component_subscribe: J,
  compute_slots: Ue,
  create_slot: Be,
  detach: R,
  element: oe,
  empty: X,
  exclude_internal_props: Y,
  get_all_dirty_from_scope: He,
  get_slot_changes: Ge,
  group_outros: qe,
  init: Ve,
  insert_hydration: T,
  safe_not_equal: Je,
  set_custom_element_data: se,
  space: Xe,
  transition_in: O,
  transition_out: z,
  update_slot_base: Ye
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ze,
  getContext: Ke,
  onDestroy: Qe,
  setContext: $e
} = window.__gradio__svelte__internal;
function Z(t) {
  let e, o;
  const s = (
    /*#slots*/
    t[7].default
  ), r = Be(
    s,
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
      r && r.l(l), l.forEach(R), this.h();
    },
    h() {
      se(e, "class", "svelte-1rt0kpf");
    },
    m(n, l) {
      T(n, e, l), r && r.m(e, null), t[9](e), o = !0;
    },
    p(n, l) {
      r && r.p && (!o || l & /*$$scope*/
      64) && Ye(
        r,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Ge(
          s,
          /*$$scope*/
          n[6],
          l,
          null
        ) : He(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (O(r, n), o = !0);
    },
    o(n) {
      z(r, n), o = !1;
    },
    d(n) {
      n && R(e), r && r.d(n), t[9](null);
    }
  };
}
function et(t) {
  let e, o, s, r, n = (
    /*$$slots*/
    t[4].default && Z(t)
  );
  return {
    c() {
      e = oe("react-portal-target"), o = Xe(), n && n.c(), s = X(), this.h();
    },
    l(l) {
      e = le(l, "REACT-PORTAL-TARGET", {
        class: !0
      }), re(e).forEach(R), o = ze(l), n && n.l(l), s = X(), this.h();
    },
    h() {
      se(e, "class", "svelte-1rt0kpf");
    },
    m(l, c) {
      T(l, e, c), t[8](e), T(l, o, c), n && n.m(l, c), T(l, s, c), r = !0;
    },
    p(l, [c]) {
      /*$$slots*/
      l[4].default ? n ? (n.p(l, c), c & /*$$slots*/
      16 && O(n, 1)) : (n = Z(l), n.c(), O(n, 1), n.m(s.parentNode, s)) : n && (qe(), z(n, 1, 1, () => {
        n = null;
      }), Me());
    },
    i(l) {
      r || (O(n), r = !0);
    },
    o(l) {
      z(n), r = !1;
    },
    d(l) {
      l && (R(e), R(o), R(s)), t[8](null), n && n.d(l);
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
function tt(t, e, o) {
  let s, r, {
    $$slots: n = {},
    $$scope: l
  } = e;
  const c = Ue(n);
  let {
    svelteInit: a
  } = e;
  const g = k(K(e)), b = k();
  J(t, b, (f) => o(0, s = f));
  const i = k();
  J(t, i, (f) => o(1, r = f));
  const _ = [], u = Ke("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: C,
    subSlotIndex: d
  } = he() || {}, h = a({
    parent: u,
    props: g,
    target: b,
    slot: i,
    slotKey: x,
    slotIndex: C,
    subSlotIndex: d,
    onDestroy(f) {
      _.push(f);
    }
  });
  $e("$$ms-gr-react-wrapper", h), Ze(() => {
    g.set(K(e));
  }), Qe(() => {
    _.forEach((f) => f());
  });
  function w(f) {
    V[f ? "unshift" : "push"](() => {
      s = f, b.set(s);
    });
  }
  function E(f) {
    V[f ? "unshift" : "push"](() => {
      r = f, i.set(r);
    });
  }
  return t.$$set = (f) => {
    o(17, e = q(q({}, e), Y(f))), "svelteInit" in f && o(5, a = f.svelteInit), "$$scope" in f && o(6, l = f.$$scope);
  }, e = Y(e), [s, r, b, i, c, a, l, n, w, E];
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
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, L = window.ms_globals.tree;
function rt(t, e = {}) {
  function o(s) {
    const r = k(), n = new nt({
      ...s,
      props: {
        svelteInit(l) {
          window.ms_globals.autokey += 1;
          const c = {
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
          }, a = l.parent ?? L;
          return a.nodes = [...a.nodes, c], Q({
            createPortal: A,
            node: L
          }), l.onDestroy(() => {
            a.nodes = a.nodes.filter((g) => g.svelteInstance !== r), Q({
              createPortal: A,
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
    const r = v.Children.toArray(t._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: l,
          clonedElement: c
        } = U(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: c,
          children: [...v.Children.toArray(n.props.children), ...l]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(A(v.cloneElement(t._reactElement, {
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
      type: c,
      useCapture: a
    }) => {
      o.addEventListener(c, l, a);
    });
  });
  const s = Array.from(t.childNodes);
  for (let r = 0; r < s.length; r++) {
    const n = s[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: l,
        portals: c
      } = U(n);
      e.push(...c), o.appendChild(l);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: e
  };
}
function ct(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const P = ae(({
  slot: t,
  clone: e,
  className: o,
  style: s,
  observeAttributes: r
}, n) => {
  const l = ue(), [c, a] = de([]), {
    forceClone: g
  } = we(), b = g ? !0 : e;
  return fe(() => {
    var C;
    if (!l.current || !t)
      return;
    let i = t;
    function _() {
      let d = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (d = i.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), ct(n, d), o && d.classList.add(...o.split(" ")), s) {
        const h = ot(s);
        Object.keys(h).forEach((w) => {
          d.style[w] = h[w];
        });
      }
    }
    let u = null, x = null;
    if (b && window.MutationObserver) {
      let d = function() {
        var f, I, m;
        (f = l.current) != null && f.contains(i) && ((I = l.current) == null || I.removeChild(i));
        const {
          portals: w,
          clonedElement: E
        } = U(t);
        i = E, a(w), i.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          _();
        }, 50), (m = l.current) == null || m.appendChild(i);
      };
      d();
      const h = Oe(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      u = new window.MutationObserver(h), u.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", _(), (C = l.current) == null || C.appendChild(i);
    return () => {
      var d, h;
      i.style.display = "", (d = l.current) != null && d.contains(i) && ((h = l.current) == null || h.removeChild(i)), u == null || u.disconnect();
    };
  }, [t, b, o, s, n, r, g]), v.createElement("react-child", {
    ref: l,
    style: {
      display: "contents"
    }
  }, ...c);
});
function it(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function at(t, e = !1) {
  try {
    if (ge(t))
      return t;
    if (e && !it(t))
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
function N(t, e) {
  return ee(() => at(t, e), [t, e]);
}
const ut = ({
  children: t,
  ...e
}) => /* @__PURE__ */ p.jsx(p.Fragment, {
  children: t(e)
});
function ce(t) {
  return v.createElement(ut, {
    children: t
  });
}
function ie(t, e, o) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((r, n) => {
      var g, b;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const l = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((g = r.props) == null ? void 0 : g.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...r.props,
        key: ((b = r.props) == null ? void 0 : b.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let c = l;
      Object.keys(r.slots).forEach((i) => {
        if (!r.slots[i] || !(r.slots[i] instanceof Element) && !r.slots[i].el)
          return;
        const _ = i.split(".");
        _.forEach((w, E) => {
          c[w] || (c[w] = {}), E !== _.length - 1 && (c = l[w]);
        });
        const u = r.slots[i];
        let x, C, d = (e == null ? void 0 : e.clone) ?? !1, h = e == null ? void 0 : e.forceClone;
        u instanceof Element ? x = u : (x = u.el, C = u.callback, d = u.clone ?? d, h = u.forceClone ?? h), h = h ?? !!C, c[_[_.length - 1]] = x ? C ? (...w) => (C(_[_.length - 1], w), /* @__PURE__ */ p.jsx(M, {
          ...r.ctx,
          params: w,
          forceClone: h,
          children: /* @__PURE__ */ p.jsx(P, {
            slot: x,
            clone: d
          })
        })) : ce((w) => /* @__PURE__ */ p.jsx(M, {
          ...r.ctx,
          forceClone: h,
          children: /* @__PURE__ */ p.jsx(P, {
            ...w,
            slot: x,
            clone: d
          })
        })) : c[_[_.length - 1]], c = l;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return r[a] ? l[a] = ie(r[a], e, `${n}`) : e != null && e.children && (l[a] = void 0, Reflect.deleteProperty(l, a)), l;
    });
}
function $(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? ce((o) => /* @__PURE__ */ p.jsx(M, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ p.jsx(P, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...o
    })
  })) : /* @__PURE__ */ p.jsx(P, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function W({
  key: t,
  slots: e,
  targets: o
}, s) {
  return e[t] ? (...r) => o ? o.map((n, l) => /* @__PURE__ */ p.jsx(v.Fragment, {
    children: $(n, {
      clone: !0,
      params: r,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }, l)) : /* @__PURE__ */ p.jsx(p.Fragment, {
    children: $(e[t], {
      clone: !0,
      params: r,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: dt,
  withItemsContextProvider: ft,
  ItemHandler: ht
} = xe("antd-menu-items"), gt = rt(ft(["menu.items"], ({
  getPopupContainer: t,
  innerStyle: e,
  children: o,
  slots: s,
  dropdownRender: r,
  popupRender: n,
  setSlotParams: l,
  ...c
}) => {
  var _, u, x;
  const a = N(t), g = N(r), b = N(n), {
    items: {
      "menu.items": i
    }
  } = dt();
  return /* @__PURE__ */ p.jsx(p.Fragment, {
    children: /* @__PURE__ */ p.jsx(pe, {
      ...c,
      menu: {
        ...c.menu,
        items: ee(() => {
          var C;
          return ((C = c.menu) == null ? void 0 : C.items) || ie(i, {
            clone: !0
          }) || [];
        }, [i, (_ = c.menu) == null ? void 0 : _.items]),
        expandIcon: s["menu.expandIcon"] ? W({
          slots: s,
          key: "menu.expandIcon"
        }, {}) : (u = c.menu) == null ? void 0 : u.expandIcon,
        overflowedIndicator: s["menu.overflowedIndicator"] ? /* @__PURE__ */ p.jsx(P, {
          slot: s["menu.overflowedIndicator"]
        }) : (x = c.menu) == null ? void 0 : x.overflowedIndicator
      },
      getPopupContainer: a,
      dropdownRender: s.dropdownRender ? W({
        slots: s,
        key: "dropdownRender"
      }, {}) : g,
      popupRender: s.popupRender ? W({
        slots: s,
        key: "popupRender"
      }, {}) : b,
      children: /* @__PURE__ */ p.jsx("div", {
        className: "ms-gr-antd-dropdown-content",
        style: {
          display: "inline-block",
          ...e
        },
        children: o
      })
    })
  });
}));
export {
  gt as Dropdown,
  gt as default
};
