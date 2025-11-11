import { i as ce, a as B, r as ue, b as de, Z as O, g as fe, c as me } from "./Index--TCIXUom.js";
const v = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, N = window.ms_globals.React.useRef, ee = window.ms_globals.React.useState, W = window.ms_globals.React.useEffect, te = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, he = window.ms_globals.internalContext.ContextPropsProvider, pe = window.ms_globals.antd.Input;
var ge = /\s/;
function we(e) {
  for (var t = e.length; t-- && ge.test(e.charAt(t)); )
    ;
  return t;
}
var xe = /^\s+/;
function be(e) {
  return e && e.slice(0, we(e) + 1).replace(xe, "");
}
var V = NaN, ye = /^[-+]0x[0-9a-f]+$/i, ve = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Ce = parseInt;
function q(e) {
  if (typeof e == "number")
    return e;
  if (ce(e))
    return V;
  if (B(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = B(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = be(e);
  var n = ve.test(e);
  return n || Ee.test(e) ? Ce(e.slice(2), n ? 2 : 8) : ye.test(e) ? V : +e;
}
var L = function() {
  return ue.Date.now();
}, Ie = "Expected a function", Se = Math.max, Re = Math.min;
function Pe(e, t, n) {
  var i, s, r, o, l, c, h = 0, g = !1, a = !1, w = !0;
  if (typeof e != "function")
    throw new TypeError(Ie);
  t = q(t) || 0, B(n) && (g = !!n.leading, a = "maxWait" in n, r = a ? Se(q(n.maxWait) || 0, t) : r, w = "trailing" in n ? !!n.trailing : w);
  function f(d) {
    var E = i, P = s;
    return i = s = void 0, h = d, o = e.apply(P, E), o;
  }
  function x(d) {
    return h = d, l = setTimeout(p, t), g ? f(d) : o;
  }
  function b(d) {
    var E = d - c, P = d - h, U = t - E;
    return a ? Re(U, r - P) : U;
  }
  function m(d) {
    var E = d - c, P = d - h;
    return c === void 0 || E >= t || E < 0 || a && P >= r;
  }
  function p() {
    var d = L();
    if (m(d))
      return y(d);
    l = setTimeout(p, b(d));
  }
  function y(d) {
    return l = void 0, w && i ? f(d) : (i = s = void 0, o);
  }
  function R() {
    l !== void 0 && clearTimeout(l), h = 0, i = c = s = l = void 0;
  }
  function u() {
    return l === void 0 ? o : y(L());
  }
  function I() {
    var d = L(), E = m(d);
    if (i = arguments, s = this, c = d, E) {
      if (l === void 0)
        return x(c);
      if (a)
        return clearTimeout(l), l = setTimeout(p, t), f(c);
    }
    return l === void 0 && (l = setTimeout(p, t)), o;
  }
  return I.cancel = R, I.flush = u, I;
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
var Oe = v, je = Symbol.for("react.element"), ke = Symbol.for("react.fragment"), Fe = Object.prototype.hasOwnProperty, Le = Oe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ae = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function re(e, t, n) {
  var i, s = {}, r = null, o = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (i in t) Fe.call(t, i) && !Ae.hasOwnProperty(i) && (s[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) s[i] === void 0 && (s[i] = t[i]);
  return {
    $$typeof: je,
    type: e,
    key: r,
    ref: o,
    props: s,
    _owner: Le.current
  };
}
F.Fragment = ke;
F.jsx = re;
F.jsxs = re;
ne.exports = F;
var _ = ne.exports;
const {
  SvelteComponent: Ne,
  assign: G,
  binding_callbacks: H,
  check_outros: We,
  children: oe,
  claim_element: ie,
  claim_space: Me,
  component_subscribe: K,
  compute_slots: Be,
  create_slot: ze,
  detach: S,
  element: se,
  empty: J,
  exclude_internal_props: X,
  get_all_dirty_from_scope: De,
  get_slot_changes: Ue,
  group_outros: Ve,
  init: qe,
  insert_hydration: j,
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
  const i = (
    /*#slots*/
    e[7].default
  ), s = ze(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = se("svelte-slot"), s && s.c(), this.h();
    },
    l(r) {
      t = ie(r, "SVELTE-SLOT", {
        class: !0
      });
      var o = oe(t);
      s && s.l(o), o.forEach(S), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(r, o) {
      j(r, t, o), s && s.m(t, null), e[9](t), n = !0;
    },
    p(r, o) {
      s && s.p && (!n || o & /*$$scope*/
      64) && Ke(
        s,
        i,
        r,
        /*$$scope*/
        r[6],
        n ? Ue(
          i,
          /*$$scope*/
          r[6],
          o,
          null
        ) : De(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      n || (k(s, r), n = !0);
    },
    o(r) {
      z(s, r), n = !1;
    },
    d(r) {
      r && S(t), s && s.d(r), e[9](null);
    }
  };
}
function Qe(e) {
  let t, n, i, s, r = (
    /*$$slots*/
    e[4].default && Y(e)
  );
  return {
    c() {
      t = se("react-portal-target"), n = He(), r && r.c(), i = J(), this.h();
    },
    l(o) {
      t = ie(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), oe(t).forEach(S), n = Me(o), r && r.l(o), i = J(), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      j(o, t, l), e[8](t), j(o, n, l), r && r.m(o, l), j(o, i, l), s = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? r ? (r.p(o, l), l & /*$$slots*/
      16 && k(r, 1)) : (r = Y(o), r.c(), k(r, 1), r.m(i.parentNode, i)) : r && (Ve(), z(r, 1, 1, () => {
        r = null;
      }), We());
    },
    i(o) {
      s || (k(r), s = !0);
    },
    o(o) {
      z(r), s = !1;
    },
    d(o) {
      o && (S(t), S(n), S(i)), e[8](null), r && r.d(o);
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
  let i, s, {
    $$slots: r = {},
    $$scope: o
  } = t;
  const l = Be(r);
  let {
    svelteInit: c
  } = t;
  const h = O(Z(t)), g = O();
  K(e, g, (u) => n(0, i = u));
  const a = O();
  K(e, a, (u) => n(1, s = u));
  const w = [], f = Xe("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: b,
    subSlotIndex: m
  } = fe() || {}, p = c({
    parent: f,
    props: h,
    target: g,
    slot: a,
    slotKey: x,
    slotIndex: b,
    subSlotIndex: m,
    onDestroy(u) {
      w.push(u);
    }
  });
  Ze("$$ms-gr-react-wrapper", p), Je(() => {
    h.set(Z(t));
  }), Ye(() => {
    w.forEach((u) => u());
  });
  function y(u) {
    H[u ? "unshift" : "push"](() => {
      i = u, g.set(i);
    });
  }
  function R(u) {
    H[u ? "unshift" : "push"](() => {
      s = u, a.set(s);
    });
  }
  return e.$$set = (u) => {
    n(17, t = G(G({}, t), X(u))), "svelteInit" in u && n(5, c = u.svelteInit), "$$scope" in u && n(6, o = u.$$scope);
  }, t = X(t), [i, s, g, a, l, c, o, r, y, R];
}
class et extends Ne {
  constructor(t) {
    super(), qe(this, t, $e, Qe, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, A = window.ms_globals.tree;
function tt(e, t = {}) {
  function n(i) {
    const s = O(), r = new et({
      ...i,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? A;
          return c.nodes = [...c.nodes, l], Q({
            createPortal: M,
            node: A
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((h) => h.svelteInstance !== s), Q({
              createPortal: M,
              node: A
            });
          }), l;
        },
        ...i.props
      }
    });
    return s.set(r), r;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((s) => {
      window.ms_globals.initialize = () => {
        s();
      };
    })), window.ms_globals.initializePromise.then(() => {
      i(n);
    });
  });
}
const nt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function rt(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const i = e[n];
    return t[n] = ot(n, i), t;
  }, {}) : {};
}
function ot(e, t) {
  return typeof t == "number" && !nt.includes(e) ? t + "px" : t;
}
function D(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const s = v.Children.toArray(e._reactElement.props.children).map((r) => {
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
    return s.originalChildren = e._reactElement.props.children, t.push(M(v.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: s
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((s) => {
    e.getEventListeners(s).forEach(({
      listener: o,
      type: l,
      useCapture: c
    }) => {
      n.addEventListener(l, o, c);
    });
  });
  const i = Array.from(e.childNodes);
  for (let s = 0; s < i.length; s++) {
    const r = i[s];
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
function it(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const C = ae(({
  slot: e,
  clone: t,
  className: n,
  style: i,
  observeAttributes: s
}, r) => {
  const o = N(), [l, c] = ee([]), {
    forceClone: h
  } = _e(), g = h ? !0 : t;
  return W(() => {
    var b;
    if (!o.current || !e)
      return;
    let a = e;
    function w() {
      let m = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (m = a.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), it(r, m), n && m.classList.add(...n.split(" ")), i) {
        const p = rt(i);
        Object.keys(p).forEach((y) => {
          m.style[y] = p[y];
        });
      }
    }
    let f = null, x = null;
    if (g && window.MutationObserver) {
      let m = function() {
        var u, I, d;
        (u = o.current) != null && u.contains(a) && ((I = o.current) == null || I.removeChild(a));
        const {
          portals: y,
          clonedElement: R
        } = D(e);
        a = R, c(y), a.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          w();
        }, 50), (d = o.current) == null || d.appendChild(a);
      };
      m();
      const p = Pe(() => {
        m(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      f = new window.MutationObserver(p), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", w(), (b = o.current) == null || b.appendChild(a);
    return () => {
      var m, p;
      a.style.display = "", (m = o.current) != null && m.contains(a) && ((p = o.current) == null || p.removeChild(a)), f == null || f.disconnect();
    };
  }, [e, g, n, i, r, s, h]), v.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
});
function st(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function lt(e, t = !1) {
  try {
    if (me(e))
      return e;
    if (t && !st(e))
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
function T(e, t) {
  return te(() => lt(e, t), [e, t]);
}
function at({
  value: e,
  onValueChange: t
}) {
  const [n, i] = ee(e), s = N(t);
  s.current = t;
  const r = N(n);
  return r.current = n, W(() => {
    s.current(n);
  }, [n]), W(() => {
    Te(e, r.current) || i(e);
  }, [e]), [n, i];
}
function ct(e, t) {
  return Object.keys(e).reduce((n, i) => (e[i] !== void 0 && (n[i] = e[i]), n), {});
}
const ut = ({
  children: e,
  ...t
}) => /* @__PURE__ */ _.jsx(_.Fragment, {
  children: e(t)
});
function dt(e) {
  return v.createElement(ut, {
    children: e
  });
}
function $(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? dt((n) => /* @__PURE__ */ _.jsx(he, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ _.jsx(C, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ _.jsx(C, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function ft({
  key: e,
  slots: t,
  targets: n
}, i) {
  return t[e] ? (...s) => n ? n.map((r, o) => /* @__PURE__ */ _.jsx(v.Fragment, {
    children: $(r, {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ _.jsx(_.Fragment, {
    children: $(t[e], {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }) : void 0;
}
const ht = tt(({
  slots: e,
  children: t,
  count: n,
  showCount: i,
  onValueChange: s,
  onChange: r,
  setSlotParams: o,
  elRef: l,
  ...c
}) => {
  const h = T(n == null ? void 0 : n.strategy), g = T(n == null ? void 0 : n.exceedFormatter), a = T(n == null ? void 0 : n.show), w = T(typeof i == "object" ? i.formatter : void 0), [f, x] = at({
    onValueChange: s,
    value: c.value
  });
  return /* @__PURE__ */ _.jsxs(_.Fragment, {
    children: [/* @__PURE__ */ _.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ _.jsx(pe, {
      ...c,
      value: f,
      ref: l,
      onChange: (b) => {
        r == null || r(b), x(b.target.value);
      },
      showCount: e["showCount.formatter"] ? {
        formatter: ft({
          slots: e,
          key: "showCount.formatter"
        })
      } : typeof i == "object" && w ? {
        ...i,
        formatter: w
      } : i,
      count: te(() => ct({
        ...n,
        exceedFormatter: g,
        strategy: h,
        show: a || (n == null ? void 0 : n.show)
      }), [n, g, h, a]),
      addonAfter: e.addonAfter ? /* @__PURE__ */ _.jsx(C, {
        slot: e.addonAfter
      }) : c.addonAfter,
      addonBefore: e.addonBefore ? /* @__PURE__ */ _.jsx(C, {
        slot: e.addonBefore
      }) : c.addonBefore,
      allowClear: e["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ _.jsx(C, {
          slot: e["allowClear.clearIcon"]
        })
      } : c.allowClear,
      prefix: e.prefix ? /* @__PURE__ */ _.jsx(C, {
        slot: e.prefix
      }) : c.prefix,
      suffix: e.suffix ? /* @__PURE__ */ _.jsx(C, {
        slot: e.suffix
      }) : c.suffix
    })]
  });
});
export {
  ht as Input,
  ht as default
};
