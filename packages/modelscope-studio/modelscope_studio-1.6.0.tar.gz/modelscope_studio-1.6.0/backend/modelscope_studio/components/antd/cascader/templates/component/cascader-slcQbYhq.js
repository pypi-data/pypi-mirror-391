import { i as ye, a as U, r as Ie, b as ve, Z as F, g as Ee, c as Re } from "./Index-CwEWeat9.js";
const S = window.ms_globals.React, be = window.ms_globals.React.forwardRef, D = window.ms_globals.React.useRef, le = window.ms_globals.React.useState, z = window.ms_globals.React.useEffect, ce = window.ms_globals.React.useMemo, V = window.ms_globals.ReactDOM.createPortal, Se = window.ms_globals.internalContext.useContextPropsContext, B = window.ms_globals.internalContext.ContextPropsProvider, Pe = window.ms_globals.antd.Cascader, ke = window.ms_globals.createItemsContext.createItemsContext;
var Te = /\s/;
function je(e) {
  for (var n = e.length; n-- && Te.test(e.charAt(n)); )
    ;
  return n;
}
var Fe = /^\s+/;
function Oe(e) {
  return e && e.slice(0, je(e) + 1).replace(Fe, "");
}
var X = NaN, Le = /^[-+]0x[0-9a-f]+$/i, Ne = /^0b[01]+$/i, We = /^0o[0-7]+$/i, Ae = parseInt;
function Y(e) {
  if (typeof e == "number")
    return e;
  if (ye(e))
    return X;
  if (U(e)) {
    var n = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = U(n) ? n + "" : n;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Oe(e);
  var o = Ne.test(e);
  return o || We.test(e) ? Ae(e.slice(2), o ? 2 : 8) : Le.test(e) ? X : +e;
}
var A = function() {
  return Ie.Date.now();
}, Me = "Expected a function", De = Math.max, ze = Math.min;
function Ve(e, n, o) {
  var c, r, t, l, s, u, w = 0, x = !1, i = !1, _ = !0;
  if (typeof e != "function")
    throw new TypeError(Me);
  n = Y(n) || 0, U(o) && (x = !!o.leading, i = "maxWait" in o, t = i ? De(Y(o.maxWait) || 0, n) : t, _ = "trailing" in o ? !!o.trailing : _);
  function d(m) {
    var y = c, k = r;
    return c = r = void 0, w = m, l = e.apply(k, y), l;
  }
  function C(m) {
    return w = m, s = setTimeout(h, n), x ? d(m) : l;
  }
  function b(m) {
    var y = m - u, k = m - w, I = n - y;
    return i ? ze(I, t - k) : I;
  }
  function a(m) {
    var y = m - u, k = m - w;
    return u === void 0 || y >= n || y < 0 || i && k >= t;
  }
  function h() {
    var m = A();
    if (a(m))
      return p(m);
    s = setTimeout(h, b(m));
  }
  function p(m) {
    return s = void 0, _ && c ? d(m) : (c = r = void 0, l);
  }
  function R() {
    s !== void 0 && clearTimeout(s), w = 0, c = u = r = s = void 0;
  }
  function f() {
    return s === void 0 ? l : p(A());
  }
  function P() {
    var m = A(), y = a(m);
    if (c = arguments, r = this, u = m, y) {
      if (s === void 0)
        return C(u);
      if (i)
        return clearTimeout(s), s = setTimeout(h, n), d(u);
    }
    return s === void 0 && (s = setTimeout(h, n)), l;
  }
  return P.cancel = R, P.flush = f, P;
}
function Ue(e, n) {
  return ve(e, n);
}
var se = {
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
var Be = S, He = Symbol.for("react.element"), qe = Symbol.for("react.fragment"), Ge = Object.prototype.hasOwnProperty, Je = Be.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Xe = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ie(e, n, o) {
  var c, r = {}, t = null, l = null;
  o !== void 0 && (t = "" + o), n.key !== void 0 && (t = "" + n.key), n.ref !== void 0 && (l = n.ref);
  for (c in n) Ge.call(n, c) && !Xe.hasOwnProperty(c) && (r[c] = n[c]);
  if (e && e.defaultProps) for (c in n = e.defaultProps, n) r[c] === void 0 && (r[c] = n[c]);
  return {
    $$typeof: He,
    type: e,
    key: t,
    ref: l,
    props: r,
    _owner: Je.current
  };
}
N.Fragment = qe;
N.jsx = ie;
N.jsxs = ie;
se.exports = N;
var g = se.exports;
const {
  SvelteComponent: Ye,
  assign: Z,
  binding_callbacks: K,
  check_outros: Ze,
  children: ae,
  claim_element: ue,
  claim_space: Ke,
  component_subscribe: Q,
  compute_slots: Qe,
  create_slot: $e,
  detach: j,
  element: de,
  empty: $,
  exclude_internal_props: ee,
  get_all_dirty_from_scope: en,
  get_slot_changes: nn,
  group_outros: tn,
  init: rn,
  insert_hydration: O,
  safe_not_equal: on,
  set_custom_element_data: fe,
  space: ln,
  transition_in: L,
  transition_out: H,
  update_slot_base: cn
} = window.__gradio__svelte__internal, {
  beforeUpdate: sn,
  getContext: an,
  onDestroy: un,
  setContext: dn
} = window.__gradio__svelte__internal;
function ne(e) {
  let n, o;
  const c = (
    /*#slots*/
    e[7].default
  ), r = $e(
    c,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      n = de("svelte-slot"), r && r.c(), this.h();
    },
    l(t) {
      n = ue(t, "SVELTE-SLOT", {
        class: !0
      });
      var l = ae(n);
      r && r.l(l), l.forEach(j), this.h();
    },
    h() {
      fe(n, "class", "svelte-1rt0kpf");
    },
    m(t, l) {
      O(t, n, l), r && r.m(n, null), e[9](n), o = !0;
    },
    p(t, l) {
      r && r.p && (!o || l & /*$$scope*/
      64) && cn(
        r,
        c,
        t,
        /*$$scope*/
        t[6],
        o ? nn(
          c,
          /*$$scope*/
          t[6],
          l,
          null
        ) : en(
          /*$$scope*/
          t[6]
        ),
        null
      );
    },
    i(t) {
      o || (L(r, t), o = !0);
    },
    o(t) {
      H(r, t), o = !1;
    },
    d(t) {
      t && j(n), r && r.d(t), e[9](null);
    }
  };
}
function fn(e) {
  let n, o, c, r, t = (
    /*$$slots*/
    e[4].default && ne(e)
  );
  return {
    c() {
      n = de("react-portal-target"), o = ln(), t && t.c(), c = $(), this.h();
    },
    l(l) {
      n = ue(l, "REACT-PORTAL-TARGET", {
        class: !0
      }), ae(n).forEach(j), o = Ke(l), t && t.l(l), c = $(), this.h();
    },
    h() {
      fe(n, "class", "svelte-1rt0kpf");
    },
    m(l, s) {
      O(l, n, s), e[8](n), O(l, o, s), t && t.m(l, s), O(l, c, s), r = !0;
    },
    p(l, [s]) {
      /*$$slots*/
      l[4].default ? t ? (t.p(l, s), s & /*$$slots*/
      16 && L(t, 1)) : (t = ne(l), t.c(), L(t, 1), t.m(c.parentNode, c)) : t && (tn(), H(t, 1, 1, () => {
        t = null;
      }), Ze());
    },
    i(l) {
      r || (L(t), r = !0);
    },
    o(l) {
      H(t), r = !1;
    },
    d(l) {
      l && (j(n), j(o), j(c)), e[8](null), t && t.d(l);
    }
  };
}
function te(e) {
  const {
    svelteInit: n,
    ...o
  } = e;
  return o;
}
function mn(e, n, o) {
  let c, r, {
    $$slots: t = {},
    $$scope: l
  } = n;
  const s = Qe(t);
  let {
    svelteInit: u
  } = n;
  const w = F(te(n)), x = F();
  Q(e, x, (f) => o(0, c = f));
  const i = F();
  Q(e, i, (f) => o(1, r = f));
  const _ = [], d = an("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: b,
    subSlotIndex: a
  } = Ee() || {}, h = u({
    parent: d,
    props: w,
    target: x,
    slot: i,
    slotKey: C,
    slotIndex: b,
    subSlotIndex: a,
    onDestroy(f) {
      _.push(f);
    }
  });
  dn("$$ms-gr-react-wrapper", h), sn(() => {
    w.set(te(n));
  }), un(() => {
    _.forEach((f) => f());
  });
  function p(f) {
    K[f ? "unshift" : "push"](() => {
      c = f, x.set(c);
    });
  }
  function R(f) {
    K[f ? "unshift" : "push"](() => {
      r = f, i.set(r);
    });
  }
  return e.$$set = (f) => {
    o(17, n = Z(Z({}, n), ee(f))), "svelteInit" in f && o(5, u = f.svelteInit), "$$scope" in f && o(6, l = f.$$scope);
  }, n = ee(n), [c, r, x, i, s, u, l, t, p, R];
}
class hn extends Ye {
  constructor(n) {
    super(), rn(this, n, mn, fn, on, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Pn
} = window.__gradio__svelte__internal, re = window.ms_globals.rerender, M = window.ms_globals.tree;
function _n(e, n = {}) {
  function o(c) {
    const r = F(), t = new hn({
      ...c,
      props: {
        svelteInit(l) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: e,
            props: l.props,
            slot: l.slot,
            target: l.target,
            slotIndex: l.slotIndex,
            subSlotIndex: l.subSlotIndex,
            ignore: n.ignore,
            slotKey: l.slotKey,
            nodes: []
          }, u = l.parent ?? M;
          return u.nodes = [...u.nodes, s], re({
            createPortal: V,
            node: M
          }), l.onDestroy(() => {
            u.nodes = u.nodes.filter((w) => w.svelteInstance !== r), re({
              createPortal: V,
              node: M
            });
          }), s;
        },
        ...c.props
      }
    });
    return r.set(t), t;
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
const gn = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function pn(e) {
  return e ? Object.keys(e).reduce((n, o) => {
    const c = e[o];
    return n[o] = wn(o, c), n;
  }, {}) : {};
}
function wn(e, n) {
  return typeof n == "number" && !gn.includes(e) ? n + "px" : n;
}
function q(e) {
  const n = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const r = S.Children.toArray(e._reactElement.props.children).map((t) => {
      if (S.isValidElement(t) && t.props.__slot__) {
        const {
          portals: l,
          clonedElement: s
        } = q(t.props.el);
        return S.cloneElement(t, {
          ...t.props,
          el: s,
          children: [...S.Children.toArray(t.props.children), ...l]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, n.push(V(S.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: r
    }), o)), {
      clonedElement: o,
      portals: n
    };
  }
  Object.keys(e.getEventListeners()).forEach((r) => {
    e.getEventListeners(r).forEach(({
      listener: l,
      type: s,
      useCapture: u
    }) => {
      o.addEventListener(s, l, u);
    });
  });
  const c = Array.from(e.childNodes);
  for (let r = 0; r < c.length; r++) {
    const t = c[r];
    if (t.nodeType === 1) {
      const {
        clonedElement: l,
        portals: s
      } = q(t);
      n.push(...s), o.appendChild(l);
    } else t.nodeType === 3 && o.appendChild(t.cloneNode());
  }
  return {
    clonedElement: o,
    portals: n
  };
}
function xn(e, n) {
  e && (typeof e == "function" ? e(n) : e.current = n);
}
const E = be(({
  slot: e,
  clone: n,
  className: o,
  style: c,
  observeAttributes: r
}, t) => {
  const l = D(), [s, u] = le([]), {
    forceClone: w
  } = Se(), x = w ? !0 : n;
  return z(() => {
    var b;
    if (!l.current || !e)
      return;
    let i = e;
    function _() {
      let a = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (a = i.children[0], a.tagName.toLowerCase() === "react-portal-target" && a.children[0] && (a = a.children[0])), xn(t, a), o && a.classList.add(...o.split(" ")), c) {
        const h = pn(c);
        Object.keys(h).forEach((p) => {
          a.style[p] = h[p];
        });
      }
    }
    let d = null, C = null;
    if (x && window.MutationObserver) {
      let a = function() {
        var f, P, m;
        (f = l.current) != null && f.contains(i) && ((P = l.current) == null || P.removeChild(i));
        const {
          portals: p,
          clonedElement: R
        } = q(e);
        i = R, u(p), i.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          _();
        }, 50), (m = l.current) == null || m.appendChild(i);
      };
      a();
      const h = Ve(() => {
        a(), d == null || d.disconnect(), d == null || d.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      d = new window.MutationObserver(h), d.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", _(), (b = l.current) == null || b.appendChild(i);
    return () => {
      var a, h;
      i.style.display = "", (a = l.current) != null && a.contains(i) && ((h = l.current) == null || h.removeChild(i)), d == null || d.disconnect();
    };
  }, [e, x, o, c, t, r, w]), S.createElement("react-child", {
    ref: l,
    style: {
      display: "contents"
    }
  }, ...s);
});
function Cn(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function bn(e, n = !1) {
  try {
    if (Re(e))
      return e;
    if (n && !Cn(e))
      return;
    if (typeof e == "string") {
      let o = e.trim();
      return o.startsWith(";") && (o = o.slice(1)), o.endsWith(";") && (o = o.slice(0, -1)), new Function(`return (...args) => (${o})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function v(e, n) {
  return ce(() => bn(e, n), [e, n]);
}
function yn({
  value: e,
  onValueChange: n
}) {
  const [o, c] = le(e), r = D(n);
  r.current = n;
  const t = D(o);
  return t.current = o, z(() => {
    r.current(o);
  }, [o]), z(() => {
    Ue(e, t.current) || c(e);
  }, [e]), [o, c];
}
const In = ({
  children: e,
  ...n
}) => /* @__PURE__ */ g.jsx(g.Fragment, {
  children: e(n)
});
function me(e) {
  return S.createElement(In, {
    children: e
  });
}
function he(e, n, o) {
  const c = e.filter(Boolean);
  if (c.length !== 0)
    return c.map((r, t) => {
      var w, x;
      if (typeof r != "object")
        return n != null && n.fallback ? n.fallback(r) : r;
      const l = n != null && n.itemPropsTransformer ? n == null ? void 0 : n.itemPropsTransformer({
        ...r.props,
        key: ((w = r.props) == null ? void 0 : w.key) ?? (o ? `${o}-${t}` : `${t}`)
      }) : {
        ...r.props,
        key: ((x = r.props) == null ? void 0 : x.key) ?? (o ? `${o}-${t}` : `${t}`)
      };
      let s = l;
      Object.keys(r.slots).forEach((i) => {
        if (!r.slots[i] || !(r.slots[i] instanceof Element) && !r.slots[i].el)
          return;
        const _ = i.split(".");
        _.forEach((p, R) => {
          s[p] || (s[p] = {}), R !== _.length - 1 && (s = l[p]);
        });
        const d = r.slots[i];
        let C, b, a = (n == null ? void 0 : n.clone) ?? !1, h = n == null ? void 0 : n.forceClone;
        d instanceof Element ? C = d : (C = d.el, b = d.callback, a = d.clone ?? a, h = d.forceClone ?? h), h = h ?? !!b, s[_[_.length - 1]] = C ? b ? (...p) => (b(_[_.length - 1], p), /* @__PURE__ */ g.jsx(B, {
          ...r.ctx,
          params: p,
          forceClone: h,
          children: /* @__PURE__ */ g.jsx(E, {
            slot: C,
            clone: a
          })
        })) : me((p) => /* @__PURE__ */ g.jsx(B, {
          ...r.ctx,
          forceClone: h,
          children: /* @__PURE__ */ g.jsx(E, {
            ...p,
            slot: C,
            clone: a
          })
        })) : s[_[_.length - 1]], s = l;
      });
      const u = (n == null ? void 0 : n.children) || "children";
      return r[u] ? l[u] = he(r[u], n, `${t}`) : n != null && n.children && (l[u] = void 0, Reflect.deleteProperty(l, u)), l;
    });
}
function oe(e, n) {
  return e ? n != null && n.forceClone || n != null && n.params ? me((o) => /* @__PURE__ */ g.jsx(B, {
    forceClone: n == null ? void 0 : n.forceClone,
    params: n == null ? void 0 : n.params,
    children: /* @__PURE__ */ g.jsx(E, {
      slot: e,
      clone: n == null ? void 0 : n.clone,
      ...o
    })
  })) : /* @__PURE__ */ g.jsx(E, {
    slot: e,
    clone: n == null ? void 0 : n.clone
  }) : null;
}
function T({
  key: e,
  slots: n,
  targets: o
}, c) {
  return n[e] ? (...r) => o ? o.map((t, l) => /* @__PURE__ */ g.jsx(S.Fragment, {
    children: oe(t, {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }, l)) : /* @__PURE__ */ g.jsx(g.Fragment, {
    children: oe(n[e], {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }) : void 0;
}
const {
  useItems: vn,
  withItemsContextProvider: En,
  ItemHandler: kn
} = ke("antd-cascader-options");
function Rn(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const Tn = _n(En(["default", "options"], ({
  slots: e,
  children: n,
  onValueChange: o,
  onChange: c,
  displayRender: r,
  elRef: t,
  getPopupContainer: l,
  tagRender: s,
  maxTagPlaceholder: u,
  dropdownRender: w,
  popupRender: x,
  optionRender: i,
  showSearch: _,
  options: d,
  setSlotParams: C,
  onLoadData: b,
  ...a
}) => {
  const h = v(l), p = v(r), R = v(s), f = v(i), P = v(w), m = v(x), y = v(u), k = typeof _ == "object" || e["showSearch.render"], I = Rn(_), _e = v(I.filter), ge = v(I.render), pe = v(I.sort), [we, xe] = yn({
    onValueChange: o,
    value: a.value
  }), {
    items: W
  } = vn(), G = W.options.length > 0 ? W.options : W.default;
  return /* @__PURE__ */ g.jsxs(g.Fragment, {
    children: [/* @__PURE__ */ g.jsx("div", {
      style: {
        display: "none"
      },
      children: n
    }), /* @__PURE__ */ g.jsx(Pe, {
      ...a,
      ref: t,
      value: we,
      options: ce(() => d || he(G, {
        clone: !0
      }), [d, G]),
      showSearch: k ? {
        ...I,
        filter: _e || I.filter,
        render: e["showSearch.render"] ? T({
          slots: e,
          key: "showSearch.render"
        }) : ge || I.render,
        sort: pe || I.sort
      } : _,
      loadData: b,
      optionRender: f,
      getPopupContainer: h,
      prefix: e.prefix ? /* @__PURE__ */ g.jsx(E, {
        slot: e.prefix
      }) : a.prefix,
      dropdownRender: e.dropdownRender ? T({
        slots: e,
        key: "dropdownRender"
      }) : P,
      popupRender: e.popupRender ? T({
        slots: e,
        key: "popupRender"
      }) : m,
      displayRender: e.displayRender ? T({
        slots: e,
        key: "displayRender"
      }) : p,
      tagRender: e.tagRender ? T({
        slots: e,
        key: "tagRender"
      }) : R,
      onChange: (J, ...Ce) => {
        c == null || c(J, ...Ce), xe(J);
      },
      suffixIcon: e.suffixIcon ? /* @__PURE__ */ g.jsx(E, {
        slot: e.suffixIcon
      }) : a.suffixIcon,
      expandIcon: e.expandIcon ? /* @__PURE__ */ g.jsx(E, {
        slot: e.expandIcon
      }) : a.expandIcon,
      removeIcon: e.removeIcon ? /* @__PURE__ */ g.jsx(E, {
        slot: e.removeIcon
      }) : a.removeIcon,
      notFoundContent: e.notFoundContent ? /* @__PURE__ */ g.jsx(E, {
        slot: e.notFoundContent
      }) : a.notFoundContent,
      maxTagPlaceholder: e.maxTagPlaceholder ? T({
        slots: e,
        key: "maxTagPlaceholder"
      }) : y || u,
      allowClear: e["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ g.jsx(E, {
          slot: e["allowClear.clearIcon"]
        })
      } : a.allowClear
    })]
  });
}));
export {
  Tn as Cascader,
  Tn as default
};
