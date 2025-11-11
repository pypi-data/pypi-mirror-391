import { i as ce, a as M, r as ue, b as de, Z as T, g as fe, c as me } from "./Index-BFrVRFBt.js";
const v = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, N = window.ms_globals.React.useRef, ee = window.ms_globals.React.useState, W = window.ms_globals.React.useEffect, te = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, he = window.ms_globals.internalContext.ContextPropsProvider, pe = window.ms_globals.antd.Input;
var ge = /\s/;
function we(e) {
  for (var t = e.length; t-- && ge.test(e.charAt(t)); )
    ;
  return t;
}
var be = /^\s+/;
function ye(e) {
  return e && e.slice(0, we(e) + 1).replace(be, "");
}
var q = NaN, xe = /^[-+]0x[0-9a-f]+$/i, ve = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Ce = parseInt;
function B(e) {
  if (typeof e == "number")
    return e;
  if (ce(e))
    return q;
  if (M(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = M(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ye(e);
  var n = ve.test(e);
  return n || Ee.test(e) ? Ce(e.slice(2), n ? 2 : 8) : xe.test(e) ? q : +e;
}
var j = function() {
  return ue.Date.now();
}, Ie = "Expected a function", Se = Math.max, Re = Math.min;
function Pe(e, t, n) {
  var s, i, r, o, l, c, _ = 0, p = !1, a = !1, w = !0;
  if (typeof e != "function")
    throw new TypeError(Ie);
  t = B(t) || 0, M(n) && (p = !!n.leading, a = "maxWait" in n, r = a ? Se(B(n.maxWait) || 0, t) : r, w = "trailing" in n ? !!n.trailing : w);
  function f(d) {
    var E = s, R = i;
    return s = i = void 0, _ = d, o = e.apply(R, E), o;
  }
  function b(d) {
    return _ = d, l = setTimeout(h, t), p ? f(d) : o;
  }
  function y(d) {
    var E = d - c, R = d - _, V = t - E;
    return a ? Re(V, r - R) : V;
  }
  function m(d) {
    var E = d - c, R = d - _;
    return c === void 0 || E >= t || E < 0 || a && R >= r;
  }
  function h() {
    var d = j();
    if (m(d))
      return x(d);
    l = setTimeout(h, y(d));
  }
  function x(d) {
    return l = void 0, w && s ? f(d) : (s = i = void 0, o);
  }
  function S() {
    l !== void 0 && clearTimeout(l), _ = 0, s = c = i = l = void 0;
  }
  function u() {
    return l === void 0 ? o : x(j());
  }
  function C() {
    var d = j(), E = m(d);
    if (s = arguments, i = this, c = d, E) {
      if (l === void 0)
        return b(c);
      if (a)
        return clearTimeout(l), l = setTimeout(h, t), f(c);
    }
    return l === void 0 && (l = setTimeout(h, t)), o;
  }
  return C.cancel = S, C.flush = u, C;
}
function Te(e, t) {
  return de(e, t);
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
var Oe = v, ke = Symbol.for("react.element"), Fe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Le = Oe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function re(e, t, n) {
  var s, i = {}, r = null, o = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (s in t) je.call(t, s) && !Ne.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: ke,
    type: e,
    key: r,
    ref: o,
    props: i,
    _owner: Le.current
  };
}
F.Fragment = Fe;
F.jsx = re;
F.jsxs = re;
ne.exports = F;
var g = ne.exports;
const {
  SvelteComponent: We,
  assign: G,
  binding_callbacks: H,
  check_outros: Ae,
  children: oe,
  claim_element: se,
  claim_space: Me,
  component_subscribe: K,
  compute_slots: ze,
  create_slot: De,
  detach: I,
  element: ie,
  empty: J,
  exclude_internal_props: X,
  get_all_dirty_from_scope: Ue,
  get_slot_changes: Ve,
  group_outros: qe,
  init: Be,
  insert_hydration: O,
  safe_not_equal: Ge,
  set_custom_element_data: le,
  space: He,
  transition_in: k,
  transition_out: z,
  update_slot_base: Ke
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function Y(e) {
  let t, n;
  const s = (
    /*#slots*/
    e[7].default
  ), i = De(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ie("svelte-slot"), i && i.c(), this.h();
    },
    l(r) {
      t = se(r, "SVELTE-SLOT", {
        class: !0
      });
      var o = oe(t);
      i && i.l(o), o.forEach(I), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(r, o) {
      O(r, t, o), i && i.m(t, null), e[9](t), n = !0;
    },
    p(r, o) {
      i && i.p && (!n || o & /*$$scope*/
      64) && Ke(
        i,
        s,
        r,
        /*$$scope*/
        r[6],
        n ? Ve(
          s,
          /*$$scope*/
          r[6],
          o,
          null
        ) : Ue(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      n || (k(i, r), n = !0);
    },
    o(r) {
      z(i, r), n = !1;
    },
    d(r) {
      r && I(t), i && i.d(r), e[9](null);
    }
  };
}
function Qe(e) {
  let t, n, s, i, r = (
    /*$$slots*/
    e[4].default && Y(e)
  );
  return {
    c() {
      t = ie("react-portal-target"), n = He(), r && r.c(), s = J(), this.h();
    },
    l(o) {
      t = se(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), oe(t).forEach(I), n = Me(o), r && r.l(o), s = J(), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      O(o, t, l), e[8](t), O(o, n, l), r && r.m(o, l), O(o, s, l), i = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? r ? (r.p(o, l), l & /*$$slots*/
      16 && k(r, 1)) : (r = Y(o), r.c(), k(r, 1), r.m(s.parentNode, s)) : r && (qe(), z(r, 1, 1, () => {
        r = null;
      }), Ae());
    },
    i(o) {
      i || (k(r), i = !0);
    },
    o(o) {
      z(r), i = !1;
    },
    d(o) {
      o && (I(t), I(n), I(s)), e[8](null), r && r.d(o);
    }
  };
}
function Z(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function $e(e, t, n) {
  let s, i, {
    $$slots: r = {},
    $$scope: o
  } = t;
  const l = ze(r);
  let {
    svelteInit: c
  } = t;
  const _ = T(Z(t)), p = T();
  K(e, p, (u) => n(0, s = u));
  const a = T();
  K(e, a, (u) => n(1, i = u));
  const w = [], f = Xe("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: y,
    subSlotIndex: m
  } = fe() || {}, h = c({
    parent: f,
    props: _,
    target: p,
    slot: a,
    slotKey: b,
    slotIndex: y,
    subSlotIndex: m,
    onDestroy(u) {
      w.push(u);
    }
  });
  Ze("$$ms-gr-react-wrapper", h), Je(() => {
    _.set(Z(t));
  }), Ye(() => {
    w.forEach((u) => u());
  });
  function x(u) {
    H[u ? "unshift" : "push"](() => {
      s = u, p.set(s);
    });
  }
  function S(u) {
    H[u ? "unshift" : "push"](() => {
      i = u, a.set(i);
    });
  }
  return e.$$set = (u) => {
    n(17, t = G(G({}, t), X(u))), "svelteInit" in u && n(5, c = u.svelteInit), "$$scope" in u && n(6, o = u.$$scope);
  }, t = X(t), [s, i, p, a, l, c, o, r, x, S];
}
class et extends We {
  constructor(t) {
    super(), Be(this, t, $e, Qe, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, L = window.ms_globals.tree;
function tt(e, t = {}) {
  function n(s) {
    const i = T(), r = new et({
      ...s,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? L;
          return c.nodes = [...c.nodes, l], Q({
            createPortal: A,
            node: L
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((_) => _.svelteInstance !== i), Q({
              createPortal: A,
              node: L
            });
          }), l;
        },
        ...s.props
      }
    });
    return i.set(r), r;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((i) => {
      window.ms_globals.initialize = () => {
        i();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(n);
    });
  });
}
const nt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function rt(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const s = e[n];
    return t[n] = ot(n, s), t;
  }, {}) : {};
}
function ot(e, t) {
  return typeof t == "number" && !nt.includes(e) ? t + "px" : t;
}
function D(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const i = v.Children.toArray(e._reactElement.props.children).map((r) => {
      if (v.isValidElement(r) && r.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = D(r.props.el);
        return v.cloneElement(r, {
          ...r.props,
          el: l,
          children: [...v.Children.toArray(r.props.children), ...o]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(A(v.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: i
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((i) => {
    e.getEventListeners(i).forEach(({
      listener: o,
      type: l,
      useCapture: c
    }) => {
      n.addEventListener(l, o, c);
    });
  });
  const s = Array.from(e.childNodes);
  for (let i = 0; i < s.length; i++) {
    const r = s[i];
    if (r.nodeType === 1) {
      const {
        clonedElement: o,
        portals: l
      } = D(r);
      t.push(...l), n.appendChild(o);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function st(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const U = ae(({
  slot: e,
  clone: t,
  className: n,
  style: s,
  observeAttributes: i
}, r) => {
  const o = N(), [l, c] = ee([]), {
    forceClone: _
  } = _e(), p = _ ? !0 : t;
  return W(() => {
    var y;
    if (!o.current || !e)
      return;
    let a = e;
    function w() {
      let m = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (m = a.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), st(r, m), n && m.classList.add(...n.split(" ")), s) {
        const h = rt(s);
        Object.keys(h).forEach((x) => {
          m.style[x] = h[x];
        });
      }
    }
    let f = null, b = null;
    if (p && window.MutationObserver) {
      let m = function() {
        var u, C, d;
        (u = o.current) != null && u.contains(a) && ((C = o.current) == null || C.removeChild(a));
        const {
          portals: x,
          clonedElement: S
        } = D(e);
        a = S, c(x), a.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          w();
        }, 50), (d = o.current) == null || d.appendChild(a);
      };
      m();
      const h = Pe(() => {
        m(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      f = new window.MutationObserver(h), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", w(), (y = o.current) == null || y.appendChild(a);
    return () => {
      var m, h;
      a.style.display = "", (m = o.current) != null && m.contains(a) && ((h = o.current) == null || h.removeChild(a)), f == null || f.disconnect();
    };
  }, [e, p, n, s, r, i, _]), v.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
});
function it(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function lt(e, t = !1) {
  try {
    if (me(e))
      return e;
    if (t && !it(e))
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
function P(e, t) {
  return te(() => lt(e, t), [e, t]);
}
function at({
  value: e,
  onValueChange: t
}) {
  const [n, s] = ee(e), i = N(t);
  i.current = t;
  const r = N(n);
  return r.current = n, W(() => {
    i.current(n);
  }, [n]), W(() => {
    Te(e, r.current) || s(e);
  }, [e]), [n, s];
}
function ct(e, t) {
  return Object.keys(e).reduce((n, s) => (e[s] !== void 0 && (n[s] = e[s]), n), {});
}
const ut = ({
  children: e,
  ...t
}) => /* @__PURE__ */ g.jsx(g.Fragment, {
  children: e(t)
});
function dt(e) {
  return v.createElement(ut, {
    children: e
  });
}
function $(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? dt((n) => /* @__PURE__ */ g.jsx(he, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ g.jsx(U, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ g.jsx(U, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function ft({
  key: e,
  slots: t,
  targets: n
}, s) {
  return t[e] ? (...i) => n ? n.map((r, o) => /* @__PURE__ */ g.jsx(v.Fragment, {
    children: $(r, {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ g.jsx(g.Fragment, {
    children: $(t[e], {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }) : void 0;
}
const ht = tt(({
  slots: e,
  children: t,
  count: n,
  showCount: s,
  onValueChange: i,
  onChange: r,
  elRef: o,
  setSlotParams: l,
  ...c
}) => {
  const _ = P(n == null ? void 0 : n.strategy), p = P(n == null ? void 0 : n.exceedFormatter), a = P(n == null ? void 0 : n.show), w = P(typeof s == "object" ? s.formatter : void 0), [f, b] = at({
    onValueChange: i,
    value: c.value
  });
  return /* @__PURE__ */ g.jsxs(g.Fragment, {
    children: [/* @__PURE__ */ g.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ g.jsx(pe.TextArea, {
      ...c,
      ref: o,
      value: f,
      onChange: (y) => {
        r == null || r(y), b(y.target.value);
      },
      showCount: e["showCount.formatter"] ? {
        formatter: ft({
          slots: e,
          key: "showCount.formatter"
        })
      } : typeof s == "object" && w ? {
        ...s,
        formatter: w
      } : s,
      count: te(() => ct({
        ...n,
        exceedFormatter: p,
        strategy: _,
        show: a || (n == null ? void 0 : n.show)
      }), [n, p, _, a]),
      allowClear: e["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ g.jsx(U, {
          slot: e["allowClear.clearIcon"]
        })
      } : c.allowClear
    })]
  });
});
export {
  ht as InputTextarea,
  ht as default
};
