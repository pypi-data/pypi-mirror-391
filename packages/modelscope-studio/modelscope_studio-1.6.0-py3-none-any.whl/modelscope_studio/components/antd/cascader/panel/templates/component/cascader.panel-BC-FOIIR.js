import { i as ce, a as M, r as ue, b as de, Z as R, g as fe } from "./Index-O9jOIzPa.js";
const y = window.ms_globals.React, ie = window.ms_globals.React.forwardRef, A = window.ms_globals.React.useRef, $ = window.ms_globals.React.useState, F = window.ms_globals.React.useEffect, ae = window.ms_globals.React.useMemo, W = window.ms_globals.ReactDOM.createPortal, me = window.ms_globals.internalContext.useContextPropsContext, U = window.ms_globals.internalContext.ContextPropsProvider, _e = window.ms_globals.antd.Cascader, he = window.ms_globals.createItemsContext.createItemsContext;
var pe = /\s/;
function ge(t) {
  for (var e = t.length; e-- && pe.test(t.charAt(e)); )
    ;
  return e;
}
var be = /^\s+/;
function we(t) {
  return t && t.slice(0, ge(t) + 1).replace(be, "");
}
var B = NaN, xe = /^[-+]0x[0-9a-f]+$/i, Ce = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, ye = parseInt;
function H(t) {
  if (typeof t == "number")
    return t;
  if (ce(t))
    return B;
  if (M(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = M(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = we(t);
  var o = Ce.test(t);
  return o || Ee.test(t) ? ye(t.slice(2), o ? 2 : 8) : xe.test(t) ? B : +t;
}
var L = function() {
  return ue.Date.now();
}, ve = "Expected a function", Ie = Math.max, Pe = Math.min;
function Se(t, e, o) {
  var s, l, n, r, i, c, h = 0, b = !1, a = !1, p = !0;
  if (typeof t != "function")
    throw new TypeError(ve);
  e = H(e) || 0, M(o) && (b = !!o.leading, a = "maxWait" in o, n = a ? Ie(H(o.maxWait) || 0, e) : n, p = "trailing" in o ? !!o.trailing : p);
  function u(m) {
    var E = s, S = l;
    return s = l = void 0, h = m, r = t.apply(S, E), r;
  }
  function w(m) {
    return h = m, i = setTimeout(_, e), b ? u(m) : r;
  }
  function C(m) {
    var E = m - c, S = m - h, V = e - E;
    return a ? Pe(V, n - S) : V;
  }
  function d(m) {
    var E = m - c, S = m - h;
    return c === void 0 || E >= e || E < 0 || a && S >= n;
  }
  function _() {
    var m = L();
    if (d(m))
      return g(m);
    i = setTimeout(_, C(m));
  }
  function g(m) {
    return i = void 0, p && s ? u(m) : (s = l = void 0, r);
  }
  function v() {
    i !== void 0 && clearTimeout(i), h = 0, s = c = l = i = void 0;
  }
  function f() {
    return i === void 0 ? r : g(L());
  }
  function I() {
    var m = L(), E = d(m);
    if (s = arguments, l = this, c = m, E) {
      if (i === void 0)
        return w(c);
      if (a)
        return clearTimeout(i), i = setTimeout(_, e), u(c);
    }
    return i === void 0 && (i = setTimeout(_, e)), r;
  }
  return I.cancel = v, I.flush = f, I;
}
function Re(t, e) {
  return de(t, e);
}
var ee = {
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
var Te = y, ke = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Le = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function te(t, e, o) {
  var s, l = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (r = e.ref);
  for (s in e) je.call(e, s) && !Ne.hasOwnProperty(s) && (l[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) l[s] === void 0 && (l[s] = e[s]);
  return {
    $$typeof: ke,
    type: t,
    key: n,
    ref: r,
    props: l,
    _owner: Le.current
  };
}
j.Fragment = Oe;
j.jsx = te;
j.jsxs = te;
ee.exports = j;
var x = ee.exports;
const {
  SvelteComponent: Ae,
  assign: q,
  binding_callbacks: G,
  check_outros: Fe,
  children: ne,
  claim_element: re,
  claim_space: We,
  component_subscribe: J,
  compute_slots: Me,
  create_slot: De,
  detach: P,
  element: le,
  empty: X,
  exclude_internal_props: Y,
  get_all_dirty_from_scope: ze,
  get_slot_changes: Ve,
  group_outros: Ue,
  init: Be,
  insert_hydration: T,
  safe_not_equal: He,
  set_custom_element_data: oe,
  space: qe,
  transition_in: k,
  transition_out: D,
  update_slot_base: Ge
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function Z(t) {
  let e, o;
  const s = (
    /*#slots*/
    t[7].default
  ), l = De(
    s,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = le("svelte-slot"), l && l.c(), this.h();
    },
    l(n) {
      e = re(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = ne(e);
      l && l.l(r), r.forEach(P), this.h();
    },
    h() {
      oe(e, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      T(n, e, r), l && l.m(e, null), t[9](e), o = !0;
    },
    p(n, r) {
      l && l.p && (!o || r & /*$$scope*/
      64) && Ge(
        l,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Ve(
          s,
          /*$$scope*/
          n[6],
          r,
          null
        ) : ze(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (k(l, n), o = !0);
    },
    o(n) {
      D(l, n), o = !1;
    },
    d(n) {
      n && P(e), l && l.d(n), t[9](null);
    }
  };
}
function Ke(t) {
  let e, o, s, l, n = (
    /*$$slots*/
    t[4].default && Z(t)
  );
  return {
    c() {
      e = le("react-portal-target"), o = qe(), n && n.c(), s = X(), this.h();
    },
    l(r) {
      e = re(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), ne(e).forEach(P), o = We(r), n && n.l(r), s = X(), this.h();
    },
    h() {
      oe(e, "class", "svelte-1rt0kpf");
    },
    m(r, i) {
      T(r, e, i), t[8](e), T(r, o, i), n && n.m(r, i), T(r, s, i), l = !0;
    },
    p(r, [i]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, i), i & /*$$slots*/
      16 && k(n, 1)) : (n = Z(r), n.c(), k(n, 1), n.m(s.parentNode, s)) : n && (Ue(), D(n, 1, 1, () => {
        n = null;
      }), Fe());
    },
    i(r) {
      l || (k(n), l = !0);
    },
    o(r) {
      D(n), l = !1;
    },
    d(r) {
      r && (P(e), P(o), P(s)), t[8](null), n && n.d(r);
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
function Qe(t, e, o) {
  let s, l, {
    $$slots: n = {},
    $$scope: r
  } = e;
  const i = Me(n);
  let {
    svelteInit: c
  } = e;
  const h = R(K(e)), b = R();
  J(t, b, (f) => o(0, s = f));
  const a = R();
  J(t, a, (f) => o(1, l = f));
  const p = [], u = Xe("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: C,
    subSlotIndex: d
  } = fe() || {}, _ = c({
    parent: u,
    props: h,
    target: b,
    slot: a,
    slotKey: w,
    slotIndex: C,
    subSlotIndex: d,
    onDestroy(f) {
      p.push(f);
    }
  });
  Ze("$$ms-gr-react-wrapper", _), Je(() => {
    h.set(K(e));
  }), Ye(() => {
    p.forEach((f) => f());
  });
  function g(f) {
    G[f ? "unshift" : "push"](() => {
      s = f, b.set(s);
    });
  }
  function v(f) {
    G[f ? "unshift" : "push"](() => {
      l = f, a.set(l);
    });
  }
  return t.$$set = (f) => {
    o(17, e = q(q({}, e), Y(f))), "svelteInit" in f && o(5, c = f.svelteInit), "$$scope" in f && o(6, r = f.$$scope);
  }, e = Y(e), [s, l, b, a, i, c, r, n, g, v];
}
class $e extends Ae {
  constructor(e) {
    super(), Be(this, e, Qe, Ke, He, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: dt
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, N = window.ms_globals.tree;
function et(t, e = {}) {
  function o(s) {
    const l = R(), n = new $e({
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
          }, c = r.parent ?? N;
          return c.nodes = [...c.nodes, i], Q({
            createPortal: W,
            node: N
          }), r.onDestroy(() => {
            c.nodes = c.nodes.filter((h) => h.svelteInstance !== l), Q({
              createPortal: W,
              node: N
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
const tt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function nt(t) {
  return t ? Object.keys(t).reduce((e, o) => {
    const s = t[o];
    return e[o] = rt(o, s), e;
  }, {}) : {};
}
function rt(t, e) {
  return typeof e == "number" && !tt.includes(t) ? e + "px" : e;
}
function z(t) {
  const e = [], o = t.cloneNode(!1);
  if (t._reactElement) {
    const l = y.Children.toArray(t._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: i
        } = z(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...y.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return l.originalChildren = t._reactElement.props.children, e.push(W(y.cloneElement(t._reactElement, {
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
      useCapture: c
    }) => {
      o.addEventListener(i, r, c);
    });
  });
  const s = Array.from(t.childNodes);
  for (let l = 0; l < s.length; l++) {
    const n = s[l];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: i
      } = z(n);
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
const O = ie(({
  slot: t,
  clone: e,
  className: o,
  style: s,
  observeAttributes: l
}, n) => {
  const r = A(), [i, c] = $([]), {
    forceClone: h
  } = me(), b = h ? !0 : e;
  return F(() => {
    var C;
    if (!r.current || !t)
      return;
    let a = t;
    function p() {
      let d = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (d = a.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), lt(n, d), o && d.classList.add(...o.split(" ")), s) {
        const _ = nt(s);
        Object.keys(_).forEach((g) => {
          d.style[g] = _[g];
        });
      }
    }
    let u = null, w = null;
    if (b && window.MutationObserver) {
      let d = function() {
        var f, I, m;
        (f = r.current) != null && f.contains(a) && ((I = r.current) == null || I.removeChild(a));
        const {
          portals: g,
          clonedElement: v
        } = z(t);
        a = v, c(g), a.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          p();
        }, 50), (m = r.current) == null || m.appendChild(a);
      };
      d();
      const _ = Se(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      u = new window.MutationObserver(_), u.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", p(), (C = r.current) == null || C.appendChild(a);
    return () => {
      var d, _;
      a.style.display = "", (d = r.current) != null && d.contains(a) && ((_ = r.current) == null || _.removeChild(a)), u == null || u.disconnect();
    };
  }, [t, b, o, s, n, l, h]), y.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...i);
});
function ot({
  value: t,
  onValueChange: e
}) {
  const [o, s] = $(t), l = A(e);
  l.current = e;
  const n = A(o);
  return n.current = o, F(() => {
    l.current(o);
  }, [o]), F(() => {
    Re(t, n.current) || s(t);
  }, [t]), [o, s];
}
const st = ({
  children: t,
  ...e
}) => /* @__PURE__ */ x.jsx(x.Fragment, {
  children: t(e)
});
function it(t) {
  return y.createElement(st, {
    children: t
  });
}
function se(t, e, o) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((l, n) => {
      var h, b;
      if (typeof l != "object")
        return e != null && e.fallback ? e.fallback(l) : l;
      const r = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...l.props,
        key: ((h = l.props) == null ? void 0 : h.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...l.props,
        key: ((b = l.props) == null ? void 0 : b.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let i = r;
      Object.keys(l.slots).forEach((a) => {
        if (!l.slots[a] || !(l.slots[a] instanceof Element) && !l.slots[a].el)
          return;
        const p = a.split(".");
        p.forEach((g, v) => {
          i[g] || (i[g] = {}), v !== p.length - 1 && (i = r[g]);
        });
        const u = l.slots[a];
        let w, C, d = (e == null ? void 0 : e.clone) ?? !1, _ = e == null ? void 0 : e.forceClone;
        u instanceof Element ? w = u : (w = u.el, C = u.callback, d = u.clone ?? d, _ = u.forceClone ?? _), _ = _ ?? !!C, i[p[p.length - 1]] = w ? C ? (...g) => (C(p[p.length - 1], g), /* @__PURE__ */ x.jsx(U, {
          ...l.ctx,
          params: g,
          forceClone: _,
          children: /* @__PURE__ */ x.jsx(O, {
            slot: w,
            clone: d
          })
        })) : it((g) => /* @__PURE__ */ x.jsx(U, {
          ...l.ctx,
          forceClone: _,
          children: /* @__PURE__ */ x.jsx(O, {
            ...g,
            slot: w,
            clone: d
          })
        })) : i[p[p.length - 1]], i = r;
      });
      const c = (e == null ? void 0 : e.children) || "children";
      return l[c] ? r[c] = se(l[c], e, `${n}`) : e != null && e.children && (r[c] = void 0, Reflect.deleteProperty(r, c)), r;
    });
}
const {
  useItems: at,
  withItemsContextProvider: ct,
  ItemHandler: ft
} = he("antd-cascader-options"), mt = et(ct(["default", "options"], ({
  slots: t,
  children: e,
  onValueChange: o,
  onChange: s,
  onLoadData: l,
  options: n,
  ...r
}) => {
  const [i, c] = ot({
    onValueChange: o,
    value: r.value
  }), {
    items: h
  } = at(), b = h.options.length > 0 ? h.options : h.default;
  return /* @__PURE__ */ x.jsxs(x.Fragment, {
    children: [/* @__PURE__ */ x.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ x.jsx(_e.Panel, {
      ...r,
      value: i,
      options: ae(() => n || se(b, {
        clone: !0
      }), [n, b]),
      loadData: l,
      onChange: (a, ...p) => {
        s == null || s(a, ...p), c(a);
      },
      expandIcon: t.expandIcon ? /* @__PURE__ */ x.jsx(O, {
        slot: t.expandIcon
      }) : r.expandIcon,
      notFoundContent: t.notFoundContent ? /* @__PURE__ */ x.jsx(O, {
        slot: t.notFoundContent
      }) : r.notFoundContent
    })]
  });
}));
export {
  mt as CascaderPanel,
  mt as default
};
